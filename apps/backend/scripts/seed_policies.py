"""
Seed script for demo data.
Run from apps/backend/ with:
    python -m scripts.seed_policies
    python -m scripts.seed_policies --clean
"""
from __future__ import annotations

import argparse
import asyncio
import uuid
from datetime import date
from decimal import Decimal

# ── DB setup ──────────────────────────────────────────────────────────────────
from sqlalchemy import select, delete
from app.core.database import Base, async_session_maker

# ── Models ────────────────────────────────────────────────────────────────────
from app.models.user import User
from app.models.policy import Policy, Benefit, Rider, Exclusion


# ── Deterministic demo user IDs ───────────────────────────────────────────────
SARAH_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
RAVI_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")


# ── Helpers ───────────────────────────────────────────────────────────────────
def _d(year: int, month: int, day: int) -> date:
    return date(year, month, day)


def _cid(cents: int) -> int:
    """Ensure even hundreds for realistic cent amounts."""
    return (cents // 100) * 100


# ── Seed data ──────────────────────────────────────────────────────────────────
POLICIES = [
    # ── Sarah Chen ───────────────────────────────────────────────────────────
    {
        "user_id": SARAH_ID,
        "insurer_code": "AIA",
        "insurer_name": "AIA",
        "product_name": "AIA Premier Life",
        "product_type": "whole_life",
        "policy_number": "AIA-PL-2019-88421",
        "issue_date": _d(2019, 3, 15),
        "expiry_date": _d(2089, 3, 15),
        "sum_assured_cents": _cid(150_000_00),  # S$150,000
        "premium_amount_cents": _cid(8_850_00),  # S$8,850/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 7,
        "parse_confidence": 0.94,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A whole-life insurance plan that pays a lump sum to your beneficiaries upon "
            "your death, with built-in critical illness coverage and cash value accumulation "
            "that can be withdrawn after 10 years."
        ),
        "benefits": [
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "Paid as a lump sum to beneficiaries upon death at any age.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(150_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.96,
                "raw_text_excerpt": "Basic Death Benefit — 100% of Sum Assured payable on death.",
            },
            {
                "benefit_type": "critical_illness",
                "benefit_subtype": "standard_ci",
                "trigger_description": "Paid on diagnosis of any one of 37 LIA-defined critical illness conditions.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(150_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"waiting_period_days": 90, "survival_period_days": 14},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.93,
                "raw_text_excerpt": "Critical Illness Benefit — 100% of Sum Assured on first CI diagnosis.",
            },
            {
                "benefit_type": "cash_value",
                "benefit_subtype": "surrender_value",
                "trigger_description": "Accumulated cash value available for withdrawal or policy surrender after year 10.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(22_500_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"min_policy_year": 10},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.91,
                "raw_text_excerpt": "Cash Value — projected at 15% of total premiums paid by year 10.",
            },
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "ward_benefit",
                "trigger_description": "S$200 per day for each day hospitalised in a public ward for up to 365 days.",
                "payout_type": "reimbursement",
                "amount_cents": _cid(200_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"min_days": 1, "max_days": 365, "ward_type": "public"},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.88,
                "raw_text_excerpt": "Hospitalisation Income — S$200/day public ward, max 365 days per year.",
            },
        ],
        "riders": [
            {
                "rider_name": "AIA Early Critical Illness Rider",
                "rider_type": "early_ci",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(1_200_00),
                "additional_sum_assured_cents": _cid(75_000_00),
                "conditions": {"stages_covered": 3},
                "parse_confidence": 0.92,
            },
            {
                "rider_name": "AIA Payor Waiver",
                "rider_type": "payor_waiver",
                "linked_benefit_id": None,
                "additional_premium_cents": None,
                "additional_sum_assured_cents": None,
                "conditions": {"trigger": "total_disability", "max_age": 65},
                "parse_confidence": 0.90,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "No benefit is payable if death or CI arises from self-inflicted injuries within 2 years of policy inception.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.97,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions diagnosed or symptoms evident before or within 90 days of policy issue are excluded.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Death or CI resulting from active participation in hazardous sports or criminal acts is excluded.",
                "exclusion_category": "lifestyle",
                "parse_confidence": 0.94,
            },
        ],
    },
    {
        "user_id": SARAH_ID,
        "insurer_code": "GE",
        "insurer_name": "Great Eastern",
        "product_name": "Great Eastern Econome",
        "product_type": "term",
        "policy_number": "GE-TERM-2020-55103",
        "issue_date": _d(2020, 7, 22),
        "expiry_date": _d(2050, 7, 22),
        "sum_assured_cents": _cid(300_000_00),  # S$300,000
        "premium_amount_cents": _cid(1_800_00),  # S$1,800/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 6,
        "parse_confidence": 0.96,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A 30-year term plan providing S$300,000 of death and total permanent disability coverage "
            "at an affordable annual premium. Ideal as temporary income protection during working years."
        ),
        "benefits": [
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "Paid as a lump sum to beneficiaries upon death during the policy term.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(300_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"policy_term_years": 30},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.97,
                "raw_text_excerpt": "Death Benefit — S$300,000 lump sum within policy term.",
            },
            {
                "benefit_type": "total_permanent_disability",
                "benefit_subtype": "tpd",
                "trigger_description": "Paid if the insured is totally and permanently disabled and unable to perform any occupation.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(300_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"definition": "own_occupation", "elimination_period_days": 180},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.95,
                "raw_text_excerpt": "TPD Benefit — payable on total permanent disability.",
            },
            {
                "benefit_type": "terminal_illness",
                "benefit_subtype": "ti",
                "trigger_description": "Paid if the insured is diagnosed with a terminal illness with less than 12 months to live.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(300_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"life_expectancy_months": 12},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.93,
                "raw_text_excerpt": "Terminal Illness Benefit — advanced payout if terminal diagnosis.",
            },
        ],
        "riders": [
            {
                "rider_name": "GE Accidental Death & TPD Rider",
                "rider_type": "accident",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(450_00),
                "additional_sum_assured_cents": _cid(150_000_00),
                "conditions": {"accident_definition": "external_visible_means"},
                "parse_confidence": 0.91,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Self-inflicted injuries or suicide within 1 year of policy start.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.96,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing medical conditions known before application.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Mental health disorders and their complications are excluded from TPD.",
                "exclusion_category": "mental_health",
                "parse_confidence": 0.93,
            },
        ],
    },
    {
        "user_id": SARAH_ID,
        "insurer_code": "PRU",
        "insurer_name": "Prudential",
        "product_name": "Prudential PruSecure Term",
        "product_type": "term",
        "policy_number": "PRU-TERM-2021-77189",
        "issue_date": _d(2021, 11, 1),
        "expiry_date": _d(2051, 11, 1),
        "sum_assured_cents": _cid(200_000_00),  # S$200,000
        "premium_amount_cents": _cid(960_00),  # S$960/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 5,
        "parse_confidence": 0.95,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A 30-year decreasing term plan with accelerated critical illness rider. "
            "Covers death, TPD, and 73 critical illness stages with partial payouts for early-stage CI."
        ),
        "benefits": [
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "Lump sum payment to beneficiaries on death during the term.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(200_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.96,
                "raw_text_excerpt": "Death Benefit — S$200,000 lump sum.",
            },
            {
                "benefit_type": "critical_illness",
                "benefit_subtype": "accelerated_ci",
                "trigger_description": "Accelerated payment on CI diagnosis; remaining sum assured reduced accordingly.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(200_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": 14,
                "conditions": {"stages": ["early", "standard", "severe"], "waiting_period_days": 90},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.94,
                "raw_text_excerpt": "Accelerated CI — S$200,000, remaining sum reduced post-payout.",
            },
        ],
        "riders": [
            {
                "rider_name": "Pru Early Stage CI Booster",
                "rider_type": "early_ci",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(720_00),
                "additional_sum_assured_cents": _cid(100_000_00),
                "conditions": {"stages": ["early", "intermediate"]},
                "parse_confidence": 0.92,
            },
            {
                "rider_name": "Pru Payor Waiver Rider",
                "rider_type": "payor_waiver",
                "linked_benefit_id": None,
                "additional_premium_cents": None,
                "additional_sum_assured_cents": None,
                "conditions": {"trigger": "death_or_tpd", "max_age": 60},
                "parse_confidence": 0.89,
            },
            {
                "rider_name": "HPB Rider",
                "rider_type": "hospitalisation",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(350_00),
                "additional_sum_assured_cents": _cid(500_00),
                "conditions": {"reimbursement_type": "daily_cash", "max_days": 60},
                "parse_confidence": 0.88,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions declared at application are excluded.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Suicide within 12 months of issue or reinstatement.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.96,
            },
        ],
    },
    {
        "user_id": SARAH_ID,
        "insurer_code": "NTUC",
        "insurer_name": "NTUC Income",
        "product_name": "NTUC Income GroCash",
        "product_type": "endowment",
        "policy_number": "NTUC-END-2018-33401",
        "issue_date": _d(2018, 5, 10),
        "expiry_date": _d(2028, 5, 10),
        "sum_assured_cents": _cid(50_000_00),  # S$50,000
        "premium_amount_cents": _cid(5_400_00),  # S$5,400/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 8,
        "parse_confidence": 0.97,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A 10-year endowment plan that pays a guaranteed maturity benefit of S$50,000 "
            "plus non-guaranteed bonuses. Provides life coverage and savings with a guaranteed "
            "return of principal at maturity."
        ),
        "benefits": [
            {
                "benefit_type": "survival_benefit",
                "benefit_subtype": "maturity_benefit",
                "trigger_description": "Paid as a lump sum on policy maturity date if the insured is alive.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(50_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"policy_term_years": 10, "survival_required": True},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.98,
                "raw_text_excerpt": "Maturity Benefit — S$50,000 + declared bonuses on 10 May 2028.",
            },
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "Paid to beneficiaries if death occurs before maturity.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(50_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.97,
                "raw_text_excerpt": "Death Benefit prior to maturity — S$50,000 + vested bonuses.",
            },
            {
                "benefit_type": "cash_value",
                "benefit_subtype": "surrender_value",
                "trigger_description": "Available if the policy is surrendered before maturity; guaranteed surrender value applies after year 3.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(12_000_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"min_policy_year": 3, "gsv_scale": "published"},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.92,
                "raw_text_excerpt": "Guaranteed Surrender Value — applicable after 3rd policy year.",
            },
        ],
        "riders": [
            {
                "rider_name": "GroCash Waiver of Premium",
                "rider_type": "payor_waiver",
                "linked_benefit_id": None,
                "additional_premium_cents": None,
                "additional_sum_assured_cents": None,
                "conditions": {"trigger": "total_disability"},
                "parse_confidence": 0.90,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Suicide within 12 months of issue is excluded from death benefit.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.96,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions are excluded from all benefits.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
        ],
    },
    {
        "user_id": SARAH_ID,
        "insurer_code": "GE",
        "insurer_name": "Great Eastern",
        "product_name": "GE HospiShield Plus",
        "product_type": "hospitalisation",
        "policy_number": "GE-HSP-2022-99012",
        "issue_date": _d(2022, 2, 14),
        "expiry_date": _d(2099, 12, 31),
        "sum_assured_cents": _cid(1_000_000_00),  # S$1,000,000 lifetime limit
        "premium_amount_cents": _cid(3_600_00),  # S$3,600/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 4,
        "parse_confidence": 0.93,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A comprehensive hospitalisation and surgical insurance covering ward charges, "
            "surgical fees, and post-hospitalisation treatment up to S$1,000,000 lifetime. "
            "Covers public and private hospitals including Class A/B1 wards."
        ),
        "benefits": [
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "ward_and_board",
                "trigger_description": "Reimbursement of eligible ward and board charges for hospital stays.",
                "payout_type": "reimbursement",
                "amount_cents": _cid(800_00),  # S$800/day
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {
                    "ward_type": "private",
                    "max_days_per_discharge": 120,
                    "max_per_discharge": 50_000_00,
                },
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.94,
                "raw_text_excerpt": "Ward & Board — S$800/day for private hospital stays.",
            },
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "surgical_benefit",
                "trigger_description": "Reimbursement of surgeon and anaesthetist fees for approved surgical procedures.",
                "payout_type": "reimbursement",
                "amount_cents": _cid(15_000_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"schedule": "msoc", "min_major_surgical": True},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.92,
                "raw_text_excerpt": "Surgical Benefit — up to S$15,000 per major surgery.",
            },
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "post_hospital",
                "trigger_description": "Covers follow-up treatment and specialist consultations within 90 days after discharge.",
                "payout_type": "reimbursement",
                "amount_cents": _cid(2_500_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"follow_up_days": 90},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.89,
                "raw_text_excerpt": "Post-Hospitalisation Treatment — 90 days follow-up coverage.",
            },
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "critical_illness_hospital",
                "trigger_description": "Additional daily hospital cash of S$300 when admitted for a covered CI.",
                "payout_type": "income_replacement",
                "amount_cents": _cid(300_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"ci_diagnosis_required": True, "max_days": 60},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.87,
                "raw_text_excerpt": "CI Hospital Income — S$300/day when admitted for CI.",
            },
        ],
        "riders": [
            {
                "rider_name": "GE Major Cancer Booster",
                "rider_type": "cancer_booster",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(840_00),
                "additional_sum_assured_cents": _cid(100_000_00),
                "conditions": {"cancer_stages": [1, 2, 3, 4], "diagnosis_type": "confirmed"},
                "parse_confidence": 0.91,
            },
            {
                "rider_name": "GE Invisible Waiting Period Waive",
                "rider_type": "waiver",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(200_00),
                "additional_sum_assured_cents": None,
                "conditions": {"covers": "invisible_waiting_period_conditions"},
                "parse_confidence": 0.85,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Treatment for mental health conditions, nervous or psychiatric disorders.",
                "exclusion_category": "mental_health",
                "parse_confidence": 0.94,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions declared at underwriting are excluded for 12 months.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Treatment for self-inflicted injuries, illegal acts, or war/travel advisories.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.93,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Cosmetic surgery, weight management programs, and experimental treatments.",
                "exclusion_category": "lifestyle",
                "parse_confidence": 0.91,
            },
        ],
    },
    # ── Ravi Kumar ───────────────────────────────────────────────────────────
    {
        "user_id": RAVI_ID,
        "insurer_code": "PRU",
        "insurer_name": "Prudential",
        "product_name": "Prudential PRUlink Active Life",
        "product_type": "whole_life",
        "policy_number": "PRU-WL-2017-11002",
        "issue_date": _d(2017, 6, 1),
        "expiry_date": _d(2087, 6, 1),
        "sum_assured_cents": _cid(500_000_00),  # S$500,000
        "premium_amount_cents": _cid(18_000_00),  # S$18,000/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 9,
        "parse_confidence": 0.92,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A participating whole-life plan with lifelong death benefit of S$500,000, "
            "critical illness coverage, and annual dividends that can accumulate as cash value. "
            "Designed for long-term wealth preservation and estate planning."
        ),
        "benefits": [
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "Paid as a lump sum to beneficiaries upon death at any age, for life.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(500_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.95,
                "raw_text_excerpt": "Basic Death — S$500,000 payable to beneficiaries on death.",
            },
            {
                "benefit_type": "critical_illness",
                "benefit_subtype": "standard_ci",
                "trigger_description": "Paid on diagnosis of any one of 73 LIA CI conditions including early, intermediate, and severe stages.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(500_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": 14,
                "conditions": {"stages": ["early", "intermediate", "severe"], "waiting_period_days": 90},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.91,
                "raw_text_excerpt": "CI Benefit — up to S$500,000 across CI stages.",
            },
            {
                "benefit_type": "cash_value",
                "benefit_subtype": "dividend_cash",
                "trigger_description": "Annual reversionary bonuses paid as cash or left to accumulate at 4.5% p.a. interest.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(40_000_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"interest_rate": 0.045},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.88,
                "raw_text_excerpt": "Reversionary Bonuses — declared annually, accumulate at 4.5% p.a.",
            },
            {
                "benefit_type": "total_permanent_disability",
                "benefit_subtype": "tpd",
                "trigger_description": "Paid if insured cannot perform 3 of 6 Activities of Daily Living or is permanently wheelchair-bound.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(500_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"adl_definition": "3_of_6", "elimination_period_days": 180},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.89,
                "raw_text_excerpt": "TPD — 3 of 6 ADL criteria or wheelchair-bound.",
            },
            {
                "benefit_type": "survival_benefit",
                "benefit_subtype": "income_replacement",
                "trigger_description": "Monthly income benefit of S$2,000 paid for 12 months if hospitalised for 7+ consecutive days.",
                "payout_type": "income_replacement",
                "amount_cents": _cid(24_000_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": 7,
                "conditions": {"monthly_amount": 2_000_00, "max_months": 12},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.86,
                "raw_text_excerpt": "Hospitalisation Income — S$2,000/month for up to 12 months.",
            },
        ],
        "riders": [
            {
                "rider_name": "PRUlink Early CI Rider Plus",
                "rider_type": "early_ci",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(3_600_00),
                "additional_sum_assured_cents": _cid(250_000_00),
                "conditions": {"stages_covered": 3, "waiting_period_days": 90},
                "parse_confidence": 0.93,
            },
            {
                "rider_name": "PRU Payor Waiver",
                "rider_type": "payor_waiver",
                "linked_benefit_id": None,
                "additional_premium_cents": None,
                "additional_sum_assured_cents": None,
                "conditions": {"trigger": "death_or_tpd_or_critical_illness", "max_age": 65},
                "parse_confidence": 0.90,
            },
            {
                "rider_name": "HPB Rider III",
                "rider_type": "hospitalisation",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(900_00),
                "additional_sum_assured_cents": _cid(100_000_00),
                "conditions": {"reimbursement_type": "as_charged", "ward_limit": "class_a"},
                "parse_confidence": 0.88,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions not disclosed at application are permanently excluded.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.96,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Suicide or self-inflicted injury within 12 months of policy issue.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Mental health treatment and psychiatric hospitalisation are excluded.",
                "exclusion_category": "mental_health",
                "parse_confidence": 0.92,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Engaging in professional sports, racing (other than foot), aviation (except as fare-paying passenger), or hazardous hobbies.",
                "exclusion_category": "lifestyle",
                "parse_confidence": 0.91,
            },
        ],
    },
    {
        "user_id": RAVI_ID,
        "insurer_code": "AIA",
        "insurer_name": "AIA",
        "product_name": "AIA Secure Flex Term",
        "product_type": "term",
        "policy_number": "AIA-TERM-2023-00241",
        "issue_date": _d(2023, 1, 15),
        "expiry_date": _d(2053, 1, 15),
        "sum_assured_cents": _cid(400_000_00),  # S$400,000
        "premium_amount_cents": _cid(2_400_00),  # S$2,400/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 3,
        "parse_confidence": 0.95,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A 30-year level term plan providing S$400,000 of death and TPD coverage "
            "at fixed premiums. Includes a terminal illness accelerated benefit and "
            "optional conversion privilege before age 65."
        ),
        "benefits": [
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "S$400,000 lump sum to beneficiaries if death occurs within the 30-year term.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(400_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"term_years": 30},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.96,
                "raw_text_excerpt": "Death Benefit — S$400,000 lump sum within 30-year term.",
            },
            {
                "benefit_type": "terminal_illness",
                "benefit_subtype": "accelerated_ti",
                "trigger_description": "Up to S$400,000 advanced payment if diagnosed with terminal illness with less than 12 months prognosis.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(400_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"prognosis_months": 12},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.93,
                "raw_text_excerpt": "Terminal Illness — accelerated payout within term.",
            },
            {
                "benefit_type": "total_permanent_disability",
                "benefit_subtype": "tpd",
                "trigger_description": "S$400,000 if the insured is totally and permanently disabled per AIA's definition.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(400_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": 180,
                "conditions": {"definition": "unable_to_perform_own_occupation"},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.91,
                "raw_text_excerpt": "TPD Benefit — S$400,000 per AIA TPD definition.",
            },
        ],
        "riders": [
            {
                "rider_name": "AIA Accidental Death & Dismemberment Rider",
                "rider_type": "accident",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(600_00),
                "additional_sum_assured_cents": _cid(200_000_00),
                "conditions": {"accident_definition": "external_sudden"},
                "parse_confidence": 0.90,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Self-inflicted injuries or suicide within 1 year from policy start date.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.96,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions omitted from the application form.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
        ],
    },
    {
        "user_id": RAVI_ID,
        "insurer_code": "GE",
        "insurer_name": "Great Eastern",
        "product_name": "Great Eastern HospiShield Gold",
        "product_type": "hospitalisation",
        "policy_number": "GE-HSG-2019-44881",
        "issue_date": _d(2019, 9, 1),
        "expiry_date": _d(2099, 12, 31),
        "sum_assured_cents": _cid(750_000_00),  # S$750,000 lifetime
        "premium_amount_cents": _cid(2_400_00),  # S$2,400/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 7,
        "parse_confidence": 0.94,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A comprehensive medical insurance covering hospital stays, surgeries, "
            "and outpatient treatments at private hospitals up to S$750,000 lifetime. "
            "Includes congenital conditions cover after 2 years."
        ),
        "benefits": [
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "ward_and_board",
                "trigger_description": "S$1,200 per day for private ward accommodation, up to 120 days per discharge.",
                "payout_type": "reimbursement",
                "amount_cents": _cid(1_200_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"ward_type": "private", "max_days": 120},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.95,
                "raw_text_excerpt": "Ward & Board Gold — S$1,200/day private ward, 120 days/incident.",
            },
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "surgical_benefit",
                "trigger_description": "As-charged reimbursement for surgeon and anaesthetist fees for listed procedures.",
                "payout_type": "reimbursement",
                "amount_cents": _cid(25_000_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"schedule": "ge_schedule_plus"},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.93,
                "raw_text_excerpt": "Surgical Benefit — as charged per GE surgical schedule.",
            },
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "pre_post_hospital",
                "trigger_description": "Covers specialist consultations and diagnostic tests 30 days before and 90 days after hospitalisation.",
                "payout_type": "reimbursement",
                "amount_cents": _cid(3_000_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"pre_days": 30, "post_days": 90},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.90,
                "raw_text_excerpt": "Pre/Post-Hospital — 30 days before, 90 days after hospital stay.",
            },
            {
                "benefit_type": "hospitalisation_benefit",
                "benefit_subtype": "daily_cash",
                "trigger_description": "S$250 per day hospital cash when hospitalised in any ward, payable up to 365 days per year.",
                "payout_type": "income_replacement",
                "amount_cents": _cid(250_00),
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"max_days_per_year": 365, "ward_type": "any"},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.88,
                "raw_text_excerpt": "Daily Hospital Cash — S$250/day, any ward, max 365 days/year.",
            },
        ],
        "riders": [
            {
                "rider_name": "GE Major Scan Booster",
                "rider_type": "diagnostic_booster",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(480_00),
                "additional_sum_assured_cents": _cid(5_000_00),
                "conditions": {"scan_types": ["mri", "ct", "pet"]},
                "parse_confidence": 0.89,
            },
            {
                "rider_name": "GE Prolonged Treatment Rider",
                "rider_type": "prolonged_treatment",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(360_00),
                "additional_sum_assured_cents": _cid(60_000_00),
                "conditions": {"min_hospital_days": 30, "payout_per_discharge": 10_000_00},
                "parse_confidence": 0.87,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Mental health and psychiatric conditions including depression and anxiety treatments.",
                "exclusion_category": "mental_health",
                "parse_confidence": 0.94,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions not disclosed and accepted at underwriting.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Suicide attempts and self-inflicted injuries within the first 2 policy years.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.93,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Treatment for obesity, elective cosmetic surgery, or refractive surgery.",
                "exclusion_category": "lifestyle",
                "parse_confidence": 0.90,
            },
        ],
    },
    {
        "user_id": RAVI_ID,
        "insurer_code": "NTUC",
        "insurer_name": "NTUC Income",
        "product_name": "NTUC Income Vantage Invest",
        "product_type": "investment_linked",
        "policy_number": "NTUC-IL-2020-66105",
        "issue_date": _d(2020, 3, 20),
        "expiry_date": _d(2035, 3, 20),
        "sum_assured_cents": _cid(75_000_00),  # S$75,000
        "premium_amount_cents": _cid(12_000_00),  # S$12,000/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 6,
        "parse_confidence": 0.90,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "An investment-linked plan that invests premiums into a diversified fund portfolio "
            "while providing S$75,000 of death and TPD coverage. Unit value fluctuates with "
            "market performance and no guaranteed surrender value is provided."
        ),
        "benefits": [
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "The higher of S$75,000 or the account value paid to beneficiaries on death.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(75_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"type": "higher_of_sum_or_account_value"},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.92,
                "raw_text_excerpt": "Death Benefit — higher of S$75,000 or account value.",
            },
            {
                "benefit_type": "total_permanent_disability",
                "benefit_subtype": "tpd",
                "trigger_description": "Higher of S$75,000 or account value paid if TPD is certified.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(75_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": 180,
                "conditions": {"definition": "own_occupation"},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.88,
                "raw_text_excerpt": "TPD Benefit — account value or S$75,000, whichever is higher.",
            },
            {
                "benefit_type": "survival_benefit",
                "benefit_subtype": "partial_withdrawal",
                "trigger_description": "Partial withdrawals allowed after the lock-in period of 3 years with no withdrawal fee.",
                "payout_type": "lump_sum",
                "amount_cents": None,
                "percentage_of_sum_assured": None,
                "survival_period_days": None,
                "conditions": {"min_withdrawal": 500_00, "lock_in_years": 3, "max_per_year": 20_000_00},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.85,
                "raw_text_excerpt": "Partial Withdrawal — free after year 3, max S$20k/year.",
            },
        ],
        "riders": [
            {
                "rider_name": "Vantage CI Accelerator",
                "rider_type": "ci_booster",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(1_500_00),
                "additional_sum_assured_cents": _cid(75_000_00),
                "conditions": {"ci_stages": ["standard", "severe"], "payout_type": "accelerated"},
                "parse_confidence": 0.87,
            },
            {
                "rider_name": "Premium Waiver on Disability",
                "rider_type": "payor_waiver",
                "linked_benefit_id": None,
                "additional_premium_cents": None,
                "additional_sum_assured_cents": None,
                "conditions": {"trigger": "total_disability", "elimination_days": 90},
                "parse_confidence": 0.86,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Death or TPD arising from pre-existing conditions not disclosed at point of application.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Suicide within 12 months of policy issue or last reinstatement.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.94,
            },
        ],
    },
    {
        "user_id": RAVI_ID,
        "insurer_code": "PRU",
        "insurer_name": "Prudential",
        "product_name": "Prudential PruTerm Vantage",
        "product_type": "term",
        "policy_number": "PRU-TV-2018-22887",
        "issue_date": _d(2018, 8, 15),
        "expiry_date": _d(2048, 8, 15),
        "sum_assured_cents": _cid(350_000_00),  # S$350,000
        "premium_amount_cents": _cid(1_575_00),  # S$1,575/annual
        "premium_frequency": "annual",
        "currency": "SGD",
        "policy_status": "active",
        "policy_year": 8,
        "parse_confidence": 0.96,
        "raw_pdf_key": None,
        "structured_data": {},
        "plain_english_summary": (
            "A 30-year convertible term plan covering death and total permanent disability "
            "with S$350,000. Can be converted to a whole-life policy before age 65 without "
            "further medical evidence. Affordable premiums ideal for young families."
        ),
        "benefits": [
            {
                "benefit_type": "death_benefit",
                "benefit_subtype": "basic_death",
                "trigger_description": "S$350,000 lump sum to beneficiaries on death during the 30-year term.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(350_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": None,
                "conditions": {"term_years": 30},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.97,
                "raw_text_excerpt": "Death Benefit — S$350,000 within 30-year term.",
            },
            {
                "benefit_type": "total_permanent_disability",
                "benefit_subtype": "tpd",
                "trigger_description": "S$350,000 paid if the insured is certified totally and permanently disabled by an approved physician.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(350_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": 180,
                "conditions": {"definition": "unable_to_work", "attending_physician_required": True},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.94,
                "raw_text_excerpt": "TPD Benefit — S$350,000 per Prudential TPD definition.",
            },
            {
                "benefit_type": "critical_illness",
                "benefit_subtype": "standard_ci",
                "trigger_description": "S$350,000 paid on diagnosis of any covered 73 CI conditions at standard or severe stage.",
                "payout_type": "lump_sum",
                "amount_cents": _cid(350_000_00),
                "percentage_of_sum_assured": 1.0,
                "survival_period_days": 14,
                "conditions": {"ci_conditions": 73, "stages": ["standard", "severe"]},
                "exclusions": {},
                "is_active": True,
                "parse_confidence": 0.93,
                "raw_text_excerpt": "CI Benefit — S$350,000 for 73 covered CI conditions.",
            },
        ],
        "riders": [
            {
                "rider_name": "Pru Dread Disease EZY Rider",
                "rider_type": "dd_booster",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(980_00),
                "additional_sum_assured_cents": _cid(175_000_00),
                "conditions": {"dd_list": 8, "payout_type": "lump_sum"},
                "parse_confidence": 0.91,
            },
            {
                "rider_name": "Pru Shield Plus Hospital Cash",
                "rider_type": "hospital_cash",
                "linked_benefit_id": None,
                "additional_premium_cents": _cid(420_00),
                "additional_sum_assured_cents": _cid(18_000_00),
                "conditions": {"daily_amount": 150_00, "max_days": 120, "icu_multiplier": 3},
                "parse_confidence": 0.88,
            },
        ],
        "exclusions": [
            {
                "benefit_ids": None,
                "exclusion_text": "Self-inflicted injury or suicide within 1 year of policy issue.",
                "exclusion_category": "self_inflicted",
                "parse_confidence": 0.96,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Pre-existing conditions declared at proposal are excluded for 12 months.",
                "exclusion_category": "pre_existing",
                "parse_confidence": 0.95,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Mental health conditions including psychotic disorders and their consequences.",
                "exclusion_category": "mental_health",
                "parse_confidence": 0.91,
            },
            {
                "benefit_ids": None,
                "exclusion_text": "Engaging in professional sports, aviation activities, or dangerous hobbies without disclosure.",
                "exclusion_category": "lifestyle",
                "parse_confidence": 0.90,
            },
        ],
    },
]


# ── Demo user definitions ──────────────────────────────────────────────────────
DEMO_USERS = [
    {
        "id": SARAH_ID,
        "email": "sarah.chen@example.com",
        "full_name": "Sarah Chen",
        "hashed_email": "sarah.chen@example.com",  # plaintext for demo purposes
    },
    {
        "id": RAVI_ID,
        "email": "ravi.kumar@example.com",
        "full_name": "Ravi Kumar",
        "hashed_email": "ravi.kumar@example.com",
    },
]


# ── Main seed function ────────────────────────────────────────────────────────
async def seed(clean: bool = False) -> None:
    async with async_session_maker() as session:
        # ── Create demo users ──────────────────────────────────────────────
        for user_def in DEMO_USERS:
            result = await session.execute(
                select(User).where(User.id == user_def["id"])
            )
            user = result.scalar_one_or_none()
            if user is None:
                user = User(**user_def)
                session.add(user)

        # ── Clean existing demo data if --clean ───────────────────────────
        if clean:
            demo_user_ids = [SARAH_ID, RAVI_ID]
            await session.execute(
                delete(Benefit).where(Benefit.policy_id.in_(
                    select(Policy.id).where(Policy.user_id.in_(demo_user_ids))
                ))
            )
            await session.execute(
                delete(Rider).where(Rider.policy_id.in_(
                    select(Policy.id).where(Policy.user_id.in_(demo_user_ids))
                ))
            )
            await session.execute(
                delete(Exclusion).where(Exclusion.policy_id.in_(
                    select(Policy.id).where(Policy.user_id.in_(demo_user_ids))
                ))
            )
            await session.execute(
                delete(Policy).where(Policy.user_id.in_(demo_user_ids))
            )
            await session.execute(
                delete(User).where(User.id.in_(demo_user_ids))
            )
            # Re-create users after clean
            for user_def in DEMO_USERS:
                user = User(**user_def)
                session.add(user)
            print("🧹 Cleaned existing demo data.")

        await session.flush()

        # ── Create policies + benefits + riders + exclusions ─────────────
        created = 0
        for pol_def in POLICIES:
            benefits_def = pol_def.pop("benefits")
            riders_def = pol_def.pop("riders")
            exclusions_def = pol_def.pop("exclusions")

            policy = Policy(**pol_def)
            session.add(policy)
            await session.flush()  # get policy.id

            for ben_def in benefits_def:
                benefit = Benefit(policy_id=policy.id, **ben_def)
                session.add(benefit)

            for rider_def in riders_def:
                rider = Rider(policy_id=policy.id, **rider_def)
                session.add(rider)

            for exc_def in exclusions_def:
                exclusion = Exclusion(policy_id=policy.id, **exc_def)
                session.add(exclusion)

            created += 1

        await session.commit()
        print(f"✅ Seeded {created} policies (5 for sarah.chen, 5 for ravi.kumar)")


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed demo policies into Insureview DB")
    parser.add_argument("--clean", action="store_true", help="Delete existing demo data before seeding")
    args = parser.parse_args()

    asyncio.run(seed(clean=args.clean))
