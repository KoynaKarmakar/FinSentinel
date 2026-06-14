from typing import Any, List

from pydantic import BaseModel


class ReportResponse(BaseModel):
    case_id: str
    transaction_summary: str
    risk_score: float
    risk_tier: str
    scoring_rationale: str
    suspicious_patterns: List[str]
    policy_citations: List[Any]
    recommended_action: str
    confidence_level: str
    transaction: dict
    raw_risk_score: float
    raw_risk_tier: str
    raw_indicators: List[str]
    raw_citations: List[Any]
