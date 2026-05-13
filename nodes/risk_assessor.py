from langchain_openai import ChatOpenAI
from langgraph.types import interrupt

from prompts.risk_prompt import RISK_PROMPT
from schemas.output_schemas import RiskReport
from state import AgentState
from tools.risk_tools import assess_breaking_changes, calculate_complexity_score, estimate_migration_effort


async def assess_risk(state: AgentState) -> dict:
    """Assess migration risk and pause for human review before graph continuation."""
    try:
        tools = [
            calculate_complexity_score,
            assess_breaking_changes,
            estimate_migration_effort,
        ]
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        llm_with_tools = llm.bind_tools(tools)
        structured_llm = llm_with_tools.with_structured_output(RiskReport)
        chain = RISK_PROMPT | structured_llm
        result = await chain.ainvoke(
            {
                "raw_code": state["raw_code"],
                "language": state.get("language", "unknown"),
                "identified_patterns": state.get("identified_patterns", []),
            }
        )
        risk_report = result.model_dump()
        interrupt({"message": "Review analysis and risk report. Set human_approved_analysis=True to continue."})
        return {"risk_report": risk_report}
    except Exception as e:
        return {"error": str(e)}
