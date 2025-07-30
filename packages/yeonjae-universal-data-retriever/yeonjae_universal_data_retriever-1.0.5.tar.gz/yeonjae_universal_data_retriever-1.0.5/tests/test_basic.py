"""
Universal Data Retriever 기본 테스트

모듈의 기본 임포트와 구조를 테스트합니다.
"""

import pytest


def test_module_import():
    """모듈 임포트 테스트"""
    try:
        import yeonjae_universal_data_retriever
        assert hasattr(yeonjae_universal_data_retriever, '__version__')
    except ImportError:
        # __init__.py가 없거나 버전이 정의되지 않은 경우
        pass


def test_models_import():
    """모델 임포트 테스트"""
    from yeonjae_universal_data_retriever.models import (
        FilterOperator, SortDirection, FilterCondition,
        QueryParams, CommitInfo, DiffInfo
    )
    
    # 열거형 값 확인
    assert FilterOperator.EQ == "eq"
    assert FilterOperator.GT == "gt"
    assert SortDirection.ASC == "asc"
    assert SortDirection.DESC == "desc"


def test_exceptions_import():
    """예외 클래스 임포트 테스트"""
    from yeonjae_universal_data_retriever.exceptions import (
        DataRetrieverException,
        InvalidQueryException,
        DataNotFoundException
    )
    
    # 예외 클래스 확인
    assert issubclass(InvalidQueryException, DataRetrieverException)
    assert issubclass(DataNotFoundException, DataRetrieverException)


def test_filter_condition_creation():
    """FilterCondition 생성 테스트"""
    from yeonjae_universal_data_retriever.models import FilterCondition, FilterOperator
    
    condition = FilterCondition(
        field="test_field",
        operator=FilterOperator.EQ,
        value="test_value"
    )
    
    assert condition.field == "test_field"
    assert condition.operator == FilterOperator.EQ
    assert condition.value == "test_value"


def test_exception_creation():
    """예외 생성 테스트"""
    from yeonjae_universal_data_retriever.exceptions import InvalidQueryException
    
    exception = InvalidQueryException("test_field", "test_reason")
    
    assert "test_field" in str(exception)
    assert "test_reason" in str(exception)
    assert exception.details["query_field"] == "test_field"
    assert exception.details["reason"] == "test_reason"


def test_commit_info_creation():
    """CommitInfo 생성 테스트"""
    from datetime import datetime
    from yeonjae_universal_data_retriever.models import CommitInfo
    
    commit = CommitInfo(
        commit_id="123",
        commit_hash="abc123",
        message="Test commit",
        author="Test Author",
        author_email="test@example.com",
        timestamp=datetime.now(),
        repository="test-repo",
        branch="main"
    )
    
    assert commit.commit_id == "123"
    assert commit.commit_hash == "abc123"
    assert commit.message == "Test commit"
    assert commit.author == "Test Author"
    assert commit.repository == "test-repo"
    assert commit.branch == "main"


def test_pagination_config():
    """PaginationConfig 테스트"""
    from yeonjae_universal_data_retriever.models import PaginationConfig
    
    # 기본값 테스트
    pagination = PaginationConfig()
    assert pagination.page == 1
    assert pagination.size == 100
    
    # 커스텀 값 테스트
    pagination_custom = PaginationConfig(page=2, size=50)
    assert pagination_custom.page == 2
    assert pagination_custom.size == 50


def test_query_metadata_creation():
    """QueryMetadata 생성 테스트"""
    from yeonjae_universal_data_retriever.models import QueryMetadata
    
    metadata = QueryMetadata(
        query_time_seconds=0.5,
        total_records=100,
        returned_records=50,
        query_hash="test_hash"
    )
    
    assert metadata.query_time_seconds == 0.5
    assert metadata.total_records == 100
    assert metadata.returned_records == 50
    assert metadata.query_hash == "test_hash"
    assert isinstance(metadata.filters_applied, list)
    assert metadata.cache_hit is False  # 기본값 