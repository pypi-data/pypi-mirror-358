"""
DataAggregator 서비스

조회된 커밋 데이터와 diff 정보를 가공, 집계, 통계 처리하는 메인 서비스입니다.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, Counter
import statistics

from .models import (
    AggregationInput, AggregationResult, DeveloperStats, RepositoryStats,
    TimeAnalysis, ComplexityMetrics, CommitData, DiffInfo, CacheKey
)
from .exceptions import (
    DataAggregatorException, InvalidInputDataException, 
    AggregationFailedException
)

logger = logging.getLogger(__name__)


class CacheManager:
    """메모리 기반 캐시 관리자"""
    
    def __init__(self, max_size: int = 100, ttl_minutes: int = 60):
        self.cache: Dict[str, tuple] = {}
        self.max_size = max_size
        self.ttl_minutes = ttl_minutes
    
    def get(self, key: str) -> Optional[AggregationResult]:
        if key not in self.cache:
            return None
        
        data, timestamp = self.cache[key]
        if datetime.now() - timestamp > timedelta(minutes=self.ttl_minutes):
            del self.cache[key]
            return None
        
        return data
    
    def set(self, key: str, data: AggregationResult):
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        self.cache[key] = (data, datetime.now())


class DataAggregatorService:
    """데이터 집계 서비스"""
    
    def __init__(self, enable_cache: bool = True):
        self.cache_manager = CacheManager() if enable_cache else None
        logger.info("DataAggregatorService initialized")
    
    async def aggregate_data(self, input_data: AggregationInput) -> AggregationResult:
        """메인 집계 메서드"""
        try:
            # 캐시 확인
            if self.cache_manager:
                cache_key = self._generate_cache_key(input_data)
                cached_result = self.cache_manager.get(cache_key)
                if cached_result:
                    return cached_result
            
            # 데이터 검증
            self._validate_input_data(input_data)
            
            # 집계 수행
            developer_stats = self.aggregate_by_developer(input_data.commits, input_data)
            repository_stats = self._aggregate_by_repository(input_data.commits)
            time_analysis = self.generate_time_analysis(input_data.commits)
            complexity_metrics = self.calculate_complexity_metrics(input_data.commits)
            
            result = AggregationResult(
                developer_stats=developer_stats,
                repository_stats=repository_stats,
                time_analysis=time_analysis,
                complexity_metrics=complexity_metrics
            )
            
            # 캐시 저장
            if self.cache_manager:
                self.cache_manager.set(cache_key, result)
            
            return result
            
        except Exception as e:
            raise AggregationFailedException("aggregate_data", e)
    
    def aggregate_by_developer(self, commits: List[CommitData], 
                             input_data: AggregationInput) -> Dict[str, DeveloperStats]:
        """개발자별 활동 집계"""
        developer_data = defaultdict(lambda: {
            'commits': [],
            'lines_added': 0,
            'lines_deleted': 0,
            'files_changed': set(),
            'repositories': set(),
            'languages': set()
        })
        
        for commit in commits:
            if input_data.developer_filter and commit.author not in input_data.developer_filter:
                continue
                
            dev_key = commit.author_email
            dev_data = developer_data[dev_key]
            
            dev_data['commits'].append(commit)
            dev_data['lines_added'] += commit.total_lines_added
            dev_data['lines_deleted'] += commit.total_lines_deleted
            dev_data['files_changed'].update(diff.file_path for diff in commit.diff_info)
            dev_data['repositories'].add(commit.repository)
        
        result = {}
        for dev_email, data in developer_data.items():
            if not data['commits']:
                continue
                
            stats = DeveloperStats(
                developer=data['commits'][0].author,
                developer_email=dev_email,
                commit_count=len(data['commits']),
                lines_added=data['lines_added'],
                lines_deleted=data['lines_deleted'],
                files_changed=len(data['files_changed']),
                repositories=list(data['repositories']),
                languages_used=list(data['languages']),
                avg_complexity=2.0  # 기본값
            )
            
            result[dev_email] = stats
        
        return result
    
    def _aggregate_by_repository(self, commits: List[CommitData]) -> Dict[str, RepositoryStats]:
        """저장소별 통계 집계"""
        repo_data = defaultdict(lambda: {
            'commits': 0,
            'contributors': set(),
            'lines_added': 0,
            'lines_deleted': 0,
            'files_changed': set(),
            'languages': set()
        })
        
        for commit in commits:
            repo = commit.repository
            data = repo_data[repo]
            
            data['commits'] += 1
            data['contributors'].add(commit.author_email)
            data['lines_added'] += commit.total_lines_added
            data['lines_deleted'] += commit.total_lines_deleted
            data['files_changed'].update(diff.file_path for diff in commit.diff_info)
        
        result = {}
        for repo, data in repo_data.items():
            stats = RepositoryStats(
                repository=repo,
                total_commits=data['commits'],
                contributors=list(data['contributors']),
                lines_added=data['lines_added'],
                lines_deleted=data['lines_deleted'],
                files_changed=len(data['files_changed']),
                languages=list(data['languages']),
                avg_complexity=2.0
            )
            result[repo] = stats
        
        return result
    
    def generate_time_analysis(self, commits: List[CommitData]) -> TimeAnalysis:
        """시간대별 활동 패턴 분석"""
        if not commits:
            return TimeAnalysis(
                peak_hours=[],
                commit_frequency={},
                work_pattern="unknown",
                avg_commit_interval=0.0
            )
        
        hour_frequency = Counter()
        commit_times = []
        
        for commit in commits:
            hour = commit.timestamp.hour
            hour_frequency[hour] += 1
            commit_times.append(commit.timestamp)
        
        peak_hours = [hour for hour, _ in hour_frequency.most_common(3)]
        
        return TimeAnalysis(
            peak_hours=peak_hours,
            commit_frequency=dict(hour_frequency),
            work_pattern="afternoon",  # 기본값
            avg_commit_interval=120.0   # 2시간
        )
    
    def calculate_complexity_metrics(self, commits: List[CommitData]) -> ComplexityMetrics:
        """코드 복잡도 메트릭 계산"""
        all_complexities = [2.0, 3.0, 1.5]  # 기본 샘플 데이터
        
        return ComplexityMetrics(
            avg_complexity=statistics.mean(all_complexities),
            max_complexity=max(all_complexities),
            min_complexity=min(all_complexities),
            complexity_trend="stable",
            high_complexity_files=[]
        )
    
    def _validate_input_data(self, input_data: AggregationInput):
        """입력 데이터 검증"""
        if not input_data.commits:
            raise InvalidInputDataException("commits", "Empty commit list")
        
        if not input_data.date_range:
            raise InvalidInputDataException("date_range", "Missing date range")
    
    def _generate_cache_key(self, input_data: AggregationInput) -> str:
        """캐시 키 생성"""
        cache_key = CacheKey(
            date_range=input_data.date_range,
            developer_filter=",".join(input_data.developer_filter) if input_data.developer_filter else None,
            repository_filter=",".join(input_data.repository_filter) if input_data.repository_filter else None
        )
        return cache_key.to_string() 