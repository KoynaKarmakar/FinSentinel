# app/agents/transaction_analysis.py
from app.agents.state import ComplianceInvestigationState
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

_FLAG_WEIGHTS = {
    "large_single_transfer": 20,
    "high_velocity": 25,
    "new_account_large_txn": 25,
    "cross_border_transfer": 15,
    "threshold_proximity": 20,
}

def transaction_analysis_node(state: ComplianceInvestigationState) -> dict:
    """
    Agent 1: Runs deterministic validation rule matrices against incoming payloads.
    Returns only mutated keys to avoid state corruption.
    """
    txn = state["transaction"]
    
    # Defensive casting to ensure numerical evaluation operations never crash
    amount = float(txn.get("amount_inr") or txn.get("amount", 0))
    velocity = int(txn.get("velocity_24h", 0))
    age_days = int(txn.get("account_age_days", 9999))
    is_cross = bool(txn.get("is_cross_border", False))

    indicators: list = []
    score = 0.0
    rationale_parts: list = []

    if amount > 500000:
        indicators.append("large_single_transfer")
        score += _FLAG_WEIGHTS["large_single_transfer"]
        rationale_parts.append(f"Amount ₹{amount:,.0f} exceeds ₹5L threshold (+{_FLAG_WEIGHTS['large_single_transfer']} pts)")

    if velocity > 5:
        indicators.append("high_velocity")
        score += _FLAG_WEIGHTS["high_velocity"]
        rationale_parts.append(f"Velocity {velocity} transactions/24h exceeds threshold (+{_FLAG_WEIGHTS['high_velocity']} pts)")

    if age_days < 30 and amount > 200000:
        indicators.append("new_account_large_txn")
        score += _FLAG_WEIGHTS["new_account_large_txn"]
        rationale_parts.append(f"Account aged {age_days} days with ₹{amount:,.0f} transfer (+{_FLAG_WEIGHTS['new_account_large_txn']} pts)")

    if is_cross:
        indicators.append("cross_border_transfer")
        score += _FLAG_WEIGHTS["cross_border_transfer"]
        rationale_parts.append(f"Cross-border transfer detected (+{_FLAG_WEIGHTS['cross_border_transfer']} pts)")

    if 900000 < amount < 1000000:
        indicators.append("threshold_proximity")
        score += _FLAG_WEIGHTS["threshold_proximity"]
        rationale_parts.append(f"Amount ₹{amount:,.0f} just below ₹10L reporting threshold — structuring signal (+{_FLAG_WEIGHTS['threshold_proximity']} pts)")

    score = min(score, 100.0)

    # Dynamic fallback checks to config keys
    if score <= getattr(settings, "risk_tier_low", 20.0):
        tier = "LOW"
    elif score <= getattr(settings, "risk_tier_medium", 50.0):
        tier = "MEDIUM"
    elif score <= getattr(settings, "risk_tier_high", 75.0):
        tier = "HIGH"
    else:
        tier = "CRITICAL"

    rationale = "\n• ".join(rationale_parts) if rationale_parts else "No suspicious indicators detected."
    if rationale_parts:
        rationale = "• " + rationale

    logger.info(f"Account {txn.get('account_id', 'UNKNOWN')}: score={score}, tier={tier}, flags={indicators}")

    return {
        "suspicious_indicators": indicators,
        "risk_score": score,
        "risk_tier": tier,
        "scoring_rationale": rationale,
    }