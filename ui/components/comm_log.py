import streamlit as st


def render_comm_log(state: dict):
    st.subheader("💬 Agent-to-Agent Communication & State Log")
    
    if not state:
        st.info("No state data available.")
        return

    st.markdown("All 8 agents communicate exclusively by reading and writing to the shared `ReviewState` object passed along LangGraph edges.")
    
    reports = [
        ("Novelty Checker", "novelty_report", ["paper_structured (title, abstract, related_work)"]),
        ("Methodology Reviewer", "methodology_report", ["paper_structured (method, results)", "paper_chunks (RAG)"]),
        ("Statistical Rigor Checker", "stats_report", ["paper_raw_text"]),
        ("Writing Quality Reviewer", "writing_report", ["paper_raw_text"]),
        ("Ethics/Plagiarism Flagging Agent", "ethics_report", ["paper_structured", "novelty_report (retrieved sources)"]),
        ("AI Content & Sentence Detection Agent", "ai_detection_report", ["paper_raw_text"]),
        ("Area Chair (Supervisor)", "meta_review", ["novelty_report", "methodology_report", "stats_report", "writing_report", "ethics_report", "ai_detection_report"])
    ]

    for agent_name, state_key, read_inputs in reports:
        val = state.get(state_key)
        with st.expander(f"📥 State Delta: {agent_name} -> `{state_key}`", expanded=bool(val)):
            st.markdown(f"**Read Inputs**: {', '.join(read_inputs)}")
            st.markdown(f"**Output State Key Written**: `{state_key}`")
            if val:
                st.json(val)
            else:
                st.caption("State key not written yet.")
