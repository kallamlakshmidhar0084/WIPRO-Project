import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.types import interrupt

from prompts.risk_prompt import RISK_PROMPT
from schemas.output_schemas import RiskReport
from state import AgentState
from tools.risk_tools import assess_breaking_changes, calculate_complexity_score, estimate_migration_effort


load_dotenv("backend/.env")


def _risk_level(code: str, patterns: list[str]) -> str:
    lowered = code.lower()
    if any(token in lowered for token in ["password=", "pwd=", "connectionstring", "api_key", "secret="]):
        return "CRITICAL"
    if "RAW_SQL" in patterns:
        return "HIGH"
    if "NO_ERROR_HANDLING" in patterns or "on error resume next" in lowered or "catch" in lowered and "{}" in code.replace(" ", ""):
        return "MEDIUM"
    return "LOW"


def _fallback_risk(state: AgentState) -> dict:
    code = state["raw_code"]
    patterns = state.get("identified_patterns", [])
    risk_level = _risk_level(code, patterns)
    complexity_score = calculate_complexity_score.invoke({"code": code, "patterns": patterns})
    breaking_changes = assess_breaking_changes.invoke({"code": code, "language": state.get("language", "unknown")})
    effort_days = estimate_migration_effort.invoke(
        {
            "risk_level": risk_level,
            "complexity_score": complexity_score,
            "lines_of_code": len(code.splitlines()),
        }
    )
    risk_factors = list(patterns) + breaking_changes["deprecated_apis"] + breaking_changes["signature_risks"]
    if not risk_factors:
        risk_factors = ["No high-confidence migration risks found by deterministic fallback rules."]
    return {
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "estimated_effort_days": effort_days,
        "breaking_change_likelihood": min(round(breaking_changes["risk_count"] / 10, 2), 1.0),
    }


async def assess_risk(state: AgentState) -> dict:
    """Assess migration risk and pause for human review before graph continuation."""
    if not os.getenv("OPENAI_API_KEY"):
        risk_report = _fallback_risk(state)
        interrupt(
            {
                "message": "Review analysis and risk report. Set human_approved_analysis=True to continue.",
                "risk_report": risk_report,
            }
        )
        return {"risk_report": risk_report}

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
    except Exception as e:
        return {"error": str(e)}

    interrupt(
        {
            "message": "Review analysis and risk report. Set human_approved_analysis=True to continue.",
            "risk_report": risk_report,
        }
    )
    return {"risk_report": risk_report}
