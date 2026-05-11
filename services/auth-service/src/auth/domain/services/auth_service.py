"""
Servicio de aplicación: AuthService.

Orquesta la lógica de registro y login. Recibe sus dependencias
por constructor (Dependency Injection). NO conoce SQLAlchemy ni FastAPI.
"""
from auth.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UserDeactivatedError,
    UserNotApprovedError,
)
from auth.domain.models.user import User, UserStatus
from auth.domain.repositories.i_password_hasher import IPasswordHasher
from auth.domain.repositories.i_user_repository import IUserRepository


class AuthService:
    """Caso de uso: registro y autenticación de usuarios."""

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._user_repo = user_repository
        self._hasher = password_hasher

    async def register(
        self,
        email: str,
        full_name: str,
        plain_password: str,
    ) -> User:
        """
        Registrar un usuario nuevo.

        Reglas:
        - El email no debe existir previamente.
        - La contraseña se hashea con Argon2id antes de persistir.
        - El usuario queda en estado PENDIENTE_APROBACION sin rol asignado.

        Raises:
            EmailAlreadyRegisteredError: si el email ya está registrado.

        Returns:
            User: el usuario creado.
        """
        # Normalizar email (lowercase) para consistencia
        normalized_email = email.strip().lower()

        # Validar que el email no exista
        if await self._user_repo.email_exists(normalized_email):
            raise EmailAlreadyRegisteredError(normalized_email)

        # Hashear la contraseña
        password_hash = self._hasher.hash(plain_password)

        # Crear el usuario en estado inicial
        user = User(
            email=normalized_email,
            full_name=full_name.strip(),
            password_hash=password_hash,
        )

        # Persistir
        return await self._user_repo.save(user)

    async def authenticate(
        self,
        email: str,
        plain_password: str,
    ) -> User:
        """
        Autenticar un usuario por email y contraseña.

        Reglas:
        - Si el usuario no existe, lanzar InvalidCredentialsError
          (mismo mensaje que contraseña incorrecta para evitar
          enumeración de cuentas).
        - Si la contraseña no coincide, mismo error.
        - Si el estado es PENDIENTE_APROBACION, lanzar UserNotApprovedError.
        - Si el estado es DESACTIVADO o RECHAZADO, lanzar UserDeactivatedError.

        Raises:
            InvalidCredentialsError, UserNotApprovedError, UserDeactivatedError

        Returns:
            User autenticado y autorizado para iniciar sesión.
        """
        normalized_email = email.strip().lower()
        user = await self._user_repo.find_by_email(normalized_email)

        # No existe → error genérico (anti-enumeración)
        if user is None:
            raise InvalidCredentialsError()

        # Contraseña incorrecta → mismo error genérico
        if not self._hasher.verify(plain_password, user.password_hash):
            raise InvalidCredentialsError()

        # Verificar estado de la cuenta
        if user.status == UserStatus.PENDIENTE_APROBACION:
            raise UserNotApprovedError()
        if user.status in (UserStatus.DESACTIVADO, UserStatus.RECHAZADO):
            raise UserDeactivatedError()

        return user
