# Bitácora — Sprint 4

**Período:** [Fecha inicio] – [Fecha fin]
**Director:** Manuel Pastrana
**Rama:** mpastrana → develop
**Estado:** PENDIENTE

## Objetivo del sprint

Levantar el `diagnostico-service` con arquitectura hexagonal completa e implementar gestión de cultivos (CRUD). Al cerrar el sprint, un usuario autenticado puede registrar y consultar sus cultivos de vid.

## Historias completadas

| HU | Título | Puntos | Estado |
|---|---|---|---|
| — | diagnostico-service base + CRUD cultivos | — | ⬜ Pendiente |

## Criterios de aceptación por verificar

- [ ] `POST /api/v1/diagnostico/cultivos` crea un cultivo vinculado al usuario.
- [ ] `GET /api/v1/diagnostico/cultivos` lista cultivos del usuario autenticado.
- [ ] `GET /api/v1/diagnostico/cultivos/{id}` devuelve cultivo específico.
- [ ] `PUT /api/v1/diagnostico/cultivos/{id}` actualiza cultivo.
- [ ] `DELETE /api/v1/diagnostico/cultivos/{id}` elimina cultivo.
- [ ] Solo variedades de vid (Vitis vinifera) son aceptadas.
- [ ] Un usuario no puede acceder a cultivos de otro.
- [ ] Tabla `diagnostico.cultivos` creada por migración Alembic.
- [ ] `diagnostico-service` integrado al docker-compose en puerto 8002.
- [ ] Gateway enruta correctamente al nuevo servicio.

## Gates de calidad

| Gate | Resultado | Detalle |
|---|---|---|
| `ruff check` | ⬜ | |
| `mypy` | ⬜ | |
| `lint-imports` | ⬜ | |
| `pytest --cov` | ⬜ | |
| Docker build | ⬜ | |
| Smoke tests | ⬜ | |

## Problemas encontrados y resueltos

<!-- Completar al ejecutar el sprint -->

## Métricas del sprint

- Tests escritos: [rellenar]
- Cobertura: [rellenar]
- PRs: [rellenar]

## Retrospectiva

<!-- Completar al cerrar el sprint -->
