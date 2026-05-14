"""
Servicio de tokens: emite access tokens JWT.

Recibe el secret y los parámetros de configuración por constructor.
NO conoce FastAPI. Devuelve strings.
"""
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt

from auth.domain.models.user import User


class TokenService:
    """Emite y valida JWTs según la política de seguridad del sistema."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
    ) -> None:
        if not secret_key or len(secret_key) < 32:
            raise ValueError(
                "JWT secret debe tener al menos 32 caracteres"
            )
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._access_expire_minutes = access_token_expire_minutes

    def create_access_token(self, user: User) -> str:
        """
        Crear un access token con claims:
        - sub: user_id (UUID como string)
        - email: email del usuario
        - role: rol asignado (validado: usuario debe estar APROBADO con rol)
        - jti: identificador único del token (para blacklist futura)
        - iat: emitido en
        - exp: expira en (15 minutos por defecto)
        """
        if not user.can_login():
            raise ValueError(
                "No se puede emitir token: usuario no puede iniciar sesión"
            )

        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if user.role else None,
            "jti": str(uuid4()),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._access_expire_minutes)).timestamp()),
            "type": "access",
        }
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict[str, object]:
        """
        Decodificar y validar un JWT.

        Raises:
            jwt.ExpiredSignatureError: si expiró.
            jwt.InvalidTokenError: si la firma o estructura es inválida.

        Returns:
            payload del token.
        """
        payload: dict[str, object] = jwt.decode(
        token, self._secret_key, algorithms=[self._algorithm]
    )
        return payload
