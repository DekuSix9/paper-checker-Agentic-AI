import streamlit as st


MERMAID_DIAGRAM = """
```mermaid
graph TD
    START([START]) --> ingestor[Paper Ingestor]
    ingestor --> novelty[Novelty Checker]
    ingestor --> methodology[Methodology Reviewer]
    ingestor --> stats_rigor[Statistical Rigor Checker]
    ingestor --> writing_quality[Writing Quality Reviewer]
    ingestor --> ai_detector[AI Sentence Detector]
    
    novelty --> ethics[Ethics & Plagiarism Flagging]
    
    methodology --> area_chair[Area Chair Supervisor]
    stats_rigor --> area_chair
    writing_quality --> area_chair
    ethics --> area_chair
    ai_detector --> area_chair
    
    area_chair --> HITL{Human-in-the-Loop Gate}
    HITL -- Resume / Approve --> finalize[Finalize Decision]
    finalize --> END([END])

    classDef agent fill:#2B6CB0,stroke:#3182CE,stroke-width:2px,color:#fff;
    classDef supervisor fill:#D69E2E,stroke:#B7791F,stroke-width:2px,color:#fff;
    classDef gate fill:#E53E3E,stroke:#C53030,stroke-width:2px,color:#fff;
    
    class ingestor,novelty,methodology,stats_rigor,writing_quality,ethics,ai_detector agent;
    class area_chair,finalize supervisor;
    class HITL gate;
```
"""


def render_graph_view(app=None):
    st.subheader("🕸️ LangGraph Multi-Agent Execution Topology")
    st.markdown("This graph models the conference paper review committee workflow. Agents run in parallel fan-out, fan-in to Area Chair, and pause at the Human-in-the-Loop approval gate.")

    try:
        if app and hasattr(app, "get_graph"):
            mermaid_str = f"```mermaid\n{app.get_graph().draw_mermaid()}\n```"
            st.markdown(mermaid_str)
        else:
            st.markdown(MERMAID_DIAGRAM)
    except Exception as e:
        st.markdown(MERMAID_DIAGRAM)
