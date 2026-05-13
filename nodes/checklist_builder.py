from langchain_core.runnables import RunnableConfig

from backend.llm_client import achat
from nodes.prompt_utils import to_litellm_messages
from prompts.checklist_prompt import CHECKLIST_PROMPT
from schemas.output_schemas import ChecklistOutput
from state import AgentState


async def build_checklist(state: AgentState, config: RunnableConfig | None = None) -> dict:
    """Build an ordered checklist only when code is approved and a checklist is requested."""
    if not state.get("human_approved_code") or not state.get("requested_checklist"):
        return {}

    messages = to_litellm_messages(
        CHECKLIST_PROMPT,
        {
            "language": state.get("language", "unknown"),
            "modern_code": state.get("modern_code", ""),
            "risk_report": state.get("risk_report", {}),
            "identified_patterns": state.get("identified_patterns", []),
        },
    )
    result = await achat(
        messages,
        response_model=ChecklistOutput,
        temperature=0,
        tags=["checklist_builder"],
        config=config,
    )
    return {"checklist": result.checklist}
