"""
Universal Data Aggregator Service 테스트
"""

import pytest
from datetime import datetime
from universal_data_aggregator import (
    DataAggregatorService, AggregationInput, DateRange,
    CommitData, DiffInfo, DiffType
)


class TestDataAggregatorService:
    """DataAggregatorService 테스트"""
    
    @pytest.fixture
    def service(self):
        """서비스 인스턴스 생성"""
        return DataAggregatorService()
    
    @pytest.fixture
    def sample_commits(self):
        """샘플 커밋 데이터"""
        diff1 = DiffInfo(
            file_path="src/main.py",
            diff_type=DiffType.ADDED,
            lines_added=20,
            lines_deleted=5,
            language="Python"
        )
        
        diff2 = DiffInfo(
            file_path="src/utils.py",
            diff_type=DiffType.MODIFIED,
            lines_added=10,
            lines_deleted=2,
            language="Python"
        )
        
        commit1 = CommitData(
            commit_id="abc123",
            author="John Doe",
            author_email="john@example.com",
            timestamp=datetime(2024, 6, 1, 14, 30),
            message="Add new feature",
            repository="test-repo",
            branch="main",
            diff_info=[diff1]
        )
        
        commit2 = CommitData(
            commit_id="def456",
            author="Jane Smith",
            author_email="jane@example.com",
            timestamp=datetime(2024, 6, 1, 16, 45),
            message="Fix bug",
            repository="test-repo",
            branch="main",
            diff_info=[diff2]
        )
        
        return [commit1, commit2]
    
    @pytest.fixture
    def aggregation_input(self, sample_commits):
        """집계 입력 데이터"""
        date_range = DateRange(start="2024-06-01", end="2024-06-01")
        return AggregationInput(
            commits=sample_commits,
            date_range=date_range
        )
    
    @pytest.mark.asyncio
    async def test_aggregate_data_success(self, service, aggregation_input):
        """데이터 집계 성공 테스트"""
        result = await service.aggregate_data(aggregation_input)
        
        assert result is not None
        assert len(result.developer_stats) == 2
        assert "john@example.com" in result.developer_stats
        assert "jane@example.com" in result.developer_stats
        
        # John의 통계 확인
        john_stats = result.developer_stats["john@example.com"]
        assert john_stats.developer == "John Doe"
        assert john_stats.commit_count == 1
        assert john_stats.lines_added == 20
        assert john_stats.lines_deleted == 5
        
        # Jane의 통계 확인
        jane_stats = result.developer_stats["jane@example.com"]
        assert jane_stats.developer == "Jane Smith"
        assert jane_stats.commit_count == 1
        assert jane_stats.lines_added == 10
        assert jane_stats.lines_deleted == 2
    
    def test_aggregate_by_developer(self, service, sample_commits, aggregation_input):
        """개발자별 집계 테스트"""
        developer_stats = service.aggregate_by_developer(sample_commits, aggregation_input)
        
        assert len(developer_stats) == 2
        assert "john@example.com" in developer_stats
        assert "jane@example.com" in developer_stats
        
        john_stats = developer_stats["john@example.com"]
        assert john_stats.lines_added == 20
        assert john_stats.files_changed == 1
    
    def test_generate_time_analysis(self, service, sample_commits):
        """시간 분석 테스트"""
        time_analysis = service.generate_time_analysis(sample_commits)
        
        assert time_analysis is not None
        assert isinstance(time_analysis.peak_hours, list)
        assert isinstance(time_analysis.commit_frequency, dict)
        assert 14 in time_analysis.commit_frequency  # John's commit hour
        assert 16 in time_analysis.commit_frequency  # Jane's commit hour
    
    def test_calculate_complexity_metrics(self, service, sample_commits):
        """복잡도 메트릭 계산 테스트"""
        complexity_metrics = service.calculate_complexity_metrics(sample_commits)
        
        assert complexity_metrics is not None
        assert complexity_metrics.avg_complexity >= 0
        assert complexity_metrics.max_complexity >= 0
        assert complexity_metrics.min_complexity >= 0
    
    def test_empty_commits_time_analysis(self, service):
        """빈 커밋 리스트에 대한 시간 분석 테스트"""
        time_analysis = service.generate_time_analysis([])
        
        assert time_analysis.peak_hours == []
        assert time_analysis.commit_frequency == {}
        assert time_analysis.work_pattern == "unknown"
        assert time_analysis.avg_commit_interval == 0.0
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, aggregation_input):
        """캐시 기능 테스트"""
        service_with_cache = DataAggregatorService(enable_cache=True)
        service_without_cache = DataAggregatorService(enable_cache=False)
        
        # 캐시 활성화된 서비스 테스트
        result1 = await service_with_cache.aggregate_data(aggregation_input)
        result2 = await service_with_cache.aggregate_data(aggregation_input)  # 캐시에서 가져와야 함
        
        assert result1 is not None
        assert result2 is not None
        
        # 캐시 비활성화된 서비스 테스트
        result3 = await service_without_cache.aggregate_data(aggregation_input)
        assert result3 is not None
    
    def test_service_initialization(self):
        """서비스 초기화 테스트"""
        service_with_cache = DataAggregatorService(enable_cache=True)
        service_without_cache = DataAggregatorService(enable_cache=False)
        
        assert service_with_cache.cache_manager is not None
        assert service_without_cache.cache_manager is None 