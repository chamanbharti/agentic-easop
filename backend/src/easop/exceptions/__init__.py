"""Support-domain exceptions."""


class SupportCaseNotFoundError(Exception):
    """Raised when a requested support case does not exist."""

    def __init__(self, case_id: str) -> None:
        self.case_id = case_id
        super().__init__(f"Support case {case_id} was not found")
