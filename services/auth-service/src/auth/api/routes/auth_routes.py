"""
Endpoints HTTP del auth-service.

Capa delgada: recibe DTO, delega al servicio, retorna respuesta.
"""
from fastapi import APIRouter, Depends, status

from auth.api.dependencies import get_auth_service
from auth.api.dtos.register_dto import RegisterRequest, RegisterResponse
from auth.domain.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/health", summary="Estado del auth-service")
async def health() -> dict[str, str]:
    """Endpoint de salud del servicio."""
    return {
        "status": "ok",
        "service": "auth-service",
        "version": "0.1.0",
    }


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nueva cuenta de usuario",
    description=(
        "Crea una cuenta nueva en estado PENDIENTE_APROBACION. "
        "Un administrador debe aprobar y asignar un rol antes de "
        "que el usuario pueda iniciar sesión."
    ),
    responses={
        409: {"description": "Email ya registrado"},
        422: {"description": "Datos de entrada inválidos"},
    },
)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    """Registro de usuario (HU-01)."""
    user = await auth_service.register(
        email=payload.email,
        full_name=payload.full_name,
        plain_password=payload.password,
    )
    return RegisterResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        status=user.status.value,
        created_at=user.created_at,
    )
