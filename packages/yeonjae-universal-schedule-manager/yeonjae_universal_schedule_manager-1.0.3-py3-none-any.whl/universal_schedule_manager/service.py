"""
ScheduleManager 서비스

매일 오전 8시에 데이터 분석 및 알림 작업을 예약하고 실행하는 범용 스케줄러입니다.
APScheduler를 사용하여 안정적인 스케줄링을 제공하며, 스케줄 상태 모니터링 및 실패 처리를 지원합니다.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.jobstores.memory import MemoryJobStore
    from apscheduler.executors.asyncio import AsyncIOExecutor
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False

from .models import (
    ScheduleConfig,
    JobStatus,
    ScheduleJobInfo,
    ScheduleExecutionResult,
    DeveloperSummary,
    JobExecutionInfo,
    DailyReportRequest,
    WeeklySummaryRequest
)
from .exceptions import (
    ScheduleManagerException,
    JobNotFoundException,
    SchedulerNotRunningException,
    JobExecutionException
)


class MockScheduler:
    """APScheduler가 없을 때 사용하는 Mock 스케줄러"""
    
    def __init__(self, timezone='Asia/Seoul'):
        self.timezone = timezone
        self.jobs = {}
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    def add_job(self, func, trigger=None, id=None, name=None, **kwargs):
        """Mock job 추가"""
        job_info = {
            'id': id,
            'name': name,
            'func': func,
            'trigger': trigger,
            'kwargs': kwargs
        }
        self.jobs[id] = job_info
        self.logger.info(f"Mock job added: {id}")
        return job_info
    
    def start(self):
        """Mock 스케줄러 시작"""
        self.running = True
        self.logger.info("Mock scheduler started")
    
    def shutdown(self, wait=True):
        """Mock 스케줄러 중지"""
        self.running = False
        self.logger.info("Mock scheduler stopped")
    
    def get_job(self, job_id):
        """Mock job 조회"""
        return self.jobs.get(job_id)
    
    def remove_job(self, job_id):
        """Mock job 제거"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self.logger.info(f"Mock job removed: {job_id}")


class ScheduleManagerService:
    """스케줄 관리 서비스"""
    
    def __init__(self, timezone: str = "Asia/Seoul"):
        """
        ScheduleManagerService 초기화
        
        Args:
            timezone: 시간대 설정 (기본값: Asia/Seoul)
        """
        self.timezone = timezone
        self.logger = logging.getLogger(__name__)
        self.jobs: Dict[str, ScheduleJobInfo] = {}
        self.execution_history: Dict[str, List[JobExecutionInfo]] = {}
        
        # APScheduler 설정 또는 Mock 사용
        if APSCHEDULER_AVAILABLE:
            jobstores = {
                'default': MemoryJobStore()
            }
            executors = {
                'default': AsyncIOExecutor()
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone=timezone
            )
            self.logger.info("APScheduler initialized")
        else:
            self.scheduler = MockScheduler(timezone)
            self.logger.warning("APScheduler not available, using mock scheduler")
    
    async def start(self) -> None:
        """
        스케줄러 시작 및 기본 작업 등록
        
        메모리에 따라 매일 08:00 Asia/Seoul 시간대에 일일 요약 스케줄러를 등록합니다.
        """
        try:
            # 스케줄러 시작
            self.scheduler.start()
            
            # 기본 일일 리포트 작업 등록 (매일 08:00 Asia/Seoul)
            await self.add_daily_report_job()
            
            self.logger.info("ScheduleManager started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start ScheduleManager: {e}")
            raise ScheduleManagerException(f"Failed to start scheduler: {str(e)}")
    
    async def stop(self) -> None:
        """스케줄러 중지"""
        try:
            if hasattr(self.scheduler, 'running') and self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                self.logger.info("ScheduleManager stopped")
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
    
    async def add_daily_report_job(self) -> str:
        """
        일일 리포트 작업 등록 (매일 08:00 Asia/Seoul)
        
        Returns:
            str: 등록된 작업 ID
        """
        config = ScheduleConfig(
            schedule_time="0 8 * * *",  # 매일 오전 8시
            job_id="daily_developer_report",
            function_name="trigger_daily_report",
            timezone="Asia/Seoul"
        )
        
        return await self.add_job(config, self.trigger_daily_report)
    
    async def add_job(
        self, 
        config: ScheduleConfig, 
        func: Callable,
        **kwargs
    ) -> str:
        """
        새로운 스케줄 작업 추가
        
        Args:
            config: 스케줄 설정
            func: 실행할 함수
            **kwargs: 추가 인자
            
        Returns:
            str: 등록된 작업 ID
        """
        try:
            # 설정 검증
            self._validate_schedule_config(config)
            
            # APScheduler에 작업 등록
            if APSCHEDULER_AVAILABLE:
                job = self.scheduler.add_job(
                    func=func,
                    trigger=CronTrigger.from_crontab(config.schedule_time, timezone=config.timezone),
                    id=config.job_id,
                    name=f"{config.function_name}_{config.job_id}",
                    replace_existing=config.replace_existing,
                    max_instances=config.max_instances,
                    **kwargs
                )
                next_run_time = job.next_run_time
            else:
                # Mock 스케줄러 사용
                job = self.scheduler.add_job(
                    func=func,
                    trigger=config.schedule_time,
                    id=config.job_id,
                    name=f"{config.function_name}_{config.job_id}",
                    **kwargs
                )
                next_run_time = None
            
            # 작업 정보 저장
            job_info = ScheduleJobInfo(
                job_id=config.job_id,
                name=f"{config.function_name}_{config.job_id}",
                status=JobStatus.SCHEDULED,
                next_run_time=next_run_time,
                schedule_config=config
            )
            
            self.jobs[config.job_id] = job_info
            self.execution_history[config.job_id] = []
            
            self.logger.info(f"Job added successfully: {config.job_id}")
            return config.job_id
            
        except Exception as e:
            self.logger.error(f"Failed to add job {config.job_id}: {e}")
            raise ScheduleManagerException(f"Failed to add job: {str(e)}")
    
    def get_job_status(self, job_id: str) -> ScheduleJobInfo:
        """
        작업 상태 조회
        
        Args:
            job_id: 작업 ID
            
        Returns:
            ScheduleJobInfo: 작업 정보
        """
        if job_id not in self.jobs:
            raise JobNotFoundException(job_id)
        
        return self.jobs[job_id]
    
    def list_jobs(self) -> List[ScheduleJobInfo]:
        """
        모든 작업 목록 조회
        
        Returns:
            List[ScheduleJobInfo]: 작업 목록
        """
        return list(self.jobs.values())
    
    async def trigger_daily_report(self) -> ScheduleExecutionResult:
        """
        일일 개발자 활동 리포트 생성
        
        Returns:
            ScheduleExecutionResult: 실행 결과
        """
        job_id = "daily_developer_report"
        start_time = datetime.now()
        
        try:
            self.logger.info("Starting daily report generation")
            
            # 작업 상태 업데이트
            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.RUNNING
            
            # 어제 날짜 범위 계산
            yesterday = datetime.now() - timedelta(days=1)
            date_range = {
                "start": yesterday.replace(hour=0, minute=0, second=0).isoformat(),
                "end": yesterday.replace(hour=23, minute=59, second=59).isoformat()
            }
            
            # DataRetriever를 통한 데이터 조회는 실제 구현 시 추가
            # 현재는 기본 구조만 구현
            processed_developers = []
            
            # 실행 시간 계산
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # 실행 결과 생성
            result = ScheduleExecutionResult(
                job_id=job_id,
                execution_time=start_time,
                success=True,
                processed_developers=processed_developers,
                performance_metrics={
                    "execution_time_seconds": execution_time,
                    "processed_count": len(processed_developers)
                },
                total_execution_time_seconds=execution_time
            )
            
            # 실행 기록 저장
            execution_info = JobExecutionInfo(
                timestamp=start_time,
                status=JobStatus.COMPLETED,
                execution_time_seconds=execution_time
            )
            
            if job_id in self.execution_history:
                self.execution_history[job_id].append(execution_info)
            
            # 작업 상태 업데이트
            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.COMPLETED
                self.jobs[job_id].last_execution = execution_info
            
            self.logger.info(f"Daily report completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            # 실행 실패 처리
            execution_time = (datetime.now() - start_time).total_seconds()
            
            execution_info = JobExecutionInfo(
                timestamp=start_time,
                status=JobStatus.FAILED,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
            
            if job_id in self.execution_history:
                self.execution_history[job_id].append(execution_info)
            
            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.FAILED
                self.jobs[job_id].last_execution = execution_info
            
            self.logger.error(f"Daily report generation failed: {e}")
            
            return ScheduleExecutionResult(
                job_id=job_id,
                execution_time=start_time,
                success=False,
                error_message=str(e),
                total_execution_time_seconds=execution_time
            )
    
    def _validate_schedule_config(self, config: ScheduleConfig) -> None:
        """
        스케줄 설정 검증
        
        Args:
            config: 스케줄 설정
            
        Raises:
            InvalidScheduleConfigException: 잘못된 설정인 경우
        """
        if not config.job_id:
            raise InvalidScheduleConfigException("job_id", "Job ID is required")
        
        if not config.function_name:
            raise InvalidScheduleConfigException("function_name", "Function name is required")
        
        if not config.schedule_time:
            raise InvalidScheduleConfigException("schedule_time", "Schedule time is required")
        
        # Cron 표현식 기본 검증 (5개 필드)
        cron_parts = config.schedule_time.split()
        if len(cron_parts) != 5:
            raise InvalidScheduleConfigException(
                "schedule_time", 
                "Invalid cron format. Expected 5 fields: minute hour day month day_of_week"
            ) 