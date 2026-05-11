# Bitácora — Sprint 0

**Período:** [fecha inicio] – [fecha fin]
**Director:** Manuel
**Rama:** mpastrana → develop → main

## Objetivo del sprint

Realizar la HU-01 que permite crear un usuario en base de datos utilzando la arquitectura propuesta

## Historias incluidas

HU 01 del backlog en este sprint.

## Tareas

- [X] Implementar HU-01
- [X] Crear pruebas unitarias
- [X] Verificación análisis estático de código y pruebas unitarias con covertura de más de 80%
- [X] Verificar `docker-compose up -d` levanta los servicios.
- [X] Verificar endpoint /api/v1/health responde.
- [X] Verificar consola de MinIO accesible.
- [X] Actualizar repositorio en GitHub con visibilidad pública.
- [X] Probar pipeline CI con un PR de prueba.

## Criterios de aceptación del sprint

- [X] `docker-compose up -d` no devuelve errores.
- [X] `docker-compose ps` muestra postgres, minio y gateway en estado Up.
- [X] `curl http://localhost:8080/api/v1/health` devuelve `{"status":"ok",...}`.
- [X] Consola MinIO accesible en http://localhost:9001.
- [X] Pipeline CI pasa al menos una vez sobre un PR de prueba.
- [X] Qodo Merge publica al menos una review en un PR.

## Decisiones tomadas

Se implementa la primera HU del prototipo y se consolidan las pruebas unitarias respectivas. 
Se verfica de forma preventiva la calidad con las pruebas unitarias, ruff y qodo. Se hacen
ajustes sugeridos por qodo para que el código sea limpio. 

Se mantiene una arquitectura hexangonal limpia en la implementación

## Hallazgos y problemas encontrados

Por el momento ninguno a parte de las sugerencias que dió qodo y fueron depuradas.

## Demo

<!-- Capturas o evidencia de que los criterios se cumplen. -->

## Métricas del sprint

- Story points planificados: 1 (sprint preparatorio)
- Story points completados: 1
- Horas dedicadas: 4
- PRs abiertos: 0
- PRs mergeados: 2

## Retrospectiva

### Qué funcionó

- La asistencia de Claude y Qodo para construir una arquitectura solida guiada, pero no delegando la códificación complemtamente
sino siendo una extensión de lo implementado por el desarrollador para hacerlo más rápido

### Qué se puede mejorar

- El plugin de Qodo local no funciona muy bien por ser beta, pero el que está conectado en el respositorio si. 
No se debe dedicar tiempo en el IDE, sino directamente al hacer el pull request para sacarle más provecho

### Acciones para el próximo sprint

- implementar en lo posible más de una HU y pantallas, con el animo de poder garantizar un avance real del prototipo en 
dos semanas
