"""
Modelo de dominio: Cultivo.

Representa un cultivo de vid registrado por un usuario.
Solo se aceptan variedades de Vitis vinifera (dominio acotado).
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class VariedadVid(str, Enum):
    """Variedades de Vitis vinifera permitidas."""

    ISABELLA = "Isabella"
    CABERNET_SAUVIGNON = "Cabernet Sauvignon"
    MALBEC = "Malbec"
    SYRAH = "Syrah"
    TEMPRANILLO = "Tempranillo"
    CHARDONNAY = "Chardonnay"
    MERLOT = "Merlot"
    PINOT_NOIR = "Pinot Noir"
    SAUVIGNON_BLANC = "Sauvignon Blanc"
    MUSCAT = "Muscat"


@dataclass
class Cultivo:
    """
    Entidad de dominio Cultivo.

    Reglas invariantes:
    - Cada cultivo pertenece a un usuario (user_id del JWT).
    - La variedad debe ser Vitis vinifera.
    - La identificación de la finca es obligatoria.
    """

    user_id: UUID
    nombre_finca: str
    variedad: VariedadVid
    id: UUID = field(default_factory=uuid4)
    vereda: str = ""
    fila: str = ""
    subparcela: str = ""
    notas: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def actualizar(
        self,
        nombre_finca: str | None = None,
        variedad: VariedadVid | None = None,
        vereda: str | None = None,
        fila: str | None = None,
        subparcela: str | None = None,
        notas: str | None = None,
    ) -> None:
        """Actualizar campos del cultivo. Solo actualiza los campos provistos."""
        if nombre_finca is not None:
            self.nombre_finca = nombre_finca.strip()
        if variedad is not None:
            self.variedad = variedad
        if vereda is not None:
            self.vereda = vereda.strip()
        if fila is not None:
            self.fila = fila.strip()
        if subparcela is not None:
            self.subparcela = subparcela.strip()
        if notas is not None:
            self.notas = notas.strip()
        self.updated_at = datetime.now(UTC)
