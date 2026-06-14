# app/agents/state.py
from typing import List, Dict, Any, TypedDict

class ComplianceInvestigationState(TypedDict):
    """
    Centralized LangGraph State Schema.
    Each field handles top-level assignments reliably across node transitions.
    """
    transaction: dict
    suspicious_indicators: List[str]
    risk_score: float
    risk_tier: str
    scoring_rationale: str
    policy_citations: List[dict]
    final_report: dict