"""
Overlap detection — identifies coverage types where multiple active policies
provide the same protection, creating potential double-coverage.

Key Singapore-specific rules:
- MediShield Life + IP: intended to stack (IP pays excess over MediShield claim)
- Multiple DI policies: can stack (each pays its own % of income)
- Hospitalisation plans: CANNOT exceed 100% of actual costs across ALL plans
  (LIA/Hospitalisation benefit stacking rule)
- Death/TPD: CAN stack (multiple policies pay independently)
"""

import uuid
from typing import Any

from app.services.analysis._fetch import get_user_policies_with_relations


def _benefit_overlap_key(benefit_type: str, trigger_desc: str | None) -> str:
    """Normalise benefit type for overlap grouping."""
    return f"{benefit_type.lower()}::{trigger_desc or ''}"


async def detect_overlaps(
    user_id: uuid.UUID,
    policy_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Detect overlapping coverage across a user's active policies.

    Returns a list of overlap records, each describing:
    - coverage_type
    - severity (info, warning)
    - overlapping_policy_ids
    - total_sum_assured_cents
    - note (e.g. stacking rules)
    """
    policies = await get_user_policies_with_relations(user_id, policy_ids)

    if len(policies) < 2:
        return []

    # Group policies by coverage type
    by_coverage: dict[str, list[dict]] = {}

    for policy in policies:
        product_type = policy.product_type.upper()

        # Map to canonical coverage bucket
        coverage_bucket = _canonical_coverage(product_type)
        if not coverage_bucket:
            continue

        if coverage_bucket not in by_coverage:
            by_coverage[coverage_bucket] = []

        by_coverage[coverage_bucket].append({
            "policy_id": str(policy.id),
            "product_name": policy.product_name,
            "insurer": policy.insurer_name,
            "sum_assured_cents": policy.sum_assured_cents or 0,
            "benefit_count": len(policy.benefits),
        })

    overlaps: list[dict[str, Any]] = []

    for coverage_type, policy_list in by_coverage.items():
        if len(policy_list) < 2:
            continue

        total_sum = sum(p["sum_assured_cents"] for p in policy_list)

        # Special severity rules per coverage type
        if coverage_type in ("HOSPITALISATION",):
            severity = "warning"
            note = (
                "Hospitalisation plans cannot collectively exceed 100% of actual "
                "medical costs across all insurers (LIA stacking rule). "
                "Review whether you are over-insured on hospitalisation."
            )
        elif coverage_type == "MEDISHIELD_LIFE":
            # MediShield + IP is intentional stacking
            severity = "info"
            note = (
                "MediShield Life and Integrated Shield Plan (IP) are designed to stack. "
                "MediShield Life covers B2/C wards; IP covers the gap up to private ward/A class."
            )
        elif coverage_type == "IP":
            severity = "info"
            note = (
                "Multiple IP plans are uncommon. Verify each plan covers different ward types "
                "or providers before holding multiple IPs."
            )
        elif coverage_type in ("DEATH", "TPD"):
            severity = "info"
            note = (
                "Death and TPD benefits stack across multiple policies — each pays independently. "
                "This is often intentional for increasing coverage over time."
            )
        elif coverage_type == "CI":
            severity = "warning"
            note = (
                "Multiple CI policies stack. However, some insurers may reduce payouts "
                "if total CI coverage exceeds a threshold (check policy terms). "
                "Also note: CI policies pay once on diagnosis (not ongoing)."
            )
        elif coverage_type == "DISABILITY":
            severity = "info"
            note = (
                "Disability income policies typically stack — each pays a % of monthly income. "
                "Confirm no policy has an 'other insurance' offset clause."
            )
        else:
            severity = "info"
            note = "Multiple policies cover this risk. Verify stacking is intended."

        overlaps.append({
            "coverage_type": coverage_type,
            "severity": severity,
            "overlapping_policies": policy_list,
            "policy_count": len(policy_list),
            "total_sum_assured_cents": total_sum,
            "note": note,
        })

    # Sort by severity then policy count
    severity_order = {"warning": 0, "info": 1}
    overlaps.sort(key=lambda o: (severity_order.get(o["severity"], 2), -o["policy_count"]))

    return overlaps


def _canonical_coverage(product_type: str) -> str | None:
    """Map parsed product_type to canonical coverage bucket."""
    mapping = {
        "TERM_LIFE": "DEATH",
        "WHOLE_LIFE": "DEATH",
        "CRITICAL_ILLNESS": "CI",
        "HOSPITALISATION": "HOSPITALISATION",
        "MEDISHIELD_LIFE": "MEDISHIELD_LIFE",
        "IP": "IP",
        "DISABILITY": "DISABILITY",
        "ACCIDENT": "ACCIDENT",
        "ENDOWMENT": "SAVINGS",  # Endowment is primarily savings, not pure risk
    }
    return mapping.get(product_type.upper())
