"""Validated contracts for support request intake."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SupportCategory(StrEnum):
    GENERAL = "general"
    ORDER = "order"
    BILLING = "billing"


class SupportRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    customer_id: str = Field(
        pattern=r"^CUST-[0-9]+$",
        max_length=40,
    )
    message: str = Field(
        min_length=10,
        max_length=2000,
    )
    category: SupportCategory = SupportCategory.GENERAL


class SupportValidationResponse(BaseModel):
    valid: Literal[True]
    request: SupportRequest
