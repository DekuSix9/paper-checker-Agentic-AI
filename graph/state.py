from typing import TypedDict, Optional, Literal
from typing_extensions import Annotated
import operator


class AgentReport(TypedDict):
    agent_name: str
    score: int  # 1-10
    confidence: Literal["low", "medium", "high"]
    strengths: list[str]
    weaknesses: list[str]
    flags: list[str]
    recommendation: Literal["accept", "minor_revision", "major_revision", "reject"]
    raw_notes: str


class ReviewState(TypedDict):
    # Input
    paper_path: str
    paper_raw_text: str
    paper_structured: dict  # {title, abstract, sections: {...}, references: [...], tables: [...]}

    # Reviewer outputs
    novelty_report: Optional[AgentReport]
    methodology_report: Optional[AgentReport]
    stats_report: Optional[AgentReport]
    writing_report: Optional[AgentReport]
    ethics_report: Optional[AgentReport]
    ai_detection_report: Optional[AgentReport]

    # Supervisor output
    meta_review: Optional[str]
    final_decision: Optional[Literal["accept", "minor_revision", "major_revision", "reject", "pending"]]

    # Human-in-the-loop
    human_feedback: Optional[str]
    human_approved: bool

    # Observability (append-only lists use operator.add reducer)
    agent_trace: Annotated[list[dict], operator.add]
    token_usage: Annotated[list[dict], operator.add]
    errors: Annotated[list[dict], operator.add]
