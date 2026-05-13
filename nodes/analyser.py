from langchain_openai import ChatOpenAI

from prompts.analyser_prompt import ANALYSER_PROMPT
from schemas.output_schemas import AnalysisOutput
from state import AgentState


async def analyse_code(state: AgentState) -> dict:
    """Analyse raw legacy code and return structured analysis fields."""
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        structured_llm = llm.with_structured_output(AnalysisOutput)
        chain = ANALYSER_PROMPT | structured_llm
        result = await chain.ainvoke(
            {
                "raw_code": state["raw_code"],
                "language": state.get("language", "unknown"),
            }
        )
        return {
            "summary": result.summary,
            "identified_patterns": result.identified_patterns,
            "complexity_score": result.complexity_score,
            "language": result.language,
        }
    except Exception as e:
        return {"error": str(e)}
