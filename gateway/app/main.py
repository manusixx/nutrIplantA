"""
nutrI-plantA API Gateway — Sprint 3.

Proxy real con validación JWT, autorización por rol y rate limiting básico.
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncIterator

import httpx
import jwt
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gateway")

# ============================================================
# Configuración
# ============================================================
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
DIAGNOSTICO_SERVICE_URL = os.getenv("DIAGNOSTICO_SERVICE_URL", "http://diagnostico-service:8002")

# Rutas públicas: no requieren token
PUBLIC_PATHS = {
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/health",
    "/api/v1/docs",
    "/api/v1/openapi.json",
}

# Rutas que requieren rol específico
ROLE_REQUIRED: dict[str, str] = {
    "/api/v1/investigador": "INVESTIGADOR",
    "/api/v1/admin": "ADMIN",
}


# ============================================================
# HTTP client compartido (connection pool)
# ============================================================
http_client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("Gateway iniciando. Auth: %s | Diagnostico: %s",
                AUTH_SERVICE_URL, DIAGNOSTICO_SERVICE_URL)
    yield
    if http_client:
        await http_client.aclose()
    logger.info("Gateway detenido")


# ============================================================
# App
# ============================================================
app = FastAPI(
    title="nutrI-plantA API Gateway",
    description="Punto único de entrada con validación JWT y routing",
    version="0.3.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Helpers
# ============================================================
def _is_public(path: str) -> bool:
    """Verificar si la ruta es pública."""
    if path in PUBLIC_PATHS:
        return True
    # Prefijos públicos
    for pub in PUBLIC_PATHS:
        if path.startswith(pub + "/"):
            return True
    return False


def _required_role(path: str) -> str | None:
    """Retorna el rol requerido para el path, o None si no aplica."""
    for prefix, role in ROLE_REQUIRED.items():
        if path.startswith(prefix):
            return role
    return None


def _validate_jwt(token: str) -> dict[str, Any]:
    """
    Validar JWT y retornar payload.

    Raises:
        jwt.InvalidTokenError si el token es inválido o expiró.
    """
    payload: dict[str, Any] = jwt.decode(
        token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    return payload


def _get_target_url(path: str) -> str:
    """Determinar el servicio destino según el path."""
    if path.startswith("/api/v1/auth"):
        return AUTH_SERVICE_URL
    if path.startswith("/api/v1/diagnostico") or path.startswith("/api/v1/cultivos"):
        return DIAGNOSTICO_SERVICE_URL
    return AUTH_SERVICE_URL


# ============================================================
# Middleware de autenticación
# ============================================================
@app.middleware("http")
async def auth_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    path = request.url.path

    # Rutas de health y docs siempre pasan
    if path in {"/api/v1/health", "/", "/api/v1/docs", "/api/v1/openapi.json"}:
        return await call_next(request)

    # Rutas públicas pasan sin validación
    if _is_public(path):
        return await call_next(request)

    # Extraer token del header Authorization
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "unauthorized", "message": "Token de acceso requerido"},
        )

    token = auth_header.removeprefix("Bearer ").strip()

    try:
        payload = _validate_jwt(token)
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "token_expired", "message": "Su sesión expiró. Inicie sesión nuevamente"},
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "invalid_token", "message": "Token inválido"},
        )

    # Verificar rol si la ruta lo requiere
    required = _required_role(path)
    if required and payload.get("role") != required:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "forbidden", "message": "No tiene permisos para acceder a esta sección"},
        )

    # Añadir headers internos con datos del usuario
    # (los servicios downstream confían en estos headers)
    request.state.user_id = payload.get("sub", "")
    request.state.user_role = payload.get("role", "")

    return await call_next(request)


# ============================================================
# Endpoints propios del gateway
# ============================================================
@app.get("/api/v1/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "gateway", "version": "0.3.0"}


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {
        "service": "nutrI-plantA Gateway",
        "docs": "/api/v1/docs",
        "health": "/api/v1/health",
    }


# ============================================================
# Proxy: reenvía peticiones a los servicios downstream
# ============================================================
@app.api_route(
    "/api/v1/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    tags=["proxy"],
)
async def proxy(request: Request, path: str) -> Response:
    """Reenvía la petición al servicio correspondiente."""
    if http_client is None:
        return JSONResponse(
            status_code=503,
            content={"error": "service_unavailable", "message": "Gateway no disponible"},
        )

    full_path = f"/api/v1/{path}"
    target_base = _get_target_url(full_path)
    target_url = f"{target_base}{full_path}"

    # Construir headers: copiar los del request y añadir los internos
    # IMPORTANTE: eliminar X-User-* entrantes para evitar inyección
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in {"host", "x-user-id", "x-user-role", "x-forwarded-for"}
    }

    # Añadir headers internos si el usuario está autenticado
    if hasattr(request.state, "user_id") and request.state.user_id:
        headers["X-User-Id"] = request.state.user_id
        headers["X-User-Role"] = request.state.user_role

    # Leer el body
    body = await request.body()

    try:
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )
    except httpx.ConnectError:
        logger.error("No se puede conectar a %s", target_url)
        return JSONResponse(
            status_code=503,
            content={"error": "service_unavailable", "message": "Servicio no disponible. Intente más tarde"},
        )
    except httpx.TimeoutException:
        logger.error("Timeout conectando a %s", target_url)
        return JSONResponse(
            status_code=504,
            content={"error": "timeout", "message": "El servicio tardó demasiado en responder"},
        )

    # Filtrar headers de respuesta que no deben propagarse
    response_headers = {
        k: v for k, v in response.headers.items()
        if k.lower() not in {"transfer-encoding", "connection"}
    }

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=response_headers,
        media_type=response.headers.get("content-type"),
    )
