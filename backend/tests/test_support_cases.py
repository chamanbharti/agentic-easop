"""Business and HTTP tests for support-case intake."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from easop.api.case_status import CaseStatus
from easop.api.support import get_support_case_service

# from easop.domain.support_case import CaseStatus
from easop.domain.support_category import SupportCategory
from easop.exceptions import SupportCaseNotFoundError
from easop.main import app
from easop.repositories.support_cases import InMemorySupportCaseRepository

# from easop.schemas.support import SupportCategory, SupportRequest
from easop.schemas.support import SupportRequest
from easop.services.support_cases import SupportCaseService

VALID_REQUEST = {
    "customer_id": "CUST-1001",
    "message": "My order arrived damaged.",
    "category": "order",
}


@pytest.fixture
def client() -> Iterator[TestClient]:
    service = SupportCaseService(InMemorySupportCaseRepository())

    def override_service() -> SupportCaseService:
        return service

    app.dependency_overrides[get_support_case_service] = override_service
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_support_case_service, None)


def test_service_creates_open_case() -> None:
    service = SupportCaseService(InMemorySupportCaseRepository())
    request = SupportRequest.model_validate(VALID_REQUEST)

    case = service.create(request)

    assert case.case_id.startswith("CASE-")
    assert case.status == CaseStatus.OPEN
    assert case.message == "My order arrived damaged."
    assert service.get(case.case_id) == case


def test_post_creates_case_and_get_retrieves_it(client: TestClient) -> None:
    created = client.post("/api/v1/support/cases", json=VALID_REQUEST)

    assert created.status_code == 201
    body = created.json()
    assert body["case_id"].startswith("CASE-")
    assert body["customer_id"] == "CUST-1001"
    assert body["message"] == "My order arrived damaged."
    assert body["category"] == SupportCategory.ORDER
    assert body["status"] == "open"
    # assert body["created_at"].endswith("+00:00")
    assert body["created_at"].endswith("+00:00") or body["created_at"].endswith("Z")

    retrieved = client.get(f"/api/v1/support/cases/{body['case_id']}")
    assert retrieved.status_code == 200
    assert retrieved.json() == body


def test_unknown_case_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/support/cases/CASE-unknown")

    assert response.status_code == 404
    # assert response.json() == {"detail": "Support case not found"}
    body = response.json()

    assert body["code"] == "SUPPORT_CASE_NOT_FOUND"
    assert body["message"] == "Support case CASE-unknown was not found"
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_invalid_input_does_not_create_a_case(client: TestClient) -> None:
    response = client.post(
        "/api/v1/support/cases",
        json={**VALID_REQUEST, "message": "short"},
    )
    assert response.status_code == 422


def test_two_posts_create_distinct_cases(client: TestClient) -> None:
    first = client.post("/api/v1/support/cases", json=VALID_REQUEST)
    second = client.post("/api/v1/support/cases", json=VALID_REQUEST)

    assert first.status_code == second.status_code == 201
    assert first.json()["case_id"] != second.json()["case_id"]


def test_get_required_raises_when_case_does_not_exist() -> None:
    service = SupportCaseService(InMemorySupportCaseRepository())

    with pytest.raises(
        SupportCaseNotFoundError,
        match="Support case CASE-unknown was not found",
    ):
        service.get_required("CASE-unknown")
