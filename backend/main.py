import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.agent import analyse_code, get_patterns, migrate_code
from backend.logging_config import configure_logging
from backend.schemas import AnalysisRequest, AnalysisResponse, MigrationResponse, PatternsResponse
from backend.snippet_store import snippet_store


configure_logging()
logger = logging.getLogger("backend.api")

app = FastAPI(title="AI Code Modernisation Agent", version="0.1.0")

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:8501,http://127.0.0.1:8501,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyse", response_model=AnalysisResponse)
def analyse(request: AnalysisRequest) -> AnalysisResponse:
    logger.info("query received | endpoint=/analyse")
    logger.info("input validation done | endpoint=/analyse")
    snippet = snippet_store.create(code=request.code, query=request.query)
    analysis = analyse_code(code=snippet.code, query=snippet.query)
    response = AnalysisResponse(snippet_id=snippet.snippet_id, analysis=analysis)
    logger.info("response sent back to frontend | endpoint=/analyse | snippet_id=%s", snippet.snippet_id)
    return response


@app.post("/migrate/{snippet_id}", response_model=MigrationResponse)
def migrate(snippet_id: str) -> MigrationResponse:
    logger.info("query received | endpoint=/migrate | snippet_id=%s", snippet_id)
    snippet = snippet_store.get(snippet_id)
    if snippet is None:
        logger.warning("validation failed | endpoint=/migrate | snippet_id=%s | reason=not_found", snippet_id)
        raise HTTPException(status_code=404, detail="snippet_id not found")

    logger.info("input validation done | endpoint=/migrate | snippet_id=%s", snippet_id)
    migration = migrate_code(snippet_id=snippet.snippet_id, code=snippet.code)
    response = MigrationResponse(**migration)
    logger.info("response sent back to frontend | endpoint=/migrate | snippet_id=%s", snippet_id)
    return response


@app.post("/generate", response_model=MigrationResponse)
def generate() -> MigrationResponse:
    logger.info("query received | endpoint=/generate")
    snippet = snippet_store.latest()
    if snippet is None:
        logger.warning("validation failed | endpoint=/generate | reason=no_active_snippet")
        raise HTTPException(status_code=404, detail="no analysed snippet found in conversation memory")

    logger.info("input validation done | endpoint=/generate | snippet_id=%s", snippet.snippet_id)
    migration = migrate_code(snippet_id=snippet.snippet_id, code=snippet.code)
    response = MigrationResponse(**migration)
    logger.info("response sent back to frontend | endpoint=/generate | snippet_id=%s", snippet.snippet_id)
    return response


@app.get("/patterns", response_model=PatternsResponse)
def patterns() -> PatternsResponse:
    logger.info("query received | endpoint=/patterns")
    logger.info("input validation done | endpoint=/patterns")
    pattern_data = get_patterns()
    response = PatternsResponse(**pattern_data)
    logger.info("response sent back to frontend | endpoint=/patterns")
    return response
