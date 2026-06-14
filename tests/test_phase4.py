"""Phase 4 tests — evaluation dataset integrity and eval runner correctness."""
import pytest
from app.evaluation.eval_dataset import EVAL_CASES
from app.evaluation.run_eval import run_indicator_recall_eval, run_tier_accuracy_eval


# ── Eval Dataset Structure ────────────────────────────────────────────────────

def test_eval_dataset_minimum_size():
    assert len(EVAL_CASES) >= 5


def test_eval_cases_have_required_keys():
    required = {"transaction", "expected_tier", "expected_indicators",
                "expected_citation_keywords", "expected_score"}
    for i, case in enumerate(EVAL_CASES):
        assert required.issubset(case.keys()), f"Case {i} missing keys"


def test_eval_cases_transaction_fields():
    txn_fields = {"account_id", "amount_inr", "velocity_24h", "account_age_days", "is_cross_border"}
    for case in EVAL_CASES:
        assert txn_fields.issubset(case["transaction"].keys())


def test_eval_cases_cover_all_tiers():
    tiers = {c["expected_tier"] for c in EVAL_CASES}
    assert "LOW" in tiers
    assert "MEDIUM" in tiers
    assert "HIGH" in tiers
    assert "CRITICAL" in tiers


def test_eval_cases_valid_tiers():
    valid = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    for case in EVAL_CASES:
        assert case["expected_tier"] in valid


def test_eval_scores_are_non_negative():
    for case in EVAL_CASES:
        assert case["expected_score"] >= 0.0


def test_eval_scores_do_not_exceed_100():
    for case in EVAL_CASES:
        assert case["expected_score"] <= 100.0


# ── Eval Runner Correctness ───────────────────────────────────────────────────

def test_tier_accuracy_eval_structure():
    results = run_tier_accuracy_eval()
    assert "accuracy" in results
    assert "correct" in results
    assert "total" in results
    assert results["total"] == len(EVAL_CASES)


def test_tier_accuracy_is_100_percent():
    results = run_tier_accuracy_eval()
    failed = [r for r in results["results"] if not r["correct"]]
    assert results["accuracy"] == 1.0, (
        f"Expected 100% tier accuracy, got {results['accuracy']:.1%}.\n"
        f"Failed cases: {failed}"
    )


def test_indicator_recall_eval_structure():
    results = run_indicator_recall_eval()
    assert "indicator_recall" in results
    assert "found" in results
    assert "expected" in results


def test_indicator_recall_is_100_percent():
    results = run_indicator_recall_eval()
    assert results["indicator_recall"] == 1.0, (
        f"Expected 100% indicator recall, got {results['indicator_recall']:.1%}. "
        f"Found {results['found']}/{results['expected']}"
    )


def test_per_case_score_matches_expected():
    from app.agents.transaction_analysis import transaction_analysis_node
    from app.agents.state import ComplianceInvestigationState

    for case in EVAL_CASES:
        state = ComplianceInvestigationState(
            transaction=case["transaction"],
            suspicious_indicators=[],
            risk_score=0.0,
            risk_tier="LOW",
            scoring_rationale="",
            policy_citations=[],
            final_report={},
        )
        result = transaction_analysis_node(state)
        assert result["risk_score"] == case["expected_score"], (
            f"Case {case['transaction']['account_id']}: "
            f"expected score {case['expected_score']}, got {result['risk_score']}"
        )
