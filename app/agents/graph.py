# app/agents/graph.py
from langgraph.graph import END, StateGraph
from app.agents.compliance_retrieval import compliance_retrieval_node
from app.agents.report_generation import report_generation_node
from app.agents.state import ComplianceInvestigationState
from app.agents.transaction_analysis import transaction_analysis_node
from app.core.logger import get_logger

logger = get_logger(__name__)

def route_based_on_risk(state: ComplianceInvestigationState) -> str:
    risk_tier = state.get("risk_tier", "LOW")
    indicators = state.get("suspicious_indicators", [])
    
    if risk_tier == "LOW" or not indicators:
        logger.info(f"Routing Matrix Decision: Tier is {risk_tier}. Short-circuiting directly to reporting.")
        return "skip_to_report"
        
    logger.info(f"Routing Matrix Decision: Tier is {risk_tier}. Routing to full Hybrid RAG track.")
    return "execute_rag"

def build_graph():
    builder = StateGraph(ComplianceInvestigationState)
    
    builder.add_node("transaction_analysis", transaction_analysis_node)
    builder.add_node("compliance_retrieval", compliance_retrieval_node)
    builder.add_node("report_generation", report_generation_node)
    
    builder.set_entry_point("transaction_analysis")
    
    builder.add_conditional_edges(
        "transaction_analysis",
        route_based_on_risk,
        {
            "execute_rag": "compliance_retrieval",
            "skip_to_report": "report_generation"
        }
    )
    
    builder.add_edge("compliance_retrieval", "report_generation")
    builder.add_edge("report_generation", END)
    
    graph = builder.compile()
    logger.info("LangGraph Core Compliance pipeline successfully compiled.")
    return graph

compliance_graph = build_graph()