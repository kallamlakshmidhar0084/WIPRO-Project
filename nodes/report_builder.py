from langchain_core.runnables import RunnableConfig

from backend.llm_client import achat
from nodes.prompt_utils import to_litellm_messages
from prompts.report_prompt import REPORT_PROMPT
from schemas.output_schemas import MigrationReportOutput
from state import AgentState


async def build_report(state: AgentState, config: RunnableConfig | None = None) -> dict:
    """Build the final markdown migration report."""
    messages = to_litellm_messages(
        REPORT_PROMPT,
        {
            "language": state.get("language", "unknown"),
            "summary": state.get("summary", ""),
            "identified_patterns": state.get("identified_patterns", []),
            "complexity_score": state.get("complexity_score", 0.0),
            "risk_report": state.get("risk_report", {}),
            "modern_code": state.get("modern_code", ""),
            "checklist": state.get("checklist", []),
            "changes_made": state.get("changes_made", []),
        },
    )
    result = await achat(
        messages,
        response_model=MigrationReportOutput,
        temperature=0,
        tags=["report_builder"],
        config=config,
    )
    return {"migration_report": result.migration_report}
