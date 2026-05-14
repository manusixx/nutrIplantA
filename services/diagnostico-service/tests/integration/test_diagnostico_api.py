from fastapi.testclient import TestClient

from diagnostico.main import app


def test_healthcheck():
    client = TestClient(app)

    response = client.get("/api/v1/diagnostico/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
