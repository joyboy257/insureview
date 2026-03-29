import asyncio
import uuid
import logging
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "analysis_worker",
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
def run_portfolio_analysis(self, user_id: str, policy_ids: list[str]) -> dict:
    logger = logging.getLogger(__name__)
    logger.info(f"Starting analysis for user: {user_id}")

    async def _run():
        from app.core.database import async_session_maker
        from sqlalchemy import select
        from app.models.session import AnalysisResult

        from app.services.analysis.gap_detector import detect_gaps
        from app.services.analysis.overlap_detector import detect_overlaps
        from app.services.analysis.conflict_detector import detect_conflicts

        user_uuid = uuid.UUID(user_id)
        policy_uuids = [uuid.UUID(p) for p in policy_ids] if policy_ids else None

        gaps = await detect_gaps(user_uuid, policy_uuids)
        overlaps = await detect_overlaps(user_uuid, policy_uuids)
        conflicts = await detect_conflicts(user_uuid, policy_uuids)

        output_data = {
            "gaps": gaps,
            "overlaps": overlaps,
            "conflicts": conflicts,
            "summary": {
                "total_gaps": len(gaps),
                "critical_gaps": sum(1 for g in gaps if g["severity"] == "critical"),
                "warning_gaps": sum(1 for g in gaps if g["severity"] == "warning"),
                "total_overlaps": len(overlaps),
                "warning_overlaps": sum(1 for o in overlaps if o["severity"] == "warning"),
                "total_conflicts": len(conflicts),
                "critical_conflicts": sum(1 for c in conflicts if c["severity"] == "critical"),
            },
        }

        # Store results in DB
        async with async_session_maker() as db:
            result = await db.execute(
                select(AnalysisResult)
                .where(
                    AnalysisResult.user_id == user_uuid,
                    AnalysisResult.analysis_type == "portfolio_snapshot",
                )
                .order_by(AnalysisResult.created_at.desc())
                .limit(1)
            )
            record: AnalysisResult | None = result.scalar_one_or_none()
            if record:
                record.output_data = output_data
                await db.commit()

        # Wire gap-alert email notification
        if gaps and gaps.get("gaps"):
            from app.core.database import async_session_maker
            from sqlalchemy import select
            from app.models.user import User
            from app.workers.notification_worker import send_gap_alert_notification

            async with async_session_maker() as db:
                user_record = await db.execute(select(User).where(User.id == user_uuid))
                user = user_record.scalar_one_or_none()
                if user and user.email:
                    send_gap_alert_notification.delay(
                        user_id=user_id,
                        user_email=user.email,
                        gap_count=output_data["summary"]["total_gaps"],
                        policy_count=len(policy_uuids) if policy_uuids else 0,
                        gap_names=[g.get("coverage_type", "Unknown") for g in gaps.get("gaps", [])],
                    )
        return output_data

    try:
        result = asyncio.run(_run())
        logger.info(f"Analysis completed for user: {user_id}")
        return result
    except Exception as exc:
        logger.exception(f"Analysis task failed for user: {user_id}")
        raise self.retry(exc=exc, countdown=120)


def trigger_analysis_job(user_id: str, policy_ids: list[str]) -> uuid.UUID:
    """Create an AnalysisResult record and queue the Celery task."""
    import asyncio

    async def _create():
        from app.core.database import async_session_maker
        from app.models.session import AnalysisResult

        async with async_session_maker() as session:
            record = AnalysisResult(
                user_id=uuid.UUID(user_id),
                analysis_type="portfolio_snapshot",
                trigger="manual",
                input_payload={"policy_ids": policy_ids},
                output_data={},
            )
            session.add(record)
            await session.commit()
            await session.refresh(record)
            return record.id

    analysis_id = asyncio.run(_create())
    run_portfolio_analysis.delay(user_id, policy_ids)
    return analysis_id
