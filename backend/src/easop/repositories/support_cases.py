"""Storage contract and temporary in-memory implementation."""

from threading import Lock
from typing import Protocol

from easop.domain.support_case import SupportCase


class SupportCaseRepository(Protocol):
    def save(self, case: SupportCase) -> None: ...

    def get(self, case_id: str) -> SupportCase | None: ...


class InMemorySupportCaseRepository:
    def __init__(self) -> None:
        self._cases: dict[str, SupportCase] = {}
        self._lock = Lock()

    def save(self, case: SupportCase) -> None:
        with self._lock:
            self._cases[case.case_id] = case

    def get(self, case_id: str) -> SupportCase | None:
        with self._lock:
            return self._cases.get(case_id)
