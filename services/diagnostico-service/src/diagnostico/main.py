"""
nutrI-plantA diagnostico-service — Sprint 9.

Sprint 9: persistencia real en PostgreSQL para todos los repositorios.
"""
import logging
import os
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from diagnostico.api.routes.cultivo_routes import _get_cultivo_service
from diagnostico.api.routes.cultivo_routes import router as cultivo_router
from diagnostico.api.routes.diagnostico_routes import (
    _get_diagnostico_service,
    _get_plan_service,
)
from diagnostico.api.routes.diagnostico_routes import router as diagnostico_router
from diagnostico.config import get_settings
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
from diagnostico.infrastructure.persistence.database import (
    create_engine,
    create_session_factory,
)
from diagnostico.infrastructure.persistence.postgres_cultivo_repository import (
    PostgresCultivoRepository,
)
from diagnostico.infrastructure.persistence.postgres_diagnostico_repository import (
    PostgresDiagnosticoRepository,
)
from diagnostico.infrastructure.persistence.postgres_plan_abono_repository import (
    PostgresPlanAbonoRepository,
    PostgresRecordatorioRepository,
)
from diagnostico.infrastructure.vision.mock_vision_provider import MockVisionProvider

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("diagnostico")

# Estado global inicializado en lifespan
_session_factory: async_sessionmaker[AsyncSession] | None = None
_vision_provider: MockVisionProvider | None = None

def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Session factory no inicializada")
    return _session_factory

def _get_vision_provider() -> MockVisionProvider:
    if _vision_provider is None:
        raise RuntimeError("Vision provider no inicializado")
    return _vision_provider

# ============================================================
# Dependencias de sesión
# ============================================================
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Generador de sesión con rollback y close garantizados."""
    async with _get_session_factory()() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Singleton a nivel de módulo — evita B008
DB_SESSION = Depends(get_db_session)

async def get_cultivo_svc(
    session: AsyncSession = DB_SESSION,
) -> CultivoService:
    return CultivoService(PostgresCultivoRepository(session))

async def get_diagnostico_svc(
    session: AsyncSession = DB_SESSION,
) -> DiagnosticoService:
    return DiagnosticoService(
        PostgresDiagnosticoRepository(session),
        PostgresCultivoRepository(session),
        _get_vision_provider(),
    )

async def get_plan_svc(
    session: AsyncSession = DB_SESSION,
) -> PlanAbonoService:
    return PlanAbonoService(
        PostgresDiagnosticoRepository(session),
        PostgresPlanAbonoRepository(session),
        PostgresRecordatorioRepository(session),
    )

# ============================================================
# Lifespan
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global _session_factory, _vision_provider

    settings = get_settings()
    engine = create_engine(settings.database_url)
    _session_factory = create_session_factory(engine)
    _vision_provider = MockVisionProvider()

    logger.info("diagnostico-service iniciando con PostgreSQL...")

    app.dependency_overrides[_get_cultivo_service] = get_cultivo_svc
    app.dependency_overrides[_get_diagnostico_service] = get_diagnostico_svc
    app.dependency_overrides[_get_plan_service] = get_plan_svc

    yield

    await engine.dispose()
    logger.info("diagnostico-service detenido")

# ============================================================
# App
# ============================================================
app = FastAPI(
    title="nutrI-plantA diagnostico-service",
    description="Servicio de diagnóstico nutricional y fitosanitario en vid",
    version="0.3.0",
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
    return {"status": "ok", "service": "diagnostico-service", "version": "0.3.0"}
