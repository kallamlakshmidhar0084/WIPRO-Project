from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command
from pydantic import BaseModel, Field

from agent_graph import compiled


app = FastAPI(title="LangGraph Code Modernization Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyseRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: str = "unknown"
    target_framework: str = "Python/FastAPI"


class GenerateRequest(BaseModel):
    thread_id: str
    approved: bool


class ChecklistRequest(BaseModel):
    thread_id: str
    request_checklist: bool


def _interrupted_value(snapshot, key: str):
    for interrupt in getattr(snapshot, "interrupts", ()) or ():
        value = getattr(interrupt, "value", None)
        if isinstance(value, dict) and key in value:
            return value[key]
    return None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "nodes": list(compiled.graph.nodes.keys())}


@app.post("/analyse")
async def analyse(request: AnalyseRequest) -> dict:
    thread_id = str(uuid4())
    thread_config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "raw_code": request.code,
        "language": request.language,
        "target_framework": request.target_framework,
        "messages": [],
        "human_approved_analysis": False,
        "human_approved_code": False,
        "requested_checklist": False,
    }

    await compiled.ainvoke(initial_state, thread_config)
    snapshot = compiled.get_state(thread_config)
    values = snapshot.values
    risk_report = values.get("risk_report") or _interrupted_value(snapshot, "risk_report")
    return {
        "thread_id": thread_id,
        "summary": values.get("summary"),
        "identified_patterns": values.get("identified_patterns"),
        "complexity_score": values.get("complexity_score"),
        "language": values.get("language"),
        "risk_report": risk_report,
        "error": values.get("error"),
    }


@app.post("/generate")
async def generate(request: GenerateRequest) -> dict:
    if not request.approved:
        return {"status": "rejected"}

    thread_config = {"configurable": {"thread_id": request.thread_id}}
    await compiled.ainvoke(
        Command(update={"human_approved_analysis": True}, resume=True),
        thread_config,
    )
    snapshot = compiled.get_state(thread_config)
    values = snapshot.values
    generated = _interrupted_value(snapshot, "generated_code") or {}
    return {
        "modern_code": values.get("modern_code") or generated.get("modern_code"),
        "changes_made": values.get("changes_made") or generated.get("changes_made"),
    }


@app.post("/checklist")
async def checklist(request: ChecklistRequest) -> dict:
    thread_config = {"configurable": {"thread_id": request.thread_id}}
    await compiled.ainvoke(
        Command(
            update={
                "human_approved_code": True,
                "requested_checklist": request.request_checklist,
            },
            resume=True,
        ),
        thread_config,
    )
    snapshot = compiled.get_state(thread_config)
    values = snapshot.values
    return {
        "migration_report": values.get("migration_report"),
        "checklist": values.get("checklist"),
    }


@app.get("/patterns")
def patterns() -> dict:
    return {
        "patterns": [
            "GOD_CLASS",
            "HARDCODED_CONFIG",
            "MAGIC_NUMBER",
            "TIGHT_COUPLING",
            "NO_ERROR_HANDLING",
            "RAW_SQL",
            "DEAD_CODE",
        ]
    }
