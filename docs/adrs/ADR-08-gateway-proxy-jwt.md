# ADR-08: API Gateway como proxy real con validación JWT centralizada

**Estado:** Aceptado
**Fecha:** Mayo 2026
**Sprint:** 3
**Autor:** Manuel Pastrana

## Contexto

En Sprint 0 el Gateway era un hello-world. En Sprint 3 debe convertirse en el guardián del sistema. Hay dos enfoques para implementar autenticación en una arquitectura de microservicios:

1. **Validación distribuida**: cada servicio valida el JWT por su cuenta.
2. **Validación centralizada en gateway**: el gateway valida el JWT y propaga el `user_id` y `role` a los servicios downstream en headers internos.

## Decisión

Validación centralizada en el gateway. El gateway verifica la firma del JWT, extrae `user_id` y `role`, y los añade como headers internos (`X-User-Id`, `X-User-Role`) en la petición reenviada. Los servicios downstream confían en esos headers sin re-validar el JWT.

## Justificación

**Validación distribuida implica:** que cada servicio tenga acceso al `JWT_SECRET_KEY`, que cada servicio importe la librería JWT, y que si el secret cambia, se deba actualizar en todos los servicios. Viola el principio de responsabilidad única.

**Validación centralizada implica:** un único punto de control (el gateway), servicios downstream más simples, y actualización del secret en un solo lugar. El riesgo es que si el gateway tiene un bug de autorización, afecta a todos los servicios.

Para el contexto de nutrI-plantA, la centralización es la opción correcta. La complejidad del sistema no justifica la distribución del secreto JWT a múltiples servicios.

## Consecuencias

**Positivas:**
- Servicios downstream no necesitan conocer el JWT_SECRET_KEY.
- Lógica de autenticación/autorización en un único lugar.
- Más fácil de auditar: todos los accesos pasan por el gateway.
- Servicios downstream son más simples (confían en headers internos).

**Negativas:**
- Si el gateway cae, todo el sistema queda inaccesible.
- Headers internos (`X-User-Id`) deben protegerse: no deben poder ser inyectados por clientes externos.

## Medidas de seguridad

El gateway debe **remover** los headers `X-User-Id` y `X-User-Role` de cualquier petición entrante antes de validar el JWT y añadir los suyos. Esto previene que un cliente malintencionado inyecte esos headers directamente.
