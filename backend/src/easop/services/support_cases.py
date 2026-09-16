"""Support-case business operations."""

from datetime import UTC, datetime
from uuid import uuid4

from easop.api.case_status import CaseStatus
from easop.domain.support_case import SupportCase
from easop.exceptions import SupportCaseNotFoundError
from easop.repositories.support_cases import SupportCaseRepository
from easop.schemas.support import SupportRequest


class SupportCaseService:
    def __init__(self, repository: SupportCaseRepository) -> None:
        self._repository = repository

    def create(self, request: SupportRequest) -> SupportCase:
        case = SupportCase(
            case_id=f"CASE-{uuid4().hex}",
            customer_id=request.customer_id,
            message=request.message,
            category=request.category,
            status=CaseStatus.OPEN,
            created_at=datetime.now(UTC),
        )
        self._repository.save(case)
        return case

    def get(self, case_id: str) -> SupportCase | None:
        return self._repository.get(case_id)

    def find(self, case_id: str) -> SupportCase | None:
        """Return a case or None when it does not exist."""
        return self._repository.get(case_id)

    def get_required(self, case_id: str) -> SupportCase:
        """Return a case or raise an application-level exception."""
        case = self._repository.get(case_id)

        if case is None:
            raise SupportCaseNotFoundError(case_id)

        return case
