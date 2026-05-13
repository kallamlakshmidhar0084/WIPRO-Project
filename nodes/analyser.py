import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from prompts.analyser_prompt import ANALYSER_PROMPT
from schemas.output_schemas import AnalysisOutput
from state import AgentState


load_dotenv("backend/.env")


def _detect_patterns(code: str) -> list[str]:
    patterns: list[str] = []
    lowered = code.lower()
    if "select " in lowered and ("+" in code or "&" in code):
        patterns.append("RAW_SQL")
    if "on error resume next" in lowered or "catch" in lowered and "{}" in code.replace(" ", ""):
        patterns.append("NO_ERROR_HANDLING")
    if any(token in lowered for token in ["password=", "pwd=", "connectionstring", "api_key"]):
        patterns.append("HARDCODED_CONFIG")
    if any(char.isdigit() for char in code):
        patterns.append("MAGIC_NUMBER")
    return patterns or ["DEAD_CODE"] if not code.strip() else patterns


def _fallback_analysis(state: AgentState) -> dict:
    code = state["raw_code"]
    patterns = _detect_patterns(code)
    line_count = max(len(code.splitlines()), 1)
    complexity_score = min(round((line_count / 50) + (len(patterns) * 0.75), 2), 10.0)
    return {
        "summary": "The snippet was analysed with deterministic fallback rules and should be reviewed for legacy behaviour, data access, configuration, and error-handling risks.",
        "identified_patterns": patterns,
        "complexity_score": complexity_score,
        "language": state.get("language", "unknown"),
    }


async def analyse_code(state: AgentState) -> dict:
    """Analyse raw legacy code and return structured analysis fields."""
    if not os.getenv("OPENAI_API_KEY"):
        return _fallback_analysis(state)

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
