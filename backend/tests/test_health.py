"""HTTP contract tests for the liveness endpoint."""

from fastapi.testclient import TestClient

from easop.main import app


def test_liveness_returns_http_200() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200


def test_liveness_returns_exact_public_contract() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "status": "ok",
        "service": "easop-api",
    }
