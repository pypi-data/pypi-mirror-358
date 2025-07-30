"""
Universal Data Aggregator 기본 테스트

모듈의 기본 임포트와 구조를 테스트합니다.
"""

import pytest
from datetime import datetime


def test_models_import():
    """모델 임포트 테스트"""
    from universal_data_aggregator.models import (
        AggregationType, DateRange, AggregationRequest, 
        DeveloperSummary, AggregationResult
    )
    
    # 열거형 값 확인
    assert AggregationType.DAILY == "daily"
    assert AggregationType.WEEKLY == "weekly"
    assert AggregationType.MONTHLY == "monthly"


def test_exceptions_import():
    """예외 클래스 임포트 테스트"""
    from universal_data_aggregator.exceptions import (
        DataAggregatorException,
        InvalidDateRangeException,
        AggregationException
    )
    
    # 예외 클래스 확인
    assert issubclass(InvalidDateRangeException, DataAggregatorException)
    assert issubclass(AggregationException, DataAggregatorException)


def test_date_range_creation():
    """DateRange 생성 테스트"""
    from universal_data_aggregator.models import DateRange
    
    date_range = DateRange(
        start="2024-01-01",
        end="2024-01-31"
    )
    
    assert date_range.start == "2024-01-01"
    assert date_range.end == "2024-01-31"


def test_aggregation_request_creation():
    """AggregationRequest 생성 테스트"""
    from universal_data_aggregator.models import AggregationRequest, AggregationType, DateRange
    
    request = AggregationRequest(
        aggregation_type=AggregationType.DAILY,
        date_range=DateRange(
            start="2024-01-01",
            end="2024-01-31"
        )
    )
    
    assert request.aggregation_type == AggregationType.DAILY
    assert request.date_range.start == "2024-01-01"


def test_developer_summary_creation():
    """DeveloperSummary 생성 테스트"""
    from universal_data_aggregator.models import DeveloperSummary
    
    summary = DeveloperSummary(
        developer_email="test@example.com",
        developer_name="Test User",
        total_commits=10,
        total_lines_added=100,
        total_lines_deleted=50,
        active_days=5
    )
    
    assert summary.developer_email == "test@example.com"
    assert summary.developer_name == "Test User"
    assert summary.total_commits == 10
    assert summary.total_lines_added == 100
    assert summary.total_lines_deleted == 50
    assert summary.active_days == 5


def test_exception_creation():
    """예외 생성 테스트"""
    from universal_data_aggregator.exceptions import InvalidDateRangeException
    
    exception = InvalidDateRangeException("2024-01-31", "2024-01-01")
    
    assert "2024-01-31" in str(exception)
    assert "2024-01-01" in str(exception)
    assert exception.details["start_date"] == "2024-01-31"
    assert exception.details["end_date"] == "2024-01-01" 