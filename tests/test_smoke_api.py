from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_analyse_valid_code_returns_snippet_and_markdown() -> None:
    response = client.post("/analyse", json={"code": "print('legacy')", "query": "focus on risks"})

    assert response.status_code == 200
    data = response.json()
    assert data["snippet_id"]
    assert "## Legacy Code Analysis" in data["analysis"]


def test_analyse_empty_code_returns_validation_error() -> None:
    response = client.post("/analyse", json={"code": "   "})

    assert response.status_code == 422


def test_generate_after_analysis_returns_structured_output() -> None:
    analyse_response = client.post("/analyse", json={"code": "print('legacy')"})
    snippet_id = analyse_response.json()["snippet_id"]

    response = client.post("/generate")

    assert response.status_code == 200
    data = response.json()
    assert data["snippet_id"] == snippet_id
    assert data["modernized_code"]
    assert data["checklist"]
    assert data["risks"]


def test_migrate_path_remains_backward_compatible() -> None:
    analyse_response = client.post("/analyse", json={"code": "print('legacy')"})
    snippet_id = analyse_response.json()["snippet_id"]

    response = client.post(f"/migrate/{snippet_id}")

    assert response.status_code == 200


def test_migrate_unknown_snippet_returns_not_found() -> None:
    response = client.post("/migrate/unknown-snippet")

    assert response.status_code == 404


def test_get_patterns_returns_structured_patterns() -> None:
    response = client.get("/patterns")

    assert response.status_code == 200
    data = response.json()
    assert data["patterns"]
    assert data["patterns"][0]["name"]
