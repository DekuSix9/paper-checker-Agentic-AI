# AI Conference Review Committee: Multi-Agent Paper Review System

An end-to-end multi-agent research paper review system built with **LangGraph**, **ChromaDB**, and **Streamlit**. The system evaluates uploaded PDF research papers like an IEEE/ACM conference review committee, producing 6 specialist agent reviews and a supervisor Area Chair meta-review with a Human-in-the-Loop approval gate.

![Architecture Diagram](architecture_diagram.png)

---

## 🌟 Key Features

1. **8 Specialized Agents**:
   - **Paper Ingestor** (`agents/ingestor.py`): PDF section extraction, table/figure parsing, ChromaDB indexing.
   - **Novelty Checker** (`agents/novelty.py`): Literature search (Tavily), embedding similarity, contribution assessment.
   - **Methodology Reviewer** (`agents/methodology.py`): RAG retrieval over paper chunks, reproducibility & baseline checks.
   - **Statistical Rigor Checker** (`agents/stats_rigor.py`): Regex extraction of p-values, sample sizes ($n$), CIs, effect sizes, variance checks.
   - **Writing Quality Reviewer** (`agents/writing_quality.py`): Flesch-Kincaid readability scoring, section structure & flow.
   - **Ethics/Plagiarism Flagging Agent** (`agents/ethics.py`): Text similarity, IRB/consent statements, dual-use risk, ethics veto logic.
   - **AI Content & Sentence Detection Agent** (`agents/ai_detector.py`): Sentence-level perplexity/burstiness proxies, LLM phrase detection, synthetic sentence ratio scoring.
   - **Area Chair Supervisor** (`agents/area_chair.py`): Weighted rubric scoring (Methodology 25%, Novelty 20%, Stats 20%, Writing 10%, Ethics 15%, AI Detection 10%), meta-review synthesis, HITL approval.

2. **Human-in-the-Loop (HITL) Gate**:
   - LangGraph pauses execution before decision commitment via `interrupt_before=["finalize"]`.
   - Streamlit controls: Approve, Edit Meta-Review, Single Agent Retry, or Reject Outright.

3. **9 Interactive Streamlit UI Tabs**:
   - 📊 **Dashboard**: Active committee status, progress bar, decision metrics.
   - 🔍 **Live Trace**: Expandable real-time agent execution step log.
   - 💬 **Comm Log**: State diff showing read inputs and written state keys per node.
   - 🕸️ **Graph Topology**: Interactive Mermaid execution topology rendering.
   - 💰 **Token / Cost**: Agent token breakdown & total estimated cost (USD).
   - 📋 **Logs & Errors**: Filterable structured JSON log viewer (`logs/execution.json`).
   - 🧠 **Memory Viewer**: ChromaDB collection browser (`paper_chunks`, `related_work`, `past_reviews`).
   - 🛑 **Human Controls**: Approve, edit meta-review text, or re-invoke individual agents.
   - 📄 **Final Report**: Rendered IEEE-style decision report with Markdown and PDF export.

---

## 🚀 Quickstart Guide

### 1. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd paper-review-committee

# Install requirements
pip install -r requirements.txt
```

### 2. Environment Setup (Optional)

Copy `.env.example` to `.env` and set optional API keys for online Tavily search or specific LLM providers:

```bash
cp .env.example .env
```

*(Note: The system contains intelligent offline fallbacks and works out-of-the-box even without API keys!)*

### 3. Launching the App

```bash
streamlit run ui/app.py
```

Open `http://localhost:8501` in your browser.

---

## 🧪 Running Automated Tests

Run the full pytest suite:

```bash
python -m pytest tests/
```

---

## 📐 Repository Structure

```
paper-review-committee/
├── agents/
│   ├── __init__.py
│   ├── ingestor.py          # Paper Ingestor agent
│   ├── novelty.py           # Novelty Checker agent
│   ├── methodology.py       # Methodology Reviewer agent
│   ├── stats_rigor.py       # Statistical Rigor Checker agent
│   ├── writing_quality.py   # Writing Quality Reviewer agent
│   ├── ethics.py            # Ethics/Plagiarism Flagging agent
│   └── area_chair.py        # Area Chair (Supervisor) agent
├── graph/
│   ├── __init__.py
│   ├── state.py             # ReviewState TypedDict
│   └── build_graph.py       # StateGraph topology & interrupt_before
├── tools/
│   ├── __init__.py
│   ├── pdf_tools.py         # PyMuPDF section extraction
│   ├── search_tools.py      # Tavily web search wrapper
│   ├── rag_tools.py         # Chroma indexing & retrieval
│   └── stats_tools.py       # Regex statistical claim extraction
├── memory/
│   ├── __init__.py
│   ├── vector_store.py      # Chroma client & collection manager
│   └── checkpointer.py      # LangGraph SqliteSaver checkpointer
├── logging_utils/
│   ├── __init__.py
│   └── logger.py            # Structured JSON logger & cost estimator
├── ui/
│   ├── app.py               # Streamlit multi-tab entry point
│   └── components/          # 9 UI tab view components
├── data/
│   ├── sample_papers/      # Benchmark sample paper inputs
│   └── uploads/            # Uploaded PDF workspace
├── logs/                    # Execution logs
├── tests/                   # Pytest smoke and state tests
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── architecture_diagram.png
```
