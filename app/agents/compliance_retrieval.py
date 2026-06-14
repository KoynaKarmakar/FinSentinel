# app/agents/compliance_retrieval.py
from app.agents.state import ComplianceInvestigationState
from app.core.logger import get_logger
from app.retrieval.hybrid_retrieve import hybrid_retrieve

logger = get_logger(__name__)

_INDICATOR_QUERIES = {
    "large_single_transfer": "large single cash transfer reporting obligation RBI regulations",
    "high_velocity": "high frequency multiple transactions AML suspicious activity",
    "new_account_large_txn": "new account large transaction KYC enhanced due diligence",
    "cross_border_transfer": "cross border international wire transfer FATF AML compliance",
    "threshold_proximity": "structuring transactions below reporting threshold PMLA section 12",
}

def compliance_retrieval_node(state: ComplianceInvestigationState) -> dict:
    """
    Agent 2: Hybrid RAG Retrieval Engine.
    Queries Qdrant + BM25 and explicitly maps layout hierarchy metadata arrays.
    """
    indicators = state.get("suspicious_indicators", [])

    if not indicators:
        return {"policy_citations": []}

    seen: dict = {}

    for indicator in indicators:
        query = _INDICATOR_QUERIES.get(indicator, indicator.replace("_", " "))
        results = hybrid_retrieve(query, doc_type=None)
        
        for result in results:
            text = result["text"]
            if text not in seen or result["rerank_score"] > seen[text]["relevance_score"]:
                seen[text] = {
                    "text": text,
                    "chunk_text": text, # Keeps legacy support intact for UI views
                    "relevance_score": result["rerank_score"],
                    "source": result.get("source", ""),
                    "doc_type": result.get("doc_type", ""),
                    "page": result.get("page", 0),
                    "indicator": indicator,
                    "chapter": result.get("chapter", "N/A"),
                    "section": result.get("section", "N/A"),
                    "subsection": result.get("subsection", "N/A"),
                }

    citations = sorted(seen.values(), key=lambda x: x["relevance_score"], reverse=True)[:5]
    logger.info(f"Retrieved {len(citations)} unique structured citations for {len(indicators)} indicators")
    return {"policy_citations": citations}