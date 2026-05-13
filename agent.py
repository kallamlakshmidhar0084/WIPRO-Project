from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "nodes": list(compiled.graph.nodes.keys())}


@app.post("/analyse")
def analyse(request: AnalyseRequest) -> dict:
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

    compiled.invoke(initial_state, thread_config)
    snapshot = compiled.get_state(thread_config)
    values = snapshot.values
    return {
        "thread_id": thread_id,
        "summary": values.get("summary"),
        "identified_patterns": values.get("identified_patterns"),
        "complexity_score": values.get("complexity_score"),
        "language": values.get("language"),
        "risk_report": values.get("risk_report"),
    }


@app.post("/generate")
def generate(request: GenerateRequest) -> dict:
    if not request.approved:
        return {"status": "rejected"}

    thread_config = {"configurable": {"thread_id": request.thread_id}}
    compiled.invoke({"human_approved_analysis": True}, thread_config)
    snapshot = compiled.get_state(thread_config)
    values = snapshot.values
    return {
        "modern_code": values.get("modern_code"),
        "changes_made": values.get("changes_made"),
    }


@app.post("/checklist")
def checklist(request: ChecklistRequest) -> dict:
    thread_config = {"configurable": {"thread_id": request.thread_id}}
    compiled.invoke(
        {
            "human_approved_code": True,
            "requested_checklist": request.request_checklist,
        },
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
