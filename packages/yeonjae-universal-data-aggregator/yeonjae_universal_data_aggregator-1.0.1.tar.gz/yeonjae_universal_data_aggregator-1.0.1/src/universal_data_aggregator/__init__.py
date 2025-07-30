"""
Universal Data Aggregator

커밋 데이터와 diff 정보를 가공, 집계, 통계 처리하는 범용 모듈입니다.
개발자별 일일 작업 내용, 코드 변경사항, 작업 패턴 분석을 수행합니다.
"""

from .service import DataAggregatorService
from .models import (
    AggregationInput,
    AggregationResult,
    DeveloperStats,
    RepositoryStats,
    TimeAnalysis,
    ComplexityMetrics,
    DateRange,
    CommitData,
    DiffInfo,
    DiffType,
    CacheKey
)
from .exceptions import (
    DataAggregatorException,
    InvalidInputDataException,
    AggregationFailedException,
    ComplexityCalculationException,
    CacheException,
    DataValidationException
)

__version__ = "1.0.0"

__all__ = [
    # Service
    'DataAggregatorService',
    
    # Models
    'AggregationInput',
    'AggregationResult', 
    'DeveloperStats',
    'RepositoryStats',
    'TimeAnalysis',
    'ComplexityMetrics',
    'DateRange',
    'CommitData',
    'DiffInfo',
    'DiffType',
    'CacheKey',
    
    # Exceptions
    'DataAggregatorException',
    'InvalidInputDataException',
    'AggregationFailedException',
    'ComplexityCalculationException',
    'CacheException',
    'DataValidationException'
] 