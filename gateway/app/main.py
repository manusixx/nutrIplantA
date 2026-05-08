"""
nutrI-plantA Gateway — Sprint 0

API Gateway. En esta versión solo expone un endpoint /health.
Sprints posteriores añadirán: validación JWT, routing, rate limiting.
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

# ============================================================
# Configuración de logging estructurado
# ============================================================
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("gateway")


# ============================================================
# Modelos de respuesta
# ============================================================
class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud."""
    status: str
    version: str
    service: str


# ============================================================
# Lifespan: inicialización y cierre limpio
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Eventos de inicio y cierre de la aplicación."""
    logger.info("nutrI-plantA Gateway iniciando...")
    logger.info(f"Entorno: {os.getenv('APP_ENV', 'unknown')}")
    yield
    logger.info("nutrI-plantA Gateway deteniéndose...")


# ============================================================
# Aplicación FastAPI
# ============================================================
app = FastAPI(
    title="nutrI-plantA Gateway",
    description="API Gateway para diagnóstico nutricional y fitosanitario en vid",
    version="0.1.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)


# ============================================================
# Endpoints
# ============================================================
@app.get(
    "/api/v1/health",
    response_model=HealthResponse,
    summary="Estado del gateway",
    tags=["health"],
)
async def health() -> HealthResponse:
    """
    Endpoint de salud para verificar que el gateway está operativo.

    Retorna el estado, versión y nombre del servicio. Usado por:
    - Healthcheck de Docker.
    - Monitoreo externo (futuro).
    - Smoke tests del Sprint 0.
    """
    return HealthResponse(
        status="ok",
        version="0.1.0",
        service="nutrI-plantA gateway",
    )


@app.get(
    "/",
    summary="Root",
    tags=["root"],
)
async def root() -> dict:
    """Página de bienvenida básica."""
    return {
        "message": "nutrI-plantA Gateway",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health",
    }
