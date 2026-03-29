SG_HOUSEHOLD_BENCHMARKS = {
    "DEATH": {
        "description": "Life insurance coverage as multiple of annual income",
        "ranges": [
            {"min_multiple": 10, "max_multiple": 12, "label": "Typical household"},
            {"min_multiple": 8, "max_multiple": 15, "label": "Acceptable range"},
        ],
        "source": "MAS / industry guidance for Singapore households",
        "note": "Based on income replacement for dependants until children finish education",
    },
    "CRITICAL_ILLNESS": {
        "description": "CI coverage as multiple of annual income",
        "ranges": [
            {"min_multiple": 3, "max_multiple": 5, "label": "Typical household"},
            {"min_multiple": 2, "max_multiple": 7, "label": "Acceptable range"},
        ],
        "source": "LIA Singapore / industry guidance",
        "note": "LIA Core 3 conditions (heart attack, cancer, stroke) are the primary focus",
    },
    "HOSPITALISATION": {
        "description": "Ward class and annual premium benchmarks",
        "ward_classes": {
            "B2_C": {"description": "Public ward B2/C (MediShield Life only)", "typical_premium_annual": "S$200-S$600"},
            "B1": {"description": "Public ward B1", "typical_premium_annual": "S$600-S$1,200"},
            "A": {"description": "Private hospital A ward", "typical_premium_annual": "S$1,500-S$4,000"},
            "Private": {"description": "Private hospital", "typical_premium_annual": "S$3,000-S$8,000"},
        },
        "source": "CPF Board / MAS published MediShield Life parameters",
    },
    "DISABILITY": {
        "description": "Monthly income replacement for disability",
        "ranges": [
            {"percentage": 75, "label": "Typical target", "note": "Of monthly income"},
        ],
        "source": "Industry standard / MAS guidance",
        "note": "Occupation-specific definitions vary significantly between insurers",
    },
    "TPD": {
        "description": "TPD coverage typically mirrors life coverage",
        "ranges": [
            {"min_multiple": 10, "max_multiple": 12, "label": "Typical household"},
        ],
        "source": "LIA Singapore",
        "note": "LIA definition: inability to perform 3 of 6 ADLs",
    },
}

def get_benchmark_for_coverage_type(coverage_type: str, annual_income_cents: int | None = None) -> dict:
    benchmark = SG_HOUSEHOLD_BENCHMARKS.get(coverage_type, {})
    if not benchmark:
        return {}
    result = dict(benchmark)
    if annual_income_cents and coverage_type in ("DEATH", "CRITICAL_ILLNESS"):
        income_sgd = annual_income_cents / 100
        ranges = benchmark.get("ranges", [])
        if ranges:
            typical = ranges[0]
            result["calculated_min_cents"] = int(typical["min_multiple"] * income_sgd * 100)
            result["calculated_max_cents"] = int(typical["max_multiple"] * income_sgd * 100)
    return result
