# Bitácora — Sprint 1

**Período:** Mayo 2026
**Director:** Manuel Pastrana
**Rama:** mpastrana → develop
**Estado:** CERRADO

## Objetivo del sprint

Implementar HU-01 (Registro de cuenta de usuario) con arquitectura hexagonal completa en `auth-service`. Incluir estructura de servicio, migraciones Alembic, tests con cobertura mínima del 80%, y validación de calidad con ruff, mypy e import-linter.

## Historias completadas

| HU | Título | Puntos | Estado |
|---|---|---|---|
| HU-01 | Registro de cuenta de usuario | 5 | ✅ Cerrada |

## Criterios de aceptación verificados

- [x] Endpoint `POST /api/v1/auth/register` responde HTTP 201 con usuario en estado `PENDIENTE_APROBACION`.
- [x] Email duplicado responde HTTP 409 con mensaje en español.
- [x] Email con formato inválido responde HTTP 422.
- [x] Contraseña débil (menos de 10 chars, sin mayúscula, minúscula, número o especial) responde HTTP 422.
- [x] Campo faltante responde HTTP 422.
- [x] La contraseña se almacena hasheada con Argon2id. Nunca en texto plano.
- [x] Email se normaliza a minúsculas antes de persistir.
- [x] Usuario queda con `role = NULL` hasta que un admin apruebe.
- [x] Tabla `auth.users` creada por migración Alembic `0001_create_users_table`.
- [x] Endpoint `/api/v1/auth/health` responde correctamente.
- [x] Swagger UI accesible en `http://localhost:8001/api/v1/auth/docs`.

## Gates de calidad

| Gate | Resultado | Detalle |
|---|---|---|
| `ruff check src tests` | ✅ PASS | 0 errores tras ajustes de UP017, B008, N811, F401 |
| `mypy src` | ✅ PASS | 0 errores con `strict = true` |
| `lint-imports` | ✅ PASS | 3 contratos arquitectura hexagonal sin violaciones |
| `pytest --cov` | ✅ PASS | 49 tests, cobertura 82% |
| Docker build | ✅ PASS | Imagen construida y servicio levantado |
| Smoke tests en Docker | ✅ PASS | Endpoints verificados, tabla creada en BD |

## Implementación entregada

### Estructura hexagonal

```
services/auth-service/src/auth/
├── api/
│   ├── dependencies.py          (DI por request)
│   ├── exception_handler.py     (handler global, mensajes en español)
│   ├── dtos/register_dto.py     (validación Pydantic con regex de contraseña)
│   └── routes/auth_routes.py   (endpoints /health y /register)
├── domain/
│   ├── models/user.py           (entidad User pura, sin SQLAlchemy)
│   ├── repositories/            (interfaces IUserRepository, IPasswordHasher)
│   ├── services/auth_service.py (registro + authenticate)
│   ├── services/token_service.py (JWT HS256, exp 15min, jti único)
│   └── exceptions/              (excepciones de dominio en español)
├── infrastructure/
│   ├── persistence/             (UserModel SQLAlchemy, Postgres e InMemory repos)
│   └── security/                (Argon2PasswordHasher)
├── config.py                    (Pydantic Settings)
├── container.py                 (DI Container)
└── main.py                      (FastAPI app, lifespan)
```

### Tests (49 tests, 82% cobertura)

| Archivo | Tests | Qué cubre |
|---|---|---|
| `test_user_model.py` | 7 | Modelo User, estados, reglas de negocio |
| `test_auth_service.py` | 10 | Registro y authenticate, casos límite |
| `test_argon2_hasher.py` | 7 | Hash Argon2id, verify, edge cases |
| `test_token_service.py` | 14 | JWT, claims, expiración, validación |
| `test_dependencies.py` | 5 | DI por request, rollback, session |
| `test_register_endpoint.py` | 8 | Endpoint integration tests |

### Decisiones técnicas tomadas

- **Argon2id** como algoritmo de hash (recomendación OWASP 2025).
- **dependency-injector** para DI declarativo (no manual).
- **Capa de excepciones en dominio** sin referencias HTTP. El handler global las traduce.
- **Email normalizado a lowercase** en el servicio, no en el DTO.
- **Puerto PostgreSQL externo: 2332** (no 5432 por defecto), para evitar colisiones con otras instancias locales.
- **Puerto Gateway externo: 8085** (no 8080).

### Problemas encontrados y resueltos

| Problema | Causa | Solución |
|---|---|---|
| `ruff B008` en Depends() | Ruff no reconoce patrón FastAPI | Silenciar en `per-file-ignores` para `api/**` |
| `mypy UP017` en datetime | `timezone.utc` deprecado en Python 3.12 | Cambiar a `datetime.UTC` |
| `psycopg2` no encontrado en Docker | Alembic requiere driver síncrono, `asyncpg` es async | Añadir `psycopg2-binary` a dependencias |
| `test_token_service.py` con imports inválidos | Copilot generó archivo con `from app.services...` inventado | Eliminar archivo y escribir tests correctos |
| MinIO en bucle `Restarting (1)` | Contraseña en `.env` no cumplía mínimo de 8 caracteres | Corregir `MINIO_ROOT_PASSWORD` en `.env` |
| Cobertura inicial 54% | Tests basura de Copilot contaminaban la suite | Eliminar archivos, escribir tests dirigidos |

## Métricas del sprint

- Story points completados: 5 (HU-01)
- Tests escritos: 49
- Cobertura: 82%
- Archivos Python del servicio: 22
- PRs abiertos: 1
- Hallazgos de Qodo Merge atendidos: sí

## Retrospectiva

### Qué funcionó

- La arquitectura hexagonal separó claramente las responsabilidades. Cuando mypy fallaba, era en archivos específicos y el dominio del error era claro.
- El flujo de gates locales (ruff → mypy → lint-imports → pytest) antes de Docker ahorró tiempo al aislar problemas.
- Los tests unitarios con `InMemoryUserRepository` corrieron sin Docker, acelerando el ciclo de feedback.

### Qué mejorar

- Revisar cada archivo que Copilot genere antes de ejecutarlo. Los tres archivos de tests inventados (`test_token_service.py`, `test_container.py`, `test_database.py`) costaron tiempo innecesario.
- Probar el build Docker antes del PR, no después. El `psycopg2-binary` faltante se habría detectado antes.
- Hacer commits más frecuentes. Varias horas de trabajo local sin commit es riesgo innecesario.

### Acciones para Sprint 2

- Añadir `psycopg2-binary` a cualquier nuevo servicio desde el inicio.
- Incluir `start_period: 30s` en healthchecks de MinIO y servicios con arranque lento.
- No pedir a Copilot que genere archivos completos; solo usarlo para autocompletar líneas.
