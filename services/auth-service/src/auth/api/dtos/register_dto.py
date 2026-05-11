"""
Data Transfer Objects (DTOs) para el endpoint de registro.

Validación con Pydantic v2. Los mensajes de error de campo son
internos; el endpoint los traduce a mensajes en español para el usuario.
"""
import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

# Regex para contraseña: mín 10 chars, 1 mayúscula, 1 minúscula, 1 dígito, 1 especial
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':\",.<>/?\\|`~]).{10,}$"
)


class RegisterRequest(BaseModel):
    """Cuerpo de la petición POST /auth/register."""

    email: EmailStr = Field(
        ...,
        description="Correo electrónico (RFC 5322)",
        examples=["agricultor@example.com"],
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nombre completo del usuario",
        examples=["Manuel Pastrana"],
    )
    password: str = Field(
        ...,
        min_length=10,
        max_length=128,
        description="Contraseña: mín 10 caracteres con mayúscula, minúscula, número y carácter especial",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not _PASSWORD_PATTERN.match(v):
            raise ValueError(
                "La contraseña debe tener al menos 10 caracteres con "
                "mayúscula, minúscula, número y carácter especial"
            )
        return v

    @field_validator("full_name")
    @classmethod
    def strip_full_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("El nombre no puede estar vacío")
        return stripped


class RegisterResponse(BaseModel):
    """Respuesta del POST /auth/register."""

    id: UUID
    email: EmailStr
    full_name: str
    status: str
    created_at: datetime
    message: str = Field(
        default="Su cuenta fue creada. Un administrador asignará su rol pronto",
        description="Mensaje en español para mostrar al usuario",
    )
