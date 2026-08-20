import os
import sys
import site

# Ensure workspace root and user site-packages are in sys.path
user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.insert(0, user_site)

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from graph.build_graph import build_graph

TEST_PAPER_PATH = os.path.join(os.path.dirname(__file__), "sample_test_paper.txt")


def ensure_test_paper():
    content = """
    Multi-Agent Peer Review Systems for AI Conferences
    
    Abstract
    We present a novel multi-agent review architecture for automated paper evaluation using LangGraph and Streamlit.
    
    1. Introduction
    Peer review is the cornerstone of scientific publication. Our system automates reviewer specialist roles.
    
    2. Related Work
    Prior work relied on single-prompt LLM evaluation without specialized agent roles or statistical validation.
    
    3. Methodology
    We deploy 7 specialized agents: Ingestor, Novelty, Methodology, Stats Rigor, Writing Quality, Ethics, and Area Chair.
    Hyperparameters: batch size = 32, learning rate = 1e-4, optimizer = AdamW. Code is available at github.com/test/repo.
    
    4. Results & Experiments
    Experiments demonstrate p = 0.001 with sample size n = 150 across 5 benchmarks. 95% CI [0.88, 0.94].
    Standard deviation error bars are reported across 10 random seeds.
    
    5. Ethics & Conflict of Interest
    No human subjects were involved. No conflict of interest to declare.
    
    6. Conclusion
    Multi-agent review committee improves review objectivity and depth.
    """
    with open(TEST_PAPER_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def test_graph_end_to_end_smoke():
    ensure_test_paper()
    
    app = build_graph()
    
    initial_state = {
        "paper_path": TEST_PAPER_PATH,
        "paper_raw_text": "",
        "paper_structured": {},
        "novelty_report": None,
        "methodology_report": None,
        "stats_report": None,
        "writing_report": None,
        "ethics_report": None,
        "ai_detection_report": None,
        "meta_review": None,
        "final_decision": None,
        "human_feedback": None,
        "human_approved": False,
        "agent_trace": [],
        "token_usage": [],
        "errors": []
    }
    
    config = {"configurable": {"thread_id": "test_thread_smoke_1"}}
    
    # 1. Execute graph until interrupt gate before finalize
    res = app.invoke(initial_state, config=config)
    
    assert res.get("ai_detection_report") is not None
    assert res.get("meta_review") is not None
    assert res.get("final_decision") == "pending"
    assert len(res.get("agent_trace", [])) >= 7

    # 2. Update state for Human-in-the-Loop resume
    app.update_state(config, {"human_approved": True, "human_feedback": "Approved draft decision."}, as_node="area_chair")
    res_resumed = app.invoke(None, config=config)
    
    assert res_resumed.get("final_decision") in ["accept", "minor_revision", "major_revision", "reject"]
    assert res_resumed.get("final_decision") != "pending"

    # Cleanup
    if os.path.exists(TEST_PAPER_PATH):
        try:
            os.remove(TEST_PAPER_PATH)
        except Exception:
            pass


if __name__ == "__main__":
    test_graph_end_to_end_smoke()
    print("Graph smoke test completed successfully!")
