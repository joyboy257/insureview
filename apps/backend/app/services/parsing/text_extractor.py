"""
PDF text extraction with born-digital vs scanned detection.

Born-digital PDFs: pdfplumber text extraction (near 100% accuracy)
Scanned PDFs: Google Document AI OCR (85-93% accuracy) — falls back gracefully
"""

import io
import logging
from dataclasses import dataclass
from typing import Literal

import pdfplumber
from pdfplumber.exceptions import PdfminerError

logger = logging.getLogger(__name__)

# Minimum text length below which we suspect OCR is needed
_MIN_TEXT_LENGTH_THRESHOLD = 500


@dataclass
class TextExtractionResult:
    """Result of PDF text extraction."""

    text: str
    provider: Literal["pdfplumber", "docai"]
    page_count: int
    is_born_digital: bool
    page_texts: list[str]  # Per-page text for chunking
    docai_job_id: str | None = None


@dataclass
class BornDigitalResult:
    """Result of born-digital detection."""

    is_born_digital: bool
    confidence: float  # 0-1
    reason: str


def detect_born_digital(pdf_bytes: bytes) -> BornDigitalResult:
    """
    Detect whether a PDF is born-digital (machine-generated) or scanned.

    Born-digital signals:
    - Text layer present (pdfplumber extracts >500 chars/page on average)
    - Font embeddings present
    - No OCR'd image blocks

    Scanned signals:
    - Very little extractable text (<100 chars/page)
    - Text is garbled/positions are wrong
    - Only image content

    Returns (is_born_digital, confidence, reason).
    """
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            page_count = len(pdf.pages)
            if page_count == 0:
                return BornDigitalResult(
                    is_born_digital=False,
                    confidence=0.5,
                    reason="PDF has no pages",
                )

            texts: list[str] = []
            for page in pdf.pages[:3]:  # Sample first 3 pages
                t = page.extract_text() or ""
                texts.append(t)

            avg_chars = sum(len(t) for t in texts) / max(len(texts), 1)

            if avg_chars > 200:
                return BornDigitalResult(
                    is_born_digital=True,
                    confidence=0.9,
                    reason=f"Born-digital detected: {avg_chars:.0f} chars/page avg",
                )
            elif avg_chars > 50:
                return BornDigitalResult(
                    is_born_digital=True,
                    confidence=0.6,
                    reason=f"Possibly born-digital: {avg_chars:.0f} chars/page avg",
                )
            else:
                return BornDigitalResult(
                    is_born_digital=False,
                    confidence=0.85,
                    reason=f"Scanned document: only {avg_chars:.0f} chars/page avg",
                )

    except Exception as e:
        logger.warning(f"pdfplumber detection failed: {e}")
        return BornDigitalResult(
            is_born_digital=False,
            confidence=0.5,
            reason=f"Could not parse PDF structure: {e}",
        )


def extract_text_with_plumber(pdf_bytes: bytes) -> TextExtractionResult:
    """
    Extract text from a born-digital PDF using pdfplumber.

    Returns per-page text for accurate section chunking.
    """
    page_texts: list[str] = []
    full_text_parts: list[str] = []

    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            page_count = len(pdf.pages)

            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                page_texts.append(text)
                full_text_parts.append(f"[Page {i+1}]\n{text}")

        full_text = "\n\n".join(full_text_parts)

        logger.info(
            f"pdfplumber extraction: {page_count} pages, "
            f"{len(full_text)} total chars"
        )

        return TextExtractionResult(
            text=full_text,
            provider="pdfplumber",
            page_count=len(pdf.pages) if "pdf" in locals() else page_count,
            is_born_digital=True,
            page_texts=page_texts,
        )

    except PdfminerError as e:
        logger.error(f"pdfplumber failed: {e}")
        raise RuntimeError(f"Text extraction failed: {e}")


def extract_text_with_docai(
    pdf_bytes: bytes,
    project_id: str,
    location: str,
    processor_id: str,
    credentials_path: str | None = None,
) -> TextExtractionResult:
    """
    Extract text from a scanned PDF using Google Document AI OCR.

    Falls back gracefully if docai is not configured.
    """
    try:
        from google.cloud import documentai_v1 as docai
        from google.oauth2 import service_account
    except ImportError:
        raise RuntimeError(
            "google-cloud-documentai not installed. "
            "Run: pip install google-cloud-documentai"
        )

    if credentials_path:
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        client = docai.DocumentProcessorServiceClient(credentials=credentials)
    else:
        client = docai.DocumentProcessorServiceClient()

    document = {"content": pdf_bytes.decode("latin-1"), "mime_type": "application/pdf"}

    request = docai.ProcessDocumentRequest(
        name=f"projects/{project_id}/locations/{location}/processors/{processor_id}",
        raw_document=document,
    )

    response = client.process_document(request=request)
    doc = response.document

    full_text = doc.text
    # Document AI doesn't easily give per-page. Use page anchors if available.
    page_texts = [full_text]  # Simplified; can enhance with page_anchors

    logger.info(
        f"Document AI OCR: {len(full_text)} chars extracted"
    )

    return TextExtractionResult(
        text=full_text,
        provider="docai",
        page_count=1,
        is_born_digital=False,
        page_texts=page_texts,
        docai_job_id=None,
    )


def extract_pdf_text(pdf_bytes: bytes) -> TextExtractionResult:
    """
    Main entry point. Detects PDF type and routes to appropriate extractor.

    1. Try pdfplumber (born-digital, fast, accurate)
    2. If it looks scanned (<500 chars/page), try Document AI OCR
    3. If Document AI is not configured or fails, return what pdfplumber got
       with is_born_digital=False so downstream chunking knows to be more lenient
    """
    # Step 1: Born-digital detection
    detection = detect_born_digital(pdf_bytes)
    logger.info(f"PDF detection: {detection}")

    if not detection.is_born_digital:
        # Step 2: Try Document AI for scanned docs
        from app.core.config import settings

        if settings.google_docai_project_id and settings.google_docai_processor_id:
            try:
                return extract_text_with_docai(
                    pdf_bytes,
                    project_id=settings.google_docai_project_id,
                    location=settings.google_docai_location,
                    processor_id=settings.google_docai_processor_id,
                    credentials_path=settings.google_application_credentials,
                )
            except Exception as e:
                logger.warning(f"Document AI OCR failed, falling back: {e}")

        # Fallback: try pdfplumber anyway even for scanned docs
        try:
            result = extract_text_with_plumber(pdf_bytes)
            result.is_born_digital = False
            return result
        except Exception as e:
            logger.error(f"Even pdfplumber fallback failed: {e}")
            return TextExtractionResult(
                text="",
                provider="pdfplumber",
                page_count=0,
                is_born_digital=False,
                page_texts=[],
            )

    # Born-digital: use pdfplumber directly
    return extract_text_with_plumber(pdf_bytes)
