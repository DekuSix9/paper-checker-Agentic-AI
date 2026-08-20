from datetime import datetime
from typing import Optional, Dict, Any
from graph.state import ReviewState, AgentReport
from logging_utils.logger import StructuredLogger, calculate_cost


def default_report(name: str) -> AgentReport:
    return {
        "agent_name": name,
        "score": 5,
        "confidence": "medium",
        "strengths": ["Review completed with default settings."],
        "weaknesses": ["Agent output incomplete or errored."],
        "flags": ["FLAG: Review Incomplete"],
        "recommendation": "minor_revision",
        "raw_notes": "Degraded default report used."
    }


def run(state: ReviewState) -> dict:
    """Area Chair / Supervisor Agent: Aggregates specialist reviews, applies weighted rubric & ethics veto, drafts meta-review."""
    agent_name = "Area Chair (Supervisor)"
    StructuredLogger.log(agent_name, "start_area_chair_synthesis", {})

    # 1. Fetch & Validate all 6 reports
    novelty = state.get("novelty_report") or default_report("Novelty Checker")
    methodology = state.get("methodology_report") or default_report("Methodology Reviewer")
    stats = state.get("stats_report") or default_report("Statistical Rigor Checker")
    writing = state.get("writing_report") or default_report("Writing Quality Reviewer")
    ethics = state.get("ethics_report") or default_report("Ethics/Plagiarism Flagging Agent")
    ai_detect = state.get("ai_detection_report") or default_report("AI Content & Sentence Detection Agent")

    # 2. Check Ethics / AI Veto
    ethics_flags = ethics.get("flags", [])
    ai_flags = ai_detect.get("flags", [])
    has_ethics_veto = any("High Risk" in f for f in ethics_flags)
    has_ai_veto = any("High AI Content" in f for f in ai_flags)

    # 3. Calculate Weighted Score
    # Methodology 25%, Novelty 20%, Stats 20%, Writing 10%, Ethics 15%, AI Detect 10%
    w_method = methodology.get("score", 5) * 0.25
    w_novelty = novelty.get("score", 5) * 0.20
    w_stats = stats.get("score", 5) * 0.20
    w_writing = writing.get("score", 5) * 0.10
    w_ethics = ethics.get("score", 5) * 0.15
    w_ai_detect = ai_detect.get("score", 5) * 0.10

    weighted_score = round(w_method + w_novelty + w_stats + w_writing + w_ethics + w_ai_detect, 2)

    # Determine recommendation based on score and veto
    if has_ethics_veto:
        tentative_decision = "reject"
        decision_rationale = "Rejected due to Ethics / Plagiarism Veto (High Risk flag detected)."
    elif has_ai_veto and weighted_score < 6.5:
        tentative_decision = "reject"
        decision_rationale = "Rejected due to high concentration of uncredited AI-generated sentences."
    elif weighted_score >= 7.5:
        tentative_decision = "accept"
        decision_rationale = f"Strong overall paper score of {weighted_score}/10 with solid methodology and novelty."
    elif weighted_score >= 6.0:
        tentative_decision = "minor_revision"
        decision_rationale = f"Moderate paper score of {weighted_score}/10. Recommending minor revisions to address stats/writing."
    elif weighted_score >= 4.5:
        tentative_decision = "major_revision"
        decision_rationale = f"Paper score of {weighted_score}/10 requires significant methodological or statistical revisions."
    else:
        tentative_decision = "reject"
        decision_rationale = f"Overall weighted score ({weighted_score}/10) is below conference acceptance threshold."

    # 4. Synthesize Meta-Review
    all_strengths = methodology.get("strengths", []) + novelty.get("strengths", []) + ai_detect.get("strengths", [])
    all_weaknesses = methodology.get("weaknesses", []) + stats.get("weaknesses", []) + ethics.get("weaknesses", []) + ai_detect.get("weaknesses", [])
    
    meta_review = (
        f"**Meta-Review Summary (Area Chair)**\n\n"
        f"**Overall Weighted Score**: {weighted_score} / 10\n"
        f"**Tentative Decision**: {tentative_decision.upper()}\n\n"
        f"**Key Strengths**:\n" + "\n".join([f"- {s}" for s in all_strengths[:4]]) + "\n\n"
        f"**Main Concerns & Flags**:\n" + "\n".join([f"- {w}" for w in all_weaknesses[:4]]) + "\n\n"
        f"**Synthesis**: {decision_rationale} The committee appreciated the novelty ({novelty.get('score')}/10) "
        f"and methodology ({methodology.get('score')}/10). Statistical rigor was scored at {stats.get('score')}/10, "
        f"and writing authenticity (AI Sentence Detection) was scored at {ai_detect.get('score')}/10. "
        f"This draft decision is now paused for Human-in-the-Loop review."
    )

    trace_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "message": f"Aggregated all 6 specialist reviews (including AI Sentence Detection). Calculated weighted score: {weighted_score}/10. Drafted meta-review, pausing at HITL gate."
    }

    StructuredLogger.log(agent_name, "finish_area_chair_synthesis", {
        "weighted_score": weighted_score,
        "tentative_decision": tentative_decision,
        "has_ethics_veto": has_ethics_veto
    })

    return {
        "meta_review": meta_review,
        "final_decision": "pending",
        "agent_trace": [trace_entry]
    }


def finalize(state: ReviewState) -> dict:
    """Finalize node: Called after Human-in-the-Loop approval/edit to lock final decision."""
    agent_name = "Area Chair (Supervisor)"
    
    human_approved = state.get("human_approved", False)
    human_feedback = state.get("human_feedback")
    current_decision = state.get("final_decision", "pending")
    meta_review = state.get("meta_review", "")

    StructuredLogger.log(agent_name, "finalize_decision", {
        "human_approved": human_approved,
        "human_feedback": human_feedback
    })

    if human_approved:
        if current_decision == "pending" or not current_decision:
            # Infer decision from meta_review text if still pending
            if "ACCEPT" in meta_review.upper():
                final_dec = "accept"
            elif "REJECT" in meta_review.upper():
                final_dec = "reject"
            elif "MINOR" in meta_review.upper():
                final_dec = "minor_revision"
            else:
                final_dec = "accept"
        else:
            final_dec = current_decision
    else:
        final_dec = "reject" if not current_decision or current_decision == "pending" else current_decision

    trace_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "message": f"Human-in-the-Loop review completed. Final decision committed: '{final_dec.upper()}'."
    }

    return {
        "final_decision": final_dec,
        "agent_trace": [trace_entry]
    }
