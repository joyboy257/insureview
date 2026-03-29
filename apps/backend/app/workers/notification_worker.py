import asyncio
import uuid
import logging
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "notification_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Singapore",
    enable_utc=True,
)


@celery_app.task(bind=True, max_retries=3)
def send_parse_complete_notification(self, session_id: str, user_email: str, filename: str) -> dict:
    """
    Send an email when a policy parse session completes.
    Call this from parse_worker.py after run_parsing_pipeline succeeds.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Sending parse-complete notification for session {session_id}")

    async def _send():
        from app.services.email.sender import send_parse_complete_email

        dashboard_url = f"{settings.frontend_url}/dashboard"
        success = await send_parse_complete_email(
            to_email=user_email,
            filename=filename,
            dashboard_url=dashboard_url,
        )
        return {"session_id": session_id, "email_sent": success, "recipient": user_email}

    try:
        result = asyncio.run(_send())
        logger.info(f"Parse-complete notification result: {result}")
        return result
    except Exception as exc:
        logger.exception(f"Failed to send parse-complete notification: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def send_gap_alert_notification(
    self,
    user_id: str,
    user_email: str,
    gap_count: int,
    policy_count: int,
    gap_names: list[str],
) -> dict:
    """
    Send an email when new gaps are detected in a user's portfolio.
    Call this from analysis_worker.py after gaps are detected.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Sending gap alert notification for user {user_id}: {gap_count} gaps")

    async def _send():
        from app.services.email.sender import send_gap_detected_email

        dashboard_url = f"{settings.frontend_url}/dashboard"
        success = await send_gap_detected_email(
            to_email=user_email,
            gap_count=gap_count,
            policy_count=policy_count,
            gap_names=gap_names,
            dashboard_url=dashboard_url,
        )
        return {"user_id": user_id, "email_sent": success, "recipient": user_email, "gaps": gap_count}

    try:
        result = asyncio.run(_send())
        logger.info(f"Gap alert notification result: {result}")
        return result
    except Exception as exc:
        logger.exception(f"Failed to send gap alert notification: {exc}")
        raise self.retry(exc=exc, countdown=120)
