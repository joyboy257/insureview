import asyncio
import uuid
import logging
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "parse_worker",
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
def parse_policy_task(self, session_id: str) -> dict:
    logger = logging.getLogger(__name__)
    logger.info(f"Starting parse task for session: {session_id}")
    try:
        # run_parsing_pipeline is async so we run it in an event loop
        from app.services.parsing.pipeline import run_parsing_pipeline
        result = asyncio.run(run_parsing_pipeline(session_id))
        logger.info(f"Parse task completed for session: {session_id}")
        return {"status": "completed", "policy_id": str(result)}
        # Wire parse-complete email notification
        from app.core.database import async_session_maker
        from sqlalchemy import select
        from app.models.session import ParsingSession
        from app.models.user import User
        from app.workers.notification_worker import send_parse_complete_notification

        async with async_session_maker() as db:
            session_record = await db.execute(
                select(ParsingSession).where(ParsingSession.id == uuid.UUID(session_id))
            )
            parsed_session = session_record.scalar_one_or_none()
            if parsed_session and parsed_session.user_id:
                user_record = await db.execute(
                    select(User).where(User.id == parsed_session.user_id)
                )
                user = user_record.scalar_one_or_none()
                if user and user.email:
                    send_parse_complete_notification.delay(
                        session_id=session_id,
                        user_email=user.email,
                        filename=parsed_session.original_filename or "policy document",
                    )
    except Exception as exc:
        logger.exception(f"Parse task failed for session: {session_id}")
        raise self.retry(exc=exc, countdown=60)


def trigger_parse_job(session_id: str) -> str:
    task = parse_policy_task.delay(session_id)
    return task.id
