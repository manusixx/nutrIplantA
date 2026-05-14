"""Tests unitarios del CultivoService."""
from uuid import uuid4

import pytest

from diagnostico.domain.exceptions import CultivoNoAutorizadoError, CultivoNotFoundError
from diagnostico.domain.models.cultivo import VariedadVid
from diagnostico.domain.services.cultivo_service import CultivoService
from diagnostico.infrastructure.persistence.in_memory_cultivo_repository import (
    InMemoryCultivoRepository,
)


@pytest.fixture
def repo() -> InMemoryCultivoRepository:
    return InMemoryCultivoRepository()


@pytest.fixture
def service(repo: InMemoryCultivoRepository) -> CultivoService:
    return CultivoService(repo)


USER_ID = uuid4()
OTRO_USER_ID = uuid4()


class TestCultivoServiceCrear:
    @pytest.mark.asyncio
    async def test_crea_cultivo_y_lo_persiste(self, service: CultivoService, repo: InMemoryCultivoRepository) -> None:
        cultivo = await service.crear(
            user_id=USER_ID,
            nombre_finca="Finca El Valle",
            variedad=VariedadVid.ISABELLA,
            vereda="El Placer",
        )

        assert cultivo.id is not None
        assert cultivo.user_id == USER_ID
        assert cultivo.nombre_finca == "Finca El Valle"
        assert cultivo.variedad == VariedadVid.ISABELLA
        assert repo.count == 1

    @pytest.mark.asyncio
    async def test_normaliza_strings_quitando_espacios(self, service: CultivoService) -> None:
        cultivo = await service.crear(
            user_id=USER_ID,
            nombre_finca="  Finca Norte  ",
            variedad=VariedadVid.MALBEC,
        )
        assert cultivo.nombre_finca == "Finca Norte"


class TestCultivoServiceListar:
    @pytest.mark.asyncio
    async def test_lista_solo_cultivos_del_usuario(
        self, service: CultivoService
    ) -> None:
        await service.crear(USER_ID, "Finca A", VariedadVid.ISABELLA)
        await service.crear(USER_ID, "Finca B", VariedadVid.MALBEC)
        await service.crear(OTRO_USER_ID, "Finca C", VariedadVid.SYRAH)

        mis_cultivos = await service.listar(USER_ID)

        assert len(mis_cultivos) == 2
        assert all(c.user_id == USER_ID for c in mis_cultivos)

    @pytest.mark.asyncio
    async def test_lista_vacia_si_no_hay_cultivos(self, service: CultivoService) -> None:
        cultivos = await service.listar(USER_ID)
        assert cultivos == []


class TestCultivoServiceObtener:
    @pytest.mark.asyncio
    async def test_obtiene_cultivo_del_usuario(self, service: CultivoService) -> None:
        creado = await service.crear(USER_ID, "Finca A", VariedadVid.ISABELLA)
        obtenido = await service.obtener(creado.id, USER_ID)
        assert obtenido.id == creado.id

    @pytest.mark.asyncio
    async def test_falla_si_no_existe(self, service: CultivoService) -> None:
        with pytest.raises(CultivoNotFoundError):
            await service.obtener(uuid4(), USER_ID)

    @pytest.mark.asyncio
    async def test_falla_si_es_de_otro_usuario(self, service: CultivoService) -> None:
        creado = await service.crear(USER_ID, "Finca A", VariedadVid.ISABELLA)
        with pytest.raises(CultivoNoAutorizadoError):
            await service.obtener(creado.id, OTRO_USER_ID)


class TestCultivoServiceActualizar:
    @pytest.mark.asyncio
    async def test_actualiza_campos_del_cultivo(self, service: CultivoService) -> None:
        creado = await service.crear(USER_ID, "Finca A", VariedadVid.ISABELLA)
        actualizado = await service.actualizar(
            creado.id, USER_ID, nombre_finca="Finca Actualizada"
        )
        assert actualizado.nombre_finca == "Finca Actualizada"
        assert actualizado.variedad == VariedadVid.ISABELLA  # Sin cambio

    @pytest.mark.asyncio
    async def test_falla_si_actualizar_cultivo_de_otro(self, service: CultivoService) -> None:
        creado = await service.crear(USER_ID, "Finca A", VariedadVid.ISABELLA)
        with pytest.raises(CultivoNoAutorizadoError):
            await service.actualizar(creado.id, OTRO_USER_ID, nombre_finca="Hack")


class TestCultivoServiceEliminar:
    @pytest.mark.asyncio
    async def test_elimina_cultivo_del_usuario(
        self, service: CultivoService, repo: InMemoryCultivoRepository
    ) -> None:
        creado = await service.crear(USER_ID, "Finca A", VariedadVid.ISABELLA)
        await service.eliminar(creado.id, USER_ID)
        assert repo.count == 0

    @pytest.mark.asyncio
    async def test_falla_si_eliminar_cultivo_de_otro(self, service: CultivoService) -> None:
        creado = await service.crear(USER_ID, "Finca A", VariedadVid.ISABELLA)
        with pytest.raises(CultivoNoAutorizadoError):
            await service.eliminar(creado.id, OTRO_USER_ID)
