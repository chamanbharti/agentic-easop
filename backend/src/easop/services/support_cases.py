"""Support-case business operations."""

from datetime import datetime, UTC
from uuid import uuid4

from easop.domain.support_case import CaseStatus, SupportCase
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
