"""
Excepciones de dominio del auth-service.

Estas excepciones representan reglas de negocio violadas. NO deben
contener detalles de infraestructura (HTTP, SQL, etc.).
El exception handler global las traduce a respuestas HTTP apropiadas.
"""


class AuthDomainError(Exception):
    """Base para todas las excepciones del dominio de auth."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class EmailAlreadyRegisteredError(AuthDomainError):
    """El email ya existe en el sistema."""

    def __init__(self, email: str) -> None:
        super().__init__(f"El email '{email}' ya está registrado")
        self.email = email


class InvalidCredentialsError(AuthDomainError):
    """Email o contraseña incorrectos. Mensaje genérico para no permitir
    enumeración de usuarios."""

    def __init__(self) -> None:
        super().__init__("Credenciales inválidas")


class UserNotFoundError(AuthDomainError):
    """No se encontró el usuario solicitado."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"Usuario no encontrado: {identifier}")
        self.identifier = identifier


class UserNotApprovedError(AuthDomainError):
    """El usuario existe pero no ha sido aprobado por un administrador."""

    def __init__(self) -> None:
        super().__init__(
            "Su cuenta aún no ha sido aprobada. Contacte al administrador"
        )


class UserDeactivatedError(AuthDomainError):
    """La cuenta ha sido desactivada por un administrador."""

    def __init__(self) -> None:
        super().__init__(
            "Esta cuenta ha sido desactivada. Contacte al administrador"
        )
