import os
import sys
import uuid
import streamlit as st

# Add workspace root to python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.build_graph import build_graph
from ui.components import (
    render_dashboard,
    render_trace_view,
    render_comm_log,
    render_graph_view,
    render_cost_view,
    render_logs_view,
    render_memory_view,
    render_hitl_controls,
    render_report_view
)

st.set_page_config(
    page_title="AI Conference Review Committee",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "graph_app" not in st.session_state:
    st.session_state["graph_app"] = build_graph()

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = f"session_{uuid.uuid4().hex[:8]}"

if "review_state" not in st.session_state:
    st.session_state["review_state"] = {}

if "past_threads" not in st.session_state:
    st.session_state["past_threads"] = []


# Custom CSS styling for modern UI
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #63B3ED; margin-bottom: 0px; }
    .sub-header { font-size: 1.0rem; color: #A0AEC0; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 16px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)


# Title Header
st.markdown('<div class="main-header">🎓 AI Conference Review Committee</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Multi-Agent Paper Review Platform (LangGraph + Streamlit)</div>', unsafe_allow_html=True)


# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/academic-insight.png", width=64)
    st.title("⚙️ Control Panel")
    
    st.markdown("### 1. Paper Input")
    uploaded_file = st.file_uploader("Upload Paper (PDF / TXT)", type=["pdf", "txt", "md"])
    
    sample_choice = st.selectbox("Or Choose Sample Benchmark Paper:", [
        "None",
        "Strong Paper (ConsensusGraph)",
        "Flawed Stats Paper (Quantum Optimizer)"
    ])

    paper_file_path = None
    
    if uploaded_file:
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        paper_file_path = os.path.join(uploads_dir, uploaded_file.name)
        with open(paper_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded: `{uploaded_file.name}`")
    elif sample_choice != "None":
        samples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_papers")
        if "Strong" in sample_choice:
            paper_file_path = os.path.join(samples_dir, "strong_paper.txt")
        else:
            paper_file_path = os.path.join(samples_dir, "flawed_stats_paper.txt")
        st.info(f"Selected: `{os.path.basename(paper_file_path)}`")

    st.markdown("### 2. Session Persistence")
    st.text_input("Active Thread ID", value=st.session_state["thread_id"], disabled=True)

    if st.button("🚀 Start Committee Review", type="primary", use_container_width=True):
        if not paper_file_path or not os.path.exists(paper_file_path):
            st.error("Please upload a PDF paper or select a sample benchmark paper.")
        else:
            st.session_state["thread_id"] = f"session_{uuid.uuid4().hex[:8]}"
            if st.session_state["thread_id"] not in st.session_state["past_threads"]:
                st.session_state["past_threads"].append(st.session_state["thread_id"])

            app = st.session_state["graph_app"]
            config = {"configurable": {"thread_id": st.session_state["thread_id"]}}
            
            initial_state = {
                "paper_path": paper_file_path,
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

            with st.spinner("Executing 8-Agent LangGraph Review Pipeline..."):
                # Stream updates through LangGraph stream mode
                res = app.invoke(initial_state, config=config)
                st.session_state["review_state"] = res
                st.success("Review reached Human-in-the-Loop gate!")
                st.rerun()

    st.divider()
    st.markdown("### 📚 Session History")
    if st.session_state["past_threads"]:
        st.write("Recent Thread IDs:")
        for t_id in st.session_state["past_threads"][-5:]:
            st.caption(f"- `{t_id}`")


# App Tabs (Section 6 UI Requirements)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📊 Dashboard",
    "🔍 Live Trace",
    "💬 Comm Log",
    "🕸️ Graph Topology",
    "💰 Token / Cost",
    "📋 Logs & Errors",
    "🧠 Memory Viewer",
    "🛑 Human Controls",
    "📄 Final Report"
])

current_state = st.session_state.get("review_state", {})
app = st.session_state.get("graph_app")
config = {"configurable": {"thread_id": st.session_state.get("thread_id")}}

with tab1:
    render_dashboard(current_state)

with tab2:
    render_trace_view(current_state)

with tab3:
    render_comm_log(current_state)

with tab4:
    render_graph_view(app)

with tab5:
    render_cost_view(current_state)

with tab6:
    render_logs_view(current_state)

with tab7:
    render_memory_view(current_state)

with tab8:
    render_hitl_controls(current_state, app=app, config=config)

with tab9:
    render_report_view(current_state)
