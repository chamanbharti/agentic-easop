"""Application composition root."""

from fastapi import FastAPI

from easop.api.health import router as health_router
from easop.api.support import router as support_router

app = FastAPI(title="EASOP API", version="0.1.0")

app.include_router(health_router)
app.include_router(support_router)
