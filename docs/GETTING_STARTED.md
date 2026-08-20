# Getting Started

This guide runs the AI Conference Review Committee locally and explains the path from an uploaded paper to the final human-approved report.

## Prerequisites

- Python 3.10 or newer
- pip
- Windows PowerShell, macOS/Linux shell, or an equivalent terminal
- Optional: a Groq API key for LLM-backed novelty and methodology reviews
- Optional: a Tavily API key for live related-paper search

The remaining agents use local deterministic analysis and the application includes offline fallbacks, so the UI can start without API keys.

## Installation

```powershell
cd D:\Review_paper_Checker
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS/Linux, activate the environment with:

```bash
source .venv/bin/activate
```

## Environment Configuration

Create a `.env` file in the repository root:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
TAVILY_API_KEY=your_tavily_api_key
```

`GROQ_MODEL` is optional. The default is `openai/gpt-oss-20b`. The configured Groq account must have access to the selected model.

Never commit `.env`. It contains secrets and is ignored by Git.

## Start The Dashboard

```powershell
python -m streamlit run ui/app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. If that port is occupied, Streamlit selects another port such as `8502` or `8503`.

## Run A Review

1. Upload a PDF, TXT, or Markdown paper in the sidebar.
2. Or select one of the bundled benchmark papers.
3. Click `Start Committee Review`.
4. Inspect the dashboard, trace, communication log, token usage, and report tabs.
5. Use `Human Controls` to approve, edit, retry, or reject the draft.
6. Download the Markdown or PDF report from `Final Report`.

## Bundled Samples

- `data/sample_papers/strong_paper.txt`
- `data/sample_papers/flawed_stats_paper.txt`

These samples are useful for verifying that different paper content produces different findings.

## Run Tests

```powershell
python -m pytest -q
```

The alternate test runner is:

```powershell
python run_tests.py
```

## Troubleshooting

### Groq calls are not shown as used

Open the `Token / Cost` tab. Each LLM-backed row includes a provider marker. `groq` means the request returned structured output; `heuristic_fallback` means the local reviewer path was used. Check `GROQ_API_KEY`, `GROQ_MODEL`, and the terminal log for provider errors.

### The same paper appears repeatedly

Start a new review with the sidebar button. Each run receives a new LangGraph thread ID, and each paper is indexed with a content-derived Chroma identifier.

### PDF text is empty

Try a text-based PDF or upload a TXT/Markdown version. Scanned PDFs require OCR before this application can analyze their text.
