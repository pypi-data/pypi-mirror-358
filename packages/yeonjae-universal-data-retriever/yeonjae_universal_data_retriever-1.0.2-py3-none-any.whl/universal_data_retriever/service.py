"""
DataRetriever 서비스

다양한 조건과 필터를 사용하여 저장된 데이터를 조회하는 범용 조회 모듈입니다.
개발자별, 날짜별, 프로젝트별 커밋 데이터와 diff 정보를 조회하며,
효율적인 쿼리 최적화 및 캐싱 지원을 제공합니다.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy import select, func, and_, or_, text
from sqlalchemy.orm import Session

# Database configuration - standalone implementation
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
import os

# Create base for models
Base = declarative_base()

def get_session():
    """Get database session - standalone implementation"""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# Simplified Event model for standalone operation
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    pusher = Column(String, index=True)
    author_email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    commit_sha = Column(String)
    payload = Column(Text)
    ref = Column(String)
    repository = Column(String)
    files_changed = Column(Integer, default=0)
    added_lines = Column(Integer, default=0)
    deleted_lines = Column(Integer, default=0)

from .models import (
    QueryParams,
    FilterCondition,
    FilterOperator,
    SortOption,
    SortDirection,
    PaginationConfig,
    RetrievalResult,
    CommitQueryResult,
    DiffQueryResult,
    CommitInfo,
    DiffInfo,
    DeveloperStatistics,
    QueryMetadata,
    ActiveDeveloper,
    DateRangeQuery,
    AggregationResult
)
from .exceptions import (
    DataRetrieverException,
    InvalidQueryException,
    DataNotFoundException,
    QueryExecutionException,
    DatabaseConnectionException,
    FilterValidationException
)


class CacheManager:
    """간단한 메모리 캐시 매니저"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        if key in self._cache:
            cache_entry = self._cache[key]
            # TTL 확인
            if cache_entry['expires_at'] > time.time():
                self.logger.debug(f"Cache hit for key: {key}")
                return cache_entry['data']
            else:
                # 만료된 캐시 제거
                del self._cache[key]
                self.logger.debug(f"Cache expired for key: {key}")
        
        self.logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, data: Any, ttl: int = 3600) -> None:
        """캐시에 데이터 저장"""
        self._cache[key] = {
            'data': data,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        self.logger.debug(f"Cache set for key: {key}, TTL: {ttl}")
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        self._cache.clear()
        self.logger.info("Cache cleared")


class DataRetrieverService:
    """데이터 조회 서비스"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        DataRetrieverService 초기화
        
        Args:
            db_session: 데이터베이스 세션 (선택적, 테스트용)
        """
        self.db_session = db_session
        self.cache_manager = CacheManager()
        self.logger = logging.getLogger(__name__)
    
    def get_commits_by_developer(
        self,
        developer_id: str,
        date_range: Dict[str, datetime],
        include_statistics: bool = True
    ) -> CommitQueryResult:
        """
        개발자별 커밋 데이터 조회
        
        Args:
            developer_id: 개발자 식별자
            date_range: 조회 날짜 범위
            include_statistics: 통계 포함 여부
            
        Returns:
            CommitQueryResult: 커밋 조회 결과
        """
        start_time = time.time()
        
        try:
            # 캐시 키 생성
            cache_key = self._generate_cache_key("commits_by_developer", {
                "developer_id": developer_id,
                "date_range": date_range
            })
            
            # 캐시 확인
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                return CommitQueryResult(**cached_result)
            
            # 데이터베이스 조회
            with self._get_session() as session:
                query = select(Event).where(
                    and_(
                        Event.pusher == developer_id,
                        Event.created_at >= date_range['start'],
                        Event.created_at <= date_range['end']
                    )
                ).order_by(Event.created_at.desc())
                
                events = session.execute(query).scalars().all()
                
                # 커밋 정보 변환
                commits = []
                for event in events:
                    # 이벤트 데이터에서 커밋 정보 추출
                    event_data = json.loads(event.payload) if event.payload else {}
                    
                    # ref에서 브랜치명 추출 (refs/heads/main -> main)
                    branch = event.ref.split('/')[-1] if event.ref else 'main'
                    
                    # head_commit 또는 commits 배열에서 커밋 정보 추출
                    head_commit = event_data.get('head_commit', {})
                    if not head_commit and event_data.get('commits'):
                        head_commit = event_data['commits'][-1]  # 마지막 커밋 사용
                    
                    commit_info = CommitInfo(
                        commit_id=str(event.id),
                        commit_hash=event.commit_sha or head_commit.get('id', ''),
                        message=head_commit.get('message', ''),
                        author=event.pusher,
                        author_email=event.author_email or head_commit.get('author', {}).get('email', ''),
                        timestamp=event.created_at,
                        repository=event.repository,
                        branch=branch,
                        file_count=event.files_changed or len(head_commit.get('modified', [])),
                        lines_added=event.added_lines or 0,
                        lines_deleted=event.deleted_lines or 0
                    )
                    commits.append(commit_info)
                
                query_time = time.time() - start_time
                
                # 메타데이터 생성
                metadata = QueryMetadata(
                    query_time_seconds=query_time,
                    total_records=len(events),
                    returned_records=len(commits),
                    filters_applied=[f"developer_id={developer_id}", "date_range"],
                    cache_hit=False,
                    query_hash=cache_key
                )
                
                result = CommitQueryResult(
                    commits=commits,
                    metadata=metadata
                )
                
                # 결과 캐싱
                self.cache_manager.set(cache_key, result.dict(), ttl=3600)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to get commits by developer {developer_id}: {e}")
            raise QueryExecutionException("commits_by_developer", e)
    
    def get_diff_data(
        self,
        developer_id: Optional[str] = None,
        date_range: Optional[Dict[str, datetime]] = None,
        repository_name: Optional[str] = None
    ) -> DiffQueryResult:
        """
        Diff 데이터 조회
        
        Args:
            developer_id: 개발자 식별자
            date_range: 조회 날짜 범위
            repository_name: 저장소 이름
            
        Returns:
            DiffQueryResult: Diff 조회 결과
        """
        start_time = time.time()
        
        try:
            # 캐시 키 생성
            cache_key = self._generate_cache_key("diff_data", {
                "developer_id": developer_id,
                "date_range": date_range,
                "repository_name": repository_name
            })
            
            # 캐시 확인
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                return DiffQueryResult(**cached_result)
            
            # 데이터베이스 조회
            with self._get_session() as session:
                query = select(Event)
                
                # 필터 조건 적용
                conditions = []
                if developer_id:
                    conditions.append(Event.pusher == developer_id)
                if date_range:
                    conditions.append(Event.created_at >= date_range['start'])
                    conditions.append(Event.created_at <= date_range['end'])
                if repository_name:
                    conditions.append(Event.repository == repository_name)
                
                if conditions:
                    query = query.where(and_(*conditions))
                
                query = query.order_by(Event.created_at.desc())
                events = session.execute(query).scalars().all()
                
                # Diff 정보 변환
                diffs = []
                for event in events:
                    if event.payload:
                        event_data = json.loads(event.payload)
                        head_commit = event_data.get('head_commit', {})
                        
                        # commits 배열에서 모든 파일 변경사항 추출
                        all_files = set()
                        for commit in event_data.get('commits', []):
                            all_files.update(commit.get('added', []))
                            all_files.update(commit.get('modified', []))
                            all_files.update(commit.get('removed', []))
                        
                        # head_commit에서도 파일 정보 추가
                        if head_commit:
                            all_files.update(head_commit.get('added', []))
                            all_files.update(head_commit.get('modified', []))
                            all_files.update(head_commit.get('removed', []))
                        
                        # 각 파일에 대한 diff 정보 생성
                        for file_path in all_files:
                            # 파일 변경 타입 결정
                            change_type = "modified"
                            if any(file_path in commit.get('added', []) for commit in event_data.get('commits', [])):
                                change_type = "added"
                            elif any(file_path in commit.get('removed', []) for commit in event_data.get('commits', [])):
                                change_type = "deleted"
                            
                            diff_info = DiffInfo(
                                diff_id=f"{event.id}_{hash(file_path)}",
                                commit_hash=event.commit_sha or head_commit.get('id', ''),
                                file_path=file_path,
                                file_name=file_path.split('/')[-1],
                                file_extension=file_path.split('.')[-1] if '.' in file_path else None,
                                additions=event.added_lines or 0,  # 이벤트 전체 추가 라인
                                deletions=event.deleted_lines or 0,  # 이벤트 전체 삭제 라인
                                changes="",   # 실제 구현 시 추가
                                language=self._detect_language(file_path),
                                change_type=change_type
                            )
                            diffs.append(diff_info)
                
                query_time = time.time() - start_time
                
                # 메타데이터 생성
                metadata = QueryMetadata(
                    query_time_seconds=query_time,
                    total_records=len(events),
                    returned_records=len(diffs),
                    filters_applied=[f for f in ["developer_id", "date_range", "repository_name"] 
                                   if locals().get(f) is not None],
                    cache_hit=False,
                    query_hash=cache_key
                )
                
                result = DiffQueryResult(
                    diffs=diffs,
                    metadata=metadata
                )
                
                # 결과 캐싱
                self.cache_manager.set(cache_key, result.dict(), ttl=3600)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to get diff data: {e}")
            raise QueryExecutionException("diff_data", e)
    
    def get_active_developers(
        self,
        date_range: Dict[str, datetime]
    ) -> List[ActiveDeveloper]:
        """
        활성 개발자 목록 조회
        
        Args:
            date_range: 조회 날짜 범위
            
        Returns:
            List[ActiveDeveloper]: 활성 개발자 목록
        """
        try:
            with self._get_session() as session:
                query = select(
                    Event.pusher,
                    func.count(Event.id).label('commit_count'),
                    func.max(Event.created_at).label('last_activity')
                ).where(
                    and_(
                        Event.created_at >= date_range['start'],
                        Event.created_at <= date_range['end']
                    )
                ).group_by(Event.pusher)
                
                results = session.execute(query).all()
                
                active_developers = []
                for result in results:
                    developer = ActiveDeveloper(
                        developer_id=result.pusher,
                        name=result.pusher,  # 실제 구현 시 개발자 이름 조회
                        email=f"{result.pusher}@example.com",  # 실제 구현 시 이메일 조회
                        commit_count=result.commit_count,
                        last_activity=result.last_activity
                    )
                    active_developers.append(developer)
                
                return active_developers
                
        except Exception as e:
            self.logger.error(f"Failed to get active developers: {e}")
            raise QueryExecutionException("active_developers", e)
    
    def get_developer_statistics(
        self,
        developer_id: str,
        date_range: Dict[str, datetime]
    ) -> DeveloperStatistics:
        """
        개발자 통계 생성
        
        Args:
            developer_id: 개발자 식별자
            date_range: 통계 기간
            
        Returns:
            DeveloperStatistics: 개발자 통계
        """
        try:
            with self._get_session() as session:
                # 기본 통계 쿼리
                query = select(
                    func.count(Event.id).label('total_commits'),
                    func.count(func.distinct(Event.repository)).label('repositories'),
                    func.count(func.distinct(func.date(Event.created_at))).label('active_days')
                ).where(
                    and_(
                        Event.pusher == developer_id,
                        Event.created_at >= date_range['start'],
                        Event.created_at <= date_range['end']
                    )
                )
                
                result = session.execute(query).first()
                
                # 저장소 목록 조회
                repo_query = select(func.distinct(Event.repository)).where(
                    and_(
                        Event.pusher == developer_id,
                        Event.created_at >= date_range['start'],
                        Event.created_at <= date_range['end']
                    )
                )
                repositories = [row[0] for row in session.execute(repo_query).all()]
                
                statistics = DeveloperStatistics(
                    developer_id=developer_id,
                    developer_name=developer_id,  # 실제 구현 시 이름 조회
                    date_range=date_range,
                    total_commits=result.total_commits or 0,
                    total_files_changed=0,  # 실제 구현 시 계산
                    total_lines_added=0,    # 실제 구현 시 계산
                    total_lines_deleted=0,  # 실제 구현 시 계산
                    active_days=result.active_days or 0,
                    repositories=repositories,
                    languages={},  # 실제 구현 시 언어별 통계
                    daily_activity={}  # 실제 구현 시 일별 활동량
                )
                
                return statistics
                
        except Exception as e:
            self.logger.error(f"Failed to get developer statistics for {developer_id}: {e}")
            raise QueryExecutionException("developer_statistics", e)
    
    def get_daily_summary(
        self,
        target_date: Optional[datetime] = None
    ) -> RetrievalResult:
        """
        일일 요약 데이터 조회
        
        Args:
            target_date: 대상 날짜 (기본값: 어제)
            
        Returns:
            RetrievalResult: 조회 결과
        """
        if target_date is None:
            target_date = datetime.now() - timedelta(days=1)
        
        date_range = {
            'start': target_date.replace(hour=0, minute=0, second=0),
            'end': target_date.replace(hour=23, minute=59, second=59)
        }
        
        try:
            start_time = time.time()
            
            # 활성 개발자 조회
            active_developers = self.get_active_developers(date_range)
            
            all_commits = []
            all_diffs = []
            
            # 각 개발자별 데이터 조회
            for developer in active_developers:
                commits_result = self.get_commits_by_developer(
                    developer.developer_id, 
                    date_range, 
                    include_statistics=False
                )
                all_commits.extend(commits_result.commits)
                
                diffs_result = self.get_diff_data(
                    developer_id=developer.developer_id,
                    date_range=date_range
                )
                all_diffs.extend(diffs_result.diffs)
            
            query_time = time.time() - start_time
            
            # 메타데이터 생성
            metadata = QueryMetadata(
                query_time_seconds=query_time,
                total_records=len(all_commits) + len(all_diffs),
                returned_records=len(all_commits) + len(all_diffs),
                filters_applied=["date_range", "daily_summary"],
                cache_hit=False,
                query_hash=self._generate_cache_key("daily_summary", {"target_date": target_date})
            )
            
            return RetrievalResult(
                commits=all_commits,
                diffs=all_diffs,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get daily summary for {target_date}: {e}")
            raise QueryExecutionException("daily_summary", e)
    
    def _get_session(self) -> Session:
        """데이터베이스 세션 조회"""
        if self.db_session:
            return self.db_session
        else:
            return get_session()
    
    def _generate_cache_key(self, query_type: str, params: Dict[str, Any]) -> str:
        """캐시 키 생성"""
        # 파라미터를 정렬하여 일관된 키 생성
        sorted_params = json.dumps(params, sort_keys=True, default=str)
        key_string = f"{query_type}:{sorted_params}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _detect_language(self, file_path: str) -> Optional[str]:
        """파일 경로에서 프로그래밍 언어 감지"""
        extension_mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.xml': 'XML'
        }
        
        for ext, lang in extension_mapping.items():
            if file_path.lower().endswith(ext):
                return lang
        
        return None 