"""Support request validation endpoints."""

from fastapi import APIRouter

from easop.schemas.support import SupportRequest, SupportValidationResponse

router = APIRouter(
    prefix="/api/v1/support",
    tags=["Support"],
)


@router.post(
    "/validate",
    response_model=SupportValidationResponse,
)
async def validate_support_request(
    request: SupportRequest,
) -> SupportValidationResponse:
    """Return the validated and normalized support request."""
    return SupportValidationResponse(
        valid=True,
        request=request,
    )
