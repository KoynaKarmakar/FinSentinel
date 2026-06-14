from app.agents.state import ComplianceInvestigationState
from app.agents.transaction_analysis import transaction_analysis_node
from app.core.logger import get_logger
from app.evaluation.eval_dataset import EVAL_CASES

logger = get_logger(__name__)


def run_tier_accuracy_eval() -> dict:
    correct = 0
    total = len(EVAL_CASES)
    results = []

    for case in EVAL_CASES:
        initial_state = ComplianceInvestigationState(
            transaction=case["transaction"],
            suspicious_indicators=[],
            risk_score=0.0,
            risk_tier="LOW",
            scoring_rationale="",
            policy_citations=[],
            final_report={},
        )
        result = transaction_analysis_node(initial_state)
        predicted = result["risk_tier"]
        expected = case["expected_tier"]
        hit = predicted == expected
        if hit:
            correct += 1
        results.append({
            "account_id": case["transaction"]["account_id"],
            "expected": expected,
            "predicted": predicted,
            "correct": hit,
            "score": result["risk_score"],
            "indicators": result["suspicious_indicators"],
        })

    accuracy = correct / total if total > 0 else 0.0
    return {"accuracy": accuracy, "correct": correct, "total": total, "results": results}


def run_indicator_recall_eval() -> dict:
    total_expected = 0
    total_found = 0

    for case in EVAL_CASES:
        initial_state = ComplianceInvestigationState(
            transaction=case["transaction"],
            suspicious_indicators=[],
            risk_score=0.0,
            risk_tier="LOW",
            scoring_rationale="",
            policy_citations=[],
            final_report={},
        )
        result = transaction_analysis_node(initial_state)
        expected_inds = set(case["expected_indicators"])
        predicted_inds = set(result["suspicious_indicators"])
        total_expected += len(expected_inds)
        total_found += len(expected_inds & predicted_inds)

    recall = total_found / total_expected if total_expected > 0 else 1.0
    return {"indicator_recall": recall, "found": total_found, "expected": total_expected}


if __name__ == "__main__":
    print("\n=== FinSentinel Evaluation ===\n")

    tier_results = run_tier_accuracy_eval()
    print(f"Risk Tier Accuracy : {tier_results['accuracy']:.1%}  ({tier_results['correct']}/{tier_results['total']})")
    print("\nPer-case breakdown:")
    for r in tier_results["results"]:
        status = "✓" if r["correct"] else "✗"
        print(f"  {status} {r['account_id']}: expected={r['expected']}, predicted={r['predicted']}, score={r['score']}")

    indicator_results = run_indicator_recall_eval()
    print(f"\nIndicator Recall   : {indicator_results['indicator_recall']:.1%}  ({indicator_results['found']}/{indicator_results['expected']})")
    print("\nNote: Run with documents indexed for full retrieval + RAGAS evaluation.")
