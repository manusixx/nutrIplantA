"""DTOs para endpoints de administración de usuarios."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from auth.domain.models.user import UserRole, UserStatus


class UserAdminResponse(BaseModel):
    """Respuesta con datos de usuario para admin."""
    id: UUID
    email: str
    full_name: str
    status: UserStatus
    role: UserRole | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AprobarUsuarioRequest(BaseModel):
    """Request para aprobar un usuario."""
    rol: UserRole


class ReactivarUsuarioRequest(BaseModel):
    """Request para reactivar un usuario."""
    rol: UserRole


class MeResponse(BaseModel):
    """Datos del usuario autenticado (endpoint /me)."""
    id: UUID
    email: str
    full_name: str
    status: UserStatus
    role: UserRole | None
