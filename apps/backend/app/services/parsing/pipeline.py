"""
LLM parsing pipeline orchestrator.

Flow:
  1. Fetch PDF from S3 using session's s3_upload_key
  2. Extract text (pdfplumber or Document AI OCR)
  3. Chunk into semantic sections
  4. Call Claude to extract structured data
  5. Validate and normalise the output
  6. Write to DB (Policy + Benefits + Riders + Exclusions)
  7. Delete PDF from S3
  8. Update ParsingSession status
"""

import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.core.database import async_session_maker
from app.models.session import ParsingSession
from app.services.llm.client import get_llm_client
from app.services.parsing.chunker import chunk_by_sections
from app.services.parsing.db_writer import write_parsed_policy
from app.services.parsing.output_parser import parse_and_validate
from app.services.parsing.text_extractor import extract_pdf_text

logger = logging.getLogger(__name__)

# ─── S3 client ────────────────────────────────────────────────────────────────


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


def _fetch_pdf_from_s3(s3_key: str) -> bytes:
    """Download PDF bytes from S3."""
    client = _get_s3_client()
    try:
        response = client.get_object(Bucket=settings.s3_bucket_name, Key=s3_key)
        return response["Body"].read()
    except ClientError as e:
        raise RuntimeError(f"Failed to fetch PDF from S3 ({s3_key}): {e}")


def _delete_pdf_from_s3(s3_key: str) -> None:
    """Delete PDF from S3 after successful parsing (PDPA compliance)."""
    client = _get_s3_client()
    try:
        client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)
        logger.info(f"Deleted PDF from S3: {s3_key}")
    except ClientError as e:
        # Log but don't fail — PDF may already be gone
        logger.warning(f"Failed to delete PDF from S3 ({s3_key}): {e}")


# ─── Pipeline ─────────────────────────────────────────────────────────────────


async def run_parsing_pipeline(session_id: str) -> str:
    """
    Run the full LLM parsing pipeline for a given session.

    Returns the created Policy UUID as a string.
    """
    from sqlalchemy import select

    async with async_session_maker() as db:
        # Step 0: Load ParsingSession to get S3 key and filename
        result = await db.execute(
            select(ParsingSession).where(ParsingSession.id == session_id)
        )
        parsing_session: ParsingSession | None = result.scalar_one_or_none()

    if not parsing_session:
        raise ValueError(f"ParsingSession {session_id} not found")

    if not parsing_session.s3_upload_key:
        raise ValueError(f"No s3_upload_key set for session {session_id}")

    s3_key = parsing_session.s3_upload_key
    filename = parsing_session.original_filename or "policy.pdf"

    logger.info(f"[Pipeline:{session_id}] Starting — file={filename}, s3_key={s3_key}")

    # Step 1: Fetch PDF from S3
    pdf_bytes = _fetch_pdf_from_s3(s3_key)
    parsing_session.file_size_bytes = len(pdf_bytes)
    logger.info(f"[Pipeline:{session_id}] Fetched PDF ({len(pdf_bytes):,} bytes)")

    # Step 2: Extract text (auto-detects born-digital vs scanned)
    extraction_result = extract_pdf_text(pdf_bytes)
    parsing_session.ocr_provider = extraction_result.provider
    logger.info(
        f"[Pipeline:{session_id}] Extracted text via {extraction_result.provider} "
        f"({extraction_result.page_count} pages, "
        f"born_digital={extraction_result.is_born_digital})"
    )

    # Step 3: Chunk into semantic sections
    chunks = chunk_by_sections(extraction_result.page_texts)
    chunk_summary = chunks.get_chunk_summary()
    logger.info(
        f"[Pipeline:{session_id}] Chunked into {len(chunks.raw)} sections: "
        f"{[c.section_type for c in chunks.raw]}"
    )

    # Step 4: Call Claude LLM to extract structured data
    llm_client = get_llm_client()
    policy_text = extraction_result.text

    extraction = llm_client.extract_from_text(
        policy_text=policy_text,
        filename=filename,
        section_chunks=chunk_summary,
    )

    parsing_session.claude_model = extraction.model
    parsing_session.tokens_used = extraction.input_tokens + extraction.output_tokens
    # $3/input-token + $15/output-token for Opus
    parsing_session.parse_cost_cents = int(
        (extraction.input_tokens * 3 + extraction.output_tokens * 15) / 1_000_000 * 100
    )

    logger.info(
        f"[Pipeline:{session_id}] LLM extraction done — "
        f"confidence={extraction.confidence:.2f}, tokens={extraction.input_tokens + extraction.output_tokens:,}"
    )

    # Attach token info to raw_json for db_writer to use
    extraction.raw_json["input_tokens"] = extraction.input_tokens
    extraction.raw_json["output_tokens"] = extraction.output_tokens
    extraction.raw_json["model_used"] = extraction.model

    # Step 5: Validate and normalise
    parsed = parse_and_validate(extraction.raw_json)
    logger.info(
        f"[Pipeline:{session_id}] Validation done — "
        f"insurer={parsed.insurer_code}, type={parsed.product_type}, "
        f"sum_assured={parsed.sum_assured_cents:,} cents"
    )

    # Step 6: Write to DB (handles its own session internally)
    policy = await write_parsed_policy(parsed, session_id)

    # Step 7: Delete PDF from S3 (PDPA — raw PDFs deleted after parsing)
    _delete_pdf_from_s3(s3_key)

    # Step 8: Update session status
    async with async_session_maker() as db:
        result = await db.execute(
            select(ParsingSession).where(ParsingSession.id == session_id)
        )
        session_obj: ParsingSession | None = result.scalar_one_or_none()
        if session_obj:
            session_obj.parse_status = "completed"
            session_obj.completed_at = datetime.utcnow()
            await db.commit()

    logger.info(f"[Pipeline:{session_id}] Completed — Policy {policy.id} created")

    return str(policy.id)
