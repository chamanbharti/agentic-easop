"""Request correlation and access logging middleware."""

import logging
from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import UUID, uuid4

from fastapi import Request, Response

logger = logging.getLogger("easop.access")

CallNext = Callable[[Request], Awaitable[Response]]


def resolve_request_id(header_value: str | None) -> str:
    """Reuse a valid UUID request ID or generate a new one."""
    if header_value is not None:
        try:
            return str(UUID(header_value))
        except ValueError:
            pass

    return str(uuid4())


async def request_context_middleware(
    request: Request,
    call_next: CallNext,
) -> Response:
    request_id = resolve_request_id(request.headers.get("X-Request-ID"))
    request.state.request_id = request_id

    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((perf_counter() - started_at) * 1000, 2)

        logger.exception(
            "request_failed",
            extra={
                "event": "request_failed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
        )
        raise

    duration_ms = round((perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_completed",
        extra={
            "event": "request_completed",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    return response
