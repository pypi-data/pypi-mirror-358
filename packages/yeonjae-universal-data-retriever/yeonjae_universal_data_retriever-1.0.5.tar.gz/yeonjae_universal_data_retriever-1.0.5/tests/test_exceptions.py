"""
Universal Data Retriever 예외 테스트

예외 클래스들의 기능과 메시지를 테스트합니다.
"""

import pytest
from yeonjae_universal_data_retriever.exceptions import (
    DataRetrieverException,
    InvalidQueryException,
    DataNotFoundException,
    QueryExecutionException,
    CacheException,
    DatabaseConnectionException,
    FilterValidationException
)


class TestDataRetrieverException:
    """DataRetrieverException 기본 예외 테스트"""
    
    def test_basic_exception(self):
        """기본 예외 생성 테스트"""
        exception = DataRetrieverException("Test error message")
        
        assert str(exception) == "Test error message"
        assert exception.message == "Test error message"
        assert exception.details == {}
    
    def test_exception_with_details(self):
        """상세 정보가 포함된 예외 테스트"""
        details = {"field": "test_field", "value": "test_value"}
        exception = DataRetrieverException("Test error", details)
        
        assert exception.message == "Test error"
        assert exception.details == details
        assert exception.details["field"] == "test_field"


class TestInvalidQueryException:
    """InvalidQueryException 테스트"""
    
    def test_invalid_query_exception(self):
        """잘못된 쿼리 예외 테스트"""
        exception = InvalidQueryException("date_range", "Invalid date format")
        
        assert "date_range" in str(exception)
        assert "Invalid date format" in str(exception)
        assert exception.details["query_field"] == "date_range"
        assert exception.details["reason"] == "Invalid date format"
    
    def test_invalid_query_exception_developer_id(self):
        """개발자 ID 관련 잘못된 쿼리 예외 테스트"""
        exception = InvalidQueryException("developer_id", "Developer ID cannot be empty")
        
        assert "developer_id" in str(exception)
        assert "Developer ID cannot be empty" in str(exception)
        assert exception.details["query_field"] == "developer_id"
        assert exception.details["reason"] == "Developer ID cannot be empty"
    
    def test_invalid_query_exception_pagination(self):
        """페이징 관련 잘못된 쿼리 예외 테스트"""
        exception = InvalidQueryException("pagination", "Page size must be between 1 and 1000")
        
        assert "pagination" in str(exception)
        assert "Page size must be between 1 and 1000" in str(exception)


class TestDataNotFoundException:
    """DataNotFoundException 테스트"""
    
    def test_data_not_found_exception(self):
        """데이터 없음 예외 테스트"""
        query_params = {"developer_id": "test@example.com", "date_range": "2024-01-01"}
        exception = DataNotFoundException("commits_by_developer", query_params)
        
        assert "commits_by_developer" in str(exception)
        assert exception.details["query_type"] == "commits_by_developer"
        assert exception.details["query_params"] == query_params
    
    def test_data_not_found_exception_diff_data(self):
        """Diff 데이터 없음 예외 테스트"""
        query_params = {"commit_hash": "abc123def456"}
        exception = DataNotFoundException("diff_data", query_params)
        
        assert "diff_data" in str(exception)
        assert exception.details["query_type"] == "diff_data"
        assert exception.details["query_params"]["commit_hash"] == "abc123def456"
    
    def test_data_not_found_exception_empty_params(self):
        """빈 파라미터로 데이터 없음 예외 테스트"""
        exception = DataNotFoundException("developer_statistics", {})
        
        assert "developer_statistics" in str(exception)
        assert exception.details["query_params"] == {}


class TestQueryExecutionException:
    """QueryExecutionException 테스트"""
    
    def test_query_execution_exception(self):
        """쿼리 실행 예외 테스트"""
        original_error = Exception("Database connection timeout")
        exception = QueryExecutionException("get_commits", original_error)
        
        assert "get_commits" in str(exception)
        assert exception.details["query_type"] == "get_commits"
        assert exception.details["error_type"] == "Exception"
        assert exception.details["error_message"] == "Database connection timeout"
    
    def test_query_execution_exception_sql_error(self):
        """SQL 오류로 인한 쿼리 실행 예외 테스트"""
        sql_error = ValueError("Invalid SQL syntax")
        exception = QueryExecutionException("complex_aggregation", sql_error)
        
        assert "complex_aggregation" in str(exception)
        assert exception.details["error_type"] == "ValueError"
        assert exception.details["error_message"] == "Invalid SQL syntax"
    
    def test_query_execution_exception_with_nested_error(self):
        """중첩된 오류가 있는 쿼리 실행 예외 테스트"""
        nested_error = ConnectionError("Network unreachable")
        exception = QueryExecutionException("remote_data_fetch", nested_error)
        
        assert exception.details["error_type"] == "ConnectionError"
        assert exception.details["error_message"] == "Network unreachable"


class TestCacheException:
    """CacheException 테스트"""
    
    def test_cache_exception(self):
        """캐시 예외 테스트"""
        cache_error = KeyError("Cache key not found")
        exception = CacheException("get", cache_error)
        
        assert "get" in str(exception)
        assert exception.details["operation"] == "get"
        assert exception.details["error_type"] == "KeyError"
        assert exception.details["error_message"] == "'Cache key not found'"
    
    def test_cache_exception_set_operation(self):
        """캐시 설정 작업 예외 테스트"""
        memory_error = MemoryError("Out of memory")
        exception = CacheException("set", memory_error)
        
        assert "set" in str(exception)
        assert exception.details["operation"] == "set"
        assert exception.details["error_type"] == "MemoryError"
    
    def test_cache_exception_clear_operation(self):
        """캐시 삭제 작업 예외 테스트"""
        permission_error = PermissionError("Access denied")
        exception = CacheException("clear", permission_error)
        
        assert "clear" in str(exception)
        assert exception.details["operation"] == "clear"
        assert exception.details["error_type"] == "PermissionError"


class TestDatabaseConnectionException:
    """DatabaseConnectionException 테스트"""
    
    def test_database_connection_exception(self):
        """데이터베이스 연결 예외 테스트"""
        connection_error = ConnectionError("Unable to connect to database")
        exception = DatabaseConnectionException(connection_error)
        
        assert "Database connection failed" in str(exception)
        assert exception.details["error_type"] == "ConnectionError"
        assert exception.details["error_message"] == "Unable to connect to database"
    
    def test_database_connection_exception_timeout(self):
        """데이터베이스 연결 타임아웃 예외 테스트"""
        timeout_error = TimeoutError("Connection timeout after 30 seconds")
        exception = DatabaseConnectionException(timeout_error)
        
        assert exception.details["error_type"] == "TimeoutError"
        assert "timeout" in exception.details["error_message"].lower()
    
    def test_database_connection_exception_auth(self):
        """데이터베이스 인증 오류 예외 테스트"""
        auth_error = PermissionError("Authentication failed")
        exception = DatabaseConnectionException(auth_error)
        
        assert exception.details["error_type"] == "PermissionError"
        assert "Authentication failed" in exception.details["error_message"]


class TestFilterValidationException:
    """FilterValidationException 테스트"""
    
    def test_filter_validation_exception(self):
        """필터 검증 예외 테스트"""
        exception = FilterValidationException("date_range", "between", "End date must be after start date")
        
        assert "date_range" in str(exception)
        assert "between" in str(exception)
        assert "End date must be after start date" in str(exception)
        assert exception.details["filter_field"] == "date_range"
        assert exception.details["filter_operator"] == "between"
        assert exception.details["reason"] == "End date must be after start date"
    
    def test_filter_validation_exception_invalid_operator(self):
        """잘못된 연산자 필터 검증 예외 테스트"""
        exception = FilterValidationException("status", "invalid_op", "Operator 'invalid_op' is not supported")
        
        assert exception.details["filter_field"] == "status"
        assert exception.details["filter_operator"] == "invalid_op"
        assert "not supported" in exception.details["reason"]
    
    def test_filter_validation_exception_value_type(self):
        """값 타입 오류 필터 검증 예외 테스트"""
        exception = FilterValidationException("commit_count", "gt", "Value must be a number")
        
        assert exception.details["filter_field"] == "commit_count"
        assert exception.details["filter_operator"] == "gt"
        assert "must be a number" in exception.details["reason"]


class TestExceptionInheritance:
    """예외 상속 구조 테스트"""
    
    def test_all_exceptions_inherit_from_base(self):
        """모든 예외가 기본 예외를 상속하는지 테스트"""
        exceptions = [
            InvalidQueryException("field", "reason"),
            DataNotFoundException("type", {}),
            QueryExecutionException("type", Exception()),
            CacheException("op", Exception()),
            DatabaseConnectionException(Exception()),
            FilterValidationException("field", "op", "reason")
        ]
        
        for exception in exceptions:
            assert isinstance(exception, DataRetrieverException)
            assert isinstance(exception, Exception)
    
    def test_exception_details_structure(self):
        """예외 상세 정보 구조 테스트"""
        exceptions = [
            InvalidQueryException("field", "reason"),
            DataNotFoundException("type", {"param": "value"}),
            QueryExecutionException("type", ValueError("test")),
            CacheException("op", KeyError("test")),
            DatabaseConnectionException(ConnectionError("test")),
            FilterValidationException("field", "op", "reason")
        ]
        
        for exception in exceptions:
            assert hasattr(exception, 'details')
            assert isinstance(exception.details, dict)
            assert hasattr(exception, 'message')
            assert isinstance(exception.message, str)


class TestExceptionMessages:
    """예외 메시지 테스트"""
    
    def test_exception_message_formatting(self):
        """예외 메시지 포맷팅 테스트"""
        # 다양한 예외 메시지 확인
        exceptions_and_expected = [
            (InvalidQueryException("test_field", "test reason"), "Invalid query parameter - test_field: test reason"),
            (DataNotFoundException("test_query", {}), "No data found for test_query"),
            (QueryExecutionException("test_query", Exception("test error")), "Query execution failed for test_query"),
            (CacheException("test_op", Exception("test error")), "Cache operation failed: test_op"),
            (DatabaseConnectionException(Exception("test error")), "Database connection failed"),
            (FilterValidationException("test_field", "test_op", "test reason"), "Filter validation failed - test_field test_op: test reason")
        ]
        
        for exception, expected_message in exceptions_and_expected:
            assert str(exception) == expected_message
    
    def test_exception_message_with_special_characters(self):
        """특수 문자가 포함된 예외 메시지 테스트"""
        exception = InvalidQueryException("field_with_underscore", "Reason with 'quotes' and numbers 123")
        
        assert "field_with_underscore" in str(exception)
        assert "'quotes'" in str(exception)
        assert "123" in str(exception) 