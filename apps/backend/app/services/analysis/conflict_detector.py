"""
Conflict detection — identifies contradictory terms between a user's policies.

A conflict exists when two or more policies cover the same risk but have
different terms that could lead to inconsistent outcomes.

Examples of conflicts:
- CI policies with different survival period requirements (e.g. 14 days vs 30 days)
- Multiple hospitalisation plans with conflicting ward-class coverage
- Policies with different definitions of TPD (own occupation vs any occupation)
- Conflicting cancellation/surrender values
"""

import uuid
from typing import Any

from app.services.analysis._fetch import get_user_policies_with_relations


async def detect_conflicts(
    user_id: uuid.UUID,
    policy_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Detect conflicting terms across a user's active policies.

    Returns a list of conflict records, each containing:
    - conflict_type
    - severity (warning, critical)
    - description (plain English)
    - affected_policies (list of {policy_id, product_name, detail})
    - resolution_hint
    """
    policies = await get_user_policies_with_relations(user_id, policy_ids)

    if len(policies) < 2:
        return []

    conflicts: list[dict[str, Any]] = []

    # ── 1. CI survival period conflicts ─────────────────────────────────────
    ci_conflicts = _detect_ci_survival_conflicts(policies)
    conflicts.extend(ci_conflicts)

    # ── 2. Hospitalisation ward-class conflicts ─────────────────────────────
    hosp_conflicts = _detect_hospitalisation_conflicts(policies)
    conflicts.extend(hosp_conflicts)

    # ── 3. TPD definition conflicts ─────────────────────────────────────────
    tpd_conflicts = _detect_tpd_definition_conflicts(policies)
    conflicts.extend(tpd_conflicts)

    # ── 4. Multiple active CI policies with different staging rules ──────────
    ci_staging_conflicts = _detect_ci_staging_conflicts(policies)
    conflicts.extend(ci_staging_conflicts)

    # ── 5. Policy year conflicts — policies at same age with different status
    maturity_conflicts = _detect_maturity_conflicts(policies)
    conflicts.extend(maturity_conflicts)

    # Sort by severity (critical first)
    severity_order = {"critical": 0, "warning": 1}
    conflicts.sort(key=lambda c: severity_order.get(c["severity"], 2))

    return conflicts


# ─── Individual conflict detectors ───────────────────────────────────────────


def _detect_ci_survival_conflicts(policies: list) -> list[dict[str, Any]]:
    """Detect CI policies with different survival period requirements."""
    ci_policies = [
        {
            "policy_id": str(p.id),
            "product_name": p.product_name,
            "insurer": p.insurer_name,
            "survival_days": _extract_ci_survival_days(p.structured_data),
        }
        for p in policies
        if p.product_type.upper() in ("CRITICAL_ILLNESS",)
        or any(
            b.benefit_type.lower() == "critical_illness"
            for b in p.benefits
        )
    ]

    if len(ci_policies) < 2:
        return []

    survival_groups: dict[int | None, list[dict]] = {}
    for ci in ci_policies:
        days = ci["survival_days"]
        survival_groups.setdefault(days, []).append(ci)

    if len(survival_groups) < 2:
        return []

    groups = list(survival_groups.items())
    conflicts = []
    for days_a, group_a in groups:
        for days_b, group_b in groups:
            if days_a is not None and days_b is not None and days_a < days_b:
                conflicts.append({
                    "conflict_type": "ci_survival_period",
                    "severity": "warning",
                    "description": (
                        f"CI policies have conflicting survival period requirements: "
                        f"one requires surviving {days_a} days after diagnosis, "
                        f"another requires {days_b} days. "
                        f"This affects when the CI payout is triggered."
                    ),
                    "affected_policies": group_a + group_b,
                    "detail": {
                        "group_a_days": days_a,
                        "group_b_days": days_b,
                    },
                    "resolution_hint": (
                        f"Review whether the shorter survival period policy provides "
                        f"more favorable terms. LIA Singapore standard for early CI "
                        f"is typically 14 days survival. "
                        f"If both policies pay on diagnosis (no survival requirement), "
                        f"there is no conflict."
                    ),
                })

    return [conflicts[0]] if conflicts else []


def _extract_ci_survival_days(structured_data: dict) -> int | None:
    """Extract survival period in days from structured_data benefits."""
    benefits = structured_data.get("benefits", [])
    for b in benefits:
        if b.get("benefit_type", "").lower() == "critical_illness":
            conditions = b.get("conditions") or {}
            if isinstance(conditions, dict):
                return conditions.get("survival_period_days")
    return None


def _detect_hospitalisation_conflicts(policies: list) -> list[dict[str, Any]]:
    """Detect conflicting ward-class coverage across hospitalisation plans."""
    hosp_policies = []

    for p in policies:
        if p.product_type.upper() not in ("HOSPITALISATION", "MEDISHIELD_LIFE", "IP"):
            continue

        sd = p.structured_data or {}
        ward_options = _extract_ward_options(sd)
        policy_info = {
            "policy_id": str(p.id),
            "product_name": p.product_name,
            "insurer": p.insurer_name,
            "ward_options": ward_options,
            "product_type": p.product_type,
        }
        hosp_policies.append(policy_info)

    if len(hosp_policies) < 2:
        return []

    # Check if multiple IPs exist (unusual)
    ip_policies = [h for h in hosp_policies if h["product_type"] == "IP"]
    if len(ip_policies) > 1:
        insurers = [h["insurer"] for h in ip_policies]
        product_names = [h["product_name"] for h in ip_policies]
        return [{
            "conflict_type": "multiple_ip",
            "severity": "warning",
            "description": (
                f"You have {len(ip_policies)} Integrated Shield Plans (IPs) from "
                f"{', '.join(set(insurers))}. "
                f"Holding multiple IPs is unusual and may indicate overlap."
            ),
            "affected_policies": ip_policies,
            "detail": {"product_names": product_names},
            "resolution_hint": (
                "Integrated Shield Plans are typically one-per-person. "
                "Review whether both plans provide meaningful differentiation in ward/ward-class coverage. "
                "Consider surrendering one IP if coverage overlaps."
            ),
        }]

    return []


def _extract_ward_options(structured_data: dict) -> list[str]:
    """Extract ward-class options from structured_data."""
    sd = structured_data or {}
    benefits = sd.get("benefits", [])
    options = []
    for b in benefits:
        benefit_type = b.get("benefit_type", "").lower()
        if "hospitalization" in benefit_type or "medical" in benefit_type:
            conditions = b.get("conditions") or {}
            if isinstance(conditions, dict):
                ward = conditions.get("ward_class") or conditions.get("ward_type")
                if ward:
                    options.append(str(ward))
    return options


def _detect_tpd_definition_conflicts(policies: list) -> list[dict[str, Any]]:
    """Detect TPD policies with different occupation definitions."""
    tpd_policies = [
        {
            "policy_id": str(p.id),
            "product_name": p.product_name,
            "insurer": p.insurer_name,
            "tpd_definition": _extract_tpd_definition(p.structured_data),
        }
        for p in policies
        if p.product_type.upper() in ("TERM_LIFE", "WHOLE_LIFE")
        or any(b.benefit_type.lower() in ("death_or_tpd", "tpd") for b in p.benefits)
    ]

    if len(tpd_policies) < 2:
        return []

    def_groups: dict[str | None, list[dict]] = {}
    for t in tpd_policies:
        def_groups.setdefault(t["tpd_definition"], []).append(t)

    if len(def_groups) < 2:
        return []

    conflicts = []
    definitions = list(def_groups.keys())
    for i, def_a in enumerate(definitions):
        for def_b in definitions[i + 1:]:
            if def_a and def_b:
                conflicts.append({
                    "conflict_type": "tpd_definition",
                    "severity": "warning",
                    "description": (
                        f"TPD policies use different disability definitions: "
                        f"'{def_a}' vs '{def_b}'. "
                        f"'Own occupation' is generally more favorable than 'any occupation'."
                    ),
                    "affected_policies": def_groups[def_a] + def_groups[def_b],
                    "detail": {
                        "definition_a": def_a,
                        "definition_b": def_b,
                    },
                    "resolution_hint": (
                        "TPD definitions ranked by favorability (most → least): "
                        "own occupation > any occupation > Activities of Daily Living (ADL). "
                        "Review the policy contracts for exact definitions. "
                        "An 'own occupation' definition pays out if you can't perform your own job. "
                        "An 'any occupation' definition is harder to claim under."
                    ),
                })

    return [conflicts[0]] if conflicts else []


def _extract_tpd_definition(structured_data: dict) -> str | None:
    """Extract TPD occupation definition from structured_data."""
    sd = structured_data or {}
    benefits = sd.get("benefits", [])
    for b in benefits:
        if b.get("benefit_type", "").lower() in ("death_or_tpd", "tpd"):
            conditions = b.get("conditions") or {}
            if isinstance(conditions, dict):
                return conditions.get("tpd_definition")
    return None


def _detect_ci_staging_conflicts(policies: list) -> list[dict[str, Any]]:
    """Detect if some CI policies pay on early-stage diagnosis and some only on late-stage."""
    ci_policies = []

    for p in policies:
        if p.product_type.upper() != "CRITICAL_ILLNESS":
            continue
        sd = p.structured_data or {}
        for b in sd.get("benefits", []):
            if b.get("benefit_type", "").lower() == "critical_illness":
                ci_policies.append({
                    "policy_id": str(p.id),
                    "product_name": p.product_name,
                    "insurer": p.insurer_name,
                    "staging_required": b.get("conditions", {}).get("staging_required")
                    if isinstance(b.get("conditions"), dict)
                    else None,
                })

    if len(ci_policies) < 2:
        return []

    staging_groups: dict[bool | None, list[dict]] = {}
    for ci in ci_policies:
        staging_groups.setdefault(ci["staging_required"], []).append(ci)

    if len(staging_groups) < 2:
        return []

    return [{
        "conflict_type": "ci_staging",
        "severity": "warning",
        "description": (
            "CI policies have different staging requirements: "
            "some pay on early-stage diagnosis (e.g. Stage 1 cancer), "
            "others only pay on late-stage/advanced disease. "
            "LIA Singapore defines early-stage CI for 37 conditions — "
            "but not all policies include early CI payout."
        ),
        "affected_policies": [
            ci for group in staging_groups.values() for ci in group
        ],
        "detail": {
            "staging_required_groups": {
                str(k): [c["product_name"] for c in v]
                for k, v in staging_groups.items()
            }
        },
        "resolution_hint": (
            "Check each CI policy's product summary for 'early CI' or 'stage 1' payout. "
            "Some policies pay a reduced % (e.g. 50%) for early-stage diagnosis. "
            "LIA standardized early CI definitions include Stage 1 cancer, "
            "early-stage heart attack (Class 1), and early-stage stroke."
        ),
    }]


def _detect_maturity_conflicts(policies: list) -> list[dict[str, Any]]:
    """
    Detect endowment/whole life policies that have reached different maturity
    statuses at similar policy years — indicating conflicting surrender values.
    """
    matured = []
    active = []

    for p in policies:
        if p.product_type.upper() not in ("ENDOWMENT", "WHOLE_LIFE"):
            continue
        if p.policy_status == "surrendered":
            matured.append({
                "policy_id": str(p.id),
                "product_name": p.product_name,
                "insurer": p.insurer_name,
                "status": "surrendered",
                "policy_year": p.policy_year,
            })
        elif p.policy_status == "active":
            active.append({
                "policy_id": str(p.id),
                "product_name": p.product_name,
                "insurer": p.insurer_name,
                "status": "active",
                "policy_year": p.policy_year,
            })

    if matured and active:
        return [{
            "conflict_type": "surrender_value",
            "severity": "info",
            "description": (
                f"You have {len(matured)} surrendered endowment/whole life policies alongside "
                f"{len(active)} active policies of the same type. "
                f"Surrendered policies may have reduced surrender values depending on "
                f"policy year at surrender. "
                f"Review whether early surrender was due to a better alternative."
            ),
            "affected_policies": matured + active,
            "detail": {
                "matured_count": len(matured),
                "active_count": len(active),
            },
            "resolution_hint": (
                "Review surrender value projections in the original policy documents. "
                "Compare with the expected returns from the active policy. "
                "Consider whether the active policy's projected maturity benefit "
                "justifies continued premium payments."
            ),
        }]

    return []
