import operator
from graph.state import ReviewState, AgentReport


def test_agent_report_structure():
    report: AgentReport = {
        "agent_name": "Test Agent",
        "score": 8,
        "confidence": "high",
        "strengths": ["Clear writing"],
        "weaknesses": ["Small dataset"],
        "flags": [],
        "recommendation": "accept",
        "raw_notes": "Test notes"
    }
    assert report["score"] == 8
    assert report["recommendation"] == "accept"
    assert report["confidence"] == "high"


def test_review_state_structure():
    state: ReviewState = {
        "paper_path": "data/sample.pdf",
        "paper_raw_text": "Sample text",
        "paper_structured": {"title": "Sample Paper"},
        "novelty_report": None,
        "methodology_report": None,
        "stats_report": None,
        "writing_report": None,
        "ethics_report": None,
        "ai_detection_report": None,
        "meta_review": None,
        "final_decision": "pending",
        "human_feedback": None,
        "human_approved": False,
        "agent_trace": [],
        "token_usage": [],
        "errors": []
    }
    assert state["paper_path"] == "data/sample.pdf"
    assert state["final_decision"] == "pending"
