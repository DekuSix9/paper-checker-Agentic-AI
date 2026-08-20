import streamlit as st


def render_trace_view(state: dict):
    st.subheader("🔍 Live Agent Execution Trace")
    
    traces = state.get("agent_trace", [])
    if not traces:
        st.info("No active agent execution trace. Start a review to view live agent logs.")
        return

    st.markdown(f"**Total Trace Entries**: {len(traces)}")
    
    for idx, entry in enumerate(traces):
        agent = entry.get("agent", "Agent")
        status = entry.get("status", "info")
        msg = entry.get("message", "")
        ts = entry.get("timestamp", "")
        
        status_label = f"[{ts}] {agent}: {status.upper()}"
        with st.status(status_label, expanded=(idx == len(traces)-1), state="complete" if status == "success" else "running"):
            st.write(msg)
            if "details" in entry:
                st.json(entry["details"])
