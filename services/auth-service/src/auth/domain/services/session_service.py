"""
Servicio de sesión: login, logout y rotación de refresh tokens.
"""
from uuid import UUID

from auth.domain.exceptions.token_exceptions import (
    InvalidRefreshTokenError,
    TokenReuseDetectedError,
)
from auth.domain.models.refresh_token import RefreshToken
from auth.domain.repositories.i_refresh_token_repository import IRefreshTokenRepository
from auth.domain.repositories.i_user_repository import IUserRepository
from auth.domain.services.auth_service import AuthService
from auth.domain.services.token_service import TokenService


class SessionService:
    """Caso de uso: gestión de sesiones de usuario."""

    def __init__(
        self,
        auth_service: AuthService,
        token_service: TokenService,
        refresh_token_repo: IRefreshTokenRepository,
        user_repo: IUserRepository,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self._auth = auth_service
        self._token = token_service
        self._rt_repo = refresh_token_repo
        self._user_repo = user_repo
        self._expire_days = refresh_token_expire_days

    async def login(self, email: str, plain_password: str) -> tuple[str, RefreshToken]:
        """
        Autenticar usuario y emitir par de tokens.

        Returns:
            Tupla (access_token_str, refresh_token_entity).

        Raises:
            InvalidCredentialsError, UserNotApprovedError, UserDeactivatedError
        """
        user = await self._auth.authenticate(email, plain_password)
        access_token = self._token.create_access_token(user)
        refresh_token = RefreshToken.create(user.id, self._expire_days)
        await self._rt_repo.save(refresh_token)
        return access_token, refresh_token

    async def logout(self, refresh_token_jti: UUID) -> None:
        """Cerrar sesión revocando el refresh token. Idempotente."""
        token = await self._rt_repo.find_by_jti(refresh_token_jti)
        if token and not token.is_revoked:
            token.revoke()
            await self._rt_repo.save(token)

    async def refresh(self, refresh_token_jti: UUID) -> tuple[str, RefreshToken]:
        """
        Rotar refresh token y emitir nuevo par de tokens.

        Si detecta reuso de token ya rotado, revoca todos los tokens
        del usuario (señal de posible robo) y lanza TokenReuseDetectedError.
        """
        token = await self._rt_repo.find_by_jti(refresh_token_jti)

        if token is None:
            raise InvalidRefreshTokenError()

        if not token.is_valid:
            activos = await self._rt_repo.find_active_by_user(token.user_id)
            hijo_existe = any(t.parent_jti == token.jti for t in activos)
            if hijo_existe:
                await self._rt_repo.revoke_all_for_user(token.user_id)
                raise TokenReuseDetectedError()
            raise InvalidRefreshTokenError()

        new_refresh = token.rotate(self._expire_days)
        await self._rt_repo.save(token)
        await self._rt_repo.save(new_refresh)

        user = await self._user_repo.find_by_id(token.user_id)
        if user is None or not user.can_login():
            await self._rt_repo.revoke_all_for_user(token.user_id)
            raise InvalidRefreshTokenError()

        new_access = self._token.create_access_token(user)
        return new_access, new_refresh
