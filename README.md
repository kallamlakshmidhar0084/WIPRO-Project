# AI Code Modernisation Agent

An AI-assisted legacy code modernisation workflow built with LangGraph, FastAPI, and Streamlit.

The application helps reviewers paste legacy code, analyse its behaviour and anti-patterns, assess migration risk, approve the analysis, generate modern code, and produce a professional migration report.

## Executive Summary

Modernising legacy systems is risky because teams need to understand old behaviour, hidden anti-patterns, migration effort, breaking changes, and target-platform design choices before rewriting code. This project turns that review process into a structured, human-in-the-loop agent workflow.

The app focuses on three outcomes:

- Analyse legacy code and identify what it does.
- Detect anti-patterns, complexity, and migration risks.
- Generate modern code and a markdown migration report after human approval.

The workflow is intentionally review-driven. The graph pauses after risk assessment and after code generation so a human can approve before moving to the next stage.

## How To Run

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the FastAPI backend:

```bash
uvicorn agent:app --reload --host 127.0.0.1 --port 8000
```

Start the Streamlit UI in another terminal:

```bash
API_BASE_URL=http://localhost:8000 streamlit run backend/streamlit_app.py
```

Or run both with:

```bash
./startup.sh
```

The UI will be available at:

```text
http://localhost:8501
```

## Application Flow

1. Code Input

   The user pastes a legacy code snippet, selects the declared legacy language, and chooses the desired target framework.

2. Analysis

   The app calls `POST /analyse`. LangGraph starts a new thread, runs the analyser node, then runs the risk assessor node.

3. Human Review

   The graph pauses after risk assessment using LangGraph `interrupt()`. The UI displays:

   - Code summary
   - Identified anti-patterns
   - Complexity score
   - Risk level and risk factors
   - Raw JSON for reviewer inspection

4. Code Generation

   If the reviewer approves, the app calls `POST /generate`. The graph resumes and generates modern code. It pauses again for code approval.

5. Migration Report

   The user can optionally request a migration checklist. The app calls `POST /checklist`, the graph completes, and the UI displays a markdown migration report with a download button.

## Architecture

The project is organised around a LangGraph state machine.

```text
START
  -> analyser
  -> risk_assessor
  -> code_generator
  -> checklist_builder or report_builder
  -> report_builder
  -> END
```

The graph uses `MemorySaver` checkpointing so each request can resume by `thread_id`.

Human approval gates are implemented with LangGraph interrupts:

- After risk assessment: reviewer approves or rejects analysis.
- After code generation: reviewer approves code before report generation.

## API Summary

FastAPI app: [agent.py](agent.py)

- `GET /health`
  - Confirms the API is running and lists graph nodes.

- `POST /analyse`
  - Starts a new graph thread.
  - Inputs: `code`, `language`, `target_framework`.
  - Returns: `thread_id`, summary, patterns, complexity score, language, risk report.

- `POST /generate`
  - Resumes the existing graph thread after analysis approval.
  - Inputs: `thread_id`, `approved`.
  - Returns: modern code and changes made.

- `POST /checklist`
  - Resumes the graph after generated-code approval.
  - Inputs: `thread_id`, `request_checklist`.
  - Returns: migration report and optional checklist.

- `GET /patterns`
  - Returns the supported anti-pattern catalogue.

## Supported Anti-Patterns

The current analysis schema recognises:

- `GOD_CLASS`
- `HARDCODED_CONFIG`
- `MAGIC_NUMBER`
- `TIGHT_COUPLING`
- `NO_ERROR_HANDLING`
- `RAW_SQL`
- `DEAD_CODE`

## Folder Structure

```text
WIPRO-Project/
  agent.py                    # FastAPI API layer for the LangGraph workflow
  agent_graph.py              # Graph registration, routing, edges, and compile
  state.py                    # Shared LangGraph AgentState type
  schemas/
    output_schemas.py         # Pydantic structured output models
  prompts/
    analyser_prompt.py
    risk_prompt.py
    generator_prompt.py
    checklist_prompt.py
    report_prompt.py
  nodes/
    analyser.py
    risk_assessor.py
    code_generator.py
    checklist_builder.py
    report_builder.py
  tools/
    risk_tools.py             # LangChain tools for complexity and risk estimation
  backend/
    streamlit_app.py          # Streamlit UI
    .env                      # Local environment configuration
  tests/
    test_smoke_api.py         # Smoke tests for existing API integration
  docker-compose.yml          # Postgres and pgAdmin only
  startup.sh                  # Starts FastAPI and Streamlit locally
  startupDocker.sh            # Starts Postgres and pgAdmin
  requirements.txt
```

## Key Design Choices

- LangGraph is used for workflow control, state, checkpointing, and human-in-the-loop pauses.
- FastAPI exposes a small REST interface for UI and automation clients.
- Streamlit provides a lightweight reviewer-facing interface.
- Pydantic models define structured outputs for analysis, risk, generated code, checklists, and reports.
- Risk tools are explicit LangChain tools so complexity and migration effort can be measured consistently.
- The graph file is intentionally clean: imports, node registration, edge wiring, routing, and compile only.

## Environment

Configuration lives in:

```text
backend/.env
```

Important values:

- `OPENAI_API_KEY`
- `LANGSMITH_TRACING`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `BACKEND_PORT`
- `STREAMLIT_PORT`

LangSmith can be enabled by filling the LangSmith variables and setting tracing to true.

## Docker Services

Docker is used only for infrastructure services, not for running the app.

Start Postgres and pgAdmin:

```bash
./startupDocker.sh
```

Manual equivalent:

```bash
docker compose --env-file backend/.env up postgres_db pgadmin
```

Stop services:

```bash
docker compose --env-file backend/.env down
```

## Testing

Run smoke tests:

```bash
pytest -q
```

The smoke tests check API integration and response shape. They are not intended to judge LLM output quality.

## Reviewer Notes

This project demonstrates the full skeleton of a production-style modernisation workflow:

- Structured graph state
- Typed outputs
- Tool-backed risk calculations
- Human approval gates
- API-driven graph resume using `thread_id`
- Reviewer-facing Streamlit UI
- Downloadable migration report

The current implementation is ready for model-backed refinement by improving prompts, expanding tools, adding persistence, and broadening test coverage around graph resumes and interrupt handling.


## Future Vision if time permits

### Observability & Evaluation
- [ ] LangSmith tracing integration for every node run
- [ ] Ragas-based evaluation pipeline to score modernisation quality
- [ ] Token usage and latency dashboards per node
- [ ] Structured logging with run IDs tied to thread IDs

### Agent Intelligence
- [ ] Multi-agent architecture — separate specialist agents for analysis, security audit, and generation
- [ ] Reflection loop — agent self-reviews generated code before presenting to human
- [ ] RAG pipeline over internal codebase to match organisation-specific patterns
- [ ] Few-shot examples pulled dynamically from a vector store per language

### Security & Compliance
- [ ] OWASP vulnerability scanner node before code generation
- [ ] PII/secrets detection pre-flight before code is sent to LLM
- [ ] Audit trail — immutable log of every human approval decision with timestamp
- [ ] Role-based approval — separate approver for analysis vs generated code

### Scale & Deployment
- [ ] Redis checkpointer replacing MemorySaver for production multi-instance deployments
- [ ] Async task queue (Celery/ARQ) for long-running generation jobs
- [ ] Webhook callbacks so CI/CD pipelines can trigger modernisation runs
- [ ] Batch mode — process entire repositories, not just single snippets

### Developer Experience
- [ ] VS Code extension — right-click any file to trigger modernisation
- [ ] GitHub Actions integration — PR comment triggers analysis on legacy files
- [ ] Diff view with accept/reject per change block, not just full code approval
- [ ] Export to Jira — auto-create migration tickets from checklist items
