"""Excepciones de dominio del diagnostico-service."""


class DiagnosticoDomainError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class CultivoNotFoundError(DiagnosticoDomainError):
    def __init__(self, cultivo_id: str) -> None:
        super().__init__(f"Cultivo no encontrado: {cultivo_id}")
        self.cultivo_id = cultivo_id


class CultivoNoAutorizadoError(DiagnosticoDomainError):
    def __init__(self) -> None:
        super().__init__("No tiene permisos para acceder a este cultivo")


class VariedadInvalidaError(DiagnosticoDomainError):
    def __init__(self, variedad: str) -> None:
        super().__init__(
            f"La variedad '{variedad}' no es una variedad válida de vid (Vitis vinifera)"
        )
        self.variedad = variedad
