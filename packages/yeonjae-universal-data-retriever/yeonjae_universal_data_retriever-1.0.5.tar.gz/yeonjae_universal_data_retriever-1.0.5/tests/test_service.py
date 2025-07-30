"""
Universal Data Retriever 서비스 테스트

데이터 조회 서비스의 기능을 테스트합니다.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from yeonjae_universal_data_retriever.service import DataRetrieverService, CacheManager
from yeonjae_universal_data_retriever.models import (
    QueryParams, CommitQueryResult, DiffQueryResult, CommitInfo,
    DiffInfo, QueryMetadata, DeveloperStatistics, ActiveDeveloper,
    FilterCondition, FilterOperator, DateRangeQuery
)
from yeonjae_universal_data_retriever.exceptions import (
    DataRetrieverException, InvalidQueryException, DataNotFoundException,
    QueryExecutionException, DatabaseConnectionException
)


class TestCacheManager:
    """CacheManager 테스트"""
    
    def test_cache_set_and_get(self):
        """캐시 저장 및 조회 테스트"""
        cache = CacheManager()
        test_data = {"key": "value", "number": 42}
        
        cache.set("test_key", test_data, ttl=3600)
        result = cache.get("test_key")
        
        assert result == test_data
    
    def test_cache_miss(self):
        """캐시 미스 테스트"""
        cache = CacheManager()
        result = cache.get("nonexistent_key")
        
        assert result is None
    
    def test_cache_expiration(self):
        """캐시 만료 테스트"""
        cache = CacheManager()
        test_data = {"key": "value"}
        
        # TTL을 0으로 설정하여 즉시 만료되도록 함
        cache.set("test_key", test_data, ttl=0)
        
        # 약간의 시간 지연 후 조회
        import time
        time.sleep(0.1)
        
        result = cache.get("test_key")
        assert result is None
    
    def test_cache_clear(self):
        """캐시 전체 삭제 테스트"""
        cache = CacheManager()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestDataRetrieverService:
    """DataRetrieverService 테스트"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock 데이터베이스 세션"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db_session):
        """테스트용 서비스 인스턴스"""
        return DataRetrieverService(db_session=mock_db_session)
    
    def test_service_initialization(self, service):
        """서비스 초기화 테스트"""
        assert service.db_session is not None
        assert service.cache_manager is not None
        assert hasattr(service, 'logger')
    
    @patch('yeonjae_universal_data_retriever.service.select')
    @patch('yeonjae_universal_data_retriever.service.Event')
    def test_get_commits_by_developer_success(self, mock_event, mock_select, service):
        """개발자별 커밋 조회 성공 테스트"""
        # Mock 세션을 컨텍스트 매니저로 설정
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        service.db_session = mock_session
        
        # Mock 데이터 설정
        mock_event_instance = Mock()
        mock_event_instance.id = 1
        mock_event_instance.pusher = "john.doe@example.com"
        mock_event_instance.author_email = "john.doe@example.com"
        mock_event_instance.created_at = datetime.now()
        mock_event_instance.commit_sha = "abc123"
        mock_event_instance.payload = "{}"
        mock_event_instance.ref = "refs/heads/main"
        mock_event_instance.repository = "test-repo"
        mock_event_instance.files_changed = 2
        mock_event_instance.added_lines = 10
        mock_event_instance.deleted_lines = 5
        
        # Mock 쿼리 결과
        mock_scalars = Mock()
        mock_scalars.all.return_value = [mock_event_instance]
        mock_execute = Mock()
        mock_execute.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_execute
        
        # 테스트 실행
        date_range = {
            "start": datetime.now() - timedelta(days=7),
            "end": datetime.now()
        }
        
        result = service.get_commits_by_developer(
            developer_id="john.doe@example.com",
            date_range=date_range
        )
        
        # 검증
        assert isinstance(result, CommitQueryResult)
        assert len(result.commits) == 1
        assert result.commits[0].author == "john.doe@example.com"
        assert result.commits[0].repository == "test-repo"
        assert result.metadata.total_records == 1
    
    def test_get_commits_by_developer_cache_hit(self, service):
        """개발자별 커밋 조회 캐시 히트 테스트"""
        # Mock 세션을 컨텍스트 매니저로 설정
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        service.db_session = mock_session
        
        # 캐시에 데이터 미리 저장
        cached_data = {
            "commits": [],
            "metadata": {
                "query_time_seconds": 0.1,
                "total_records": 0,
                "returned_records": 0,
                "filters_applied": [],
                "cache_hit": True,
                "query_hash": "test_hash"
            }
        }
        
        cache_key = service._generate_cache_key("commits_by_developer", {
            "developer_id": "test@example.com",
            "date_range": {"start": datetime.now(), "end": datetime.now()}
        })
        
        service.cache_manager.set(cache_key, cached_data)
        
        # 테스트 실행
        date_range = {
            "start": datetime.now(),
            "end": datetime.now()
        }
        
        result = service.get_commits_by_developer(
            developer_id="test@example.com",
            date_range=date_range
        )
        
        # 검증
        assert isinstance(result, CommitQueryResult)
        assert len(result.commits) == 0
    
    @patch('yeonjae_universal_data_retriever.service.select')
    def test_get_commits_by_developer_no_data(self, mock_select, service):
        """개발자별 커밋 조회 데이터 없음 테스트"""
        # Mock 세션을 컨텍스트 매니저로 설정
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        service.db_session = mock_session
        
        # Mock 빈 결과
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_execute = Mock()
        mock_execute.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_execute
        
        # 테스트 실행
        date_range = {
            "start": datetime.now() - timedelta(days=7),
            "end": datetime.now()
        }
        
        result = service.get_commits_by_developer(
            developer_id="nonexistent@example.com",
            date_range=date_range
        )
        
        # 검증
        assert isinstance(result, CommitQueryResult)
        assert len(result.commits) == 0
        assert result.metadata.total_records == 0
    
    def test_get_commits_by_developer_database_error(self, service):
        """개발자별 커밋 조회 데이터베이스 오류 테스트"""
        # Mock 데이터베이스 오류
        service.db_session.execute.side_effect = Exception("Database connection failed")
        
        # 테스트 실행 및 검증
        date_range = {
            "start": datetime.now() - timedelta(days=7),
            "end": datetime.now()
        }
        
        with pytest.raises(QueryExecutionException):
            service.get_commits_by_developer(
                developer_id="test@example.com",
                date_range=date_range
            )
    
    @patch('yeonjae_universal_data_retriever.service.select')
    def test_get_active_developers(self, mock_select, service):
        """활성 개발자 목록 조회 테스트"""
        # Mock 세션을 컨텍스트 매니저로 설정
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        service.db_session = mock_session
        
        # Mock 데이터 설정
        mock_result = Mock()
        mock_result.pusher = "john.doe@example.com"
        mock_result.commit_count = 5
        mock_result.last_activity = datetime.now()
        
        mock_execute = Mock()
        mock_execute.all.return_value = [mock_result]
        mock_session.execute.return_value = mock_execute
        
        # 테스트 실행
        date_range = {
            "start": datetime.now() - timedelta(days=7),
            "end": datetime.now()
        }
        
        result = service.get_active_developers(date_range)
        
        # 검증
        assert isinstance(result, list)
        # Mock 데이터의 구조에 따라 결과가 달라질 수 있음
    
    @patch('yeonjae_universal_data_retriever.service.select')
    def test_get_developer_statistics(self, mock_select, service):
        """개발자 통계 조회 테스트"""
        # Mock 세션을 컨텍스트 매니저로 설정
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        service.db_session = mock_session
        
        # Mock 데이터 설정
        mock_result = Mock()
        mock_result.total_commits = 10
        mock_result.repositories = 2
        mock_result.active_days = 5
        
        mock_execute = Mock()
        mock_execute.first.return_value = mock_result
        mock_execute.all.return_value = [("test-repo",)]
        mock_session.execute.return_value = mock_execute
        
        # 테스트 실행
        date_range = {
            "start": datetime.now() - timedelta(days=7),
            "end": datetime.now()
        }
        
        result = service.get_developer_statistics(
            developer_id="john.doe@example.com",
            date_range=date_range
        )
        
        # 검증
        assert isinstance(result, DeveloperStatistics)
        assert result.developer_id == "john.doe@example.com"
    
    def test_get_daily_summary(self, service):
        """일일 요약 조회 테스트"""
        # Mock 세션을 컨텍스트 매니저로 설정
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        
        # Mock 데이터베이스 응답
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_execute = Mock()
        mock_execute.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_execute
        
        service.db_session = mock_session
        
        # 테스트 실행
        result = service.get_daily_summary()
        
        # 기본적인 구조 검증
        assert hasattr(result, 'commits')
        assert hasattr(result, 'metadata')
    
    def test_generate_cache_key(self, service):
        """캐시 키 생성 테스트"""
        params = {
            "developer_id": "test@example.com",
            "date_range": {"start": datetime(2024, 1, 1), "end": datetime(2024, 1, 31)}
        }
        
        cache_key = service._generate_cache_key("test_query", params)
        
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0
    
    def test_detect_language(self, service):
        """언어 감지 테스트"""
        # Python 파일
        assert service._detect_language("test.py") == "Python"
        
        # JavaScript 파일
        assert service._detect_language("test.js") == "JavaScript"
        
        # 알 수 없는 확장자
        assert service._detect_language("test.unknown") is None
        
        # 확장자 없는 파일
        assert service._detect_language("README") is None
    
    @patch('yeonjae_universal_data_retriever.service.get_session')
    def test_get_session_context_manager(self, mock_get_session, service):
        """세션 컨텍스트 매니저 테스트"""
        # db_session이 None인 경우
        service.db_session = None
        
        mock_session = Mock()
        mock_get_session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_get_session.return_value.__exit__ = Mock(return_value=None)
        
        with service._get_session() as session:
            assert session == mock_session
    
    def test_get_session_existing(self, service):
        """기존 세션 사용 테스트"""
        # db_session이 이미 설정된 경우
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)
        service.db_session = mock_session
        
        with service._get_session() as session:
            assert session == mock_session


class TestDataRetrieverServiceIntegration:
    """DataRetrieverService 통합 테스트"""
    
    @pytest.fixture
    def service_no_session(self):
        """세션 없는 서비스 인스턴스"""
        return DataRetrieverService()
    
    def test_service_without_session(self, service_no_session):
        """세션 없이 서비스 초기화 테스트"""
        assert service_no_session.db_session is None
        assert service_no_session.cache_manager is not None
    
    @patch('yeonjae_universal_data_retriever.service.get_session')
    def test_auto_session_management(self, mock_get_session, service_no_session):
        """자동 세션 관리 테스트"""
        # Mock 세션 설정
        mock_session = Mock()
        mock_get_session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_get_session.return_value.__exit__ = Mock(return_value=None)
        
        # Mock 쿼리 결과
        mock_scalars = Mock()
        mock_scalars.all.return_value = []
        mock_execute = Mock()
        mock_execute.scalars.return_value = mock_scalars
        mock_session.execute.return_value = mock_execute
        
        # 테스트 실행
        date_range = {
            "start": datetime.now() - timedelta(days=7),
            "end": datetime.now()
        }
        
        result = service_no_session.get_commits_by_developer(
            developer_id="test@example.com",
            date_range=date_range
        )
        
        # 검증
        assert isinstance(result, CommitQueryResult)
        mock_get_session.assert_called_once()


class TestDataRetrieverExceptions:
    """DataRetriever 예외 테스트"""
    
    def test_invalid_query_exception(self):
        """잘못된 쿼리 예외 테스트"""
        exception = InvalidQueryException("date_range", "Invalid date format")
        
        assert "date_range" in str(exception)
        assert "Invalid date format" in str(exception)
        assert exception.details["query_field"] == "date_range"
        assert exception.details["reason"] == "Invalid date format"
    
    def test_data_not_found_exception(self):
        """데이터 없음 예외 테스트"""
        query_params = {"developer_id": "test@example.com"}
        exception = DataNotFoundException("commits_by_developer", query_params)
        
        assert "commits_by_developer" in str(exception)
        assert exception.details["query_type"] == "commits_by_developer"
        assert exception.details["query_params"] == query_params
    
    def test_query_execution_exception(self):
        """쿼리 실행 예외 테스트"""
        original_error = Exception("Database connection failed")
        exception = QueryExecutionException("get_commits", original_error)
        
        assert "get_commits" in str(exception)
        assert exception.details["query_type"] == "get_commits"
        assert exception.details["error_type"] == "Exception"
        assert exception.details["error_message"] == "Database connection failed" 