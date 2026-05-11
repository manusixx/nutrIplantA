"""
Exception handler global del auth-service.

Traduce excepciones de dominio a respuestas HTTP coherentes.
La capa API es la única que conoce de HTTP; el dominio solo lanza
excepciones puras.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from auth.domain.exceptions import (
    AuthDomainError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UserDeactivatedError,
    UserNotApprovedError,
    UserNotFoundError,
)

logger = logging.getLogger("auth.exception_handler")


def register_exception_handlers(app: FastAPI) -> None:
    """Registrar todos los handlers de excepciones."""

    @app.exception_handler(EmailAlreadyRegisteredError)
    async def email_already_registered(
        request: Request, exc: EmailAlreadyRegisteredError
    ) -> JSONResponse:
        # 409 Conflict
        return JSONResponse(
            status_code=409,
            content={
                "error": "email_already_registered",
                "message": "Este correo ya está registrado. Inicie sesión o recupere su contraseña",
            },
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials(
        request: Request, exc: InvalidCredentialsError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "error": "invalid_credentials",
                "message": "Correo o contraseña incorrectos",
            },
        )

    @app.exception_handler(UserNotApprovedError)
    async def user_not_approved(
        request: Request, exc: UserNotApprovedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "error": "user_not_approved",
                "message": exc.message,
            },
        )

    @app.exception_handler(UserDeactivatedError)
    async def user_deactivated(
        request: Request, exc: UserDeactivatedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={
                "error": "user_deactivated",
                "message": exc.message,
            },
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found(
        request: Request, exc: UserNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": "user_not_found",
                "message": "Usuario no encontrado",
            },
        )

    @app.exception_handler(AuthDomainError)
    async def auth_domain_error(
        request: Request, exc: AuthDomainError
    ) -> JSONResponse:
        # Catch-all para errores de dominio no clasificados
        logger.warning(f"Error de dominio no clasificado: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "domain_error",
                "message": exc.message,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Pydantic devuelve los errores en inglés. Los traducimos
        # al primer mensaje legible de los errores.
        first_error = exc.errors()[0] if exc.errors() else {}
        msg = first_error.get("msg", "Datos inválidos")
        return JSONResponse(
            status_code=422,
            content={
                "error": "validation_error",
                "message": msg,
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_error(request: Request, exc: Exception) -> JSONResponse:
        # 500 — solo para errores inesperados
        logger.exception(f"Error no manejado: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "Error interno del servidor. Intente más tarde",
            },
        )
