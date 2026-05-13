from langchain_openai import ChatOpenAI

from prompts.checklist_prompt import CHECKLIST_PROMPT
from schemas.output_schemas import ChecklistOutput
from state import AgentState


async def build_checklist(state: AgentState) -> dict:
    """Build an ordered checklist only when code is approved and a checklist is requested."""
    if not state.get("human_approved_code") or not state.get("requested_checklist"):
        return {}

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(ChecklistOutput)
    chain = CHECKLIST_PROMPT | structured_llm
    result = await chain.ainvoke(
        {
            "language": state.get("language", "unknown"),
            "modern_code": state.get("modern_code", ""),
            "risk_report": state.get("risk_report", {}),
            "identified_patterns": state.get("identified_patterns", []),
        }
    )
    return {"checklist": result.checklist}
