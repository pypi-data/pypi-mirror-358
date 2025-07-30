"""
Universal Data Aggregator 예외 클래스

데이터 집계와 관련된 예외들을 정의합니다.
"""

from typing import Dict, Any, Optional


class DataAggregatorException(Exception):
    """데이터 집계 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidDateRangeException(DataAggregatorException):
    """잘못된 날짜 범위 예외"""
    
    def __init__(self, start_date: str, end_date: str):
        message = f"Invalid date range: start_date '{start_date}' must be before end_date '{end_date}'"
        details = {
            "start_date": start_date,
            "end_date": end_date
        }
        super().__init__(message, details)


class AggregationException(DataAggregatorException):
    """집계 작업 예외"""
    
    def __init__(self, aggregation_type: str, original_error: Exception):
        message = f"Aggregation failed for type '{aggregation_type}'"
        details = {
            "aggregation_type": aggregation_type,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class DataValidationException(DataAggregatorException):
    """데이터 검증 예외"""
    
    def __init__(self, field: str, value: Any, reason: str):
        message = f"Data validation failed for field '{field}': {reason}"
        details = {
            "field": field,
            "value": value,
            "reason": reason
        }
        super().__init__(message, details)


class RepositoryNotFoundException(DataAggregatorException):
    """저장소를 찾을 수 없는 예외"""
    
    def __init__(self, repository: str):
        message = f"Repository not found: {repository}"
        details = {
            "repository": repository
        }
        super().__init__(message, details)


class DeveloperNotFoundException(DataAggregatorException):
    """개발자를 찾을 수 없는 예외"""
    
    def __init__(self, developer_email: str):
        message = f"Developer not found: {developer_email}"
        details = {
            "developer_email": developer_email
        }
        super().__init__(message, details)


class InvalidInputDataException(DataAggregatorException):
    """잘못된 입력 데이터 예외"""
    
    def __init__(self, input_type: str, reason: str):
        message = f"Invalid input data for {input_type}: {reason}"
        details = {
            "input_type": input_type,
            "reason": reason
        }
        super().__init__(message, details)


class AggregationFailedException(DataAggregatorException):
    """집계 실패 예외"""
    
    def __init__(self, operation: str, reason: str):
        message = f"Aggregation failed for operation '{operation}': {reason}"
        details = {
            "operation": operation,
            "reason": reason
        }
        super().__init__(message, details)


class ComplexityCalculationException(DataAggregatorException):
    """복잡도 계산 예외"""
    
    def __init__(self, file_path: str, reason: str):
        message = f"Complexity calculation failed for {file_path}: {reason}"
        details = {
            "file_path": file_path,
            "reason": reason
        }
        super().__init__(message, details)


class CacheException(DataAggregatorException):
    """캐시 관련 예외"""
    
    def __init__(self, operation: str, reason: str):
        message = f"Cache operation failed for '{operation}': {reason}"
        details = {
            "operation": operation,
            "reason": reason
        }
        super().__init__(message, details)


class DataValidationException(DataAggregatorException):
    """데이터 검증 예외"""
    
    def __init__(self, field: str, value: str, reason: str):
        message = f"Data validation failed for field '{field}' with value '{value}': {reason}"
        details = {
            "field": field,
            "value": value,
            "reason": reason
        }
        super().__init__(message, details) 