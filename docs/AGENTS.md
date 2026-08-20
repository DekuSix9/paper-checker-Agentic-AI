# Review Agents

The committee has eight workflow nodes: one ingestion node, six specialist reviewers, and one Area Chair supervisor.

| Agent | Implementation | Responsibility |
| --- | --- | --- |
| Paper Ingestor | `agents/ingestor.py` | Extracts PDF/TXT/Markdown text, parses academic sections, and indexes chunks. |
| Novelty Checker | `agents/novelty.py` | Searches related work and evaluates contribution positioning. |
| Methodology Reviewer | `agents/methodology.py` | Reviews reproducibility, baselines, ablations, datasets, and experimental design. |
| Statistical Rigor Checker | `agents/stats_rigor.py` | Extracts p-values, sample sizes, confidence intervals, and error reporting. |
| Writing Quality Reviewer | `agents/writing_quality.py` | Measures readability and checks paper structure and captions. |
| Ethics/Plagiarism Agent | `agents/ethics.py` | Checks IRB and consent disclosures, conflicts, dual-use risk, and corpus overlap. |
| AI Content Detector | `agents/ai_detector.py` | Estimates synthetic sentence patterns, burstiness, and writing authenticity. |
| Area Chair Supervisor | `agents/area_chair.py` | Applies the weighted rubric, synthesizes findings, and prepares the decision draft. |

## Weighted Decision Rubric

The Area Chair combines scores as follows:

| Dimension | Weight |
| --- | ---: |
| Methodology | 25% |
| Novelty | 20% |
| Statistical rigor | 20% |
| Writing quality | 10% |
| Ethics | 15% |
| AI content detection | 10% |

High-risk ethics flags can veto the weighted score. The draft remains `pending` until a human approves, edits, or rejects it.

## Provider Accounting

Token rows are recorded for every reviewer. LLM-backed rows include `provider=groq` and `api_used=true`; local rows include `provider=heuristic_fallback` or are marked as local deterministic analysis. The Token / Cost tab displays both estimated usage and provider counts.

## Adding An Agent

1. Add a `run(state: ReviewState) -> dict` function under `agents/`.
2. Return one report key plus trace, token, and error data as appropriate.
3. Export the function from `agents/__init__.py`.
4. Register the node and graph edges in `graph/build_graph.py`.
5. Add its state field to `graph/state.py`.
6. Add a focused test and a corresponding UI entry if the result is user-facing.
