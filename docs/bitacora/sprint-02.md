# Bitácora — Sprint 2

**Período:** [Fecha inicio] – [Fecha fin]
**Director:** Manuel Pastrana
**Rama:** mpastrana → develop
**Estado:** EN CURSO

## Objetivo del sprint

Implementar HU-02 (Login con JWT) y HU-03 (Logout seguro) en `auth-service`. Al cerrar el sprint, un usuario aprobado puede autenticarse y recibir tokens de acceso y refresco. Puede cerrar sesión revocando sus tokens.

## Historias completadas

| HU | Título | Puntos | Estado |
|---|---|---|---|
| HU-02 | Inicio de sesión con email y contraseña | 5 | ⬜ En progreso |
| HU-03 | Cierre de sesión seguro | 2 | ⬜ Pendiente |

## Criterios de aceptación por verificar

### HU-02

- [ ] `POST /api/v1/auth/login` con credenciales válidas responde HTTP 200.
- [ ] Respuesta incluye `access_token` con vigencia 15 minutos.
- [ ] Refresh token se entrega en cookie `HttpOnly Secure SameSite=Strict`.
- [ ] Credenciales inválidas responden HTTP 401 con mensaje genérico.
- [ ] Usuario `PENDIENTE_APROBACION` responde HTTP 403.
- [ ] Usuario `DESACTIVADO` responde HTTP 403.
- [ ] Refresh token se persiste en tabla `auth.refresh_tokens`.
- [ ] `POST /api/v1/auth/refresh` con refresh token válido emite nuevos tokens.
- [ ] Refresh token rotado queda invalidado inmediatamente.
- [ ] Reuso de refresh token ya rotado revoca todos los tokens del usuario.

### HU-03

- [ ] `POST /api/v1/auth/logout` invalida el access token por `jti`.
- [ ] Cookie de refresh token eliminada tras logout.
- [ ] Cualquier uso del token revocado responde HTTP 401.
- [ ] Logout es idempotente: hacerlo dos veces no falla.

## Gates de calidad

| Gate | Resultado | Detalle |
|---|---|---|
| `ruff check src tests` | ⬜ | |
| `mypy src` | ⬜ | |
| `lint-imports` | ⬜ | |
| `pytest --cov` | ⬜ | |
| Docker build | ⬜ | |
| Smoke tests en Docker | ⬜ | |

## Problemas encontrados y resueltos

<!-- Completar al ejecutar el sprint -->

## Métricas del sprint

- Story points completados: [rellenar]
- Tests escritos: [rellenar]
- Cobertura: [rellenar]
- PRs abiertos: [rellenar]
- Hallazgos de Qodo Merge atendidos: [rellenar]

## Retrospectiva

### Qué funcionó

<!-- Completar al cerrar el sprint -->

### Qué mejorar

<!-- Completar al cerrar el sprint -->

### Acciones para Sprint 3

<!-- Completar al cerrar el sprint -->
