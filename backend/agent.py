import logging
import os
from typing import Any

from dotenv import load_dotenv

from backend.agent_graph import invoke_graph


load_dotenv("backend/.env")
logger = logging.getLogger("backend.agent")


def _runnable_config(action: str, snippet_id: str | None = None) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "app": "code-modernisation-agent",
        "action": action,
        "langsmith_project": os.getenv("LANGSMITH_PROJECT", "Wipro"),
    }
    if snippet_id:
        metadata["snippet_id"] = snippet_id

    return {
        "run_name": f"code-modernisation-{action}",
        "tags": ["code-modernisation", action],
        "metadata": metadata,
    }


def analyse_code(code: str, query: str | None = None) -> str:
    logger.info("agent triggered | action=analyse")
    logger.info("graph invoked | action=analyse")
    result = invoke_graph(
        {"action": "analyse", "code": code, "query": query},
        config=_runnable_config("analyse"),
    )
    logger.info("response received | action=analyse")
    return result["analysis"]


def migrate_code(snippet_id: str, code: str) -> dict[str, Any]:
    logger.info("agent triggered | action=migrate | snippet_id=%s", snippet_id)
    logger.info("graph invoked | action=migrate | snippet_id=%s", snippet_id)
    result = invoke_graph(
        {"action": "migrate", "snippet_id": snippet_id, "code": code},
        config=_runnable_config("generate", snippet_id=snippet_id),
    )
    logger.info("response received | action=migrate | snippet_id=%s", snippet_id)
    return result["migration"]


def get_patterns() -> dict[str, Any]:
    logger.info("agent triggered | action=patterns")
    logger.info("graph invoked | action=patterns")
    result = invoke_graph(
        {"action": "patterns"},
        config=_runnable_config("patterns"),
    )
    logger.info("response received | action=patterns")
    return result["patterns"]
