"""
Excepciones adicionales de dominio para Sprint 2.
Añadir a auth/domain/exceptions/__init__.py
"""


class InvalidRefreshTokenError(Exception):
    """Refresh token inválido, expirado o ya rotado."""

    def __init__(self) -> None:
        self.message = "Sesión inválida. Inicie sesión nuevamente"
        super().__init__(self.message)


class TokenReuseDetectedError(Exception):
    """
    Se detectó reuso de un refresh token ya rotado.
    Señal de posible robo de token. Se revocan todos los tokens
    del usuario afectado.
    """

    def __init__(self) -> None:
        self.message = (
            "Se detectó actividad sospechosa en su cuenta. "
            "Por seguridad, cierre sesión en todos sus dispositivos"
        )
        super().__init__(self.message)
