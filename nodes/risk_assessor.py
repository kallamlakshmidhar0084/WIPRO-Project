from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from backend.llm_client import achat
from nodes.prompt_utils import to_litellm_messages
from prompts.risk_prompt import RISK_PROMPT
from schemas.output_schemas import RiskReport
from state import AgentState
from tools.risk_tools import assess_breaking_changes, calculate_complexity_score, estimate_migration_effort


def _risk_level(code: str, patterns: list[str]) -> str:
    lowered = code.lower()
    if any(token in lowered for token in ["password=", "pwd=", "connectionstring", "api_key", "secret="]):
        return "CRITICAL"
    if "RAW_SQL" in patterns:
        return "HIGH"
    if "NO_ERROR_HANDLING" in patterns or "on error resume next" in lowered or "catch" in lowered and "{}" in code.replace(" ", ""):
        return "MEDIUM"
    return "LOW"


def _tool_results(state: AgentState) -> dict:
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
        "complexity_score": complexity_score,
        "breaking_changes": breaking_changes,
        "estimated_effort_days": effort_days,
        "breaking_change_likelihood": min(round(breaking_changes["risk_count"] / 10, 2), 1.0),
    }


async def assess_risk(state: AgentState, config: RunnableConfig | None = None) -> dict:
    """Assess migration risk and pause for human review before graph continuation."""
    try:
        tool_results = _tool_results(state)
        messages = to_litellm_messages(
            RISK_PROMPT,
            {
                "raw_code": state["raw_code"],
                "language": state.get("language", "unknown"),
                "identified_patterns": state.get("identified_patterns", []),
            },
        )
        messages.append(
            {
                "role": "user",
                "content": f"Tool results from all three required tools:\n{tool_results}",
            }
        )
        result = await achat(
            messages,
            response_model=RiskReport,
            temperature=0,
            tags=["risk_assessor"],
            config=config,
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
