from fastapi import APIRouter, HTTPException

from app.agents.graph import compliance_graph
from app.agents.state import ComplianceInvestigationState
from app.api.models.transaction import TransactionInput
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/investigate")
async def investigate_transaction(transaction: TransactionInput):
    initial_state: ComplianceInvestigationState = {
        "transaction": transaction.model_dump(),
        "suspicious_indicators": [],
        "risk_score": 0.0,
        "risk_tier": "LOW",
        "scoring_rationale": "",
        "policy_citations": [],
        "final_report": {},
    }

    try:
        result = compliance_graph.invoke(initial_state)
        case_id = result["final_report"]["case_id"]
        logger.info(f"Investigation complete: case_id={case_id}")
        return {"case_id": case_id}
    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
