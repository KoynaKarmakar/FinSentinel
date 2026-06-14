from fastapi import APIRouter, HTTPException

from app.core.logger import get_logger
from app.store.case_store import get_case

logger = get_logger(__name__)
router = APIRouter()


@router.get("/report/{case_id}")
async def get_report(case_id: str):
    report = get_case(case_id)
    if not report:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return report
