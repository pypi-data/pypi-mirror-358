"""Celery tasks for schedule manager."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from celery import shared_task

from yeonjae_universal_data_retriever.service import DataRetrieverService
from yeonjae_universal_llm_service import LLMService, LLMInput, LLMProvider, ModelConfig
from yeonjae_universal_data_aggregator.service import DataAggregatorService
from yeonjae_universal_prompt_builder.service import PromptBuilderService
from yeonjae_universal_notification_service import NotificationService
# Simplified logging for standalone operation
def log_module_io(module_name: str, operation: str, data: dict):
    pass

logger = logging.getLogger(__name__)


@shared_task(name="schedule_manager.daily_summary_task")
def daily_summary_task() -> Dict[str, Any]:
    """
    매일 오전 8시에 실행되는 일일 개발자 활동 요약 작업
    
    기획서 준수 흐름:
    ScheduleManager → DataRetriever → DataAggregator → PromptBuilder → LLMService → NotificationService
    
    Returns:
        Dict[str, Any]: 실행 결과
    """
    start_time = datetime.now()
    
    try:
        logger.info("🌅 Starting daily developer summary at 08:00 Asia/Seoul")
        
        # 어제 날짜 범위 계산 (Asia/Seoul 기준)
        from zoneinfo import ZoneInfo
        seoul_tz = ZoneInfo("Asia/Seoul")
        now_seoul = datetime.now(seoul_tz)
        yesterday_start = (now_seoul - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_end = (now_seoul - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
        
        logger.info(f"📅 Processing data for: {yesterday_start.strftime('%Y-%m-%d')} (Asia/Seoul)")
        
        # 1️⃣ DataRetriever: 어제 데이터 조회
        logger.info("📊 DataRetriever: Starting data retrieval")
        
        log_module_io("DataRetriever", "INPUT", metadata={
            "operation": "get_daily_summary",
            "target_date": yesterday_start.isoformat(),
            "timezone": "Asia/Seoul"
        })
        
        data_retriever = DataRetrieverService()
        retrieved_data = data_retriever.get_daily_summary(target_date=yesterday_start)
        
        log_module_io("DataRetriever", "OUTPUT", output_data=retrieved_data, metadata={
            "commits_found": len(retrieved_data.commits),
            "developers_count": len(set(commit.author for commit in retrieved_data.commits)),
            "query_time": retrieved_data.metadata.query_time_seconds if retrieved_data.metadata else 0
        })
        
        logger.info(
            "✅ DataRetriever: Found %d records from daily summary",
            len(retrieved_data.commits)
        )
        
        # 데이터가 없으면 종료
        if not retrieved_data.commits:
            logger.info("📭 No data found for yesterday. Skipping daily summary.")
            return {
                "success": True,
                "message": "No data found for yesterday",
                "execution_time_seconds": (datetime.now() - start_time).total_seconds()
            }
        
        # 2️⃣ DataAggregator: 개발자별 활동 집계
        logger.info("🔢 DataAggregator: Starting data aggregation")
        
        # 데이터를 AggregationInput 형태로 변환
        from yeonjae_universal_data_aggregator.models import AggregationInput, CommitData, DiffInfo, DateRange
        
        commits = []
        for commit_info in retrieved_data.commits:
            # CommitInfo를 CommitData로 변환
            commit_data = CommitData(
                commit_id=commit_info.commit_hash,
                author=commit_info.author,
                author_email=commit_info.author_email,
                timestamp=commit_info.timestamp,
                message=commit_info.message,
                repository=commit_info.repository,
                branch=commit_info.branch,
                diff_info=[]  # 기본값
            )
            commits.append(commit_data)
        
        # DateRange를 문자열 형식으로 생성
        date_range = DateRange(
            start=yesterday_start.strftime('%Y-%m-%d'),
            end=yesterday_end.strftime('%Y-%m-%d')
        )
        
        aggregation_input = AggregationInput(
            commits=commits,
            date_range=date_range
        )
        
        log_module_io("DataAggregator", "INPUT", input_data=aggregation_input, metadata={
            "operation": "aggregate_data",
            "input_commits_count": len(commits)
        })
        
        data_aggregator = DataAggregatorService()
        # async 메서드를 동기적으로 실행
        import asyncio
        try:
            # 이미 이벤트 루프가 실행 중인 경우 새 루프 생성
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, data_aggregator.aggregate_data(aggregation_input))
                    aggregated_data = future.result()
            else:
                aggregated_data = asyncio.run(data_aggregator.aggregate_data(aggregation_input))
        except RuntimeError:
            # 이벤트 루프가 없는 경우
            aggregated_data = asyncio.run(data_aggregator.aggregate_data(aggregation_input))
        
        log_module_io("DataAggregator", "OUTPUT", output_data=aggregated_data, metadata={
            "developers_processed": len(aggregated_data.developer_stats),
            "repositories_processed": len(aggregated_data.repository_stats),
            "time_analysis_completed": aggregated_data.time_analysis is not None,
            "complexity_metrics_completed": aggregated_data.complexity_metrics is not None
        })
        
        logger.info(
            "✅ DataAggregator: Processed %d developers, %d repositories",
            len(aggregated_data.developer_stats),
            len(aggregated_data.repository_stats)
        )
        
        # 3️⃣ PromptBuilder: LLM용 프롬프트 생성
        logger.info("📝 PromptBuilder: Starting prompt generation")
        
        log_module_io("PromptBuilder", "INPUT", input_data=aggregated_data, metadata={
            "operation": "build_daily_summary_prompt",
            "template_type": "daily_developer_summary",
            "language": "korean"
        })
        
        prompt_builder = PromptBuilderService()
        
        # 전체 개발자 목록에서 첫 번째 개발자를 대상으로 하거나, 
        # 개발자가 없으면 "전체 팀"으로 설정
        if aggregated_data.developer_stats:
            # 첫 번째 개발자 선택
            first_developer = list(aggregated_data.developer_stats.values())[0]
            target_developer = first_developer.developer
        else:
            target_developer = "개발팀"
        
        # AggregationResult를 딕셔너리로 변환
        aggregated_dict = {
            "developer_stats": {
                email: {
                    "developer": stats.developer,
                    "commit_count": stats.commit_count,
                    "lines_added": stats.lines_added,
                    "lines_deleted": stats.lines_deleted,
                    "files_changed": stats.files_changed,
                    "languages_used": stats.languages_used,
                    "avg_complexity": stats.avg_complexity
                }
                for email, stats in aggregated_data.developer_stats.items()
            }
        }
        
        prompt_result = prompt_builder.build_daily_summary_prompt(aggregated_dict, target_developer)
        
        log_module_io("PromptBuilder", "OUTPUT", output_data=prompt_result, metadata={
            "prompt_length": len(prompt_result.prompt),
            "template_used": prompt_result.template_used,
            "variables_count": len(prompt_result.context_data) if hasattr(prompt_result, 'context_data') else 0
        })
        
        logger.info(
            "✅ PromptBuilder: Generated prompt (%d chars) using template '%s'",
            len(prompt_result.prompt),
            prompt_result.template_used
        )
        
        # 4️⃣ LLMService: 코드 분석 및 요약 생성
        logger.info("🤖 LLMService: Starting LLM analysis")
        
        log_module_io("LLMService", "INPUT", input_data=prompt_result, metadata={
            "operation": "generate_summary",
            "prompt_length": len(prompt_result.prompt),
            "provider": "openai"  # 기본값
        })
        
        llm_service = LLMService()
        
        # LLMInput 객체 생성
        model_config = ModelConfig(
            model="gpt-3.5-turbo",  # 기본 모델
            temperature=0.7,
            max_tokens=1000
        )
        
        llm_input = LLMInput(
            prompt=prompt_result.prompt,
            llm_provider=LLMProvider.OPENAI,
            model_config=model_config
        )
        
        # async 메서드를 동기적으로 실행
        try:
            # 이미 이벤트 루프가 실행 중인 경우 새 루프 생성
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, llm_service.generate_summary(llm_input))
                    llm_response = future.result()
            else:
                llm_response = asyncio.run(llm_service.generate_summary(llm_input))
        except RuntimeError:
            # 이벤트 루프가 없는 경우
            llm_response = asyncio.run(llm_service.generate_summary(llm_input))
        
        log_module_io("LLMService", "OUTPUT", output_data=llm_response, metadata={
            "response_length": len(llm_response.summary),
            "confidence_score": llm_response.confidence_score,
            "provider_used": llm_response.metadata.provider if llm_response.metadata else "unknown",
            "model_used": llm_response.metadata.model_used if llm_response.metadata else "unknown"
        })
        
        logger.info(
            "✅ LLMService: Generated summary (%d chars) using %s/%s",
            len(llm_response.summary),
            llm_response.metadata.provider if llm_response.metadata else "unknown",
            llm_response.metadata.model_used if llm_response.metadata else "unknown"
        )
        
        # 5️⃣ NotificationService: Slack 알림 전송
        logger.info("📢 NotificationService: Starting notification delivery")
        
        # 알림 메시지 구성
        notification_message = f"""🌅 **일일 개발 활동 요약** - {yesterday_start.strftime('%Y년 %m월 %d일')}

{llm_response.summary}

---
📊 **전체 통계**
• 개발자: {len(aggregated_data.developer_stats)}명
• 저장소: {len(aggregated_data.repository_stats)}개
• 처리된 커밋: {len(commits)}개

_CodePing.AI 자동 생성 리포트_"""
        
        log_module_io("NotificationService", "INPUT", metadata={
            "operation": "send_slack_message",
            "message_length": len(notification_message),
            "channel": "default"
        })
        
        notification_service = NotificationService()
        notification_result = notification_service.send_daily_summary(
            summary_report=notification_message,
            developer=target_developer,
            developer_email="team@codeping.ai",  # 기본 이메일
            slack_channel="#dev-reports"  # 기본 채널
        )
        
        log_module_io("NotificationService", "OUTPUT", output_data=notification_result, metadata={
            "success": notification_result.success,
            "channel_used": notification_result.channel,
            "delivery_time": notification_result.timestamp.isoformat() if notification_result.timestamp else None
        })
        
        if notification_result.success:
            logger.info(
                "✅ NotificationService: Message sent successfully to %s",
                notification_result.channel
            )
        else:
            logger.error(
                "❌ NotificationService: Failed to send message: %s",
                notification_result.error_message
            )
        
        # 실행 완료
        total_execution_time = (datetime.now() - start_time).total_seconds()
        
        result = {
            "success": True,
            "date_processed": yesterday_start.strftime('%Y-%m-%d'),
            "developers_count": len(aggregated_data.developer_stats),
            "commits_count": len(commits),
            "notification_sent": notification_result.success,
            "execution_time_seconds": total_execution_time,
            "modules_executed": ["DataRetriever", "DataAggregator", "PromptBuilder", "LLMService", "NotificationService"]
        }
        
        logger.info(
            "🎉 Daily summary completed successfully in %.2fs: %d developers, %d commits, notification=%s",
            total_execution_time,
            len(aggregated_data.developer_stats),
            len(commits),
            "✅" if notification_result.success else "❌"
        )
        
        return result
        
    except Exception as exc:
        total_execution_time = (datetime.now() - start_time).total_seconds()
        
        logger.exception("❌ Daily summary task failed: %s", exc)
        
        return {
            "success": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "execution_time_seconds": total_execution_time
        }
