"""
nutrI-plantA diagnostico-service — Sprint 4.

En este sprint: CRUD de cultivos.
Sprints posteriores añadirán: diagnóstico por foto, planes de abono.
"""
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("diagnostico")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("diagnostico-service iniciando...")
    yield
    logger.info("diagnostico-service detenido")


app = FastAPI(
    title="nutrI-plantA diagnostico-service",
    description="Servicio de diagnóstico nutricional y fitosanitario en vid",
    version="0.1.0",
    docs_url="/api/v1/diagnostico/docs",
    openapi_url="/api/v1/diagnostico/openapi.json",
    lifespan=lifespan,
)


@app.get("/api/v1/diagnostico/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "diagnostico-service", "version": "0.1.0"}
