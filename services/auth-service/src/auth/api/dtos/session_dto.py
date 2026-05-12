"""DTOs para endpoints de sesión: login, logout, refresh."""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Cuerpo de POST /auth/login."""

    email: EmailStr = Field(..., examples=["agricultor@example.com"])
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Respuesta de POST /auth/login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        default=900,
        description="Segundos hasta expiración del access token (15 min = 900 s)",
    )
    message: str = "Sesión iniciada correctamente"


class RefreshResponse(BaseModel):
    """Respuesta de POST /auth/refresh."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900


class LogoutResponse(BaseModel):
    """Respuesta de POST /auth/logout."""

    message: str = "Sesión cerrada correctamente"
