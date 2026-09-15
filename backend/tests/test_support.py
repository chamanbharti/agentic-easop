"""Support intake API contract tests."""

import pytest
from fastapi.testclient import TestClient

from easop.main import app


def test_valid_request_returns_normalized_body() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/support/validate",
            json={
                "customer_id": "CUST-1001",
                "message": "  My order arrived damaged.  ",
                "category": "order",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "valid": True,
        "request": {
            "customer_id": "CUST-1001",
            "message": "My order arrived damaged.",
            "category": "order",
        },
    }


def test_omitted_category_defaults_to_general() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/support/validate",
            json={
                "customer_id": "CUST-1001",
                "message": "Please explain your support policy.",
            },
        )

    assert response.status_code == 200
    assert response.json()["request"]["category"] == "general"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("customer_id", "INVALID"),
        ("message", "short"),
        ("message", " " * 20),
        ("message", "x" * 2001),
        ("category", "refund"),
        ("unexpected_field", "unsupported"),
    ],
)
def test_invalid_input_returns_field_error(
    field: str,
    value: str,
) -> None:
    payload = {
        "customer_id": "CUST-1001",
        "message": "My order arrived damaged.",
        "category": "order",
    }
    payload[field] = value

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/support/validate",
            json=payload,
        )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"] == ["body", field] for error in errors)


def test_missing_message_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/support/validate",
            json={"customer_id": "CUST-1001"},
        )

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", "message"] for error in response.json()["detail"]
    )
