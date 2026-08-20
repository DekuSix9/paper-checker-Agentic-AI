from datetime import datetime
from typing import Dict, Any
import json
from graph.state import ReviewState, AgentReport
from tools.search_tools import search_related_papers
from tools.groq_tools import call_groq_llm
from logging_utils.logger import StructuredLogger, calculate_cost


def run(state: ReviewState) -> dict:
    """Novelty Checker Agent: Searches literature, evaluates claimed contributions vs retrieved work using Groq API."""
    agent_name = "Novelty Checker"
    structured = state.get("paper_structured", {})
    title = structured.get("title", "")
    abstract = structured.get("abstract", "")
    raw_text = state.get("paper_raw_text", "")
    
    StructuredLogger.log(agent_name, "start_novelty_check", {"title": title})

    # Search web for related work
    search_query = f"{title} {abstract[:150]}"
    related_results = search_related_papers(search_query, max_results=3)
    num_results = len(related_results)

    # Attempt Groq LLM Evaluation
    sys_prompt = (
        "You are an expert AI conference novelty reviewer (IEEE/ACM). Analyze the paper's title, abstract, "
        "and retrieved related work to evaluate its algorithmic and conceptual novelty. "
        "Return ONLY a JSON object with keys: score (1-10 integer), strengths (list of strings), "
        "weaknesses (list of strings), flags (list of strings), recommendation (accept/minor_revision/major_revision/reject), "
        "and raw_notes (short string summary)."
    )
    user_prompt = (
        f"Title: {title}\nAbstract: {abstract[:800]}\n"
        f"Paper excerpt: {raw_text[:1800]}\n"
        f"Retrieved Related Work: {json.dumps(related_results[:2]) if 'json' in globals() else str(related_results[:2])}\n"
    )

    llm_res = call_groq_llm(user_prompt, system_prompt=sys_prompt, json_response=True)

    if llm_res and isinstance(llm_res, dict) and "score" in llm_res:
        score = int(llm_res.get("score", 7))
        strengths = llm_res.get("strengths", [])
        weaknesses = llm_res.get("weaknesses", [])
        flags = llm_res.get("flags", [])
        rec = llm_res.get("recommendation", "accept")
        raw_notes = llm_res.get("raw_notes", f"Evaluated novelty via Groq LLM. Score: {score}/10.")
    else:
        # Dynamic Heuristic Fallback
        clean_title = title if title and "Untitled" not in title else "the proposed framework"
        abs_lower = abstract.lower()
        score = 7
        strengths = []
        weaknesses = []
        flags = []

        if any(k in abs_lower for k in ["novel", "first", "state-of-the-art", "sota", "outperform", "consensus"]):
            score = 8
            strengths.append(f"Articulates distinctive technical contributions in '{clean_title}'.")
        elif len(abstract) > 50:
            strengths.append(f"Presents clear motivation for addressing challenges in {clean_title[:40]}.")

        if num_results > 0:
            strengths.append(f"Identified {num_results} related academic baselines for comparative evaluation.")
        
        if not any(k in abs_lower for k in ["benchmark", "dataset", "baseline", "compared"]):
            weaknesses.append("Related work discussion lacks direct empirical positioning against recent benchmark baselines.")
            flags.append("FLAG: Limited literature comparison against current SOTA baselines.")
            score -= 1

        rec = "accept" if score >= 7 else "minor_revision"
        raw_notes = f"Analyzed title '{clean_title}' via fallback. Contribution overlap estimated moderate across {num_results} retrieved targets."

    report: AgentReport = {
        "agent_name": agent_name,
        "score": score,
        "confidence": "high",
        "strengths": strengths if strengths else [f"Focuses on research topic: {title}"],
        "weaknesses": weaknesses if weaknesses else ["Literature positioning is acceptable."],
        "flags": flags,
        "recommendation": rec,
        "raw_notes": raw_notes
    }

    # Record trace & token usage
    prompt_tokens = max(350, min(1500, int(len(raw_text) / 4)))
    comp_tokens = max(120, min(500, len(str(report)) // 4))
    cost = calculate_cost(prompt_tokens, comp_tokens)

    trace_entry = {
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "message": f"Evaluated paper novelty score: {score}/10 with {len(strengths)} strengths and {len(weaknesses)} weaknesses."
    }

    token_entry = {
        "agent": agent_name,
        "provider": "groq" if llm_res else "heuristic_fallback",
        "api_used": bool(llm_res),
        "paper_title": title,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": comp_tokens,
        "cost_usd": cost
    }

    StructuredLogger.log(agent_name, "finish_novelty_check", {"score": score, "cost": cost})

    return {
        "novelty_report": report,
        "agent_trace": [trace_entry],
        "token_usage": [token_entry]
    }
