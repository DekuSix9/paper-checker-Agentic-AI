from datetime import datetime
from graph.state import ReviewState, AgentReport
from tools.ai_detect_tools import analyze_sentence_ai_content
from logging_utils.logger import StructuredLogger, calculate_cost


def run(state: ReviewState) -> dict:
    """AI Content & Sentence Detection Agent: Evaluates sentence-level AI generation probability, LLM markers, and burstiness."""
    agent_name = "AI Content & Sentence Detection Agent"
    raw_text = state.get("paper_raw_text", "")

    StructuredLogger.log(agent_name, "start_ai_detection_review", {"raw_text_len": len(raw_text)})

    analysis = analyze_sentence_ai_content(raw_text)

    total_sentences = analysis["total_sentences"]
    ai_percentage = analysis["ai_percentage"]
    burstiness_score = analysis["burstiness_score"]
    authenticity_score = analysis["authenticity_score"]
    flagged_sentences = analysis["flagged_sentences"]

    strengths = []
    weaknesses = []
    flags = []

    if ai_percentage < 15.0:
        strengths.append(f"High writing authenticity: Only {ai_percentage}% of sentences match synthetic LLM patterns.")
    elif ai_percentage < 30.0:
        strengths.append(f"Moderate sentence naturalness with acceptable stylistic variation (AI content: {ai_percentage}%).")
    else:
        weaknesses.append(f"High concentration of AI-generated phrasing detected ({ai_percentage}% of sentences flagged).")
        flags.append(f"FLAG: High AI Content ({ai_percentage}% of paper sentences exhibit characteristic LLM syntax).")

    if burstiness_score >= 8.0:
        strengths.append(f"Natural sentence length variation across paragraphs (Burstiness score: {burstiness_score}).")
    else:
        weaknesses.append(f"Low sentence burstiness detected (score: {burstiness_score}), indicating uniform synthetic length distribution.")
        flags.append("FLAG: Uniform sentence length distribution characteristic of LLM output.")

    if len(flagged_sentences) > 0:
        weaknesses.append(f"{len(flagged_sentences)} specific sentences flagged for containing uncredited ChatGPT/LLM boilerplate.")

    # Score calculation (1-10)
    score = authenticity_score
    rec = "accept" if score >= 7 else ("minor_revision" if score >= 5 else "reject")

    raw_notes = (
        f"Analyzed {total_sentences} sentences. AI-generated sentence ratio: {ai_percentage}%. "
        f"Sentence burstiness score: {burstiness_score}. "
        f"Flagged sentences count: {len(flagged_sentences)}."
    )

    report: AgentReport = {
        "agent_name": agent_name,
        "score": score,
        "confidence": "high",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "flags": flags,
        "recommendation": rec,
        "raw_notes": raw_notes
    }

    prompt_tokens = 510
    comp_tokens = 210
    cost = calculate_cost(prompt_tokens, comp_tokens)

    trace_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "message": f"Sentence AI analysis complete. Authenticity score: {score}/10. AI sentence ratio: {ai_percentage}% ({len(flagged_sentences)} sentences flagged)."
    }

    token_entry = {
        "agent": agent_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": comp_tokens,
        "cost_usd": cost
    }

    StructuredLogger.log(agent_name, "finish_ai_detection_review", {
        "score": score,
        "ai_percentage": ai_percentage,
        "cost": cost
    })

    return {
        "ai_detection_report": report,
        "agent_trace": [trace_entry],
        "token_usage": [token_entry]
    }
