# Bitácora — Sprint 3

**Período:** [Fecha inicio] – [Fecha fin]
**Director:** Manuel Pastrana
**Rama:** mpastrana → develop
**Estado:** PENDIENTE

## Objetivo del sprint

Transformar el API Gateway de hello-world a proxy real con validación JWT, autorización por rol y rate limiting. Al cerrar el sprint, todas las rutas protegidas requieren token válido y el gateway rechaza solicitudes no autorizadas antes de que lleguen a los servicios downstream.

## Historias completadas

| HU | Título | Puntos | Estado |
|---|---|---|---|
| — | Gateway JWT + routing + rate limiting (trabajo técnico) | — | ⬜ Pendiente |

## Criterios de aceptación por verificar

- [ ] Gateway valida JWT en cada petición a rutas protegidas.
- [ ] Token inválido o expirado responde HTTP 401 desde el gateway.
- [ ] Ruta de rol incorrecto responde HTTP 403 desde el gateway.
- [ ] Rutas `/api/v1/auth/**` no requieren token (son públicas).
- [ ] Rate limiting activo en `/api/v1/auth/login` y `/api/v1/auth/register`.
- [ ] Gateway enruta correctamente a `auth-service` y `diagnostico-service`.
- [ ] `GET /api/v1/me` devuelve datos del usuario autenticado.
- [ ] Tests de middleware de autenticación pasan.

## Gates de calidad

| Gate | Resultado | Detalle |
|---|---|---|
| `ruff check` | ⬜ | |
| `mypy` | ⬜ | |
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
