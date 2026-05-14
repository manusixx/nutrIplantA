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
        super().__init__("No tiene permisos para acceder a este recurso")


class VariedadInvalidaError(DiagnosticoDomainError):
    def __init__(self, variedad: str) -> None:
        super().__init__(
            f"La variedad '{variedad}' no es una variedad válida de vid (Vitis vinifera)"
        )
        self.variedad = variedad


class DiagnosticoNotFoundError(DiagnosticoDomainError):
    def __init__(self, diagnostico_id: str) -> None:
        super().__init__(f"Diagnóstico no encontrado: {diagnostico_id}")
        self.diagnostico_id = diagnostico_id


class PlantaEnfermaError(DiagnosticoDomainError):
    """No se puede generar plan de abono si la planta tiene patologías urgentes."""
    pass


class RecordatorioNotFoundError(DiagnosticoDomainError):
    def __init__(self, recordatorio_id: str) -> None:
        super().__init__(f"Recordatorio no encontrado: {recordatorio_id}")
        self.recordatorio_id = recordatorio_id


class ImagenInvalidaError(DiagnosticoDomainError):
    def __init__(self, razon: str) -> None:
        super().__init__(f"La imagen no es válida para análisis: {razon}")
        self.razon = razon
