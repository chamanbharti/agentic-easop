"""Business representation of a support case."""

from dataclasses import dataclass
from datetime import datetime
# from enum import StrEnum

from easop.api.case_status import CaseStatus
from easop.schemas.support import SupportCategory


# class CaseStatus(StrEnum):
#     OPEN = "open"


@dataclass(frozen=True, slots=True)
class SupportCase:
    case_id: str
    customer_id: str
    message: str
    category: SupportCategory
    status: CaseStatus
    created_at: datetime