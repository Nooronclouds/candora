"""LangGraph workflow definition for Candora RAG."""

from langgraph.graph import StateGraph, START, END
from agent.state import RAGState
from agent.nodes import (
    retrieve_context,
    check_sufficiency,
    refine_query,
    detect_conflicts,
    generate_response,
)


def route_after_sufficiency(state: RAGState) -> str:
    """Determine the next node based on the sufficiency check verdict."""
    status = state.get("sufficiency_status", "SUFFICIENT")
    retry_count = state.get("retry_count") or 0
    
    if status == "SUFFICIENT":
        return "generate_response"
    elif status == "INSUFFICIENT":
        if retry_count < 2:
            return "refine_query"
        else:
            return "generate_response"
    elif status == "CONFLICTING":
        return "detect_conflicts"
    
    return "generate_response"


def build_graph():
    """Compile the LangGraph self-correcting RAG workflow."""
    workflow = StateGraph(RAGState)
    
    # Define the nodes
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("check_sufficiency", check_sufficiency)
    workflow.add_node("refine_query", refine_query)
    workflow.add_node("detect_conflicts", detect_conflicts)
    workflow.add_node("generate_response", generate_response)
    
    # Set entry point
    workflow.add_edge(START, "retrieve_context")
    
    # Add transition from retrieve to sufficiency check
    workflow.add_edge("retrieve_context", "check_sufficiency")
    
    # Add conditional routing after sufficiency check
    workflow.add_conditional_edges(
        "check_sufficiency",
        route_after_sufficiency,
        {
            "generate_response": "generate_response",
            "refine_query": "refine_query",
            "detect_conflicts": "detect_conflicts",
        }
    )
    
    # Loop back from refine_query to retrieve_context
    workflow.add_edge("refine_query", "retrieve_context")
    
    # Transition from conflict detection to generation
    workflow.add_edge("detect_conflicts", "generate_response")
    
    # End node transitions
    workflow.add_edge("generate_response", END)
    
    # Compile
    app = workflow.compile()
    return app
