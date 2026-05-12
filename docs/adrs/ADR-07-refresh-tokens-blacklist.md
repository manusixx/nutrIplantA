# ADR-07: Blacklist de tokens mediante tabla en base de datos

**Estado:** Aceptado
**Fecha:** Mayo 2026
**Sprint:** 2
**Autor:** Manuel Pastrana

## Contexto

Para implementar logout efectivo con JWT (que por naturaleza son stateless), se necesita un mecanismo que permita revocar tokens antes de su expiración natural. Hay tres opciones principales:

1. **Redis**: base de datos en memoria, muy rápida, ideal para blacklist de tokens.
2. **Tabla en PostgreSQL**: persiste los tokens revocados en la BD existente.
3. **Tokens de vida muy corta**: reducir la vida del access token a 1-2 minutos y no implementar blacklist.

## Decisión

Implementar la blacklist mediante una tabla `auth.refresh_tokens` en PostgreSQL. Los refresh tokens se persisten completos (con `jti`, `user_id`, `expires_at`, `revoked_at`). El access token no se añade a blacklist porque su vida de 15 minutos limita el riesgo.

## Justificación

**Por qué no Redis:** Redis añade un cuarto componente de infraestructura al docker-compose. En el contexto académico del Sprint 2, la complejidad operacional no se justifica todavía. El ADR-01 establece que se añade complejidad solo cuando hay justificación. Redis está planificado para Sprint 11 cuando se implementa rate limiting real y la blacklist de access tokens.

**Por qué no tokens muy cortos:** 1-2 minutos de vida obligaría al frontend a renovar tokens constantemente, creando complejidad en la gestión de estado. La UX se degradaría.

**Por qué tabla en PostgreSQL:** la BD ya existe, la latencia adicional de consultar la blacklist es aceptable para el volumen académico, y elimina la dependencia de Redis. Es la solución más simple que cumple el requisito.

## Consecuencias

**Positivas:**
- Logout efectivo: el usuario puede revocar su sesión inmediatamente.
- Sin nuevo componente de infraestructura.
- La lógica de blacklist es testeable con el InMemoryRefreshTokenRepository.

**Negativas:**
- La tabla de tokens revocados crece con el tiempo (requiere cleanup periódico).
- Latencia adicional por consulta a BD en cada refresh de token.
- Si la BD cae, el refresh de tokens falla junto con el servicio.

## Plan de evolución

Sprint 11 migrará la blacklist de access tokens a Redis para mejorar latencia y añadir rate limiting. La interfaz `IRefreshTokenRepository` permite el cambio sin modificar el dominio.
