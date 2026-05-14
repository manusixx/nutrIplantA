"""
Endpoints de administración de usuarios y /me.
Sprint 7 — HU-18, HU-19, HU-20.
Sprint 8 — HU-15 (/me).
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from auth.api.dependencies import (
    get_admin_service,
    get_current_claims,
    get_user_repository,
    require_admin,
)
from auth.api.dtos.admin_dto import (
    AprobarUsuarioRequest,
    MeResponse,
    ReactivarUsuarioRequest,
    UserAdminResponse,
)
from auth.domain.models.user import User
from auth.domain.services.admin_service import AdminService
from auth.infrastructure.persistence.postgres_user_repository import (
    PostgresUserRepository,
)

router = APIRouter(tags=["admin"])


def _user_to_response(user: User) -> UserAdminResponse:
    return UserAdminResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        status=user.status,
        role=user.role,
        created_at=user.created_at,
    )


# ============================================================
# /me — Sprint 8
# ============================================================
@router.get(
    "/api/v1/auth/me",
    response_model=MeResponse,
    summary="Datos del usuario autenticado (HU-15)",
)
async def me(
    claims: dict[str, object] = Depends(get_current_claims),
    user_repo: PostgresUserRepository = Depends(get_user_repository),
) -> MeResponse:
    """Retornar datos del usuario autenticado extraídos del JWT."""
    user_id = UUID(str(claims["sub"]))
    user = await user_repo.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return MeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        status=user.status,
        role=user.role,
    )


# ============================================================
# Admin — Sprint 7
# ============================================================
@router.get(
    "/api/v1/admin/users",
    response_model=list[UserAdminResponse],
    summary="Listar todos los usuarios (HU-18)",
)
async def listar_usuarios(
    _: dict[str, object] = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
) -> list[UserAdminResponse]:
    """Listar todos los usuarios del sistema. Solo ADMIN."""
    users = await service.listar_todos()
    return [_user_to_response(u) for u in users]


@router.get(
    "/api/v1/admin/users/pendientes",
    response_model=list[UserAdminResponse],
    summary="Listar usuarios pendientes de aprobación (HU-19)",
)
async def listar_pendientes(
    _: dict[str, object] = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
) -> list[UserAdminResponse]:
    """Listar usuarios en estado PENDIENTE_APROBACION."""
    users = await service.listar_pendientes()
    return [_user_to_response(u) for u in users]


@router.post(
    "/api/v1/admin/users/{user_id}/aprobar",
    response_model=UserAdminResponse,
    summary="Aprobar usuario (HU-19)",
)
async def aprobar_usuario(
    user_id: UUID,
    payload: AprobarUsuarioRequest,
    _: dict[str, object] = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
) -> UserAdminResponse:
    """Aprobar un usuario asignándole un rol."""
    user = await service.aprobar(user_id, payload.rol)
    return _user_to_response(user)


@router.post(
    "/api/v1/admin/users/{user_id}/rechazar",
    response_model=UserAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Rechazar usuario",
)
async def rechazar_usuario(
    user_id: UUID,
    _: dict[str, object] = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
) -> UserAdminResponse:
    """Rechazar un usuario pendiente."""
    user = await service.rechazar(user_id)
    return _user_to_response(user)


@router.post(
    "/api/v1/admin/users/{user_id}/desactivar",
    response_model=UserAdminResponse,
    summary="Desactivar usuario (HU-20)",
)
async def desactivar_usuario(
    user_id: UUID,
    _: dict[str, object] = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
) -> UserAdminResponse:
    """Desactivar un usuario aprobado."""
    user = await service.desactivar(user_id)
    return _user_to_response(user)


@router.post(
    "/api/v1/admin/users/{user_id}/reactivar",
    response_model=UserAdminResponse,
    summary="Reactivar usuario",
)
async def reactivar_usuario(
    user_id: UUID,
    payload: ReactivarUsuarioRequest,
    _: dict[str, object] = Depends(require_admin),
    service: AdminService = Depends(get_admin_service),
) -> UserAdminResponse:
    """Reactivar un usuario desactivado."""
    user = await service.reactivar(user_id, payload.rol)
    return _user_to_response(user)
