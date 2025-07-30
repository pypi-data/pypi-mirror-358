"""
ScheduleManager 모듈의 예외 클래스

스케줄링 작업과 관련된 모든 예외를 정의합니다.
"""


class ScheduleManagerException(Exception):
    """ScheduleManager 기본 예외"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class JobNotFoundException(ScheduleManagerException):
    """작업을 찾을 수 없는 경우"""
    def __init__(self, job_id: str):
        message = f"Job not found: {job_id}"
        super().__init__(message, {"job_id": job_id})


class SchedulerNotRunningException(ScheduleManagerException):
    """스케줄러가 실행되지 않은 경우"""
    def __init__(self):
        message = "Scheduler is not running"
        super().__init__(message)


class JobExecutionException(ScheduleManagerException):
    """작업 실행 중 오류가 발생한 경우"""
    def __init__(self, job_id: str, error: Exception):
        message = f"Job execution failed: {job_id}"
        super().__init__(message, {
            "job_id": job_id,
            "error_type": type(error).__name__,
            "error_message": str(error)
        })


class InvalidScheduleConfigException(ScheduleManagerException):
    """잘못된 스케줄 설정인 경우"""
    def __init__(self, config_field: str, reason: str):
        message = f"Invalid schedule config - {config_field}: {reason}"
        super().__init__(message, {
            "config_field": config_field,
            "reason": reason
        })


class InvalidScheduleException(ScheduleManagerException):
    """잘못된 스케줄 예외"""
    def __init__(self, schedule_type: str, expression: str):
        message = f"Invalid schedule type '{schedule_type}' with expression '{expression}'"
        super().__init__(message, {
            "schedule_type": schedule_type,
            "expression": expression
        })


class DataRetrievalException(ScheduleManagerException):
    """데이터 조회 중 오류가 발생한 경우"""
    def __init__(self, operation: str, error: Exception):
        message = f"Data retrieval failed during {operation}"
        super().__init__(message, {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error)
        }) 