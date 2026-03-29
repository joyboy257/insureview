"""
Output parser and validation for LLM extraction results.

Validates the raw Claude JSON output against the policy schema,
normalises field values, and writes structured data to the DB.
"""

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any

from jsonschema import Draft7Validator, ValidationError

from app.services.llm.client import INSURER_CODES, PRODUCT_TYPE_MAPPING

logger = logging.getLogger(__name__)

# Load canonical schema
_SCHEMA_PATH = "/Users/deon/intent-economy/packages/shared/types/policy-schema.json"


def _load_schema() -> dict:
    try:
        with open(_SCHEMA_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Schema not found at {_SCHEMA_PATH}, using embedded schema")
        return _EMBEDDED_SCHEMA


_EMBEDDED_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["insurer_code", "insurer_name", "product_name", "product_type", "structured_data"],
    "properties": {
        "insurer_code": {"type": "string"},
        "insurer_name": {"type": "string"},
        "product_name": {"type": "string"},
        "product_type": {"type": "string"},
        "policy_number": {"type": ["string", "null"]},
        "issue_date": {"type": ["string", "null"]},
        "expiry_date": {"type": ["string", "null"]},
        "sum_assured_cents": {"type": "integer", "minimum": 0},
        "premium_amount_cents": {"type": ["integer", "null"]},
        "premium_frequency": {"type": "string"},
        "currency": {"type": "string"},
        "policy_status": {"type": "string"},
        "policy_year": {"type": ["integer", "null"]},
        "parse_confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "structured_data": {"type": "object"},
        "plain_english_summary": {"type": ["string", "null"]},
    },
}


@dataclass
class ParseFailure:
    """Records a field-level parse failure for QA."""

    path: str  # JSON path e.g. "structured_data.benefits[0].amount_cents"
    expected: str
    received: Any
    fix_applied: str | None = None  # What we did to fix it


@dataclass
class ParsedPolicy:
    """Validated, normalised policy ready for DB insertion."""

    insurer_code: str
    insurer_name: str
    product_name: str
    product_type: str
    policy_number: str | None
    issue_date: date | None
    expiry_date: date | None
    sum_assured_cents: int
    premium_amount_cents: int | None
    premium_frequency: str
    currency: str
    policy_status: str
    policy_year: int | None
    parse_confidence: float
    structured_data: dict
    plain_english_summary: str | None
    extraction_notes: str | None

    raw_json: dict  # Original LLM output for audit

    @property
    def benefits(self) -> list[dict]:
        return self.structured_data.get("benefits", [])

    @property
    def riders(self) -> list[dict]:
        return self.structured_data.get("riders", [])


def parse_and_validate(raw_json: dict, schema_override: dict | None = None) -> ParsedPolicy:
    """
    Parse and validate a raw LLM extraction result.

    Steps:
    1. Validate against JSON schema
    2. Normalise field values (insurer codes, product types, dates, monetary)
    3. Apply fixups for common Claude hallucinations
    4. Return a clean ParsedPolicy

    Raises:
        ValueError if required fields are missing after normalisation
    """
    schema = schema_override or _load_schema()
    validator = Draft7Validator(schema)

    # Step 1: Schema validation
    errors = list(validator.iter_errors(raw_json))
    if errors:
        logger.warning(f"Schema validation had {len(errors)} errors")
        for err in errors[:3]:
            logger.warning(f"  {err.message} at {'.'.join(str(p) for p in err.path)}")

    # Step 2: Normalise insurer_code
    raw_insurer = raw_json.get("insurer_code", "")
    if raw_insurer in ("OTHER", "null", None, ""):
        # Try to infer from insurer_name
        inferred = _infer_insurer_code(raw_json.get("insurer_name", ""))
        raw_json["insurer_code"] = inferred

    # Step 3: Normalise product_type
    raw_type = raw_json.get("product_type", "")
    if raw_type not in (
        "TERM_LIFE",
        "WHOLE_LIFE",
        "CRITICAL_ILLNESS",
        "HOSPITALISATION",
        "MEDISHIELD_LIFE",
        "IP",
        "DISABILITY",
        "ACCIDENT",
        "ENDOWMENT",
    ):
        inferred_type = PRODUCT_TYPE_MAPPING.get(raw_type.lower(), "OTHER")
        raw_json["product_type"] = inferred_type
        logger.info(f"Normalised product_type: {raw_type!r} → {inferred_type}")

    # Step 4: Normalise monetary fields (Claude may return dollars not cents)
    for field in ("sum_assured_cents", "premium_amount_cents"):
        val = raw_json.get(field)
        if val is not None and isinstance(val, (int, float)):
            # If > 1_000_000 and product_type is not WHOLE_LIFE, might be dollars
            if val > 1_000_000 and field == "sum_assured_cents":
                # Likely returned as dollars (e.g. 500000 for 500k SGD)
                # But cents would be 50_000_000. Check magnitude.
                # SGD amounts rarely exceed 10M in dollars
                if val < 100_000_000:  # Less than 100M dollars = less than 10B SGD (unlikely)
                    raw_json[field] = int(val * 100)
                    logger.info(f"Converted {field} from dollars to cents: {val} → {raw_json[field]}")

    # Step 5: Normalise dates
    for date_field in ("issue_date", "expiry_date"):
        val = raw_json.get(date_field)
        if val and isinstance(val, str) and len(val) == 10:
            try:
                date.fromisoformat(val.replace("/", "-"))
            except ValueError:
                raw_json[date_field] = None

    # Step 6: Normalise policy_status
    status = raw_json.get("policy_status", "active").lower()
    status_map = {
        "in force": "active",
        "in-force": "active",
        "active": "active",
        "inactive": "lapsed",
        "lapsed": "lapsed",
        "suspended": "lapsed",
        "surrendered": "surrendered",
        "reduced": "reduced",
        "paid-up": "reduced",
        "matured": "surrendered",
    }
    raw_json["policy_status"] = status_map.get(status, "active")

    # Step 7: Normalise premium_frequency
    freq = raw_json.get("premium_frequency", "annual").lower()
    freq_map = {"yearly": "annual", "monthly": "monthly", "quarterly": "quarterly"}
    raw_json["premium_frequency"] = freq_map.get(freq, "annual")

    # Step 8: Set currency to SGD if not specified
    if not raw_json.get("currency"):
        raw_json["currency"] = "SGD"

    # Step 9: Ensure structured_data has required keys
    sd = raw_json.get("structured_data", {})
    if "benefits" not in sd:
        sd["benefits"] = []
    if "riders" not in sd:
        sd["riders"] = []
    raw_json["structured_data"] = sd

    # Step 10: Validate required fields after normalisation
    required = ["insurer_code", "insurer_name", "product_name", "product_type", "structured_data"]
    missing = [f for f in required if not raw_json.get(f)]
    if missing:
        raise ValueError(f"Missing required fields after normalisation: {missing}")

    return ParsedPolicy(
        insurer_code=raw_json["insurer_code"],
        insurer_name=raw_json.get("insurer_name") or "Unknown Insurer",
        product_name=raw_json.get("product_name") or "Unknown Product",
        product_type=raw_json["product_type"],
        policy_number=raw_json.get("policy_number"),
        issue_date=_parse_date(raw_json.get("issue_date")),
        expiry_date=_parse_date(raw_json.get("expiry_date")),
        sum_assured_cents=int(raw_json.get("sum_assured_cents") or 0),
        premium_amount_cents=int(raw_json["premium_amount_cents"]) if raw_json.get("premium_amount_cents") else None,
        premium_frequency=raw_json.get("premium_frequency", "annual"),
        currency=raw_json.get("currency", "SGD"),
        policy_status=raw_json.get("policy_status", "active"),
        policy_year=raw_json.get("policy_year"),
        parse_confidence=float(raw_json.get("parse_confidence") or 0.5),
        structured_data=raw_json.get("structured_data", {}),
        plain_english_summary=raw_json.get("plain_english_summary"),
        extraction_notes=raw_json.get("extraction_notes"),
        raw_json=raw_json,  # Preserve for audit
    )


def _parse_date(val: str | None) -> date | None:
    if not val:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return date.fromisoformat(val.replace("/", "-").replace(" ", ""))
        except (ValueError, AttributeError):
            continue
    return None


def _infer_insurer_code(insurer_name: str) -> str:
    if not insurer_name:
        return "OTHER"
    name_lower = insurer_name.lower()
    for key, code in INSURER_CODES.items():
        if key in name_lower:
            return code
    return "OTHER"
