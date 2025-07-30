"""
Universal Data Aggregator 모듈의 데이터 모델

커밋 데이터와 diff 정보를 가공, 집계, 통계 처리를 위한 데이터 구조를 정의합니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum

from pydantic import BaseModel, Field, validator
from typing_extensions import Literal


class AggregationType(str, Enum):
    """집계 타입"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    DEVELOPER = "developer"
    REPOSITORY = "repository"


class DiffType(str, Enum):
    """Diff 변경 타입"""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class DateRange(BaseModel):
    """집계 대상 날짜 범위"""
    start: str = Field(..., description="시작 날짜 (YYYY-MM-DD 형식)")
    end: str = Field(..., description="종료 날짜 (YYYY-MM-DD 형식)")
    
    @validator('start', 'end')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다")
    
    @validator('end')
    def end_after_start(cls, v, values):
        if 'start' in values:
            start_date = datetime.strptime(values['start'], "%Y-%m-%d")
            end_date = datetime.strptime(v, "%Y-%m-%d")
            if end_date < start_date:
                raise ValueError("종료 날짜는 시작 날짜보다 늦어야 합니다")
        return v


class DiffInfo(BaseModel):
    """Diff 정보"""
    file_path: str = Field(..., description="파일 경로")
    diff_type: DiffType = Field(..., description="변경 타입")
    lines_added: int = Field(0, ge=0, description="추가된 라인 수")
    lines_deleted: int = Field(0, ge=0, description="삭제된 라인 수")
    complexity_score: Optional[float] = Field(None, ge=0, description="복잡도 점수")
    language: Optional[str] = Field(None, description="프로그래밍 언어")


class CommitData(BaseModel):
    """커밋 데이터"""
    commit_id: str = Field(..., description="커밋 ID")
    author: str = Field(..., description="작성자 이름")
    author_email: str = Field(..., description="작성자 이메일")
    timestamp: datetime = Field(..., description="커밋 시간")
    message: str = Field(..., description="커밋 메시지")
    repository: str = Field(..., description="저장소 이름")
    branch: str = Field(..., description="브랜치 이름")
    diff_info: List[DiffInfo] = Field(default_factory=list, description="Diff 정보 목록")
    
    @property
    def total_lines_added(self) -> int:
        """총 추가된 라인 수"""
        return sum(diff.lines_added for diff in self.diff_info)
    
    @property
    def total_lines_deleted(self) -> int:
        """총 삭제된 라인 수"""
        return sum(diff.lines_deleted for diff in self.diff_info)
    
    @property
    def files_changed(self) -> int:
        """변경된 파일 수"""
        return len(self.diff_info)


class AggregationInput(BaseModel):
    """집계 입력 데이터"""
    commits: List[CommitData] = Field(..., description="커밋 데이터 목록")
    date_range: DateRange = Field(..., description="집계 대상 날짜 범위")
    developer_filter: Optional[List[str]] = Field(None, description="개발자 필터")
    repository_filter: Optional[List[str]] = Field(None, description="저장소 필터")
    
    @validator('commits')
    def validate_commits_not_empty(cls, v):
        if not v:
            raise ValueError("커밋 데이터가 비어있습니다")
        return v


class DeveloperStats(BaseModel):
    """개발자별 통계"""
    developer: str = Field(..., description="개발자 이름")
    developer_email: str = Field(..., description="개발자 이메일")
    commit_count: int = Field(0, ge=0, description="커밋 수")
    lines_added: int = Field(0, ge=0, description="추가된 라인 수")
    lines_deleted: int = Field(0, ge=0, description="삭제된 라인 수")
    files_changed: int = Field(0, ge=0, description="변경된 파일 수")
    repositories: List[str] = Field(default_factory=list, description="관련 저장소 목록")
    languages_used: List[str] = Field(default_factory=list, description="사용된 언어 목록")
    avg_complexity: float = Field(0.0, ge=0, description="평균 복잡도")
    first_commit_time: Optional[datetime] = Field(None, description="첫 커밋 시간")
    last_commit_time: Optional[datetime] = Field(None, description="마지막 커밋 시간")
    peak_hours: List[int] = Field(default_factory=list, description="활동 피크 시간대")


class RepositoryStats(BaseModel):
    """저장소별 통계"""
    repository: str = Field(..., description="저장소 이름")
    total_commits: int = Field(0, ge=0, description="총 커밋 수")
    contributors: List[str] = Field(default_factory=list, description="기여자 목록")
    lines_added: int = Field(0, ge=0, description="추가된 라인 수")
    lines_deleted: int = Field(0, ge=0, description="삭제된 라인 수")
    files_changed: int = Field(0, ge=0, description="변경된 파일 수")
    languages: List[str] = Field(default_factory=list, description="사용된 언어 목록")
    avg_complexity: float = Field(0.0, ge=0, description="평균 복잡도")


class TimeAnalysis(BaseModel):
    """시간대별 활동 분석"""
    peak_hours: List[int] = Field(default_factory=list, description="활동이 많은 시간대")
    commit_frequency: Dict[int, int] = Field(default_factory=dict, description="시간대별 커밋 수")
    work_pattern: Literal["morning", "afternoon", "evening", "night", "unknown"] = Field(
        "unknown", description="작업 패턴"
    )
    avg_commit_interval: float = Field(0.0, ge=0, description="평균 커밋 간격 (분)")


class ComplexityMetrics(BaseModel):
    """코드 복잡도 메트릭"""
    avg_complexity: float = Field(0.0, ge=0, description="평균 복잡도")
    max_complexity: float = Field(0.0, ge=0, description="최대 복잡도")
    min_complexity: float = Field(0.0, ge=0, description="최소 복잡도")
    complexity_trend: Literal["increasing", "decreasing", "stable"] = Field(
        "stable", description="복잡도 트렌드"
    )
    high_complexity_files: List[str] = Field(
        default_factory=list, description="고복잡도 파일 목록"
    )


class AggregationResult(BaseModel):
    """집계 결과 데이터"""
    developer_stats: Dict[str, DeveloperStats] = Field(
        default_factory=dict, description="개발자별 통계"
    )
    repository_stats: Dict[str, RepositoryStats] = Field(
        default_factory=dict, description="저장소별 통계"
    )
    time_analysis: TimeAnalysis = Field(
        default_factory=TimeAnalysis, description="시간대별 분석"
    )
    complexity_metrics: ComplexityMetrics = Field(
        default_factory=ComplexityMetrics, description="복잡도 메트릭"
    )
    aggregation_time: datetime = Field(
        default_factory=datetime.now, description="집계 시간"
    )
    data_quality_score: float = Field(1.0, ge=0, le=1, description="데이터 품질 점수")
    
    @property
    def total_commits(self) -> int:
        """전체 커밋 수"""
        return sum(stats.commit_count for stats in self.developer_stats.values())
    
    @property
    def total_developers(self) -> int:
        """참여 개발자 수"""
        return len(self.developer_stats)
    
    @property
    def total_repositories(self) -> int:
        """관련 저장소 수"""
        return len(self.repository_stats)


class AggregationRequest(BaseModel):
    """집계 요청"""
    aggregation_type: AggregationType = Field(..., description="집계 타입")
    date_range: DateRange = Field(..., description="날짜 범위")
    developer_filter: Optional[List[str]] = Field(None, description="개발자 필터")
    repository_filter: Optional[List[str]] = Field(None, description="저장소 필터")
    include_complexity: bool = Field(True, description="복잡도 포함 여부")


class DeveloperSummary(BaseModel):
    """개발자 요약"""
    developer_email: str = Field(..., description="개발자 이메일")
    developer_name: str = Field(..., description="개발자 이름")
    total_commits: int = Field(0, description="총 커밋 수")
    total_lines_added: int = Field(0, description="총 추가 라인")
    total_lines_deleted: int = Field(0, description="총 삭제 라인")
    active_days: int = Field(0, description="활동 일수")
    repositories: List[str] = Field(default_factory=list, description="참여 저장소")


class CacheKey(BaseModel):
    """캐시 키 생성용"""
    date_range: DateRange = Field(..., description="날짜 범위")
    developer_filter: Optional[str] = Field(None, description="개발자 필터")
    repository_filter: Optional[str] = Field(None, description="저장소 필터")
    
    def to_string(self) -> str:
        """캐시 키 문자열 생성"""
        key_parts = [f"{self.date_range.start}_{self.date_range.end}"]
        if self.developer_filter:
            key_parts.append(f"dev_{self.developer_filter}")
        if self.repository_filter:
            key_parts.append(f"repo_{self.repository_filter}")
        return "_".join(key_parts) 