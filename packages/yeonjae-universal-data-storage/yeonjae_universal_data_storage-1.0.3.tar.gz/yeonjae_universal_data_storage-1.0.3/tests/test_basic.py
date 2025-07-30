"""
Universal Data Storage 기본 테스트

모듈의 기본 임포트와 구조를 테스트합니다.
"""

import pytest
from datetime import datetime


def test_models_import():
    """모델 임포트 테스트"""
    from universal_data_storage.models import (
        StorageStatus, CommitData, DiffData, StorageResult
    )
    
    # 열거형 값 확인
    assert StorageStatus.SUCCESS == "success"
    assert StorageStatus.FAILED == "failed"
    assert StorageStatus.DUPLICATE == "duplicate"
    assert StorageStatus.PENDING == "pending"


def test_exceptions_import():
    """예외 클래스 임포트 테스트"""
    from universal_data_storage.exceptions import (
        DataStorageException,
        DatabaseConnectionException,
        DuplicateDataException
    )
    
    # 예외 클래스 확인
    assert issubclass(DatabaseConnectionException, DataStorageException)
    assert issubclass(DuplicateDataException, DataStorageException)


def test_commit_data_creation():
    """CommitData 생성 테스트"""
    from universal_data_storage.models import CommitData
    
    commit = CommitData(
        commit_hash="abc123",
        message="Test commit",
        author="Test Author",
        timestamp=datetime.now(),
        repository="test-repo",
        branch="main"
    )
    
    assert commit.commit_hash == "abc123"
    assert commit.message == "Test commit"
    assert commit.author == "Test Author"
    assert commit.repository == "test-repo"
    assert commit.branch == "main"


def test_diff_data_creation():
    """DiffData 생성 테스트"""
    from universal_data_storage.models import DiffData
    
    diff = DiffData(
        file_path="test.py",
        additions=10,
        deletions=5,
        changes="@@ -1,3 +1,3 @@"
    )
    
    assert diff.file_path == "test.py"
    assert diff.additions == 10
    assert diff.deletions == 5
    assert diff.changes == "@@ -1,3 +1,3 @@"


def test_storage_result_creation():
    """StorageResult 생성 테스트"""
    from universal_data_storage.models import StorageResult, StorageStatus
    
    result = StorageResult(
        success=True,
        status=StorageStatus.SUCCESS,
        message="Success",
        timestamp=datetime.now()
    )
    
    assert result.success is True
    assert result.status == StorageStatus.SUCCESS
    assert result.message == "Success"


def test_exception_creation():
    """예외 생성 테스트"""
    from universal_data_storage.exceptions import DuplicateDataException
    
    exception = DuplicateDataException("test_hash", {"id": 123})
    
    assert "test_hash" in str(exception)
    assert exception.details["commit_hash"] == "test_hash"
    assert exception.details["existing_data"]["id"] == 123 