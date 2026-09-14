"""Lightweight process liveness endpoint."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Public liveness response; does not describe dependency readiness."""

    status: Literal["ok"]
    service: Literal["easop-api"]


@router.get("/live", response_model=HealthResponse)
async def get_liveness() -> HealthResponse:
    """Confirm the API process can respond without querying dependencies."""
    return HealthResponse(status="ok", service="easop-api")
