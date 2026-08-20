import streamlit as st
from agents import (
    run_novelty,
    run_methodology,
    run_stats_rigor,
    run_writing_quality,
    run_ethics,
    run_ai_detector,
    run_area_chair
)


def render_hitl_controls(state: dict, app=None, config=None, on_resume_callback=None):
    st.subheader("🛑 Human-in-the-Loop Approval Gate")
    
    if not state or not state.get("meta_review"):
        st.info("Human gate inactive. Execute a paper review to pause at this decision gate.")
        return

    decision = state.get("final_decision", "pending")
    if decision != "pending":
        st.success(f"✅ Human approval completed! Final decision committed: **{decision.upper()}**")

    st.markdown("### 📝 Area Chair Draft Meta-Review")
    meta_text = state.get("meta_review", "")
    
    edited_meta = st.text_area("Edit Draft Meta-Review before committing decision:", value=meta_text, height=200)

    st.divider()
    st.markdown("### 🎛️ Human Decision Actions")

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Approve Decision", type="primary", use_container_width=True):
            if app and config:
                resume_inputs = {
                    "human_approved": True,
                    "meta_review": edited_meta,
                    "final_decision": "accept" if "ACCEPT" in edited_meta.upper() else ("minor_revision" if "MINOR" in edited_meta.upper() else "accept")
                }
                res = app.invoke(resume_inputs, config=config)
                st.session_state["review_state"] = res
                st.success("Decision Approved & Committed!")
                st.rerun()

    with col2:
        if st.button("❌ Reject Paper Outright", use_container_width=True):
            if app and config:
                resume_inputs = {
                    "human_approved": False,
                    "meta_review": edited_meta,
                    "final_decision": "reject"
                }
                res = app.invoke(resume_inputs, config=config)
                st.session_state["review_state"] = res
                st.error("Paper Rejected Outright!")
                st.rerun()

    with col3:
        if st.button("✏️ Save Edited Meta-Review", use_container_width=True):
            state["meta_review"] = edited_meta
            st.session_state["review_state"] = state
            st.info("Saved edited meta-review into state.")

    with col4:
        st.caption("Interrupt Gate Active")

    st.divider()
    st.markdown("### 🔄 Single Agent Retry Control")
    agent_to_retry = st.selectbox("Select Specialist Agent to Re-Invoke:", [
        "Novelty Checker",
        "Methodology Reviewer",
        "Statistical Rigor Checker",
        "Writing Quality Reviewer",
        "Ethics/Plagiarism Flagging Agent",
        "AI Content & Sentence Detection Agent"
    ])

    if st.button("🚀 Re-invoke Selected Agent & Re-aggregate Area Chair"):
        agent_map = {
            "Novelty Checker": run_novelty,
            "Methodology Reviewer": run_methodology,
            "Statistical Rigor Checker": run_stats_rigor,
            "Writing Quality Reviewer": run_writing_quality,
            "Ethics/Plagiarism Flagging Agent": run_ethics,
            "AI Content & Sentence Detection Agent": run_ai_detector
        }
        fn = agent_map[agent_to_retry]
        delta = fn(state)
        state.update(delta)
        # Re-run area chair
        ac_delta = run_area_chair(state)
        state.update(ac_delta)
        st.session_state["review_state"] = state
        st.success(f"Re-invoked {agent_to_retry} and re-aggregated Area Chair meta-review!")
        st.rerun()
