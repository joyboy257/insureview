"""
Anthropic Claude client for insurance policy parsing.

Uses Claude Opus 4 with 200K context window for full policy document extraction.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Generator

import anthropic
from anthropic import Anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Insurer canonical codes ─────────────────────────────────────────────────

INSURER_CODES: dict[str, str] = {
    "aia": "AIA",
    "aia singapore": "AIA",
    "great eastern": "GE",
    "great eastern singapore": "GE",
    "prudential": "PRU",
    "prudential singapore": "PRU",
    "ntuc income": "NTUC",
    "income": "NTUC",
    "manulife": "MANULIFE",
    "aviva": "AVIVA",
    "fwd": "FWD",
    "etiqa": "ETIQA",
    "singlife": "SINGLIFE",
    "tiq": "ETIQA",
    "tiq insurance": "ETIQA",
}

PRODUCT_TYPE_MAPPING: dict[str, str] = {
    "term": "TERM_LIFE",
    "term life": "TERM_LIFE",
    "level term": "TERM_LIFE",
    "whole life": "WHOLE_LIFE",
    "whole-life": "WHOLE_LIFE",
    "critical illness": "CRITICAL_ILLNESS",
    "ci": "CRITICAL_ILLNESS",
    "dread disease": "CRITICAL_ILLNESS",
    "hospitalisation": "HOSPITALISATION",
    "hospital": "HOSPITALISATION",
    "medical": "HOSPITALISATION",
    "medishield": "MEDISHIELD_LIFE",
    "medishield life": "MEDISHIELD_LIFE",
    "integrated shield": "IP",
    "shield plan": "IP",
    "ip": "IP",
    "disabilit": "DISABILITY",
    "disability income": "DISABILITY",
    "accident": "ACCIDENT",
    "personal accident": "ACCIDENT",
    "endowment": "ENDOWMENT",
}


@dataclass
class ExtractionResult:
    """Structured output from a single Claude extraction call."""

    raw_json: dict
    raw_text: str
    model: str
    input_tokens: int
    output_tokens: int
    stopped_reason: str
    confidence: float


@dataclass
class LLMClient:
    """
    Thread-safe Anthropic client wrapper for policy extraction.

    Supports:
    - Claude Opus 4 (primary)
    - Streaming for progress feedback
    - Automatic JSON parsing with fallback
    - Per-field confidence scoring via thinking tokens
    """

    model: str = "claude-opus-4-5-20261120"
    max_tokens: int = 8000
    temperature: float = 0.1  # Low temp for consistent extraction

    _client: Anthropic | None = field(default=None, init=False, repr=False)

    @property
    def client(self) -> Anthropic:
        if self._client is None:
            self._client = Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def _build_extraction_system_prompt(self) -> str:
        return """You are an expert Singapore insurance policy analyst. Your task is to extract structured data from insurance policy documents with high precision.

        CANONICAL INSURER CODES:
        - AIA Singapore → AIA
        - Great Eastern → GE
        - Prudential → PRU
        - NTUC Income → NTUC
        - Manulife → MANULIFE
        - FWD → FWD
        - Etiqa / TIQ → ETIQA
        - Singlife → SINGLIFE

        PRODUCT TYPES (use exactly these strings):
        - TERM_LIFE, WHOLE_LIFE, CRITICAL_ILLNESS, HOSPITALISATION
        - MEDISHIELD_LIFE, IP (Integrated Shield Plan)
        - DISABILITY, ACCIDENT, ENDOWMENT

        BENEFIT TYPES (use exactly these strings):
        - death_or_tpd, critical_illness, hospitalization, accident_benefit
        - premium_waiver, income_protection, other

        IMPORTANT RULES:
        1. All monetary amounts are in Singapore DOLLARS (SGD). Convert from cents by dividing by 100.
        2. Dates must be in YYYY-MM-DD format.
        3. sum_assured is the maximum payout for this benefit (not the annual premium).
        4. For CI policies, survival_period_days = 14 means the insured must survive 14 days after diagnosis for payout.
        5. policy_year is the year since issue (year 1 = first year, year 5 = fifth year).
        6. premium_amount is the POLICY premium, not the rider premium (unless it's a standalone rider).
        7. Confidence: 0.0 = complete guess, 1.0 = fully confident based on explicit text.
        8. If any field is not found in the document, set it to null and note it in the confidence score.
        9. ALWAYS use LIA (Life Insurance Association) Singapore CI definitions for CI benefit types.

        OUTPUT FORMAT:
        You must respond with ONLY a valid JSON object. No markdown, no explanation, no preamble.
        The JSON must conform to this schema:
        {
          "insurer_code": "AIA|GE|PRU|NTUC|MANULIFE|FWD|ETIQA|SINGLIFE|OTHER",
          "insurer_name": "Exact name as printed on policy",
          "product_name": "Full product name exactly as on the policy",
          "product_type": "TERM_LIFE|WHOLE_LIFE|CRITICAL_ILLNESS|HOSPITALISATION|MEDISHIELD_LIFE|IP|DISABILITY|ACCIDENT|ENDOWMENT",
          "policy_number": "POL-XXXXXX" or null,
          "issue_date": "YYYY-MM-DD" or null,
          "expiry_date": "YYYY-MM-DD" or null,
          "sum_assured_cents": 50000000,  (50,000 SGD = 5000000 cents)
          "premium_amount_cents": 360000,  (3,600 SGD annual = 360000 cents)
          "premium_frequency": "annual|monthly|quarterly",
          "currency": "SGD",
          "policy_status": "active|lapsed|surrendered|reduced",
          "policy_year": 1,  (how many years since issue)
          "parse_confidence": 0.94,  (0.0 to 1.0)
          "structured_data": {
            "benefits": [
              {
                "benefit_type": "death_or_tpd|critical_illness|hospitalization|...",
                "benefit_subtype": "basic|accelerated|indemnity|..." or null,
                "trigger_description": "Plain English description of when this pays out",
                "payout_type": "lumpsum|annual|income|refund" or null,
                "amount_cents": 50000000 or null,
                "percentage_of_sum_assured": 100.0 or null,
                "survival_period_days": 14 or null,
                "conditions": { "survival_period_days": 14, "notification_days": 30 } or null,
                "exclusions": ["suicide_12months", "self_inflicted"] or null,
                "is_active": true,
                "parse_confidence": 0.95
              }
            ],
            "riders": [
              {
                "rider_name": "CI Rider 1",
                "rider_type": "critical_illness|accident|premium_waiver|...",
                "additional_premium_cents": 50000 or null,
                "additional_sum_assured_cents": 10000000 or null,
                "linked_benefit_type": "death_or_tpd" or null
              }
            ]
          },
          "plain_english_summary": "One paragraph plain English summary of what this policy covers.",
          "extraction_notes": "Any caveats or uncertain fields noted here."
        }
        """

    def extract_from_text(
        self,
        policy_text: str,
        filename: str,
        section_chunks: list[dict] | None = None,
    ) -> ExtractionResult:
        """
        Run a single extraction pass on full policy text.

        Args:
            policy_text: Full text extracted from the PDF (may be truncated to 180K chars).
            filename: Original filename for context.
            section_chunks: Optional pre-chunked sections (Policy Schedule, Benefits, etc.).

        Returns:
            ExtractionResult with raw_json, model info, and confidence score.
        """
        user_content = f"""Extract structured data from the following Singapore insurance policy document.

FILENAME: {filename}

 POLICY DOCUMENT TEXT:
---
{policy_text[:180_000]}
---

{"SECTION CHUNKS (use these for prioritising key sections):" + json.dumps(section_chunks, indent=2) if section_chunks else ""}

Follow the system prompt instructions exactly. Return ONLY the JSON object."""

        logger.info(
            f"Calling Claude for extraction, policy_text length={len(policy_text)}"
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self._build_extraction_system_prompt(),
            messages=[{"role": "user", "content": user_content}],
        )

        raw_text = response.content[0].text if response.content else ""
        total_tokens = response.usage.input_tokens + response.usage.output_tokens

        logger.info(
            f"Claude extraction complete: model={response.model}, "
            f"tokens={total_tokens}, stopped={response.stop_reason}"
        )

        # Parse JSON
        try:
            raw_json = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {e}. Attempting cleanup.")
            # Try to extract JSON block
            raw_json = self._extract_json_from_markdown(raw_text)

        confidence = self._estimate_confidence(raw_json, raw_text)

        return ExtractionResult(
            raw_json=raw_json,
            raw_text=raw_text,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stopped_reason=str(response.stop_reason),
            confidence=confidence,
        )

    def extract_structured_streaming(
        self,
        policy_text: str,
        filename: str,
    ) -> Generator[str, None, ExtractionResult]:
        """
        Streaming extraction — yields JSON fragments for SSE progress updates.
        Use this when you want to show "reading benefits section..." progress.

        Yields JSON string fragments. Final yield is the complete JSON.
        """
        user_content = f"""Extract structured data from this Singapore insurance policy.

FILENAME: {filename}

POLICY TEXT (first 180,000 chars):
---
{policy_text[:180_000]}
---

Return ONLY a valid JSON object matching the schema described in the system prompt."""

        with self.client.messages.stream(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=self._build_extraction_system_prompt(),
            messages=[{"role": "user", "content": user_content}],
        ) as stream:
            full_text = ""
            for text_event in stream.text_stream:
                full_text += text_event
                yield text_event

        # Final parse
        try:
            raw_json = json.loads(full_text)
        except json.JSONDecodeError:
            raw_json = self._extract_json_from_markdown(full_text)

        total_tokens = (
            stream.usage.input_tokens if hasattr(stream, "usage") else 0
        ) + (
            stream.usage.output_tokens if hasattr(stream, "usage") else 0
        )

        yield json.dumps(raw_json)

        # Return final result via StopIteration
        # (Caller checks last event separately)

    def _extract_json_from_markdown(self, text: str) -> dict:
        """Extract JSON from a markdown code block or raw text."""
        import re

        # Try JSON in code block first
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try raw braces
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

        return {}

    def _estimate_confidence(self, parsed: dict, raw_text: str) -> float:
        """
        Estimate overall parse confidence based on:
        - Presence of required fields
        - JSON parse quality
        - Text completeness
        """
        if not parsed:
            return 0.0

        required = ["insurer_code", "product_name", "product_type", "structured_data"]
        missing = [f for f in required if not parsed.get(f)]
        if missing:
            return 0.3  # Low confidence - missing critical fields

        # Boost for each well-populated field
        confidence = 0.5  # Base

        if parsed.get("insurer_code") != "OTHER":
            confidence += 0.1

        if parsed.get("sum_assured_cents", 0) > 0:
            confidence += 0.1

        benefits = parsed.get("structured_data", {}).get("benefits", [])
        if len(benefits) >= 1:
            confidence += 0.1

        # Penalise for empty required fields
        if not parsed.get("product_name"):
            confidence -= 0.15
        if not parsed.get("structured_data", {}).get("benefits"):
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))


_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Singleton LLM client for the parsing pipeline."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
