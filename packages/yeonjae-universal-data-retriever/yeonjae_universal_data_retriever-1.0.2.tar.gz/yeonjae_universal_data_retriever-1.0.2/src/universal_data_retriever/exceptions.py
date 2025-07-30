"""
DataRetriever 모듈의 예외 클래스

데이터 조회와 관련된 모든 예외를 정의합니다.
"""


class DataRetrieverException(Exception):
    """DataRetriever 기본 예외"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidQueryException(DataRetrieverException):
    """잘못된 쿼리인 경우"""
    def __init__(self, query_field: str, reason: str):
        message = f"Invalid query parameter - {query_field}: {reason}"
        super().__init__(message, {
            "query_field": query_field,
            "reason": reason
        })


class DataNotFoundException(DataRetrieverException):
    """데이터를 찾을 수 없는 경우"""
    def __init__(self, query_type: str, query_params: dict):
        message = f"No data found for {query_type}"
        super().__init__(message, {
            "query_type": query_type,
            "query_params": query_params
        })


class QueryExecutionException(DataRetrieverException):
    """쿼리 실행 중 오류가 발생한 경우"""
    def __init__(self, query_type: str, error: Exception):
        message = f"Query execution failed for {query_type}"
        super().__init__(message, {
            "query_type": query_type,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class CacheException(DataRetrieverException):
    """캐시 관련 오류"""
    def __init__(self, operation: str, error: Exception):
        message = f"Cache operation failed: {operation}"
        super().__init__(message, {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class DatabaseConnectionException(DataRetrieverException):
    """데이터베이스 연결 오류"""
    def __init__(self, error: Exception):
        message = "Database connection failed"
        super().__init__(message, {
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class FilterValidationException(DataRetrieverException):
    """필터 검증 오류"""
    def __init__(self, filter_field: str, filter_operator: str, reason: str):
        message = f"Filter validation failed - {filter_field} {filter_operator}: {reason}"
        super().__init__(message, {
            "filter_field": filter_field,
            "filter_operator": filter_operator,
            "reason": reason
        }) 