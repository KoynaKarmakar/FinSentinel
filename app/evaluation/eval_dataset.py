"""
Evaluation dataset with 10 ground-truth cases.

Score/tier mapping (thresholds: LOW≤20, MEDIUM≤39, HIGH≤64, CRITICAL>64):
  Flags: large_single_transfer=20, high_velocity=25,
         new_account_large_txn=25, cross_border_transfer=15, threshold_proximity=20
"""
from typing import List


EVAL_CASES: List[dict] = [
    {   # large(20) + threshold(20) = 40 → HIGH
        "transaction": {"account_id": "E001", "amount_inr": 985000, "velocity_24h": 1, "account_age_days": 420, "is_cross_border": False},
        "expected_tier": "HIGH",
        "expected_score": 40.0,
        "expected_indicators": ["large_single_transfer", "threshold_proximity"],
        "expected_citation_keywords": ["structuring", "threshold", "reporting"],
    },
    {   # large(20) + velocity(25) + new_account(25) = 70 → CRITICAL
        "transaction": {"account_id": "E002", "amount_inr": 4500000, "velocity_24h": 7, "account_age_days": 12, "is_cross_border": False},
        "expected_tier": "CRITICAL",
        "expected_score": 70.0,
        "expected_indicators": ["large_single_transfer", "high_velocity", "new_account_large_txn"],
        "expected_citation_keywords": ["AML", "suspicious", "due diligence"],
    },
    {   # large(20) + new_account(25) + cross(15) = 60 → HIGH
        "transaction": {"account_id": "E003", "amount_inr": 2200000, "velocity_24h": 3, "account_age_days": 8, "is_cross_border": True},
        "expected_tier": "HIGH",
        "expected_score": 60.0,
        "expected_indicators": ["large_single_transfer", "new_account_large_txn", "cross_border_transfer"],
        "expected_citation_keywords": ["cross-border", "FATF", "international"],
    },
    {   # large(20) = 20 → LOW
        "transaction": {"account_id": "E004", "amount_inr": 1800000, "velocity_24h": 1, "account_age_days": 847, "is_cross_border": False},
        "expected_tier": "LOW",
        "expected_score": 20.0,
        "expected_indicators": ["large_single_transfer"],
        "expected_citation_keywords": [],
    },
    {   # large(20) + cross(15) = 35 → MEDIUM
        "transaction": {"account_id": "E005", "amount_inr": 1800000, "velocity_24h": 1, "account_age_days": 847, "is_cross_border": True},
        "expected_tier": "MEDIUM",
        "expected_score": 35.0,
        "expected_indicators": ["large_single_transfer", "cross_border_transfer"],
        "expected_citation_keywords": ["cross-border", "transfer"],
    },
    {   # large(20)+threshold(20)+velocity(25)+new_account(25) = 90 → capped=90 → CRITICAL
        "transaction": {"account_id": "E006", "amount_inr": 960000, "velocity_24h": 6, "account_age_days": 25, "is_cross_border": False},
        "expected_tier": "CRITICAL",
        "expected_score": 90.0,
        "expected_indicators": ["large_single_transfer", "threshold_proximity", "high_velocity", "new_account_large_txn"],
        "expected_citation_keywords": ["structuring", "suspicious"],
    },
    {   # no flags (300k < 500k) → 0 → LOW
        "transaction": {"account_id": "E007", "amount_inr": 300000, "velocity_24h": 2, "account_age_days": 500, "is_cross_border": False},
        "expected_tier": "LOW",
        "expected_score": 0.0,
        "expected_indicators": [],
        "expected_citation_keywords": [],
    },
    {   # large(20) + velocity(25) + cross(15) = 60 → HIGH
        "transaction": {"account_id": "E008", "amount_inr": 750000, "velocity_24h": 8, "account_age_days": 200, "is_cross_border": True},
        "expected_tier": "HIGH",
        "expected_score": 60.0,
        "expected_indicators": ["large_single_transfer", "high_velocity", "cross_border_transfer"],
        "expected_citation_keywords": ["transfer", "AML"],
    },
    {   # large(20) + new_account(25) + cross(15) = 60 → HIGH
        "transaction": {"account_id": "E009", "amount_inr": 3000000, "velocity_24h": 2, "account_age_days": 5, "is_cross_border": True},
        "expected_tier": "HIGH",
        "expected_score": 60.0,
        "expected_indicators": ["large_single_transfer", "new_account_large_txn", "cross_border_transfer"],
        "expected_citation_keywords": ["KYC", "due diligence"],
    },
    {   # large(20) + threshold(20) = 40 → HIGH
        "transaction": {"account_id": "E010", "amount_inr": 950000, "velocity_24h": 1, "account_age_days": 1200, "is_cross_border": False},
        "expected_tier": "HIGH",
        "expected_score": 40.0,
        "expected_indicators": ["large_single_transfer", "threshold_proximity"],
        "expected_citation_keywords": ["structuring", "threshold"],
    },
]
