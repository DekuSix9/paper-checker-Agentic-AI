import re
import math
from typing import Dict, Any, List


LLM_PHRASE_MARKERS = [
    "delve", "delving", "tapestry", "testament", "pivotal role", "beacon",
    "game-changer", "game changer", "underscores", "seamlessly", "overarching",
    "it is worth noting", "it is important to note", "it is essential to",
    "plays a crucial role", "plays a vital role", "paramount importance",
    "rich landscape", "fostering", "synergy", "paradigm shift", "in summary,",
    "furthermore,", "moreover,", "additionally,", "in conclusion,", "sheds light on",
    "multifaceted", "holistic approach", "meticulously", "groundbreaking",
    "subsequent analysis", "transformative impact", "serves as a"
]


def analyze_sentence_ai_content(text: str) -> Dict[str, Any]:
    """
    Sentence-level AI content detection tool.
    Splits text into sentences, evaluates perplexity/burstiness proxies and LLM stylistic markers,
    and classifies each sentence as AI-generated vs human-written.
    """
    if not text or not text.strip():
        return {
            "total_sentences": 0,
            "ai_sentence_count": 0,
            "ai_percentage": 0.0,
            "burstiness_score": 0.0,
            "authenticity_score": 10,
            "flagged_sentences": [],
            "sentence_details": []
        }

    # Split into clean sentences
    raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 10]
    if not raw_sentences:
        raw_sentences = [text.strip()]

    sentence_details = []
    ai_sentence_count = 0
    word_counts = []

    for idx, sent in enumerate(raw_sentences, start=1):
        words = re.findall(r'\b\w+\b', sent.lower())
        w_count = len(words)
        word_counts.append(w_count)

        # 1. Match LLM Phrase Markers
        matched_markers = [marker for marker in LLM_PHRASE_MARKERS if marker in sent.lower()]

        # 2. Heuristic probability scoring
        score_points = 0.0

        # Phrase marker score
        if matched_markers:
            score_points += len(matched_markers) * 0.35

        # Transition word density check at start of sentence
        if any(sent.lower().startswith(prefix) for prefix in ["furthermore,", "moreover,", "additionally,", "in summary,", "in conclusion,"]):
            score_points += 0.20

        # Uniform sentence length heuristic (LLMs often produce 18-28 word sentences consistently)
        if 18 <= w_count <= 28:
            score_points += 0.15

        # Low vocabulary variance proxy (repeated common academic jargon)
        unique_ratio = len(set(words)) / max(w_count, 1)
        if unique_ratio < 0.65 and w_count > 12:
            score_points += 0.20

        # Cap probability between 0.05 and 0.98
        ai_probability = round(min(max(score_points, 0.05), 0.98), 2)

        if ai_probability >= 0.60:
            classification = "AI-Generated"
            risk = "high"
            ai_sentence_count += 1
        elif ai_probability >= 0.40:
            classification = "Likely AI"
            risk = "medium"
            ai_sentence_count += 0.5
        else:
            classification = "Human-Written"
            risk = "low"

        reason_parts = []
        if matched_markers:
            reason_parts.append(f"Detected LLM markers: {', '.join(matched_markers[:3])}")
        if 18 <= w_count <= 28:
            reason_parts.append(f"Uniform LLM sentence length ({w_count} words)")
        if unique_ratio < 0.65:
            reason_parts.append("Repetitive structural syntax")

        reason = "; ".join(reason_parts) if reason_parts else "Natural sentence variability"

        detail = {
            "sentence_index": idx,
            "sentence_text": sent if len(sent) <= 120 else sent[:117] + "...",
            "ai_probability": ai_probability,
            "classification": classification,
            "risk_level": risk,
            "reason": reason
        }
        sentence_details.append(detail)

    total_sentences = len(raw_sentences)
    ai_percentage = round((ai_sentence_count / total_sentences) * 100, 1) if total_sentences > 0 else 0.0

    # Calculate Burstiness (Standard Deviation of sentence word counts)
    if len(word_counts) > 1:
        mean_w = sum(word_counts) / len(word_counts)
        variance = sum((x - mean_w) ** 2 for x in word_counts) / len(word_counts)
        burstiness_score = round(math.sqrt(variance), 2)
    else:
        burstiness_score = 0.0

    # Authenticity Score (1-10)
    # Higher burstiness & lower AI percentage -> Higher authenticity
    if ai_percentage < 10:
        auth_score = 10
    elif ai_percentage < 25:
        auth_score = 8
    elif ai_percentage < 40:
        auth_score = 6
    elif ai_percentage < 60:
        auth_score = 4
    else:
        auth_score = 2

    flagged_sentences = [s for s in sentence_details if s["ai_probability"] >= 0.50]

    return {
        "total_sentences": total_sentences,
        "ai_sentence_count": int(ai_sentence_count),
        "ai_percentage": ai_percentage,
        "burstiness_score": burstiness_score,
        "authenticity_score": auth_score,
        "flagged_sentences": flagged_sentences,
        "sentence_details": sentence_details
    }
