import uuid
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient

from auth.api.dependencies import get_admin_service, get_user_repository
from auth.api.routes.admin_routes import router


class FakeUser:
    def __init__(self, id=None, role="ADMIN"):
        self.id = id or str(uuid.uuid4())
        self.email = "test@test.com"
        self.full_name = "Test User"
        self.status = "PENDIENTE_APROBACION"
        self.role = role
        self.created_at = datetime.now(UTC)

class FakeUserRepository:

    async def find_by_id(self, user_id):
        return FakeUser()

class FakeAdminService:

    async def listar_todos(self):
        return [FakeUser(), FakeUser()]

    async def aprobar(self, user_id, rol):
        if str(user_id).startswith("0000"):
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if rol == "INVALIDO":
            raise ValueError("Rol inválido")

        user = FakeUser(id=user_id)
        user.role = rol
        return user

@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router)

    # Reemplazar dependencias reales por fakes
    app.dependency_overrides[get_user_repository] = lambda: FakeUserRepository()
    app.dependency_overrides[get_admin_service] = lambda: FakeAdminService()

    return app

@pytest.mark.asyncio
async def test_me_endpoint(test_app):
    transport = ASGITransport(app=test_app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"X-User-Id": "11111111-1111-1111-1111-111111111111"},
        )

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == "test@test.com"

@pytest.mark.asyncio
async def test_listar_usuarios(test_app):
    transport = ASGITransport(app=test_app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/users")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

@pytest.mark.asyncio
async def test_aprobar_usuario(test_app):
    user_id = str(uuid.uuid4())

    transport = ASGITransport(app=test_app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/admin/users/{user_id}/aprobar",
            json={"rol": "ADMIN"},
        )

    assert response.status_code == 200

    data = response.json()
    assert data["role"] == "ADMIN"

@pytest.mark.asyncio
async def test_aprobar_usuario_no_existe(test_app):
    user_id = "00000000-0000-0000-0000-000000000000"

    transport = ASGITransport(app=test_app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/admin/users/{user_id}/aprobar",
            json={"rol": "ADMIN"},
        )

    assert response.status_code == 404

async def aprobar(self, user_id, rol):
    if str(user_id).startswith("0000"):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if rol == "INVALIDO":
        raise ValueError("Rol inválido")

    user = FakeUser(id=user_id)
    user.role = rol
    return user

