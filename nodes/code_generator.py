from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from backend.llm_client import achat
from nodes.prompt_utils import to_litellm_messages
from prompts.generator_prompt import GENERATOR_PROMPT
from schemas.output_schemas import ModernCodeOutput
from state import AgentState


async def generate_modern_code(state: AgentState, config: RunnableConfig | None = None) -> dict:
    """Generate modern code after approved analysis and pause for code review."""
    if not state.get("human_approved_analysis"):
        return {"error": "Analysis not approved"}

    target_framework = state.get("target_framework", "Python/FastAPI")
    messages = to_litellm_messages(
        GENERATOR_PROMPT,
        {
            "raw_code": state["raw_code"],
            "language": state.get("language", "unknown"),
            "target_framework": target_framework,
            "identified_patterns": state.get("identified_patterns", []),
            "risk_report": state.get("risk_report", {}),
        },
    )
    result = await achat(
        messages,
        response_model=ModernCodeOutput,
        temperature=0.2,
        tags=["code_generator"],
        config=config,
    )
    modern_code = result.modern_code
    generated = {
        "modern_code": modern_code,
        "changes_made": result.changes_made,
    }
    interrupt(
        {
            "message": "Review generated code. Set human_approved_code=True to continue.",
            "generated_code": generated,
        }
    )
    return generated
