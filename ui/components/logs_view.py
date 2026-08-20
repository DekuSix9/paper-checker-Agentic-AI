import streamlit as st
from logging_utils.logger import StructuredLogger


def render_logs_view(state: dict):
    st.subheader("📋 Structured Execution Logs & Filterable Errors")
    
    col1, col2 = st.columns(2)
    with col1:
        level_filter = st.selectbox("Filter by Log Level", ["ALL", "INFO", "WARNING", "ERROR"], index=0)
    with col2:
        agent_filter = st.selectbox("Filter by Agent", [
            "ALL",
            "Paper Ingestor",
            "Novelty Checker",
            "Methodology Reviewer",
            "Statistical Rigor Checker",
            "Writing Quality Reviewer",
            "Ethics/Plagiarism Flagging Agent",
            "Area Chair (Supervisor)"
        ], index=0)

    logs = StructuredLogger.get_logs(level_filter=level_filter, agent_filter=agent_filter)
    
    # State-level errors list
    state_errors = state.get("errors", [])
    if state_errors:
        st.error(f"⚠️ **State Errors Detected ({len(state_errors)})**:")
        for err in state_errors:
            st.write(f"- **{err.get('agent')}**: {err.get('error')}")
        st.divider()

    st.markdown(f"Showing **{len(logs)}** log entries from `logs/execution.json`:")
    st.json(logs)
