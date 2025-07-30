"""
DataRetriever 모듈의 데이터 모델

데이터 조회와 관련된 모든 데이터 구조를 정의합니다.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class FilterOperator(str, Enum):
    """필터 연산자"""
    EQ = "eq"           # 같음
    NE = "ne"           # 같지 않음
    GT = "gt"           # 큰
    GTE = "gte"         # 크거나 같음
    LT = "lt"           # 작은
    LTE = "lte"         # 작거나 같음
    IN = "in"           # 포함
    NOT_IN = "not_in"   # 포함하지 않음
    LIKE = "like"       # 유사
    ILIKE = "ilike"     # 대소문자 무시 유사
    DATE_RANGE = "date_range"  # 날짜 범위
    IS_NULL = "is_null"        # NULL 여부
    IS_NOT_NULL = "is_not_null"  # NOT NULL 여부


class SortDirection(str, Enum):
    """정렬 방향"""
    ASC = "asc"
    DESC = "desc"


class FilterCondition(BaseModel):
    """필터 조건"""
    field: str = Field(..., description="필터 대상 필드")
    operator: FilterOperator = Field(..., description="필터 연산자")
    value: Union[str, int, float, bool, List[Any], Dict[str, Any]] = Field(..., description="필터 값")


class SortOption(BaseModel):
    """정렬 옵션"""
    field: str = Field(..., description="정렬 대상 필드")
    direction: SortDirection = Field(default=SortDirection.DESC, description="정렬 방향")


class PaginationConfig(BaseModel):
    """페이징 설정"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    size: int = Field(default=100, ge=1, le=1000, description="페이지 크기")


class QueryParams(BaseModel):
    """조회 파라미터"""
    developer_id: Optional[str] = Field(None, description="개발자 식별자")
    date_range: Dict[str, datetime] = Field(..., description="조회 날짜 범위")
    project_id: Optional[str] = Field(None, description="프로젝트 식별자")
    repository_name: Optional[str] = Field(None, description="저장소 이름")
    branch_name: Optional[str] = Field(None, description="브랜치명")
    filters: List[FilterCondition] = Field(default_factory=list, description="추가 필터 조건")
    sort_options: List[SortOption] = Field(
        default_factory=lambda: [SortOption(field="created_at", direction=SortDirection.DESC)],
        description="정렬 옵션"
    )
    pagination: PaginationConfig = Field(default_factory=PaginationConfig, description="페이징 설정")
    cache_enabled: bool = Field(default=True, description="캐시 사용 여부")


class QueryMetadata(BaseModel):
    """쿼리 메타데이터"""
    query_time_seconds: float = Field(..., description="쿼리 실행 시간(초)")
    total_records: int = Field(..., description="전체 레코드 수")
    returned_records: int = Field(..., description="반환된 레코드 수")
    filters_applied: List[str] = Field(default_factory=list, description="적용된 필터 목록")
    cache_hit: bool = Field(default=False, description="캐시 히트 여부")
    cache_ttl: Optional[int] = Field(None, description="캐시 TTL(초)")
    query_hash: str = Field(..., description="쿼리 해시")


class CommitInfo(BaseModel):
    """커밋 정보"""
    commit_id: str = Field(..., description="커밋 ID")
    commit_hash: str = Field(..., description="커밋 해시")
    message: str = Field(..., description="커밋 메시지")
    author: str = Field(..., description="작성자")
    author_email: str = Field(..., description="작성자 이메일")
    timestamp: datetime = Field(..., description="커밋 시간")
    repository: str = Field(..., description="저장소 이름")
    branch: str = Field(..., description="브랜치명")
    file_count: int = Field(default=0, description="변경된 파일 수")
    lines_added: int = Field(default=0, description="추가된 라인 수")
    lines_deleted: int = Field(default=0, description="삭제된 라인 수")


class DiffInfo(BaseModel):
    """Diff 정보"""
    diff_id: str = Field(..., description="Diff ID")
    commit_hash: str = Field(..., description="커밋 해시")
    file_path: str = Field(..., description="파일 경로")
    file_name: str = Field(..., description="파일명")
    file_extension: Optional[str] = Field(None, description="파일 확장자")
    additions: int = Field(..., description="추가된 라인 수")
    deletions: int = Field(..., description="삭제된 라인 수")
    changes: str = Field(..., description="변경 내용")
    complexity_score: Optional[float] = Field(None, description="복잡도 점수")
    language: Optional[str] = Field(None, description="프로그래밍 언어")
    change_type: str = Field(..., description="변경 타입 (added, modified, deleted)")


class DeveloperInfo(BaseModel):
    """개발자 정보"""
    developer_id: str = Field(..., description="개발자 ID")
    name: str = Field(..., description="개발자 이름")
    email: str = Field(..., description="이메일")
    first_commit_date: Optional[datetime] = Field(None, description="첫 커밋 날짜")
    last_commit_date: Optional[datetime] = Field(None, description="마지막 커밋 날짜")
    total_commits: int = Field(default=0, description="총 커밋 수")


class CommitQueryResult(BaseModel):
    """커밋 조회 결과"""
    commits: List[CommitInfo] = Field(default_factory=list, description="커밋 목록")
    metadata: QueryMetadata = Field(..., description="쿼리 메타데이터")


class DiffQueryResult(BaseModel):
    """Diff 조회 결과"""
    diffs: List[DiffInfo] = Field(default_factory=list, description="Diff 목록")
    metadata: QueryMetadata = Field(..., description="쿼리 메타데이터")


class DeveloperStatistics(BaseModel):
    """개발자 통계"""
    developer_id: str = Field(..., description="개발자 ID")
    developer_name: str = Field(..., description="개발자 이름")
    date_range: Dict[str, datetime] = Field(..., description="통계 기간")
    total_commits: int = Field(default=0, description="총 커밋 수")
    total_files_changed: int = Field(default=0, description="변경된 파일 수")
    total_lines_added: int = Field(default=0, description="추가된 라인 수")
    total_lines_deleted: int = Field(default=0, description="삭제된 라인 수")
    active_days: int = Field(default=0, description="활동 일수")
    repositories: List[str] = Field(default_factory=list, description="활동한 저장소 목록")
    languages: Dict[str, int] = Field(default_factory=dict, description="언어별 변경 라인 수")
    daily_activity: Dict[str, int] = Field(default_factory=dict, description="일별 활동량")


class RetrievalResult(BaseModel):
    """조회 결과"""
    commits: List[CommitInfo] = Field(default_factory=list, description="커밋 목록")
    diffs: List[DiffInfo] = Field(default_factory=list, description="Diff 목록")
    statistics: Optional[DeveloperStatistics] = Field(None, description="통계 정보")
    metadata: QueryMetadata = Field(..., description="쿼리 메타데이터")


class ActiveDeveloper(BaseModel):
    """활성 개발자 정보"""
    developer_id: str = Field(..., description="개발자 ID")
    name: str = Field(..., description="개발자 이름")
    email: str = Field(..., description="이메일")
    commit_count: int = Field(..., description="기간 내 커밋 수")
    last_activity: datetime = Field(..., description="마지막 활동 시간")


class DateRangeQuery(BaseModel):
    """날짜 범위 조회"""
    start_date: datetime = Field(..., description="시작 날짜")
    end_date: datetime = Field(..., description="종료 날짜")
    include_weekends: bool = Field(default=True, description="주말 포함 여부")
    timezone: str = Field(default="Asia/Seoul", description="시간대")


class AggregationResult(BaseModel):
    """집계 결과"""
    total_count: int = Field(..., description="총 개수")
    sum_values: Dict[str, Union[int, float]] = Field(default_factory=dict, description="합계")
    avg_values: Dict[str, float] = Field(default_factory=dict, description="평균")
    min_values: Dict[str, Union[int, float, datetime]] = Field(default_factory=dict, description="최솟값")
    max_values: Dict[str, Union[int, float, datetime]] = Field(default_factory=dict, description="최댓값")
    group_by_results: Dict[str, Any] = Field(default_factory=dict, description="그룹별 결과") 