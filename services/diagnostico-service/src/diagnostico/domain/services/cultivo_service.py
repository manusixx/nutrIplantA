"""Servicio de dominio: gestión de cultivos."""
from uuid import UUID

from diagnostico.domain.exceptions import CultivoNoAutorizadoError, CultivoNotFoundError
from diagnostico.domain.models.cultivo import Cultivo, VariedadVid
from diagnostico.domain.repositories.i_cultivo_repository import ICultivoRepository


class CultivoService:
    """Caso de uso: CRUD de cultivos de vid."""

    def __init__(self, cultivo_repo: ICultivoRepository) -> None:
        self._repo = cultivo_repo

    async def crear(
        self,
        user_id: UUID,
        nombre_finca: str,
        variedad: VariedadVid,
        vereda: str = "",
        fila: str = "",
        subparcela: str = "",
        notas: str = "",
    ) -> Cultivo:
        """Crear un nuevo cultivo vinculado al usuario."""
        cultivo = Cultivo(
            user_id=user_id,
            nombre_finca=nombre_finca.strip(),
            variedad=variedad,
            vereda=vereda.strip(),
            fila=fila.strip(),
            subparcela=subparcela.strip(),
            notas=notas.strip(),
        )
        return await self._repo.save(cultivo)

    async def listar(self, user_id: UUID) -> list[Cultivo]:
        """Listar todos los cultivos del usuario."""
        return await self._repo.find_by_user(user_id)

    async def obtener(self, cultivo_id: UUID, user_id: UUID) -> Cultivo:
        """
        Obtener un cultivo por ID, verificando que pertenezca al usuario.

        Raises:
            CultivoNotFoundError, CultivoNoAutorizadoError
        """
        cultivo = await self._repo.find_by_id(cultivo_id)
        if cultivo is None:
            raise CultivoNotFoundError(str(cultivo_id))
        if cultivo.user_id != user_id:
            raise CultivoNoAutorizadoError()
        return cultivo

    async def actualizar(
        self,
        cultivo_id: UUID,
        user_id: UUID,
        **kwargs: object,
    ) -> Cultivo:
        """Actualizar campos del cultivo. Verifica propiedad del usuario."""
        cultivo = await self.obtener(cultivo_id, user_id)
        cultivo.actualizar(**kwargs)  # type: ignore[arg-type]
        return await self._repo.save(cultivo)

    async def eliminar(self, cultivo_id: UUID, user_id: UUID) -> None:
        """Eliminar un cultivo. Verifica propiedad del usuario."""
        await self.obtener(cultivo_id, user_id)  # Verifica existencia y pertenencia
        await self._repo.delete(cultivo_id)
