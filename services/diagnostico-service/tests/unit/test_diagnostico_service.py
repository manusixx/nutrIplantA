"""Tests unitarios del DiagnosticoService."""
from uuid import uuid4

import pytest

from diagnostico.domain.exceptions import CultivoNoAutorizadoError, CultivoNotFoundError
from diagnostico.domain.models.cultivo import Cultivo, VariedadVid
from diagnostico.domain.models.diagnostico import EstadoGeneral
from diagnostico.domain.services.diagnostico_service import DiagnosticoService
from diagnostico.infrastructure.persistence.in_memory_cultivo_repository import (
    InMemoryCultivoRepository,
)
from diagnostico.infrastructure.persistence.in_memory_diagnostico_repository import (
    InMemoryDiagnosticoRepository,
)
from diagnostico.infrastructure.vision.mock_vision_provider import MockVisionProvider

USER_ID = uuid4()
OTRO_USER_ID = uuid4()


@pytest.fixture
def cultivo_repo() -> InMemoryCultivoRepository:
    return InMemoryCultivoRepository()


@pytest.fixture
def diagnostico_repo() -> InMemoryDiagnosticoRepository:
    return InMemoryDiagnosticoRepository()


@pytest.fixture
def service(
    cultivo_repo: InMemoryCultivoRepository,
    diagnostico_repo: InMemoryDiagnosticoRepository,
) -> DiagnosticoService:
    return DiagnosticoService(diagnostico_repo, cultivo_repo, MockVisionProvider())


@pytest.fixture
async def cultivo_guardado(cultivo_repo: InMemoryCultivoRepository) -> Cultivo:
    cultivo = Cultivo(
        user_id=USER_ID,
        nombre_finca="Finca Test",
        variedad=VariedadVid.ISABELLA,
    )
    return await cultivo_repo.save(cultivo)


class TestDiagnosticoServiceCrear:
    @pytest.mark.asyncio
    async def test_crea_diagnostico_para_cultivo_propio(
        self,
        service: DiagnosticoService,
        cultivo_guardado: Cultivo,
    ) -> None:
        diag = await service.crear_diagnostico(
            cultivo_id=cultivo_guardado.id,
            user_id=USER_ID,
            foto_url="minio://diagnosticos/foto.jpg",
        )

        assert diag.id is not None
        assert diag.cultivo_id == cultivo_guardado.id
        assert diag.user_id == USER_ID
        assert diag.estado_general in list(EstadoGeneral)
        assert 0.0 <= diag.confianza_global <= 1.0

    @pytest.mark.asyncio
    async def test_falla_si_cultivo_no_existe(
        self, service: DiagnosticoService
    ) -> None:
        with pytest.raises(CultivoNotFoundError):
            await service.crear_diagnostico(
                cultivo_id=uuid4(),
                user_id=USER_ID,
                foto_url="minio://diagnosticos/foto.jpg",
            )

    @pytest.mark.asyncio
    async def test_falla_si_cultivo_es_de_otro_usuario(
        self,
        service: DiagnosticoService,
        cultivo_guardado: Cultivo,
    ) -> None:
        with pytest.raises(CultivoNoAutorizadoError):
            await service.crear_diagnostico(
                cultivo_id=cultivo_guardado.id,
                user_id=OTRO_USER_ID,
                foto_url="minio://diagnosticos/foto.jpg",
            )

    @pytest.mark.asyncio
    async def test_mock_provider_es_determinista(
        self,
        service: DiagnosticoService,
        cultivo_guardado: Cultivo,
    ) -> None:
        """Misma URL siempre da mismo resultado."""
        url = "minio://diagnosticos/foto_fija.jpg"
        diag1 = await service.crear_diagnostico(cultivo_guardado.id, USER_ID, url)
        diag2 = await service.crear_diagnostico(cultivo_guardado.id, USER_ID, url)

        assert diag1.estado_general == diag2.estado_general
        assert diag1.confianza_global == diag2.confianza_global


class TestDiagnosticoServiceHistorial:
    @pytest.mark.asyncio
    async def test_historial_usuario_solo_muestra_sus_diagnosticos(
        self,
        service: DiagnosticoService,
        cultivo_repo: InMemoryCultivoRepository,
        cultivo_guardado: Cultivo,
    ) -> None:
        cultivo_otro = Cultivo(
            user_id=OTRO_USER_ID,
            nombre_finca="Finca Otro",
            variedad=VariedadVid.MALBEC,
        )
        await cultivo_repo.save(cultivo_otro)

        await service.crear_diagnostico(cultivo_guardado.id, USER_ID, "url1.jpg")
        await service.crear_diagnostico(cultivo_guardado.id, USER_ID, "url2.jpg")
        await service.crear_diagnostico(cultivo_otro.id, OTRO_USER_ID, "url3.jpg")

        historial = await service.historial_usuario(USER_ID)

        assert len(historial) == 2
        assert all(d.user_id == USER_ID for d in historial)
