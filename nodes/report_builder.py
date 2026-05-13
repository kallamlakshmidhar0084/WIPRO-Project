from langchain_openai import ChatOpenAI

from prompts.report_prompt import REPORT_PROMPT
from schemas.output_schemas import MigrationReportOutput
from state import AgentState


async def build_report(state: AgentState) -> dict:
    """Build the final markdown migration report."""
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(MigrationReportOutput)
    chain = REPORT_PROMPT | structured_llm
    result = await chain.ainvoke(
        {
            "language": state.get("language", "unknown"),
            "summary": state.get("summary", ""),
            "identified_patterns": state.get("identified_patterns", []),
            "complexity_score": state.get("complexity_score", 0.0),
            "risk_report": state.get("risk_report", {}),
            "modern_code": state.get("modern_code", ""),
            "checklist": state.get("checklist", []),
            "changes_made": state.get("changes_made", []),
        }
    )
    return {"migration_report": result.migration_report}
