"""
Universal Schedule Manager 기본 테스트

모듈의 기본 임포트와 구조를 테스트합니다.
"""

import pytest
from datetime import datetime, timedelta


def test_models_import():
    """모델 임포트 테스트"""
    from universal_schedule_manager.models import (
        ScheduleType, ScheduleStatus, ScheduleConfig,
        ScheduleRequest, ScheduleResponse, JobExecution
    )
    
    # 열거형 값 확인
    assert ScheduleType.CRON == "cron"
    assert ScheduleType.INTERVAL == "interval"
    assert ScheduleType.ONE_TIME == "one_time"
    assert ScheduleStatus.ACTIVE == "active"
    assert ScheduleStatus.INACTIVE == "inactive"


def test_exceptions_import():
    """예외 클래스 임포트 테스트"""
    from universal_schedule_manager.exceptions import (
        ScheduleManagerException,
        InvalidScheduleException,
        JobExecutionException
    )
    
    # 예외 클래스 확인
    assert issubclass(InvalidScheduleException, ScheduleManagerException)
    assert issubclass(JobExecutionException, ScheduleManagerException)


def test_schedule_config_creation():
    """ScheduleConfig 생성 테스트"""
    from universal_schedule_manager.models import ScheduleConfig, ScheduleType
    
    config = ScheduleConfig(
        schedule_type=ScheduleType.CRON,
        expression="0 9 * * 1-5",
        timezone="UTC"
    )
    
    assert config.schedule_type == ScheduleType.CRON
    assert config.expression == "0 9 * * 1-5"
    assert config.timezone == "UTC"


def test_schedule_request_creation():
    """ScheduleRequest 생성 테스트"""
    from universal_schedule_manager.models import ScheduleRequest, ScheduleType, ScheduleConfig
    
    request = ScheduleRequest(
        name="daily_report",
        description="Generate daily development report",
        schedule_config=ScheduleConfig(
            schedule_type=ScheduleType.CRON,
            expression="0 9 * * *"
        ),
        job_data={"report_type": "daily"}
    )
    
    assert request.name == "daily_report"
    assert request.description == "Generate daily development report"
    assert request.schedule_config.expression == "0 9 * * *"
    assert request.job_data["report_type"] == "daily"


def test_job_execution_creation():
    """JobExecution 생성 테스트"""
    from universal_schedule_manager.models import JobExecution
    
    execution = JobExecution(
        job_id="job_123",
        schedule_id="schedule_456",
        started_at=datetime.now(),
        status="running"
    )
    
    assert execution.job_id == "job_123"
    assert execution.schedule_id == "schedule_456"
    assert execution.status == "running"


def test_exception_creation():
    """예외 생성 테스트"""
    from universal_schedule_manager.exceptions import InvalidScheduleException
    
    exception = InvalidScheduleException("invalid_cron", "0 25 * * *")
    
    assert "invalid_cron" in str(exception)
    assert exception.details["schedule_type"] == "invalid_cron"
    assert exception.details["expression"] == "0 25 * * *" 