# Bitácora — Sprint 0

**Período:** [fecha inicio] – [fecha fin]
**Director:** Manuel
**Rama:** mpastrana → develop → main

## Objetivo del sprint

Levantar la infraestructura mínima del proyecto: PostgreSQL, MinIO y un endpoint hello-world en el API Gateway. Establecer las bases del repositorio: estructura, documentación, flujo de ramas, CI básico.

## Historias incluidas

No hay HUs del backlog en este sprint. Sprint 0 es preparatorio.

## Tareas

- [ ] Crear repositorio en GitHub con visibilidad pública.
- [ ] Configurar ramas main, develop, mpastrana con protección.
- [ ] Subir scaffolding inicial (este paquete del Sprint 0).
- [ ] Verificar `docker-compose up -d` levanta los 3 servicios.
- [ ] Verificar endpoint /api/v1/health responde.
- [ ] Verificar consola de MinIO accesible.
- [ ] Instalar Qodo Merge en el repositorio (GitHub Marketplace).
- [ ] Probar pipeline CI con un PR de prueba.
- [ ] Crear tag v0.1.0 al cerrar el sprint.

## Criterios de aceptación del sprint

- [ ] `docker-compose up -d` no devuelve errores.
- [ ] `docker-compose ps` muestra postgres, minio y gateway en estado Up.
- [ ] `curl http://localhost:8080/api/v1/health` devuelve `{"status":"ok",...}`.
- [ ] Consola MinIO accesible en http://localhost:9001.
- [ ] Pipeline CI pasa al menos una vez sobre un PR de prueba.
- [ ] Qodo Merge publica al menos una review en un PR.

## Decisiones tomadas

<!-- Listar decisiones técnicas tomadas durante el sprint con fecha y motivo. -->

## Hallazgos y problemas encontrados

<!-- Documentar issues que aparecieron y cómo se resolvieron. -->

## Demo

<!-- Capturas o evidencia de que los criterios se cumplen. -->

## Métricas del sprint

- Story points planificados: 0 (sprint preparatorio)
- Story points completados: 0
- Horas dedicadas: [a registrar]
- PRs abiertos: [a registrar]
- PRs mergeados: [a registrar]

## Retrospectiva

### Qué funcionó

- ...

### Qué se puede mejorar

- ...

### Acciones para el próximo sprint

- ...
