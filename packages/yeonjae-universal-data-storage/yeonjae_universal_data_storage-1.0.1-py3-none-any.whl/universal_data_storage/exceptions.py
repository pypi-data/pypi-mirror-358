"""
Universal Data Storage 예외 클래스

데이터 저장과 관련된 예외들을 정의합니다.
"""

from typing import Dict, Any, Optional


class DataStorageException(Exception):
    """데이터 저장 관련 기본 예외 클래스"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseConnectionException(DataStorageException):
    """데이터베이스 연결 예외"""
    
    def __init__(self, original_error: Exception):
        message = "Database connection failed"
        details = {
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class DuplicateDataException(DataStorageException):
    """중복 데이터 예외"""
    
    def __init__(self, commit_hash: str, existing_data: Dict[str, Any]):
        message = f"Duplicate commit data found for hash: {commit_hash}"
        details = {
            "commit_hash": commit_hash,
            "existing_data": existing_data
        }
        super().__init__(message, details)


class StorageValidationException(DataStorageException):
    """저장 데이터 검증 예외"""
    
    def __init__(self, field: str, value: Any, reason: str):
        message = f"Storage validation failed for field '{field}': {reason}"
        details = {
            "field": field,
            "value": value,
            "reason": reason
        }
        super().__init__(message, details)


class StorageOperationException(DataStorageException):
    """저장 작업 예외"""
    
    def __init__(self, operation: str, original_error: Exception):
        message = f"Storage operation '{operation}' failed"
        details = {
            "operation": operation,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details)


class BatchStorageException(DataStorageException):
    """배치 저장 예외"""
    
    def __init__(self, failed_count: int, total_count: int, errors: list):
        message = f"Batch storage failed: {failed_count}/{total_count} items failed"
        details = {
            "failed_count": failed_count,
            "total_count": total_count,
            "errors": errors
        }
        super().__init__(message, details)


class CompressionException(DataStorageException):
    """데이터 압축 예외"""
    
    def __init__(self, data_type: str, original_error: Exception):
        message = f"Data compression failed for {data_type}"
        details = {
            "data_type": data_type,
            "error_type": type(original_error).__name__,
            "error_message": str(original_error)
        }
        super().__init__(message, details) 