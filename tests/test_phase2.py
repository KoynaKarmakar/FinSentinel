"""Phase 2 tests — LangGraph agent logic.

Score-to-tier mapping (thresholds: LOW≤20, MEDIUM≤39, HIGH≤64, CRITICAL>64):
  Structuring       (985k, vel=1, age=420, cross=F): large(20)+threshold(20) = 40 → HIGH
  Fan-out smurfing  (4.5M, vel=7, age=12,  cross=F): large(20)+vel(25)+new(25)= 70 → CRITICAL
  Cross-border      (2.2M, vel=3, age=8,   cross=T): large(20)+new(25)+cross(15)=60 → HIGH
  Legitimate        (1.8M, vel=1, age=847, cross=F): large(20)               = 20 → LOW
  Conflicting       (1.8M, vel=1, age=847, cross=T): large(20)+cross(15)     = 35 → MEDIUM
"""
import pytest
from app.agents.state import ComplianceInvestigationState
from app.agents.transaction_analysis import transaction_analysis_node


def _state(account_id, amount_inr, velocity_24h, account_age_days, is_cross_border):
    return ComplianceInvestigationState(
        transaction={
            "account_id": account_id,
            "amount_inr": amount_inr,
            "velocity_24h": velocity_24h,
            "account_age_days": account_age_days,
            "is_cross_border": is_cross_border,
        },
        suspicious_indicators=[],
        risk_score=0.0,
        risk_tier="LOW",
        scoring_rationale="",
        policy_citations=[],
        final_report={},
    )


def test_structuring_tier_is_high():
    # ₹9.85L: large_single(20) + threshold_proximity(20) = 40 → HIGH
    result = transaction_analysis_node(_state("C1001", 985000, 1, 420, False))
    assert "threshold_proximity" in result["suspicious_indicators"]
    assert "large_single_transfer" in result["suspicious_indicators"]
    assert result["risk_score"] == 40.0
    assert result["risk_tier"] == "HIGH"


def test_fan_out_smurfing_tier_is_critical():
    # ₹45L, vel=7, age=12: large(20)+velocity(25)+new_account(25) = 70 → CRITICAL
    result = transaction_analysis_node(_state("C1002", 4500000, 7, 12, False))
    assert "high_velocity" in result["suspicious_indicators"]
    assert "new_account_large_txn" in result["suspicious_indicators"]
    assert "large_single_transfer" in result["suspicious_indicators"]
    assert result["risk_score"] == 70.0
    assert result["risk_tier"] == "CRITICAL"


def test_cross_border_layering_tier_is_high():
    # ₹22L, age=8, cross=True: large(20)+new_account(25)+cross(15) = 60 → HIGH
    result = transaction_analysis_node(_state("C1003", 2200000, 3, 8, True))
    assert "cross_border_transfer" in result["suspicious_indicators"]
    assert "new_account_large_txn" in result["suspicious_indicators"]
    assert "large_single_transfer" in result["suspicious_indicators"]
    assert result["risk_score"] == 60.0
    assert result["risk_tier"] == "HIGH"


def test_legitimate_transfer_tier_is_low():
    # ₹18L, age=847: large_single(20) = 20 → LOW (only flag, no escalation)
    result = transaction_analysis_node(_state("C1004", 1800000, 1, 847, False))
    assert result["risk_score"] == 20.0
    assert result["risk_tier"] == "LOW"
    # large_single_transfer fires (₹18L > ₹5L) but score stays within LOW threshold
    assert "large_single_transfer" in result["suspicious_indicators"]


def test_conflicting_signals_tier_is_medium():
    # ₹18L + cross-border: large(20)+cross(15) = 35 → MEDIUM
    result = transaction_analysis_node(_state("C1005", 1800000, 1, 847, True))
    assert "cross_border_transfer" in result["suspicious_indicators"]
    assert "large_single_transfer" in result["suspicious_indicators"]
    assert result["risk_score"] == 35.0
    assert result["risk_tier"] == "MEDIUM"


def test_no_flags_below_threshold():
    # ₹4L — below ₹5L threshold, no flags
    result = transaction_analysis_node(_state("C1006", 400000, 1, 500, False))
    assert result["suspicious_indicators"] == []
    assert result["risk_score"] == 0.0
    assert result["risk_tier"] == "LOW"


def test_score_caps_at_100():
    # All flags simultaneously: 20+25+25+15+20 = 105 → capped at 100
    result = transaction_analysis_node(_state("C1007", 985000, 7, 10, True))
    assert result["risk_score"] == 100.0
    assert result["risk_tier"] == "CRITICAL"


def test_rationale_populated_when_flags_fire():
    result = transaction_analysis_node(_state("C1008", 985000, 1, 420, False))
    assert result["scoring_rationale"] != ""
    assert "No suspicious indicators detected." not in result["scoring_rationale"]


def test_rationale_clean_when_no_flags():
    result = transaction_analysis_node(_state("C1009", 100000, 1, 500, False))
    assert result["scoring_rationale"] == "No suspicious indicators detected."


def test_graph_compiles_without_error():
    pytest.importorskip(
        "sentence_transformers",
        reason="sentence-transformers not installed in this environment — skipped",
    )
    from app.agents.graph import compliance_graph
    assert compliance_graph is not None


def test_state_schema_has_all_keys():
    keys = ComplianceInvestigationState.__annotations__.keys()
    expected = {
        "transaction", "suspicious_indicators", "risk_score",
        "risk_tier", "scoring_rationale", "policy_citations", "final_report",
    }
    assert expected.issubset(keys)
