"""Application composition root."""

from fastapi import FastAPI

from easop.api.error_handlers import support_case_not_found_handler
from easop.api.health import router as health_router
from easop.api.support import router as support_router
from easop.exceptions import SupportCaseNotFoundError
from easop.logging_config import configure_logging
from easop.middleware.request_context import request_context_middleware

configure_logging()

app = FastAPI(title="EASOP API", version="0.1.0")


app.middleware("http")(request_context_middleware)
app.add_exception_handler(
    SupportCaseNotFoundError,
    support_case_not_found_handler,
)

app.include_router(health_router)
app.include_router(support_router)
