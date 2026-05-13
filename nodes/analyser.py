from langchain_core.runnables import RunnableConfig

from backend.llm_client import achat
from nodes.prompt_utils import to_litellm_messages
from prompts.analyser_prompt import ANALYSER_PROMPT
from schemas.output_schemas import AnalysisOutput
from state import AgentState


async def analyse_code(state: AgentState, config: RunnableConfig | None = None) -> dict:
    """Analyse raw legacy code and return structured analysis fields."""
    try:
        messages = to_litellm_messages(
            ANALYSER_PROMPT,
            {
                "raw_code": state["raw_code"],
                "language": state.get("language", "unknown"),
            },
        )
        result = await achat(
            messages,
            response_model=AnalysisOutput,
            temperature=0,
            tags=["analyser"],
            config=config,
        )
        return {
            "summary": result.summary,
            "identified_patterns": result.identified_patterns,
            "complexity_score": result.complexity_score,
            "language": result.language,
        }
    except Exception as e:
        return {"error": str(e)}
