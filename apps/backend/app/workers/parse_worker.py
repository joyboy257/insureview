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
    except Exception as exc:
        logger.exception(f"Parse task failed for session: {session_id}")
        raise self.retry(exc=exc, countdown=60)


def trigger_parse_job(session_id: str) -> str:
    task = parse_policy_task.delay(session_id)
    return task.id
