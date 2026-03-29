COVERAGE_TYPES = {
    "DEATH": {
        "description": "Pays lump sum on death",
        "related_types": ["TPD"],
        "benchmark_metric": "10-12x annual income",
        "min_adequate": "10x annual income in SGD",
    },
    "TPD": {
        "description": "Total and Permanent Disability benefit",
        "related_types": ["DEATH"],
        "LIA_definition": "Inability to perform at least 3 of 6 ADLs permanently",
    },
    "CI": {
        "description": "Critical Illness (LIA 37 standardized conditions)",
        "related_types": ["DEATH"],
        "LIA_conditions": 37,
        "core_conditions": ["heart_attack", "cancer", "stroke"],
        "staging": True,
        "benchmark_metric": "3-5x annual income minimum",
    },
    "HOSPITALISATION": {
        "description": "Medical/hospital bill coverage",
        "related_types": ["MEDISHIELD_LIFE", "IP"],
        "Singapore_specific": True,
        "stacking_rule": "CANNOT exceed 100% of actual costs across ALL plans",
    },
    "MEDISHIELD_LIFE": {
        "description": "CPF-funded base medical insurance",
        "Singapore_only": True,
        "funding": "CPF Medisave",
        "ward_class": "B2/C",
    },
    "IP": {
        "description": "Integrated Shield Plan (private layer on MediShield Life)",
        "Singapore_only": True,
        "requires_medishield": True,
        "ward_options": ["A", "B1", "B2+", "Private"],
    },
    "ACCIDENT": {
        "description": "Accident-related injury coverage",
    },
    "DISABILITY": {
        "description": "Income replacement on disability",
        "benchmark_metric": "75% of monthly income",
    },
}
