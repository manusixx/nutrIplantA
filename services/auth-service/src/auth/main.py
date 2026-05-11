"""
Aplicación FastAPI del auth-service.

Sprint 1: HU-01 (registro). Login y refresh tokens vienen en sprints
posteriores.
"""
import logging
import os
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from auth.api.exception_handler import register_exception_handlers
from auth.api.routes.auth_routes import router as auth_router
from auth.container import Container

# Configurar logging básico
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("auth")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Eventos de inicio y cierre."""
    # Inicialización del container DI
    container = Container()
    app.state.container = container

    logger.info("auth-service iniciando...")
    logger.info(f"Entorno: {os.getenv('APP_ENV', 'unknown')}")

    yield

    # Cierre limpio
    engine = container.engine()
    await engine.dispose()
    logger.info("auth-service detenido")


app = FastAPI(
    title="nutrI-plantA auth-service",
    description="Servicio de autenticación y gestión de usuarios",
    version="0.1.0",
    docs_url="/api/v1/auth/docs",
    openapi_url="/api/v1/auth/openapi.json",
    lifespan=lifespan,
)

# Registrar handlers de excepciones
register_exception_handlers(app)

# Registrar rutas
app.include_router(auth_router)
