from datetime import datetime
from graph.state import ReviewState, AgentReport
from tools.stats_tools import extract_statistical_claims, run_statistical_checks
from logging_utils.logger import StructuredLogger, calculate_cost


def run(state: ReviewState) -> dict:
    """Statistical Rigor Checker Agent: Extracts statistical claims and validates statistical best practices."""
    agent_name = "Statistical Rigor Checker"
    raw_text = state.get("paper_raw_text", "")

    StructuredLogger.log(agent_name, "start_stats_check", {"raw_text_len": len(raw_text)})

    # Deterministic statistical extraction
    stats_data = extract_statistical_claims(raw_text)
    flags = run_statistical_checks(stats_data)

    strengths = []
    weaknesses = []

    if stats_data.get("p_values"):
        strengths.append(f"Reports {len(stats_data['p_values'])} explicit p-values for hypothesis testing.")
    if stats_data.get("confidence_intervals"):
        strengths.append(f"Provides confidence intervals for key performance metrics ({len(stats_data['confidence_intervals'])} found).")
    if stats_data.get("has_error_bars"):
        strengths.append("Includes standard deviation/variance error bars in reported tabular or graphical metrics.")

    for f in flags:
        weaknesses.append(f.replace("FLAG: ", ""))

    score = 8 - (len(flags) * 2)
    score = max(3, min(10, score))
    rec = "accept" if score >= 7 else ("minor_revision" if score >= 5 else "major_revision")

    report: AgentReport = {
        "agent_name": agent_name,
        "score": score,
        "confidence": "high",
        "strengths": strengths if strengths else ["Basic metric reporting is present."],
        "weaknesses": weaknesses if weaknesses else ["No major statistical deficiencies identified."],
        "flags": flags,
        "recommendation": rec,
        "raw_notes": f"Regex statistical extraction completed. Extracted p-values: {stats_data['p_values']}, sample sizes: {stats_data['sample_sizes']}. Flags generated: {len(flags)}."
    }

    prompt_tokens = 500
    comp_tokens = 200
    cost = calculate_cost(prompt_tokens, comp_tokens)

    trace_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "message": f"Statistical rigor check complete. Score: {score}/10. Identified {len(flags)} potential statistical flags."
    }

    token_entry = {
        "agent": agent_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": comp_tokens,
        "cost_usd": cost
    }

    StructuredLogger.log(agent_name, "finish_stats_check", {"score": score, "cost": cost})

    return {
        "stats_report": report,
        "agent_trace": [trace_entry],
        "token_usage": [token_entry]
    }
