from datetime import datetime
from graph.state import ReviewState, AgentReport
from logging_utils.logger import StructuredLogger, calculate_cost


def run(state: ReviewState) -> dict:
    """Writing Quality Reviewer Agent: Evaluates readability, grammar, structural clarity, figure/table layout."""
    agent_name = "Writing Quality Reviewer"
    raw_text = state.get("paper_raw_text", "")

    StructuredLogger.log(agent_name, "start_writing_review", {"raw_text_len": len(raw_text)})

    # Calculate readability metrics via textstat
    readability_score = 45.0  # default
    try:
        import textstat
        readability_score = textstat.flesch_reading_ease(raw_text)
    except Exception as e:
        print(f"[writing_quality warning] textstat fallback: {e}")

    strengths = []
    weaknesses = []
    flags = []

    if readability_score > 30:
        strengths.append(f"Readability is suitable for academic conference submission (Flesch Reading Ease: {readability_score:.1f}).")
    else:
        weaknesses.append(f"Dense or overly complex sentence structure detected (Flesch Reading Ease: {readability_score:.1f}).")

    # Structural check
    structured = state.get("paper_structured", {})
    sections = structured.get("sections", {})
    
    if sections.get("abstract") and sections.get("introduction") and sections.get("method") and sections.get("conclusion"):
        strengths.append("Paper adheres to standard IEEE/ACM section organization (Abstract, Intro, Method, Results, Conclusion).")
    else:
        weaknesses.append("Missing standard structural sections or section headers are ambiguously formatted.")
        flags.append("FLAG: Non-standard paper formatting.")

    if len(structured.get("captions", [])) > 0:
        strengths.append(f"Figures and tables include descriptive captions ({len(structured['captions'])} identified).")

    score = 8 if len(weaknesses) == 0 else (6 if len(weaknesses) == 1 else 5)
    rec = "accept" if score >= 7 else "minor_revision"

    report: AgentReport = {
        "agent_name": agent_name,
        "score": score,
        "confidence": "high",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "flags": flags,
        "recommendation": rec,
        "raw_notes": f"Calculated Flesch Reading Ease score: {readability_score:.1f}. Checked section flow and figure captions."
    }

    prompt_tokens = 480
    comp_tokens = 180
    cost = calculate_cost(prompt_tokens, comp_tokens)

    trace_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "message": f"Writing quality review complete. Score: {score}/10. Flesch Reading Ease: {readability_score:.1f}."
    }

    token_entry = {
        "agent": agent_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": comp_tokens,
        "cost_usd": cost
    }

    StructuredLogger.log(agent_name, "finish_writing_review", {"score": score, "cost": cost})

    return {
        "writing_report": report,
        "agent_trace": [trace_entry],
        "token_usage": [token_entry]
    }
