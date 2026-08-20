import re
from datetime import datetime
from graph.state import ReviewState, AgentReport
from memory.vector_store import vector_store
from logging_utils.logger import StructuredLogger, calculate_cost


def run(state: ReviewState) -> dict:
    """Ethics/Plagiarism Flagging Agent: Scans for plagiarism, IRB/consent statements, and dual-use risks."""
    agent_name = "Ethics/Plagiarism Flagging Agent"
    structured = state.get("paper_structured", {})
    novelty = state.get("novelty_report", {})
    raw_text = state.get("paper_raw_text", "").lower()

    StructuredLogger.log(agent_name, "start_ethics_check", {"has_novelty": bool(novelty)})

    flags = []
    strengths = []
    weaknesses = []

    # IRB & Human Subjects Consent check
    if any(k in raw_text for k in ["human subject", "user study", "participants", "survey", "interviews"]):
        if any(k in raw_text for k in ["irb", "institutional review board", "ethical approval", "informed consent"]):
            strengths.append("Human subjects study includes explicit IRB / ethical approval disclosure.")
        else:
            weaknesses.append("User study / human subjects mentioned without explicit IRB or informed consent statement.")
            flags.append("FLAG: High Risk - Missing IRB / Ethics statement for human study.")

    # Dual-use risk check
    if any(k in raw_text for k in ["dual-use", "bioweapon", "surveillance", "exfiltrate", "autonomous weapon"]):
        flags.append("FLAG: High Risk - Potential dual-use or safety hazard detected.")

    # Data privacy & disclosure check
    if "conflict of interest" in raw_text or "competing interest" in raw_text:
        strengths.append("Contains explicit Conflict of Interest statement.")
    else:
        weaknesses.append("Missing explicit Conflict of Interest / Funding disclosure.")

    # Plagiarism / overlap check against vector store
    similarity_hits = vector_store.query("related_work", raw_text[:500], n_results=2)
    if similarity_hits and any(h.get("score", 1.0) < 0.15 for h in similarity_hits):
        flags.append("FLAG: High Risk - High verbatim text overlap with existing literature corpus.")

    # Veto check
    is_high_risk = any("High Risk" in f for f in flags)
    score = 3 if is_high_risk else (7 if len(flags) > 0 else 9)
    rec = "reject" if is_high_risk else ("minor_revision" if len(flags) > 0 else "accept")

    report: AgentReport = {
        "agent_name": agent_name,
        "score": score,
        "confidence": "high",
        "strengths": strengths if strengths else ["No major plagiarism or ethics violations found."],
        "weaknesses": weaknesses if weaknesses else ["Ethics disclosures are complete."],
        "flags": flags,
        "recommendation": rec,
        "raw_notes": f"Scanned ethics, IRB, dual-use, COI, and text similarity. High-risk flags: {is_high_risk}."
    }

    prompt_tokens = 550
    comp_tokens = 220
    cost = calculate_cost(prompt_tokens, comp_tokens)

    trace_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "message": f"Ethics review complete. Score: {score}/10. High-risk veto triggered: {is_high_risk}."
    }

    token_entry = {
        "agent": agent_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": comp_tokens,
        "cost_usd": cost
    }

    StructuredLogger.log(agent_name, "finish_ethics_check", {"score": score, "cost": cost, "is_high_risk": is_high_risk})

    return {
        "ethics_report": report,
        "agent_trace": [trace_entry],
        "token_usage": [token_entry]
    }
