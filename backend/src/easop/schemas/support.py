"""Validated contracts for support request intake."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime

# from easop.domain.support_case import CaseStatus

# from easop.domain.support_case import CaseStatus
from easop.api.case_status import CaseStatus
from easop.domain.support_category import SupportCategory


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


class SupportCaseResponse(BaseModel):
    case_id: str
    customer_id: str
    message: str
    category: SupportCategory
    status: CaseStatus
    created_at: datetime
