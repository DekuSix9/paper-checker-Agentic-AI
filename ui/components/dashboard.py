import streamlit as st


def render_dashboard(state: dict):
    st.subheader("📊 Executive Committee Dashboard")
    
    if not state or not state.get("paper_structured"):
        st.info("💡 No review in progress. Upload a PDF paper from the sidebar and click **Start Review**.")
        return

    structured = state.get("paper_structured", {})
    title = structured.get("title", "Untitled Paper")
    
    st.markdown(f"### 📄 **Title**: {title}")
    
    # Progress Calculation across 8 agents
    agents = [
        ("Paper Ingestor", "paper_raw_text"),
        ("Novelty Checker", "novelty_report"),
        ("Methodology Reviewer", "methodology_report"),
        ("Statistical Rigor Checker", "stats_report"),
        ("Writing Quality Reviewer", "writing_report"),
        ("Ethics/Plagiarism Flagging Agent", "ethics_report"),
        ("AI Content & Sentence Detection Agent", "ai_detection_report"),
        ("Area Chair (Supervisor)", "meta_review")
    ]
    
    completed_count = sum(1 for _, key in agents if state.get(key) is not None)
    progress_val = completed_count / len(agents)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.progress(progress_val, text=f"Review Progress: {completed_count}/{len(agents)} Specialist Agents Completed")
    with col2:
        decision = state.get("final_decision", "pending").upper()
        if decision == "ACCEPT":
            st.success(f"🟢 Decision: **{decision}**")
        elif decision == "REJECT":
            st.error(f"🔴 Decision: **{decision}**")
        elif decision in ["MINOR_REVISION", "MAJOR_REVISION"]:
            st.warning(f"🟡 Decision: **{decision}**")
        else:
            st.info(f"⏳ Decision: **{decision}**")
    with col3:
        trace_len = len(state.get("agent_trace", []))
        st.metric("Agent Trace Steps", trace_len)

    st.divider()
    st.markdown("#### 🤖 Specialist Agent Committee Status")
    
    # Agent Status Cards Grid
    grid_cols = st.columns(3)
    reports = {
        "Novelty Checker": state.get("novelty_report"),
        "Methodology Reviewer": state.get("methodology_report"),
        "Statistical Rigor Checker": state.get("stats_report"),
        "Writing Quality Reviewer": state.get("writing_report"),
        "Ethics/Plagiarism Flagging Agent": state.get("ethics_report"),
        "AI Content & Sentence Detection Agent": state.get("ai_detection_report"),
        "Area Chair (Supervisor)": state.get("meta_review")
    }

    for idx, (agent_name, report) in enumerate(reports.items()):
        with grid_cols[idx % 3]:
            if report:
                if isinstance(report, dict):
                    score = report.get("score", "N/A")
                    rec = report.get("recommendation", "N/A").upper()
                    st.markdown(f"""
                    <div style="border:1px solid #4A5568; padding:12px; border-radius:8px; margin-bottom:12px; background-color:#1A202C;">
                        <h5 style="margin:0; color:#63B3ED;">{agent_name}</h5>
                        <p style="margin:4px 0;">Score: <strong>{score}/10</strong></p>
                        <p style="margin:4px 0;">Rec: <strong>{rec}</strong></p>
                        <p style="margin:0; font-size:12px; color:#A0AEC0;">Status: ✅ Completed</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="border:1px solid #4A5568; padding:12px; border-radius:8px; margin-bottom:12px; background-color:#1A202C;">
                        <h5 style="margin:0; color:#63B3ED;">{agent_name}</h5>
                        <p style="margin:4px 0;">Meta-Review Drafted</p>
                        <p style="margin:0; font-size:12px; color:#A0AEC0;">Status: ⏳ Paused at HITL Gate</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="border:1px solid #2D3748; padding:12px; border-radius:8px; margin-bottom:12px; background-color:#2D3748;">
                    <h5 style="margin:0; color:#A0AEC0;">{agent_name}</h5>
                    <p style="margin:4px 0; color:#718096;">Waiting for graph edge...</p>
                    <p style="margin:0; font-size:12px; color:#718096;">Status: ⏸️ Idle</p>
                </div>
                """, unsafe_allow_html=True)
