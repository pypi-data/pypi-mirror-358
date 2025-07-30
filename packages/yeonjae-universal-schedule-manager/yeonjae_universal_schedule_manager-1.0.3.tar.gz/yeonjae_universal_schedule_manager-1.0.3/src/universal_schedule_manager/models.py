"""
ScheduleManager 모듈의 데이터 모델

스케줄링 작업과 관련된 모든 데이터 구조를 정의합니다.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ScheduleType(str, Enum):
    """스케줄 타입"""
    CRON = "cron"
    INTERVAL = "interval"
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ScheduleStatus(str, Enum):
    """스케줄 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


class JobStatus(str, Enum):
    """작업 상태"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class ScheduleConfig(BaseModel):
    """스케줄 설정"""
    schedule_type: ScheduleType = Field(..., description="스케줄 타입")
    expression: str = Field(..., description="스케줄 표현식 (cron, interval 등)")
    timezone: str = Field(default="Asia/Seoul", description="시간대 설정")
    max_instances: int = Field(default=1, description="최대 동시 실행 인스턴스 수")
    replace_existing: bool = Field(default=True, description="기존 작업 교체 여부")


class JobExecutionInfo(BaseModel):
    """작업 실행 정보"""
    timestamp: datetime = Field(..., description="실행 시간")
    status: JobStatus = Field(..., description="실행 상태")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    execution_time_seconds: Optional[float] = Field(None, description="실행 시간(초)")


class ScheduleJobInfo(BaseModel):
    """스케줄 작업 정보"""
    job_id: str = Field(..., description="작업 ID")
    name: str = Field(..., description="작업 이름")
    status: JobStatus = Field(..., description="작업 상태")
    next_run_time: Optional[datetime] = Field(None, description="다음 실행 시간")
    last_execution: Optional[JobExecutionInfo] = Field(None, description="마지막 실행 결과")
    schedule_config: ScheduleConfig = Field(..., description="스케줄 설정")


class CommitData(BaseModel):
    """커밋 데이터"""
    commit_id: str = Field(..., description="커밋 ID")
    message: str = Field(..., description="커밋 메시지")
    author: str = Field(..., description="작성자")
    timestamp: datetime = Field(..., description="커밋 시간")
    repository: str = Field(..., description="저장소 이름")
    branch: str = Field(..., description="브랜치명")


class DiffData(BaseModel):
    """Diff 데이터"""
    file_path: str = Field(..., description="파일 경로")
    additions: int = Field(..., description="추가된 라인 수")
    deletions: int = Field(..., description="삭제된 라인 수")
    changes: str = Field(..., description="변경 내용")
    complexity_score: Optional[float] = Field(None, description="복잡도 점수")
    language: Optional[str] = Field(None, description="프로그래밍 언어")


class DeveloperSummary(BaseModel):
    """개발자 요약 데이터"""
    developer_id: str = Field(..., description="개발자 ID")
    developer_name: str = Field(..., description="개발자 이름")
    commits: List[CommitData] = Field(default_factory=list, description="커밋 목록")
    diffs: List[DiffData] = Field(default_factory=list, description="diff 목록")
    statistics: Dict[str, int] = Field(default_factory=dict, description="통계 정보")
    date_range: Dict[str, str] = Field(..., description="조회 날짜 범위")


class ScheduleExecutionResult(BaseModel):
    """스케줄 실행 결과"""
    job_id: str = Field(..., description="작업 ID")
    execution_time: datetime = Field(..., description="실행 시간")
    success: bool = Field(..., description="성공 여부")
    processed_developers: List[str] = Field(default_factory=list, description="처리된 개발자 목록")
    error_message: Optional[str] = Field(None, description="에러 메시지")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="성능 메트릭")
    total_execution_time_seconds: float = Field(..., description="총 실행 시간(초)")


class DailyReportRequest(BaseModel):
    """일일 리포트 요청"""
    target_date: Optional[datetime] = Field(None, description="대상 날짜 (기본값: 어제)")
    include_statistics: bool = Field(default=True, description="통계 포함 여부")
    developer_filters: Optional[List[str]] = Field(None, description="개발자 필터")
    repository_filters: Optional[List[str]] = Field(None, description="저장소 필터")


class ScheduleRequest(BaseModel):
    """스케줄 요청"""
    name: str = Field(..., description="스케줄 이름")
    description: str = Field(..., description="스케줄 설명")
    schedule_config: ScheduleConfig = Field(..., description="스케줄 설정")
    job_data: Dict[str, Any] = Field(default_factory=dict, description="작업 데이터")
    enabled: bool = Field(default=True, description="활성화 여부")


class ScheduleResponse(BaseModel):
    """스케줄 응답"""
    schedule_id: str = Field(..., description="스케줄 ID")
    name: str = Field(..., description="스케줄 이름")
    status: ScheduleStatus = Field(..., description="스케줄 상태")
    next_run_time: Optional[datetime] = Field(None, description="다음 실행 시간")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")


class JobExecution(BaseModel):
    """작업 실행"""
    job_id: str = Field(..., description="작업 ID")
    schedule_id: str = Field(..., description="스케줄 ID")
    started_at: datetime = Field(..., description="시작 시간")
    ended_at: Optional[datetime] = Field(None, description="종료 시간")
    status: str = Field(..., description="실행 상태")
    result: Optional[Dict[str, Any]] = Field(None, description="실행 결과")


class WeeklySummaryRequest(BaseModel):
    """주간 요약 요청"""
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")
    include_trends: bool = Field(default=True, description="트렌드 분석 포함 여부")
    team_grouping: bool = Field(default=False, description="팀별 그룹핑 여부") 