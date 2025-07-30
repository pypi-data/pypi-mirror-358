"""
Universal Data Retriever 모델 테스트

데이터 조회 모델들의 유효성 검증과 기능을 테스트합니다.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List

from universal_data_retriever.models import (
    FilterOperator, SortDirection, FilterCondition, SortOption,
    PaginationConfig, QueryParams, QueryMetadata, CommitInfo,
    DiffInfo, DeveloperInfo, CommitQueryResult, DiffQueryResult,
    DeveloperStatistics, RetrievalResult, ActiveDeveloper,
    DateRangeQuery, AggregationResult
)


class TestFilterCondition:
    """FilterCondition 모델 테스트"""
    
    def test_create_filter_condition(self):
        """필터 조건 생성 테스트"""
        condition = FilterCondition(
            field="author",
            operator=FilterOperator.EQ,
            value="john.doe@example.com"
        )
        
        assert condition.field == "author"
        assert condition.operator == FilterOperator.EQ
        assert condition.value == "john.doe@example.com"
    
    def test_filter_condition_with_list_value(self):
        """리스트 값을 가진 필터 조건 테스트"""
        condition = FilterCondition(
            field="repository",
            operator=FilterOperator.IN,
            value=["repo1", "repo2", "repo3"]
        )
        
        assert condition.field == "repository"
        assert condition.operator == FilterOperator.IN
        assert isinstance(condition.value, list)
        assert len(condition.value) == 3
    
    def test_filter_condition_with_dict_value(self):
        """딕셔너리 값을 가진 필터 조건 테스트"""
        date_range = {
            "start": datetime(2024, 1, 1),
            "end": datetime(2024, 1, 31)
        }
        condition = FilterCondition(
            field="created_at",
            operator=FilterOperator.DATE_RANGE,
            value=date_range
        )
        
        assert condition.field == "created_at"
        assert condition.operator == FilterOperator.DATE_RANGE
        assert isinstance(condition.value, dict)


class TestQueryParams:
    """QueryParams 모델 테스트"""
    
    def test_create_basic_query_params(self):
        """기본 쿼리 파라미터 생성 테스트"""
        date_range = {
            "start": datetime(2024, 1, 1),
            "end": datetime(2024, 1, 31)
        }
        
        params = QueryParams(date_range=date_range)
        
        assert params.date_range == date_range
        assert params.developer_id is None
        assert params.project_id is None
        assert len(params.filters) == 0
        assert len(params.sort_options) == 1  # 기본 정렬 옵션
        assert params.pagination.page == 1
        assert params.pagination.size == 100
        assert params.cache_enabled is True
    
    def test_query_params_with_filters(self):
        """필터가 포함된 쿼리 파라미터 테스트"""
        date_range = {
            "start": datetime(2024, 1, 1),
            "end": datetime(2024, 1, 31)
        }
        
        filters = [
            FilterCondition(
                field="repository",
                operator=FilterOperator.EQ,
                value="test-repo"
            ),
            FilterCondition(
                field="branch",
                operator=FilterOperator.IN,
                value=["main", "develop"]
            )
        ]
        
        params = QueryParams(
            date_range=date_range,
            developer_id="dev123",
            filters=filters
        )
        
        assert params.developer_id == "dev123"
        assert len(params.filters) == 2
        assert params.filters[0].field == "repository"
        assert params.filters[1].field == "branch"
    
    def test_query_params_with_custom_pagination(self):
        """커스텀 페이징이 포함된 쿼리 파라미터 테스트"""
        date_range = {
            "start": datetime(2024, 1, 1),
            "end": datetime(2024, 1, 31)
        }
        
        pagination = PaginationConfig(page=2, size=50)
        
        params = QueryParams(
            date_range=date_range,
            pagination=pagination
        )
        
        assert params.pagination.page == 2
        assert params.pagination.size == 50


class TestCommitInfo:
    """CommitInfo 모델 테스트"""
    
    def test_create_commit_info(self):
        """커밋 정보 생성 테스트"""
        commit = CommitInfo(
            commit_id="123",
            commit_hash="abc123def456",
            message="Fix bug in authentication",
            author="John Doe",
            author_email="john.doe@example.com",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            repository="test-repo",
            branch="main",
            file_count=3,
            lines_added=25,
            lines_deleted=10
        )
        
        assert commit.commit_id == "123"
        assert commit.commit_hash == "abc123def456"
        assert commit.message == "Fix bug in authentication"
        assert commit.author == "John Doe"
        assert commit.repository == "test-repo"
        assert commit.branch == "main"
        assert commit.file_count == 3
        assert commit.lines_added == 25
        assert commit.lines_deleted == 10


class TestDiffInfo:
    """DiffInfo 모델 테스트"""
    
    def test_create_diff_info(self):
        """Diff 정보 생성 테스트"""
        diff = DiffInfo(
            diff_id="diff123",
            commit_hash="abc123def456",
            file_path="src/auth/login.py",
            file_name="login.py",
            file_extension="py",
            additions=15,
            deletions=5,
            changes="@@ -10,7 +10,7 @@ def login(username, password):",
            complexity_score=2.5,
            language="python",
            change_type="modified"
        )
        
        assert diff.diff_id == "diff123"
        assert diff.commit_hash == "abc123def456"
        assert diff.file_path == "src/auth/login.py"
        assert diff.file_name == "login.py"
        assert diff.file_extension == "py"
        assert diff.additions == 15
        assert diff.deletions == 5
        assert diff.complexity_score == 2.5
        assert diff.language == "python"
        assert diff.change_type == "modified"


class TestDeveloperStatistics:
    """DeveloperStatistics 모델 테스트"""
    
    def test_create_developer_statistics(self):
        """개발자 통계 생성 테스트"""
        date_range = {
            "start": datetime(2024, 1, 1),
            "end": datetime(2024, 1, 31)
        }
        
        stats = DeveloperStatistics(
            developer_id="dev123",
            developer_name="John Doe",
            date_range=date_range,
            total_commits=25,
            total_files_changed=45,
            total_lines_added=500,
            total_lines_deleted=200,
            active_days=20,
            repositories=["repo1", "repo2"],
            languages={"python": 300, "javascript": 200},
            daily_activity={"2024-01-15": 5, "2024-01-16": 3}
        )
        
        assert stats.developer_id == "dev123"
        assert stats.developer_name == "John Doe"
        assert stats.total_commits == 25
        assert stats.total_files_changed == 45
        assert stats.active_days == 20
        assert len(stats.repositories) == 2
        assert "python" in stats.languages
        assert "javascript" in stats.languages


class TestQueryMetadata:
    """QueryMetadata 모델 테스트"""
    
    def test_create_query_metadata(self):
        """쿼리 메타데이터 생성 테스트"""
        metadata = QueryMetadata(
            query_time_seconds=0.45,
            total_records=150,
            returned_records=100,
            filters_applied=["developer_id=dev123", "date_range"],
            cache_hit=True,
            cache_ttl=3600,
            query_hash="hash123abc"
        )
        
        assert metadata.query_time_seconds == 0.45
        assert metadata.total_records == 150
        assert metadata.returned_records == 100
        assert len(metadata.filters_applied) == 2
        assert metadata.cache_hit is True
        assert metadata.cache_ttl == 3600
        assert metadata.query_hash == "hash123abc"


class TestCommitQueryResult:
    """CommitQueryResult 모델 테스트"""
    
    def test_create_commit_query_result(self):
        """커밋 쿼리 결과 생성 테스트"""
        commits = [
            CommitInfo(
                commit_id="1",
                commit_hash="abc123",
                message="First commit",
                author="John",
                author_email="john@example.com",
                timestamp=datetime.now(),
                repository="repo1",
                branch="main"
            )
        ]
        
        metadata = QueryMetadata(
            query_time_seconds=0.3,
            total_records=1,
            returned_records=1,
            query_hash="hash123"
        )
        
        result = CommitQueryResult(
            commits=commits,
            metadata=metadata
        )
        
        assert len(result.commits) == 1
        assert result.commits[0].commit_id == "1"
        assert result.metadata.total_records == 1


class TestRetrievalResult:
    """RetrievalResult 모델 테스트"""
    
    def test_create_retrieval_result(self):
        """조회 결과 생성 테스트"""
        commits = [
            CommitInfo(
                commit_id="1",
                commit_hash="abc123",
                message="Test commit",
                author="John",
                author_email="john@example.com",
                timestamp=datetime.now(),
                repository="repo1",
                branch="main"
            )
        ]
        
        diffs = [
            DiffInfo(
                diff_id="diff1",
                commit_hash="abc123",
                file_path="test.py",
                file_name="test.py",
                additions=10,
                deletions=5,
                changes="test changes",
                change_type="modified"
            )
        ]
        
        metadata = QueryMetadata(
            query_time_seconds=0.5,
            total_records=1,
            returned_records=1,
            query_hash="hash123"
        )
        
        result = RetrievalResult(
            commits=commits,
            diffs=diffs,
            metadata=metadata
        )
        
        assert len(result.commits) == 1
        assert len(result.diffs) == 1
        assert result.statistics is None
        assert result.metadata.query_time_seconds == 0.5


class TestDateRangeQuery:
    """DateRangeQuery 모델 테스트"""
    
    def test_create_date_range_query(self):
        """날짜 범위 쿼리 생성 테스트"""
        query = DateRangeQuery(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            include_weekends=False,
            timezone="Asia/Seoul"
        )
        
        assert query.start_date == datetime(2024, 1, 1)
        assert query.end_date == datetime(2024, 1, 31)
        assert query.include_weekends is False
        assert query.timezone == "Asia/Seoul"


class TestAggregationResult:
    """AggregationResult 모델 테스트"""
    
    def test_create_aggregation_result(self):
        """집계 결과 생성 테스트"""
        sum_values = {"lines_added": 500, "lines_deleted": 200}
        avg_values = {"complexity": 2.5, "files_per_commit": 3.2}
        min_values = {"commit_date": datetime(2024, 1, 1)}
        max_values = {"commit_date": datetime(2024, 1, 31)}
        
        result = AggregationResult(
            total_count=25,
            sum_values=sum_values,
            avg_values=avg_values,
            min_values=min_values,
            max_values=max_values
        )
        
        assert result.total_count == 25
        assert result.sum_values["lines_added"] == 500
        assert result.avg_values["complexity"] == 2.5
        assert "commit_date" in result.min_values
        assert "commit_date" in result.max_values


class TestPaginationConfig:
    """PaginationConfig 모델 테스트"""
    
    def test_create_pagination_config(self):
        """페이징 설정 생성 테스트"""
        pagination = PaginationConfig(page=3, size=50)
        
        assert pagination.page == 3
        assert pagination.size == 50
    
    def test_pagination_config_validation(self):
        """페이징 설정 유효성 검증 테스트"""
        # 유효한 값
        pagination = PaginationConfig(page=1, size=100)
        assert pagination.page == 1
        assert pagination.size == 100
        
        # 기본값 테스트
        pagination_default = PaginationConfig()
        assert pagination_default.page == 1
        assert pagination_default.size == 100
    
    def test_pagination_invalid_values(self):
        """잘못된 페이징 값 테스트"""
        with pytest.raises(ValueError):
            PaginationConfig(page=0, size=50)  # page는 1 이상이어야 함
        
        with pytest.raises(ValueError):
            PaginationConfig(page=1, size=0)  # size는 1 이상이어야 함
        
        with pytest.raises(ValueError):
            PaginationConfig(page=1, size=1001)  # size는 1000 이하여야 함


class TestSortOption:
    """SortOption 모델 테스트"""
    
    def test_create_sort_option(self):
        """정렬 옵션 생성 테스트"""
        sort = SortOption(field="timestamp", direction=SortDirection.ASC)
        
        assert sort.field == "timestamp"
        assert sort.direction == SortDirection.ASC
    
    def test_sort_option_default_direction(self):
        """정렬 옵션 기본 방향 테스트"""
        sort = SortOption(field="created_at")
        
        assert sort.field == "created_at"
        assert sort.direction == SortDirection.DESC  # 기본값


class TestActiveDeveloper:
    """ActiveDeveloper 모델 테스트"""
    
    def test_create_active_developer(self):
        """활성 개발자 정보 생성 테스트"""
        developer = ActiveDeveloper(
            developer_id="dev123",
            name="John Doe",
            email="john.doe@example.com",
            commit_count=15,
            last_activity=datetime(2024, 1, 15, 14, 30, 0)
        )
        
        assert developer.developer_id == "dev123"
        assert developer.name == "John Doe"
        assert developer.email == "john.doe@example.com"
        assert developer.commit_count == 15
        assert developer.last_activity == datetime(2024, 1, 15, 14, 30, 0) 