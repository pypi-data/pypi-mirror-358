"""
Universal Data Storage 모델 테스트

데이터 저장 모델들의 유효성 검증과 기능을 테스트합니다.
"""

import pytest
from datetime import datetime
from typing import Dict, List

from yeonjae_universal_data_storage.models import (
    StorageStatus, CommitData, DiffData, StorageResult,
    CommitSummary, DiffSummary, CommitWithDiffs, BatchStorageResult,
    EventCreate, EventResponse
)


class TestStorageStatus:
    """StorageStatus 열거형 테스트"""
    
    def test_storage_status_values(self):
        """저장 상태 값 테스트"""
        assert StorageStatus.SUCCESS == "success"
        assert StorageStatus.FAILED == "failed"
        assert StorageStatus.DUPLICATE == "duplicate"
        assert StorageStatus.PENDING == "pending"


class TestCommitData:
    """CommitData 모델 테스트"""
    
    def test_create_commit_data(self):
        """커밋 데이터 생성 테스트"""
        commit_data = CommitData(
            commit_hash="abc123def456",
            message="Fix authentication bug",
            author="John Doe",
            author_email="john.doe@example.com",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            repository="test-repo",
            branch="main",
            pusher="john.doe@example.com",
            commit_count=1
        )
        
        assert commit_data.commit_hash == "abc123def456"
        assert commit_data.message == "Fix authentication bug"
        assert commit_data.author == "John Doe"
        assert commit_data.author_email == "john.doe@example.com"
        assert commit_data.repository == "test-repo"
        assert commit_data.branch == "main"
        assert commit_data.pusher == "john.doe@example.com"
        assert commit_data.commit_count == 1
    
    def test_commit_data_optional_fields(self):
        """커밋 데이터 선택적 필드 테스트"""
        commit_data = CommitData(
            commit_hash="abc123",
            message="Test commit",
            author="Test Author",
            timestamp=datetime.now(),
            repository="test-repo",
            branch="main"
        )
        
        assert commit_data.author_email is None
        assert commit_data.pusher is None
        assert commit_data.commit_count == 1  # 기본값
    
    def test_commit_data_json_serialization(self):
        """커밋 데이터 JSON 직렬화 테스트"""
        commit_data = CommitData(
            commit_hash="abc123",
            message="Test commit",
            author="Test Author",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            repository="test-repo",
            branch="main"
        )
        
        # Pydantic 모델은 dict()로 직렬화 가능
        data_dict = commit_data.dict()
        assert isinstance(data_dict, dict)
        assert data_dict["commit_hash"] == "abc123"
        assert data_dict["message"] == "Test commit"


class TestDiffData:
    """DiffData 모델 테스트"""
    
    def test_create_diff_data(self):
        """Diff 데이터 생성 테스트"""
        diff_data = DiffData(
            file_path="src/auth/login.py",
            additions=15,
            deletions=5,
            changes="@@ -10,7 +10,7 @@ def login():",
            diff_content=b"binary diff content"
        )
        
        assert diff_data.file_path == "src/auth/login.py"
        assert diff_data.additions == 15
        assert diff_data.deletions == 5
        assert diff_data.changes == "@@ -10,7 +10,7 @@ def login():"
        assert diff_data.diff_content == b"binary diff content"
    
    def test_diff_data_defaults(self):
        """Diff 데이터 기본값 테스트"""
        diff_data = DiffData(file_path="test.py")
        
        assert diff_data.file_path == "test.py"
        assert diff_data.additions == 0
        assert diff_data.deletions == 0
        assert diff_data.changes is None
        assert diff_data.diff_content is None
    
    def test_diff_data_with_binary_content(self):
        """바이너리 내용이 포함된 Diff 데이터 테스트"""
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        diff_data = DiffData(
            file_path="image.png",
            additions=0,
            deletions=0,
            diff_content=binary_content
        )
        
        assert diff_data.diff_content == binary_content
        assert isinstance(diff_data.diff_content, bytes)


class TestStorageResult:
    """StorageResult 모델 테스트"""
    
    def test_create_storage_result_success(self):
        """성공 저장 결과 생성 테스트"""
        result = StorageResult(
            success=True,
            status=StorageStatus.SUCCESS,
            commit_id=123,
            message="Commit stored successfully",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            metadata={"files_changed": 3, "total_lines": 25}
        )
        
        assert result.success is True
        assert result.status == StorageStatus.SUCCESS
        assert result.commit_id == 123
        assert result.message == "Commit stored successfully"
        assert result.metadata["files_changed"] == 3
        assert result.metadata["total_lines"] == 25
    
    def test_create_storage_result_failure(self):
        """실패 저장 결과 생성 테스트"""
        result = StorageResult(
            success=False,
            status=StorageStatus.FAILED,
            message="Database connection failed",
            timestamp=datetime.now()
        )
        
        assert result.success is False
        assert result.status == StorageStatus.FAILED
        assert result.commit_id is None
        assert "Database connection failed" in result.message
        assert result.metadata == {}  # 기본값
    
    def test_create_storage_result_duplicate(self):
        """중복 저장 결과 생성 테스트"""
        result = StorageResult(
            success=False,
            status=StorageStatus.DUPLICATE,
            message="Commit already exists",
            timestamp=datetime.now(),
            metadata={"existing_commit_id": 456}
        )
        
        assert result.success is False
        assert result.status == StorageStatus.DUPLICATE
        assert result.metadata["existing_commit_id"] == 456


class TestCommitSummary:
    """CommitSummary 모델 테스트"""
    
    def test_create_commit_summary(self):
        """커밋 요약 생성 테스트"""
        summary = CommitSummary(
            id=1,
            hash="abc123def456",
            message="Fix bug in authentication",
            author="John Doe",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            repository="test-repo",
            branch="main",
            diff_count=3,
            total_additions=25,
            total_deletions=10
        )
        
        assert summary.id == 1
        assert summary.hash == "abc123def456"
        assert summary.message == "Fix bug in authentication"
        assert summary.author == "John Doe"
        assert summary.repository == "test-repo"
        assert summary.branch == "main"
        assert summary.diff_count == 3
        assert summary.total_additions == 25
        assert summary.total_deletions == 10


class TestDiffSummary:
    """DiffSummary 모델 테스트"""
    
    def test_create_diff_summary(self):
        """Diff 요약 생성 테스트"""
        summary = DiffSummary(
            id=1,
            file_path="src/auth/login.py",
            additions=15,
            deletions=5,
            has_content=True
        )
        
        assert summary.id == 1
        assert summary.file_path == "src/auth/login.py"
        assert summary.additions == 15
        assert summary.deletions == 5
        assert summary.has_content is True
    
    def test_diff_summary_no_content(self):
        """내용이 없는 Diff 요약 테스트"""
        summary = DiffSummary(
            id=2,
            file_path="binary_file.png",
            additions=0,
            deletions=0,
            has_content=False
        )
        
        assert summary.has_content is False


class TestCommitWithDiffs:
    """CommitWithDiffs 모델 테스트"""
    
    def test_create_commit_with_diffs(self):
        """Diff가 포함된 커밋 생성 테스트"""
        commit = CommitSummary(
            id=1,
            hash="abc123",
            message="Test commit",
            author="John Doe",
            timestamp=datetime.now(),
            repository="test-repo",
            branch="main",
            diff_count=2,
            total_additions=20,
            total_deletions=5
        )
        
        diffs = [
            DiffSummary(
                id=1,
                file_path="file1.py",
                additions=15,
                deletions=3,
                has_content=True
            ),
            DiffSummary(
                id=2,
                file_path="file2.py",
                additions=5,
                deletions=2,
                has_content=True
            )
        ]
        
        commit_with_diffs = CommitWithDiffs(
            commit=commit,
            diffs=diffs
        )
        
        assert commit_with_diffs.commit.id == 1
        assert len(commit_with_diffs.diffs) == 2
        assert commit_with_diffs.diffs[0].file_path == "file1.py"
        assert commit_with_diffs.diffs[1].file_path == "file2.py"


class TestBatchStorageResult:
    """BatchStorageResult 모델 테스트"""
    
    def test_create_batch_storage_result(self):
        """배치 저장 결과 생성 테스트"""
        results = [
            StorageResult(
                success=True,
                status=StorageStatus.SUCCESS,
                message="Success",
                timestamp=datetime.now()
            ),
            StorageResult(
                success=False,
                status=StorageStatus.FAILED,
                message="Failed",
                timestamp=datetime.now()
            ),
            StorageResult(
                success=True,
                status=StorageStatus.SUCCESS,
                message="Success",
                timestamp=datetime.now()
            )
        ]
        
        batch_result = BatchStorageResult(
            total_commits=3,
            successful_commits=2,
            failed_commits=1,
            results=results,
            duration_seconds=2.5
        )
        
        assert batch_result.total_commits == 3
        assert batch_result.successful_commits == 2
        assert batch_result.failed_commits == 1
        assert len(batch_result.results) == 3
        assert batch_result.duration_seconds == 2.5
    
    def test_batch_storage_result_success_rate(self):
        """배치 저장 결과 성공률 테스트"""
        batch_result = BatchStorageResult(
            total_commits=10,
            successful_commits=8,
            failed_commits=2,
            results=[],
            duration_seconds=5.0
        )
        
        assert batch_result.success_rate == 0.8  # 8/10 = 0.8
    
    def test_batch_storage_result_zero_commits(self):
        """커밋이 없는 배치 저장 결과 테스트"""
        batch_result = BatchStorageResult(
            total_commits=0,
            successful_commits=0,
            failed_commits=0,
            results=[],
            duration_seconds=0.0
        )
        
        assert batch_result.success_rate == 0.0


class TestEventCreate:
    """EventCreate 모델 테스트"""
    
    def test_create_event_create(self):
        """이벤트 생성 요청 모델 테스트"""
        event = EventCreate(
            repository="test-repo",
            commit_sha="abc123def456",
            event_type="push",
            payload='{"commits": []}',
            diff_data=b"diff content",
            diff_s3_url="https://s3.amazonaws.com/bucket/diff.patch"
        )
        
        assert event.repository == "test-repo"
        assert event.commit_sha == "abc123def456"
        assert event.event_type == "push"
        assert event.payload == '{"commits": []}'
        assert event.diff_data == b"diff content"
        assert event.diff_s3_url == "https://s3.amazonaws.com/bucket/diff.patch"
    
    def test_event_create_defaults(self):
        """이벤트 생성 기본값 테스트"""
        event = EventCreate(
            repository="test-repo",
            commit_sha="abc123",
            payload='{"test": "data"}'
        )
        
        assert event.event_type == "push"  # 기본값
        assert event.diff_data is None
        assert event.diff_s3_url is None


class TestEventResponse:
    """EventResponse 모델 테스트"""
    
    def test_create_event_response(self):
        """이벤트 응답 모델 테스트"""
        response = EventResponse(
            id=123,
            repository="test-repo",
            commit_sha="abc123def456",
            event_type="push",
            payload={"commits": [{"id": "abc123"}]},
            diff_s3_url="https://s3.amazonaws.com/bucket/diff.patch",
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        assert response.id == 123
        assert response.repository == "test-repo"
        assert response.commit_sha == "abc123def456"
        assert response.event_type == "push"
        assert response.payload["commits"][0]["id"] == "abc123"
        assert response.diff_s3_url == "https://s3.amazonaws.com/bucket/diff.patch"
        assert response.created_at == datetime(2024, 1, 15, 10, 30, 0)
    
    def test_event_response_optional_fields(self):
        """이벤트 응답 선택적 필드 테스트"""
        response = EventResponse(
            id=123,
            repository="test-repo",
            commit_sha="abc123",
            event_type="push",
            payload={"test": "data"},
            created_at=datetime.now()
        )
        
        assert response.diff_s3_url is None


class TestModelValidation:
    """모델 유효성 검증 테스트"""
    
    def test_commit_data_validation(self):
        """커밋 데이터 유효성 검증 테스트"""
        # 필수 필드 누락 시 오류
        with pytest.raises(ValueError):
            CommitData(
                # commit_hash 누락
                message="Test",
                author="Test Author",
                timestamp=datetime.now(),
                repository="test-repo",
                branch="main"
            )
    
    def test_storage_result_validation(self):
        """저장 결과 유효성 검증 테스트"""
        # 유효한 StorageResult
        result = StorageResult(
            success=True,
            status=StorageStatus.SUCCESS,
            message="Success",
            timestamp=datetime.now()
        )
        
        assert result.success is True
        assert result.status == StorageStatus.SUCCESS
    
    def test_batch_result_consistency(self):
        """배치 결과 일관성 테스트"""
        # 성공 + 실패 = 전체 커밋 수
        batch_result = BatchStorageResult(
            total_commits=5,
            successful_commits=3,
            failed_commits=2,
            results=[],
            duration_seconds=1.0
        )
        
        assert batch_result.successful_commits + batch_result.failed_commits == batch_result.total_commits


class TestModelSerialization:
    """모델 직렬화 테스트"""
    
    def test_commit_data_serialization(self):
        """커밋 데이터 직렬화 테스트"""
        commit_data = CommitData(
            commit_hash="abc123",
            message="Test commit",
            author="Test Author",
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            repository="test-repo",
            branch="main"
        )
        
        # JSON 직렬화 가능한지 확인
        data_dict = commit_data.dict()
        assert isinstance(data_dict, dict)
        
        # JSON 문자열로 변환 가능한지 확인
        json_str = commit_data.json()
        assert isinstance(json_str, str)
        assert "abc123" in json_str
    
    def test_storage_result_serialization(self):
        """저장 결과 직렬화 테스트"""
        result = StorageResult(
            success=True,
            status=StorageStatus.SUCCESS,
            message="Success",
            timestamp=datetime.now(),
            metadata={"test": "data"}
        )
        
        data_dict = result.dict()
        assert data_dict["success"] is True
        assert data_dict["status"] == "success"
        assert data_dict["metadata"]["test"] == "data" 