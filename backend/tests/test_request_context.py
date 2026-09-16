"""Tests for request correlation and error contracts."""

from uuid import UUID

from fastapi.testclient import TestClient

from easop.main import app


def test_response_contains_generated_request_id() -> None:
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200

    request_id = response.headers["X-Request-ID"]
    assert str(UUID(request_id)) == request_id


def test_valid_client_request_id_is_preserved() -> None:
    request_id = "c0a80121-1234-4abc-8def-1234567890ab"

    with TestClient(app) as client:
        response = client.get(
            "/health/live",
            headers={"X-Request-ID": request_id},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


def test_invalid_client_request_id_is_replaced() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/health/live",
            headers={"X-Request-ID": "not-a-valid-uuid"},
        )

    returned_id = response.headers["X-Request-ID"]

    assert returned_id != "not-a-valid-uuid"
    assert str(UUID(returned_id)) == returned_id


def test_missing_case_returns_standard_error_contract() -> None:
    request_id = "c0a80121-1234-4abc-8def-1234567890ab"

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/support/cases/CASE-unknown",
            headers={"X-Request-ID": request_id},
        )

    assert response.status_code == 404
    assert response.headers["X-Request-ID"] == request_id
    assert response.json() == {
        "code": "SUPPORT_CASE_NOT_FOUND",
        "message": "Support case CASE-unknown was not found",
        "request_id": request_id,
    }


def test_validation_error_also_contains_request_id() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/support/cases",
            json={
                "customer_id": "INVALID",
                "message": "short",
            },
        )

    assert response.status_code == 422
    assert str(UUID(response.headers["X-Request-ID"]))
