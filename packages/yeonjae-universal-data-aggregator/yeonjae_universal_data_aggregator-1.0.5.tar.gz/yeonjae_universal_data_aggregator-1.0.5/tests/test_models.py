"""
Universal Data Aggregator Models 테스트
"""

import pytest
from datetime import datetime
from yeonjae_universal_data_aggregator.models import (
    DateRange, DiffInfo, DiffType, CommitData, AggregationInput,
    DeveloperStats, RepositoryStats, TimeAnalysis, ComplexityMetrics,
    AggregationResult, CacheKey
)


class TestDateRange:
    """DateRange 모델 테스트"""
    
    def test_valid_date_range(self):
        """올바른 날짜 범위 테스트"""
        date_range = DateRange(start="2024-06-01", end="2024-06-02")
        assert date_range.start == "2024-06-01"
        assert date_range.end == "2024-06-02"
    
    def test_invalid_date_format(self):
        """잘못된 날짜 형식 테스트"""
        with pytest.raises(ValueError, match="날짜는 YYYY-MM-DD 형식이어야 합니다"):
            DateRange(start="2024/06/01", end="2024-06-02")
    
    def test_end_before_start(self):
        """종료 날짜가 시작 날짜보다 빠른 경우 테스트"""
        with pytest.raises(ValueError, match="종료 날짜는 시작 날짜보다 늦어야 합니다"):
            DateRange(start="2024-06-02", end="2024-06-01")


class TestDiffInfo:
    """DiffInfo 모델 테스트"""
    
    def test_valid_diff_info(self):
        """올바른 DiffInfo 생성 테스트"""
        diff = DiffInfo(
            file_path="test.py",
            diff_type=DiffType.ADDED,
            lines_added=10,
            lines_deleted=5,
            complexity_score=2.5,
            language="Python"
        )
        assert diff.file_path == "test.py"
        assert diff.diff_type == DiffType.ADDED
        assert diff.lines_added == 10
        assert diff.lines_deleted == 5
    
    def test_negative_lines(self):
        """음수 라인 수 테스트"""
        with pytest.raises(ValueError):
            DiffInfo(
                file_path="test.py",
                diff_type=DiffType.ADDED,
                lines_added=-1
            )


class TestCommitData:
    """CommitData 모델 테스트"""
    
    def test_commit_data_properties(self):
        """CommitData 속성 테스트"""
        diff1 = DiffInfo(file_path="file1.py", diff_type=DiffType.ADDED, lines_added=10, lines_deleted=2)
        diff2 = DiffInfo(file_path="file2.py", diff_type=DiffType.MODIFIED, lines_added=5, lines_deleted=3)
        
        commit = CommitData(
            commit_id="abc123",
            author="Test User",
            author_email="test@example.com",
            timestamp=datetime.now(),
            message="Test commit",
            repository="test-repo",
            branch="main",
            diff_info=[diff1, diff2]
        )
        
        assert commit.total_lines_added == 15
        assert commit.total_lines_deleted == 5
        assert commit.files_changed == 2


class TestAggregationInput:
    """AggregationInput 모델 테스트"""
    
    def test_empty_commits(self):
        """빈 커밋 리스트 테스트"""
        date_range = DateRange(start="2024-06-01", end="2024-06-02")
        
        with pytest.raises(ValueError, match="커밋 데이터가 비어있습니다"):
            AggregationInput(commits=[], date_range=date_range)


class TestDeveloperStats:
    """DeveloperStats 모델 테스트"""
    
    def test_developer_stats_creation(self):
        """DeveloperStats 생성 테스트"""
        stats = DeveloperStats(
            developer="John Doe",
            developer_email="john@example.com",
            commit_count=5,
            lines_added=100,
            lines_deleted=20,
            files_changed=10,
            repositories=["repo1", "repo2"],
            languages_used=["Python", "JavaScript"],
            avg_complexity=2.5
        )
        
        assert stats.developer == "John Doe"
        assert stats.commit_count == 5
        assert len(stats.repositories) == 2


class TestAggregationResult:
    """AggregationResult 모델 테스트"""
    
    def test_aggregation_result_properties(self):
        """AggregationResult 속성 테스트"""
        dev_stats = {
            "john@example.com": DeveloperStats(
                developer="John",
                developer_email="john@example.com",
                commit_count=5
            ),
            "jane@example.com": DeveloperStats(
                developer="Jane",
                developer_email="jane@example.com",
                commit_count=3
            )
        }
        
        repo_stats = {
            "repo1": RepositoryStats(repository="repo1", total_commits=8)
        }
        
        result = AggregationResult(
            developer_stats=dev_stats,
            repository_stats=repo_stats
        )
        
        assert result.total_commits == 8
        assert result.total_developers == 2
        assert result.total_repositories == 1


class TestCacheKey:
    """CacheKey 모델 테스트"""
    
    def test_cache_key_string_generation(self):
        """캐시 키 문자열 생성 테스트"""
        date_range = DateRange(start="2024-06-01", end="2024-06-02")
        cache_key = CacheKey(
            date_range=date_range,
            developer_filter="john@example.com",
            repository_filter="test-repo"
        )
        
        key_string = cache_key.to_string()
        assert "2024-06-01_2024-06-02" in key_string
        assert "dev_john@example.com" in key_string
        assert "repo_test-repo" in key_string 