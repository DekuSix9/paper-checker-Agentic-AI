from langgraph.graph import StateGraph, START, END
from graph.state import ReviewState
from memory.checkpointer import get_sqlite_checkpointer
from agents import (
    run_ingestor,
    run_novelty,
    run_methodology,
    run_stats_rigor,
    run_writing_quality,
    run_ethics,
    run_ai_detector,
    run_area_chair,
    finalize_area_chair
)


def build_graph():
    """Construct and compile the multi-agent paper review LangGraph."""
    g = StateGraph(ReviewState)

    # Add agent nodes
    g.add_node("ingestor", run_ingestor)
    g.add_node("novelty", run_novelty)
    g.add_node("methodology", run_methodology)
    g.add_node("stats_rigor", run_stats_rigor)
    g.add_node("writing_quality", run_writing_quality)
    g.add_node("ethics", run_ethics)
    g.add_node("ai_detector", run_ai_detector)
    g.add_node("area_chair", run_area_chair)
    g.add_node("finalize", finalize_area_chair)

    # Fan-out from Ingestor
    g.add_edge(START, "ingestor")
    for node in ["novelty", "methodology", "stats_rigor", "writing_quality", "ai_detector"]:
        g.add_edge("ingestor", node)

    # Ethics dependency on Novelty Checker (retrieved sources)
    g.add_edge("novelty", "ethics")

    # Fan-in to Area Chair supervisor
    for node in ["methodology", "stats_rigor", "writing_quality", "ethics", "ai_detector"]:
        g.add_edge(node, "area_chair")

    # Area Chair to Human-in-the-Loop gate before finalize
    g.add_edge("area_chair", "finalize")
    g.add_edge("finalize", END)

    # Attach SqliteSaver checkpointer and interrupt before finalize
    checkpointer = get_sqlite_checkpointer()
    if checkpointer:
        return g.compile(checkpointer=checkpointer, interrupt_before=["finalize"])
    return g.compile(interrupt_before=["finalize"])
