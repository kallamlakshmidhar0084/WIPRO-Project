from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    raw_code: str
    language: str
    target_framework: str
    summary: str
    identified_patterns: list[str]
    complexity_score: float
    risk_report: dict
    modern_code: str
    changes_made: list[str]
    checklist: list[str]
    migration_report: str
    human_approved_analysis: bool
    human_approved_code: bool
    requested_checklist: bool
    messages: Annotated[list, add_messages]
    error: str | None
