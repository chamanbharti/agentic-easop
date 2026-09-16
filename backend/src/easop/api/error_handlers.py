"""Mapping between application errors and HTTP responses."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

# from easop.exceptions.support import SupportCaseNotFoundError
from easop.exceptions import SupportCaseNotFoundError
from easop.schemas.support import ApiErrorResponse


async def support_case_not_found_handler(
    request: Request,
    # exception: SupportCaseNotFoundError,
    exception: Exception,  # Must be Exception
) -> JSONResponse:

    if not isinstance(exception, SupportCaseNotFoundError):
        raise exception

    request_id: str = request.state.request_id

    error = ApiErrorResponse(
        code="SUPPORT_CASE_NOT_FOUND",
        message=str(exception),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=error.model_dump(),
    )
