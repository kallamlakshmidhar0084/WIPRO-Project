# WIPRO-Project

AI powered code modernisation agent integration scaffold.

## Core Idea

This app analyses legacy code snippets, explains what they do, flags anti-patterns and migration risks, then generates a structured modernisation draft. The backend is a FastAPI service that validates inputs and calls an agent wrapper over a LangGraph-style workflow. The UI is a Streamlit chat-style app that sends code to the backend, displays markdown analysis, enables migration after analysis, and shows known anti-patterns.

The current agent logic is deterministic so the full integration can be tested without API keys. Fill model keys in `backend/.env` when you are ready to replace the placeholder workflow with a real LLM-backed graph.

## One-Shot Startup

Start the local app with:

```bash
./startup.sh
```

This runs FastAPI and Streamlit normally on your machine:

- FastAPI: `http://localhost:8000`
- Streamlit: `http://localhost:8501`

If you also want the database tools, start them separately:

```bash
./startupDocker.sh
```

This runs only Docker services for:

- Postgres with pgvector: `localhost:5432`
- pgAdmin: `http://localhost:5050`

If Docker Compose fails, `startupDocker.sh` prints recent Postgres and pgAdmin logs before exiting.

Configuration lives in `backend/.env`. Values with empty API keys are placeholders for you to fill.

For local Streamlit access, `startup.sh` starts Streamlit with local-friendly origin settings:

- `--server.enableCORS false`
- `--server.enableXsrfProtection false`
- `--server.address 127.0.0.1`

FastAPI also allows requests from `localhost:8501` and `127.0.0.1:8501` through `CORS_ALLOWED_ORIGINS`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Docker Compose

Manual Docker Compose startup:

```bash
docker compose --env-file backend/.env up postgres_db pgadmin
```

Stop containers:

```bash
docker compose --env-file backend/.env down
```

## Run Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## Run Frontend

In a second terminal:

```bash
streamlit run backend/streamlit_app.py
```

The Streamlit app expects the API at `http://localhost:8000` by default.
Override it with:

```bash
API_BASE_URL=http://localhost:8000 streamlit run backend/streamlit_app.py
```

`startup.sh` loads environment variables from `backend/.env` before starting the backend and Streamlit app.

## Smoke Tests

```bash
pytest -q
```

## API

- `POST /analyse`
- `POST /generate`
- `POST /migrate/{snippet_id}` for backward compatibility
- `GET /patterns`
- `GET /health`

`backend/agent.py` wraps `backend/agent_graph.py`, passes a LangSmith-aware runnable config into `graph.invoke`, and logs graph invocation for each endpoint flow. Child LLM calls should receive the same LangGraph `config` so traces nest under the active graph/node run.
