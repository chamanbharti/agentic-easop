"""Supported business categories."""

from enum import StrEnum


class SupportCategory(StrEnum):
    GENERAL = "general"
    ORDER = "order"
    BILLING = "billing"
