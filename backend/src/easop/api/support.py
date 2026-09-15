"""Support request and case endpoints."""

from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from easop.domain.support_case import SupportCase
from easop.repositories.support_cases import InMemorySupportCaseRepository
from easop.schemas.support import (
    SupportCaseResponse,
    SupportRequest,
    SupportValidationResponse,
)
from easop.services.support_cases import SupportCaseService

router = APIRouter(prefix="/api/v1/support", tags=["Support"])


@lru_cache
def get_support_case_service() -> SupportCaseService:
    """Share one temporary repository within this Python process."""
    repository = InMemorySupportCaseRepository()
    return SupportCaseService(repository)


def to_response(case: SupportCase) -> SupportCaseResponse:
    return SupportCaseResponse(
        case_id=case.case_id,
        customer_id=case.customer_id,
        message=case.message,
        category=case.category,
        status=case.status,
        created_at=case.created_at,
    )


@router.post("/validate", response_model=SupportValidationResponse)
async def validate_support_request(
    request: SupportRequest,
) -> SupportValidationResponse:
    return SupportValidationResponse(valid=True, request=request)


@router.post(
    "/cases",
    response_model=SupportCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_support_case(
    request: SupportRequest,
    service: Annotated[SupportCaseService, Depends(get_support_case_service)],
) -> SupportCaseResponse:
    case = service.create(request)
    return to_response(case)


@router.get("/cases/{case_id}", response_model=SupportCaseResponse)
def get_support_case(
    case_id: str,
    service: Annotated[SupportCaseService, Depends(get_support_case_service)],
) -> SupportCaseResponse:
    case = service.get(case_id)
    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support case not found",
        )
    return to_response(case)
