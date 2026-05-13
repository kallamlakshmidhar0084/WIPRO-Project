from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from nodes.analyser import analyse_code
from nodes.checklist_builder import build_checklist
from nodes.code_generator import generate_modern_code
from nodes.report_builder import build_report
from nodes.risk_assessor import assess_risk
from state import AgentState


def route_after_code(state: AgentState) -> str:
    return "checklist" if state["requested_checklist"] is True else "report"


graph = StateGraph(AgentState)
graph.add_node("analyser", analyse_code)
graph.add_node("risk_assessor", assess_risk)
graph.add_node("code_generator", generate_modern_code)
graph.add_node("checklist_builder", build_checklist)
graph.add_node("report_builder", build_report)

graph.add_edge(START, "analyser")
graph.add_edge("analyser", "risk_assessor")
graph.add_edge("risk_assessor", "code_generator")
graph.add_conditional_edges(
    "code_generator",
    route_after_code,
    {"checklist": "checklist_builder", "report": "report_builder"},
)
graph.add_edge("checklist_builder", "report_builder")
graph.add_edge("report_builder", END)

compiled = graph.compile(checkpointer=MemorySaver())
compiled.graph = graph


if __name__ == "__main__":
    print("[agent_graph] Graph compiled successfully")
    print("[agent_graph] Nodes:", list(compiled.graph.nodes.keys()))
