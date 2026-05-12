"""
nutrI-plantA diagnostico-service — Sprints 5 y 6.

Sprints 5-6: CRUD cultivos + diagnóstico con MockVisionProvider + planes de abono.
"""
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from diagnostico.api.routes.cultivo_routes import _get_cultivo_service
from diagnostico.api.routes.cultivo_routes import router as cultivo_router
from diagnostico.api.routes.diagnostico_routes import (
    _get_diagnostico_service,
    _get_plan_service,
)
from diagnostico.api.routes.diagnostico_routes import router as diagnostico_router
from diagnostico.domain.exceptions import (
    CultivoNoAutorizadoError,
    CultivoNotFoundError,
    DiagnosticoDomainError,
    DiagnosticoNotFoundError,
    PlantaEnfermaError,
    RecordatorioNotFoundError,
)
from diagnostico.domain.services.cultivo_service import CultivoService
from diagnostico.domain.services.diagnostico_service import DiagnosticoService
from diagnostico.domain.services.plan_abono_service import PlanAbonoService
from diagnostico.infrastructure.persistence.in_memory_cultivo_repository import (
    InMemoryCultivoRepository,
)
from diagnostico.infrastructure.persistence.in_memory_diagnostico_repository import (
    InMemoryDiagnosticoRepository,
    InMemoryPlanAbonoRepository,
    InMemoryRecordatorioRepository,
)
from diagnostico.infrastructure.vision.mock_vision_provider import MockVisionProvider

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("diagnostico")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("diagnostico-service iniciando...")

    # Repositorios en memoria (en producción serían Postgres)
    cultivo_repo = InMemoryCultivoRepository()
    diagnostico_repo = InMemoryDiagnosticoRepository()
    plan_repo = InMemoryPlanAbonoRepository()
    rec_repo = InMemoryRecordatorioRepository()
    vision_provider = MockVisionProvider()

    # Servicios
    cultivo_svc = CultivoService(cultivo_repo)
    diagnostico_svc = DiagnosticoService(diagnostico_repo, cultivo_repo, vision_provider)
    plan_svc = PlanAbonoService(diagnostico_repo, plan_repo, rec_repo)

    # Inyectar en routers via override
    app.dependency_overrides[_get_cultivo_service] = lambda: cultivo_svc
    app.dependency_overrides[_get_diagnostico_service] = lambda: diagnostico_svc
    app.dependency_overrides[_get_plan_service] = lambda: plan_svc

    yield

    logger.info("diagnostico-service detenido")


app = FastAPI(
    title="nutrI-plantA diagnostico-service",
    description="Servicio de diagnóstico nutricional y fitosanitario en vid",
    version="0.2.0",
    docs_url="/api/v1/diagnostico/docs",
    openapi_url="/api/v1/diagnostico/openapi.json",
    lifespan=lifespan,
)


# ============================================================
# Exception handlers
# ============================================================
@app.exception_handler(CultivoNotFoundError)
async def cultivo_not_found(request: Request, exc: CultivoNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "cultivo_not_found", "message": exc.message})


@app.exception_handler(DiagnosticoNotFoundError)
async def diagnostico_not_found(request: Request, exc: DiagnosticoNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "diagnostico_not_found", "message": exc.message})


@app.exception_handler(RecordatorioNotFoundError)
async def recordatorio_not_found(request: Request, exc: RecordatorioNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "recordatorio_not_found", "message": exc.message})


@app.exception_handler(CultivoNoAutorizadoError)
async def no_autorizado(request: Request, exc: CultivoNoAutorizadoError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"error": "forbidden", "message": exc.message})


@app.exception_handler(PlantaEnfermaError)
async def planta_enferma(request: Request, exc: PlantaEnfermaError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "planta_enferma", "message": exc.message})


@app.exception_handler(DiagnosticoDomainError)
async def domain_error(request: Request, exc: DiagnosticoDomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"error": "domain_error", "message": exc.message})


@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Error no manejado: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "message": "Error interno. Intente más tarde"},
    )


# ============================================================
# Routers
# ============================================================
app.include_router(cultivo_router)
app.include_router(diagnostico_router)


@app.get("/api/v1/diagnostico/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "diagnostico-service", "version": "0.2.0"}
