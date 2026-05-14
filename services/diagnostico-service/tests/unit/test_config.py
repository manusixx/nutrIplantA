from diagnostico.config import get_settings


def test_config_loads(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)

    get_settings.cache_clear()

    settings = get_settings()

    assert settings is not None
