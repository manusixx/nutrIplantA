"""
Tests del middleware de autenticación del gateway.

No levantan servicios downstream. Verifican solo la lógica del gateway.
"""
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient

TEST_SECRET = "g" * 64
TEST_ALGORITHM = "HS256"


@pytest.fixture(autouse=True)
def set_jwt_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configurar variables de entorno para los tests."""
    monkeypatch.setenv("JWT_SECRET_KEY", TEST_SECRET)
    monkeypatch.setenv("JWT_ALGORITHM", TEST_ALGORITHM)


def make_token(
    role: str = "AGRICULTOR",
    expired: bool = False,
    secret: str = TEST_SECRET,
) -> str:
    """Crear JWT de prueba."""
    now = datetime.now(UTC)
    exp = now - timedelta(minutes=5) if expired else now + timedelta(minutes=15)
    payload = {
        "sub": str(uuid4()),
        "role": role,
        "email": "test@test.com",
        "jti": str(uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, secret, algorithm=TEST_ALGORITHM)


@pytest.fixture
def client() -> TestClient:
    """Client de prueba del gateway."""
    import importlib
    import sys

    # Recargar el módulo para que tome las env vars del fixture
    if "app.main" in sys.modules:
        del sys.modules["app.main"]

    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_responde_sin_token(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "gateway"


class TestAuthMiddleware:
    def test_ruta_protegida_sin_token_da_401(self, client: TestClient) -> None:
        response = client.get("/api/v1/diagnostico/cultivos")
        assert response.status_code == 401
        assert response.json()["error"] == "unauthorized"

    def test_ruta_protegida_con_token_valido_pasa(self, client: TestClient) -> None:
        token = make_token()
        # La petición llegará al proxy y fallará por ConnectError (no hay downstream)
        # pero eso da 503, no 401. Eso confirma que el middleware dejó pasar la petición.
        response = client.get(
            "/api/v1/diagnostico/cultivos",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code != 401
        assert response.status_code != 403

    def test_token_expirado_da_401(self, client: TestClient) -> None:
        token = make_token(expired=True)
        response = client.get(
            "/api/v1/diagnostico/cultivos",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert response.json()["error"] == "token_expired"

    def test_token_con_firma_invalida_da_401(self, client: TestClient) -> None:
        token = make_token(secret="otro_secret" * 5)
        response = client.get(
            "/api/v1/diagnostico/cultivos",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401
        assert response.json()["error"] == "invalid_token"

    def test_token_malformado_da_401(self, client: TestClient) -> None:
        response = client.get(
            "/api/v1/diagnostico/cultivos",
            headers={"Authorization": "Bearer esto-no-es-un-jwt"},
        )
        assert response.status_code == 401

    def test_rutas_publicas_no_requieren_token(self, client: TestClient) -> None:
        public_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/health",
        ]
        for path in public_paths:
            # Sin token, las rutas públicas llegan al proxy (503 por falta de
            # downstream) o a un endpoint propio (200), pero nunca 401.
            response = client.post(path) if "login" in path or "register" in path or "refresh" in path else client.get(path)
            assert response.status_code != 401, f"Ruta {path} debería ser pública"


class TestRoleAuthorization:
    def test_ruta_investigador_con_rol_agricultor_da_403(
        self, client: TestClient
    ) -> None:
        token = make_token(role="AGRICULTOR")
        response = client.get(
            "/api/v1/investigador/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert response.json()["error"] == "forbidden"

    def test_ruta_investigador_con_rol_investigador_pasa(
        self, client: TestClient
    ) -> None:
        token = make_token(role="INVESTIGADOR")
        response = client.get(
            "/api/v1/investigador/dashboard",
            headers={"Authorization": f"Bearer {token}"},
        )
        # El middleware deja pasar. El proxy puede dar 503 (no hay downstream)
        # pero no 403.
        assert response.status_code != 403

    def test_ruta_admin_con_rol_agricultor_da_403(self, client: TestClient) -> None:
        token = make_token(role="AGRICULTOR")
        response = client.get(
            "/api/v1/admin/users",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
