import logging
from typing import Any

from backend.agent_graph import invoke_graph


logger = logging.getLogger("backend.agent")


def analyse_code(code: str, query: str | None = None) -> str:
    logger.info("agent triggered | action=analyse")
    logger.info("graph invoked | action=analyse")
    result = invoke_graph({"action": "analyse", "code": code, "query": query})
    logger.info("response received | action=analyse")
    return result["analysis"]


def migrate_code(snippet_id: str, code: str) -> dict[str, Any]:
    logger.info("agent triggered | action=migrate | snippet_id=%s", snippet_id)
    logger.info("graph invoked | action=migrate | snippet_id=%s", snippet_id)
    result = invoke_graph({"action": "migrate", "snippet_id": snippet_id, "code": code})
    logger.info("response received | action=migrate | snippet_id=%s", snippet_id)
    return result["migration"]


def get_patterns() -> dict[str, Any]:
    logger.info("agent triggered | action=patterns")
    logger.info("graph invoked | action=patterns")
    result = invoke_graph({"action": "patterns"})
    logger.info("response received | action=patterns")
    return result["patterns"]
