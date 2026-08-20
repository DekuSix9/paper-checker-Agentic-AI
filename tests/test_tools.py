import os
from tools.pdf_tools import parse_structured_sections
from tools.stats_tools import extract_statistical_claims, run_statistical_checks
from tools.search_tools import search_related_papers
from tools.ai_detect_tools import analyze_sentence_ai_content


def test_parse_structured_sections():
    sample_text = """
    Abstract
    This is a novel research paper on multi-agent AI systems.
    
    1. Introduction
    Multi-agent systems have evolved rapidly.
    
    2. Related Work
    Previous research focused on single agent models.
    
    3. Methodology
    We implement a fan-out graph with p < 0.01 and n = 25.
    
    4. Results
    The accuracy reached 94.2% with Cohen's d = 0.85.
    
    5. Conclusion
    Our findings validate multi-agent review architecture.
    """
    structured = parse_structured_sections(sample_text)
    assert structured["title"] != ""
    assert "Abstract" in sample_text
    assert structured["sections"]["method"] != ""


def test_extract_statistical_claims():
    sample_text = "The model achieved p = 0.005 with n = 20 and Cohen's d = 0.95. standard deviation is ± 1.2."
    stats = extract_statistical_claims(sample_text)
    assert len(stats["p_values"]) > 0
    assert 20 in stats["sample_sizes"]
    assert stats["has_error_bars"] is True
    
    flags = run_statistical_checks(stats)
    assert any("Small sample size" in f for f in flags)


def test_search_related_papers():
    results = search_related_papers("multi agent paper review", max_results=2)
    assert len(results) >= 1
    assert "title" in results[0]


def test_analyze_sentence_ai_content():
    sample_llm_text = (
        "It is worth noting that our framework serves as a testament to the power of multi-agent collaboration. "
        "Furthermore, we delve into the rich landscape of stateful graph graphs, which plays a pivotal role in AI research. "
        "In conclusion, this paradigm shift underscores the paramount importance of automated paper review systems."
    )
    res = analyze_sentence_ai_content(sample_llm_text)
    assert res["total_sentences"] == 3
    assert res["ai_percentage"] > 50.0
    assert len(res["flagged_sentences"]) >= 2
    assert "sentence_details" in res

