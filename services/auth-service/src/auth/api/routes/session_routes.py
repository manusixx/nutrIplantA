"""
Endpoints de sesión: login, logout y refresh de tokens.
Sprint 2 — HU-02 y HU-03.
"""
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Response, status

from auth.api.dependencies import get_session_service
from auth.api.dtos.session_dto import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshResponse,
)
from auth.domain.exceptions.token_exceptions import InvalidRefreshTokenError
from auth.domain.services.session_service import SessionService

router = APIRouter(prefix="/api/v1/auth", tags=["session"])

REFRESH_COOKIE = "refresh_token"

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión (HU-02)",
    responses={
        401: {"description": "Credenciales inválidas"},
        403: {"description": "Cuenta no aprobada o desactivada"},
    },
)
async def login(
    payload: LoginRequest,
    response: Response,
    session_service: SessionService = Depends(get_session_service),
) -> LoginResponse:
    """Login con email y contraseña. Emite access token + refresh token en cookie."""
    access_token, refresh_token = await session_service.login(
        email=payload.email,
        plain_password=payload.password,
    )

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=str(refresh_token.jti),
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth/refresh",
    )

    return LoginResponse(access_token=access_token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión (HU-03)",
)
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    session_service: SessionService = Depends(get_session_service),
) -> LogoutResponse:
    """Logout: revoca el refresh token y elimina la cookie."""
    if refresh_token:
        try:
            jti = UUID(refresh_token)
            await session_service.logout(jti)
        except ValueError:
            pass
        except Exception:  # noqa: BLE001
            pass

    response.delete_cookie(
        key=REFRESH_COOKIE,
        path="/api/v1/auth/refresh",
    )
    return LogoutResponse()


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar access token",
    responses={
        401: {"description": "Refresh token inválido o expirado"},
    },
)
async def refresh_token(
    response: Response,
    refresh_token_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE),
    session_service: SessionService = Depends(get_session_service),
) -> RefreshResponse:
    """Rotar refresh token y emitir nuevo access token."""
    if not refresh_token_cookie:
        raise InvalidRefreshTokenError()

    try:
        jti = UUID(refresh_token_cookie)
    except ValueError as err:
        raise InvalidRefreshTokenError() from err

    new_access, new_refresh = await session_service.refresh(jti)

    response.set_cookie(
        key=REFRESH_COOKIE,
        value=str(new_refresh.jti),
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth/refresh",
    )

    return RefreshResponse(access_token=new_access)
