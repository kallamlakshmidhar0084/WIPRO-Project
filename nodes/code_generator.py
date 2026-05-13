from langchain_openai import ChatOpenAI
from langgraph.types import interrupt

from prompts.generator_prompt import GENERATOR_PROMPT
from schemas.output_schemas import ModernCodeOutput
from state import AgentState


async def generate_modern_code(state: AgentState) -> dict:
    """Generate modern code after approved analysis and pause for code review."""
    if not state.get("human_approved_analysis"):
        return {"error": "Analysis not approved"}

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    structured_llm = llm.with_structured_output(ModernCodeOutput)
    chain = GENERATOR_PROMPT | structured_llm
    target_framework = state.get("target_framework", "Python/FastAPI")
    result = await chain.ainvoke(
        {
            "raw_code": state["raw_code"],
            "language": state.get("language", "unknown"),
            "target_framework": target_framework,
            "identified_patterns": state.get("identified_patterns", []),
            "risk_report": state.get("risk_report", {}),
        }
    )
    modern_code = result.modern_code
    interrupt({"message": "Review generated code. Set human_approved_code=True to continue."})
    return {
        "modern_code": modern_code,
        "changes_made": result.changes_made,
    }
