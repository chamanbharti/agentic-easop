"""Application composition root."""

from fastapi import FastAPI

from easop.api.health import router as health_router

app = FastAPI(title="EASOP API", version="0.1.0")
app.include_router(health_router)
