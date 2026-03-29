"""
Gap detection — identifies coverage types a user has no active policy for.

Singapore insurance best-practice coverage types (in priority order):
1. DEATH — base family protection
2. TPD — disability/accident replacement
3. CI — critical illness (lump-sum for treatment/recovery)
4. HOSPITALISATION — medical bills (layered with MediShield Life / IP)
5. DISABILITY — income replacement on disability
6. ACCIDENT — accident-specific coverage
"""

import uuid
from typing import Any

from app.data.coverage_taxonomy import COVERAGE_TYPES
from app.services.analysis._fetch import get_user_policies_with_relations

# Coverage types in priority order (core first)
_CORE_COVERAGE_ORDER = [
    "DEATH",
    "TPD",
    "CI",
    "HOSPITALISATION",
    "DISABILITY",
    "ACCIDENT",
    "MEDISHIELD_LIFE",
    "IP",
    "ENDOWMENT",
]


def _map_product_type_to_coverage(product_type: str) -> str | None:
    """Map parsed product_type to canonical coverage type."""
    mapping = {
        "TERM_LIFE": "DEATH",
        "WHOLE_LIFE": "DEATH",
        "CRITICAL_ILLNESS": "CI",
        "HOSPITALISATION": "HOSPITALISATION",
        "MEDISHIELD_LIFE": "MEDISHIELD_LIFE",
        "IP": "IP",
        "DISABILITY": "DISABILITY",
        "ACCIDENT": "ACCIDENT",
        "ENDOWMENT": "ENDOWMENT",
    }
    return mapping.get(product_type.upper())


def _map_benefit_type_to_coverage(benefit_type: str) -> str | None:
    """Map parsed benefit_type to canonical coverage type."""
    mapping = {
        "death_or_tpd": "DEATH",
        "critical_illness": "CI",
        "hospitalization": "HOSPITALISATION",
        "accident_benefit": "ACCIDENT",
        "income_protection": "DISABILITY",
        "premium_waiver": None,  # Not a coverage gap type
        "other": None,
    }
    return mapping.get(benefit_type.lower())


def _assess_gap_severity(
    coverage_type: str,
    has_sum_assured: bool,
    has_policy: bool,
) -> str:
    """Return 'critical', 'warning', or 'info' based on gap severity."""
    if not has_policy:
        if coverage_type in ("DEATH", "TPD", "CI"):
            return "critical"
        return "warning"
    if not has_sum_assured:
        return "warning"
    return "info"


def _get_recommendation(coverage_type: str, coverage_info: dict) -> str:
    """Return a plain-English recommendation for a missing coverage type."""
    recommendations = {
        "DEATH": "Consider a term life or whole life policy to protect your family's financial future. A common guideline is 10-12× your annual income.",
        "TPD": "Total and Permanent Disability coverage pays out if you can no longer work. Many policies bundle this with death benefit.",
        "CI": "Critical illness coverage provides a lump sum upon diagnosis of a covered condition. LIA Singapore defines 37 standardized CI conditions.",
        "HOSPITALISATION": "Consider hospitalisation insurance to cover medical bills. In Singapore, this layers with MediShield Life (CPF-funded) and optionally an Integrated Shield Plan (IP).",
        "MEDISHIELD_LIFE": "MediShield Life is CPF-funded base medical insurance for all Singaporeans/PRs. Check if you're adequately covered for B2/C ward stays.",
        "IP": "An Integrated Shield Plan (IP) provides private ward coverage on top of MediShield Life. Consider based on your ward preferences (A/B1 vs private).",
        "DISABILITY": "Disability income insurance replaces a portion of your monthly income if you become disabled. Industry standard is 75% of monthly income.",
        "ACCIDENT": "Personal accident coverage pays out for accident-related injuries. Consider if your commute or occupation carries elevated risk.",
        "ENDOWMENT": "Endowment policies provide savings + insurance. Review whether the returns justify the cost vs term life + investment alternatives.",
    }
    return recommendations.get(
        coverage_type,
        f"Review your coverage for {coverage_type} to ensure adequate protection.",
    )


async def detect_gaps(
    user_id: uuid.UUID,
    policy_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Detect coverage gaps across a user's active policies.

    Returns a list of gap records sorted by severity (critical → warning → info).
    Each record has: coverage_type, severity, recommendation, covered_by_policy_ids.
    """
    policies = await get_user_policies_with_relations(user_id, policy_ids)

    # Build set of coverage already provided
    covered: dict[str, dict[str, Any]] = {}  # coverage_type -> {has_sum_assured, policy_ids}

    for policy in policies:
        coverage = _map_product_type_to_coverage(policy.product_type)
        if coverage:
            if coverage not in covered:
                covered[coverage] = {"has_sum_assured": False, "policy_ids": []}
            if policy.sum_assured_cents and policy.sum_assured_cents > 0:
                covered[coverage]["has_sum_assured"] = True
            covered[coverage]["policy_ids"].append(str(policy.id))

        # Also check benefit-level coverage
        for benefit in policy.benefits:
            benefit_coverage = _map_benefit_type_to_coverage(benefit.benefit_type)
            if benefit_coverage and benefit_coverage not in covered:
                covered[benefit_coverage] = {
                    "has_sum_assured": bool(benefit.amount_cents and benefit.amount_cents > 0),
                    "policy_ids": [str(policy.id)],
                }

    gaps: list[dict[str, Any]] = []

    for coverage_type in _CORE_COVERAGE_ORDER:
        info = COVERAGE_TYPES.get(coverage_type, {})
        is_covered = coverage_type in covered
        has_sum = covered.get(coverage_type, {}).get("has_sum_assured", False) if is_covered else False

        # MediShield Life is special — every Singapore citizen/PR has basic coverage
        # IP requires MediShield Life as prerequisite
        if coverage_type == "MEDISHIELD_LIFE":
            # We can't easily check CPF membership here; flag as info only
            severity = "info"
            gaps.append({
                "coverage_type": coverage_type,
                "severity": severity,
                "description": info.get("description"),
                "recommendation": "Ensure you are covered under MediShield Life via CPF. Singapore Citizens and PRs are automatically covered.",
                "covered_by_policy_ids": [],
                "gap_amount_cents": None,
            })
            continue

        # If not covered at all
        if not is_covered:
            severity = _assess_gap_severity(coverage_type, False, False)
            gaps.append({
                "coverage_type": coverage_type,
                "severity": severity,
                "description": info.get("description"),
                "recommendation": _get_recommendation(coverage_type, info),
                "covered_by_policy_ids": [],
                "gap_amount_cents": None,
            })
            continue

        # Covered but without a sum assured (zero-dollar benefit)
        if not has_sum:
            severity = _assess_gap_severity(coverage_type, False, True)
            gaps.append({
                "coverage_type": coverage_type,
                "severity": severity,
                "description": info.get("description"),
                "recommendation": f"You have {coverage_type} coverage but the benefit amount was not parsed or is zero. Review the policy schedule.",
                "covered_by_policy_ids": covered[coverage_type]["policy_ids"],
                "gap_amount_cents": None,
            })

    # Sort: critical first, then warning, then info
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    gaps.sort(key=lambda g: severity_order.get(g["severity"], 3))

    return gaps


def build_coverage_map(policies: list) -> dict:
    """
    Build a human-readable coverage map from a list of policy objects.
    Used for the plain-english portfolio summary.
    """
    coverage: dict[str, list[dict]] = {}

    for policy in policies:
        coverage_type = _map_product_type_to_coverage(policy.product_type) or policy.product_type
        if coverage_type not in coverage:
            coverage[coverage_type] = []
        coverage[coverage_type].append({
            "policy_id": str(policy.id),
            "product_name": policy.product_name,
            "insurer": policy.insurer_name,
            "sum_assured_cents": policy.sum_assured_cents,
            "policy_status": policy.policy_status,
            "benefit_count": len(policy.benefits),
        })

    return coverage


def calculate_benchmark(
    coverage_type: str,
    annual_income_cents: int | None,
) -> int | None:
    """
    Calculate the recommended coverage amount based on coverage type and income.

    Returns amount in cents, or None if no benchmark applies.
    """
    if annual_income_cents is None:
        return None

    benchmarks = {
        "DEATH": (10, 12),      # 10-12× annual income
        "TPD": (10, 12),
        "CI": (3, 5),           # 3-5× annual income minimum
        "DISABILITY": (0.75, 0.75),  # 75% of annual income (= 9× monthly)
    }

    if coverage_type not in benchmarks:
        return None

    low, high = benchmarks[coverage_type]
    return {
        "low": int(annual_income_cents * low),
        "high": int(annual_income_cents * high),
    }
