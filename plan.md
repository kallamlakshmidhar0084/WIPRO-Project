# AI Powered Code Modernisation Agent Plan

## Goal

Build an AI powered code modernisation agent that can accept legacy code snippets, analyse what they do, detect anti-patterns and migration risks, and generate equivalent modern code with a structured migration checklist.

The system will use:

- LangGraph for the agent workflow.
- FastAPI for the backend REST API.
- Streamlit for a ChatGPT-inspired streaming UI.
- Smoke tests for endpoint integration.
- Input validation for all user and API inputs.
- Structured output for generated migration responses.

## Core Tasks

### 1. Analyse Legacy Code

Endpoint: `POST /analyse`

Purpose:

- Accept a legacy code snippet as a string.
- Accept an optional user query for analysis focus.
- Validate the request before invoking the agent.
- Trigger the LangGraph workflow through `agent.py`.
- Return a markdown analysis string.

Expected analysis:

- What the code appears to do.
- Detected anti-patterns.
- Potential bugs or unsafe behavior.
- Migration risks.
- Recommended modernisation direction.

Request shape:

```json
{
  "code": "string",
  "query": "optional string"
}
```

Response shape:

```json
{
  "snippet_id": "string",
  "analysis": "markdown string"
}
```

Validation rules:

- `code` is required.
- `code` must be a non-empty string.
- `query` is optional but must be a string when present.
- Reject overly large snippets with a clear validation error.

Logging flow:

- Query received.
- Input validation done.
- Agent triggered.
- Graph invoked.
- Response received.
- Response sent back to frontend.

### 2. Generate Modernised Code

Endpoint: `POST /migrate/{snippet_id}`

Purpose:

- Enable only after `/analyse` has produced a valid `snippet_id`.
- Reuse the already submitted code snippet from backend state or storage.
- Trigger the LangGraph workflow through `agent.py`.
- Generate equivalent modern code.
- Return structured output with checklist items.

Response shape:

```json
{
  "snippet_id": "string",
  "modernized_code": "string",
  "language": "string",
  "summary": "string",
  "checklist": [
    {
      "item": "string",
      "status": "changed | review_required | not_applicable",
      "notes": "string"
    }
  ],
  "risks": [
    {
      "risk": "string",
      "severity": "low | medium | high",
      "mitigation": "string"
    }
  ]
}
```

Validation rules:

- `snippet_id` is required as a path parameter.
- `snippet_id` must exist in backend state or storage.
- Return `404` for unknown snippets.
- Return structured validation errors for invalid requests.

Logging flow:

- Query received.
- Input validation done.
- Agent triggered.
- Graph invoked.
- Response received.
- Response sent back to frontend.

### 3. Get Anti-Patterns

Endpoint: `GET /patterns`

Purpose:

- Return a list of known anti-patterns with descriptions.
- Can be backed by the agent, static catalogue, or a hybrid approach.
- Enable this button after analysis is available in the UI.

Response shape:

```json
{
  "patterns": [
    {
      "name": "string",
      "description": "string",
      "example": "optional string",
      "modern_alternative": "optional string"
    }
  ]
}
```

Validation rules:

- No request body required.
- Response must always use the structured schema.

Logging flow:

- Query received.
- Input validation done.
- Agent triggered.
- Graph invoked.
- Response received.
- Response sent back to frontend.

## Proposed Project Structure

```text
WIPRO-Project/
  backend/
    main.py
    agent.py
    agent_graph.py
    schemas.py
    logging_config.py
    snippet_store.py
    streamlit_app.py
  tests/
    test_smoke_api.py
  requirements.txt
  plan.md
  README.md
```

## Backend Design

FastAPI app responsibilities:

- Expose `/analyse`, `/migrate/{snippet_id}`, and `/patterns`.
- Validate requests and responses with Pydantic schemas.
- Store analysed snippets by `snippet_id`.
- Call `agent.py` instead of calling `agent_graph.py` directly.
- Return consistent JSON errors.

`agent.py` responsibilities:

- Provide a simple wrapper around `agent_graph.py`.
- Log `graph invoked` every time the graph is called.
- Expose simple functions:
  - `analyse_code(code: str, query: str | None)`
  - `migrate_code(snippet_id: str, code: str)`
  - `get_patterns()`

`agent_graph.py` responsibilities:

- Define the LangGraph workflow.
- Keep node-level logic isolated from API concerns.
- Return markdown for analysis.
- Return structured dictionaries for migration and patterns.

Initial implementation note:

- The first version can use deterministic placeholder agent logic to prove integration.
- The LangGraph path, schemas, logs, API calls, and UI flow should work before connecting a production LLM.

## Streamlit UI Design

The frontend should follow a ChatGPT-inspired layout:

- Conversation content centered on the screen.
- Chat/input area fixed near the bottom middle.
- Two inputs:
  - Code snippet input.
  - Optional query input.
- Initial action:
  - `Analyse` button only.
- After successful analysis:
  - Enable `Generate` button.
  - Enable `Get Patterns` button.

Display behavior:

- Show analysis as markdown.
- Show generated code in a code block.
- Show migration checklist as structured markdown or table.
- Show risks clearly with severity labels.
- Show anti-patterns as markdown cards or a compact list.

Streaming behavior:

- Stream frontend status updates while waiting for backend responses.
- Show progress messages such as:
  - Validating input.
  - Sending to backend.
  - Agent analysing.
  - Response received.

## Smoke Tests

Smoke tests must verify that the backend and endpoint integration are working.

Required tests:

- `POST /analyse` with valid code returns `200`, `snippet_id`, and markdown analysis.
- `POST /analyse` with empty code returns validation error.
- `POST /migrate/{snippet_id}` after analysis returns `200` and structured modernisation output.
- `POST /migrate/{snippet_id}` with unknown ID returns `404`.
- `GET /patterns` returns `200` and a structured list of anti-patterns.

Smoke test scope:

- Test API routing.
- Test schema validation.
- Test wrapper-to-graph invocation.
- Test response shape.
- Avoid testing model quality in smoke tests.

## Logging Requirements

Every endpoint must emit clear logs in this order:

```text
query received
input validation done
agent triggered
graph invoked
response received
response sent back to frontend
```

Logs should include:

- Endpoint name.
- `snippet_id` when available.
- Request lifecycle stage.
- Error reason for failed validation or failed agent invocation.

Logs should not include:

- Full code snippets by default.
- Secrets or environment variables.

## Input Validation Requirements

Use Pydantic models for:

- Analysis request.
- Analysis response.
- Migration response.
- Pattern response.
- Checklist item.
- Risk item.

Validation should be enforced at the API boundary and should return readable FastAPI errors.

## Structured Output Requirements

Structured output is mandatory for:

- `POST /migrate/{snippet_id}`
- `GET /patterns`

Markdown output is acceptable for:

- `POST /analyse`

All structured responses must be validated by response models before being sent to the frontend.

## Implementation Order

1. Create backend package structure.
2. Add Pydantic schemas.
3. Add logging setup.
4. Add in-memory snippet store.
5. Add `agent_graph.py` with a minimal LangGraph workflow.
6. Add `agent.py` wrapper with graph invocation logging.
7. Add FastAPI endpoints.
8. Add Streamlit chat-style UI.
9. Add smoke tests for all endpoints.
10. Run smoke tests and fix integration issues.
11. Update README with run commands.

## Acceptance Criteria

- FastAPI app starts successfully.
- Streamlit app starts successfully.
- User can paste code and optional query.
- User can run analysis first.
- User can generate modernised code only after analysis.
- User can fetch anti-patterns after analysis.
- All endpoint responses use validated schemas.
- Smoke tests pass.
- Logs clearly show request lifecycle and agent invocation flow.
