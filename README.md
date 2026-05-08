# nutrI-plantA

Plataforma Lab-to-Land para diagnóstico nutricional y fitosanitario en cultivos de vid (Vitis vinifera) mediante visión por computador.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Sprint%200-yellow.svg)]()

## Descripción

nutrI-plantA permite a agricultores e investigadores analizar fotografías de hojas de vid para detectar deficiencias nutricionales y patologías. El sistema entrega diagnósticos con confianza calibrada, planes de abono ajustados al inventario del usuario, y recordatorios de aplicación.

Lab-to-Land: dos roles complementarios sobre la misma plataforma. Investigador (Lab) accede a vista técnica densa. Agricultor (Land) accede a UX simplificada con tipografía grande y lenguaje natural.

## Arquitectura

Monorepo con dos servicios backend independientes (auth-service, diagnostico-service), un API Gateway como punto único de entrada, y un frontend SPA con dos sub-aplicaciones según rol.

Documentos de referencia:

- `docs/arquitectura/nutrIplantA_Arquitectura_v2.1.docx` — arquitectura completa con diagramas y ADRs.
- `docs/backlog/nutrIplantA_ProductBacklog_v1.0.docx` — historias de usuario con criterios de aceptación e INVEST.
- `docs/adrs/` — registros de decisiones arquitectónicas.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.12 + FastAPI 0.115 |
| ORM | SQLAlchemy 2 + Alembic |
| Auth | PyJWT + pwdlib (Argon2id) |
| Frontend | React 18 + TypeScript + Redux Toolkit + Vite |
| BD | PostgreSQL 16 |
| Storage | MinIO (S3-compatible) |
| Cache | Redis 7 |
| Orquestación | Docker Compose |
| CI/CD | GitHub Actions + Qodo Merge |

## Requisitos previos

- Windows 10/11 con WSL2 habilitado (recomendado) o Windows nativo.
- Docker Desktop 4.20 o superior.
- Git 2.40 o superior.
- Editor: VS Code o IntelliJ IDEA.

## Inicio rápido (Sprint 0)

Levantar la infraestructura mínima del Sprint 0: PostgreSQL, MinIO y un endpoint hello-world.

### 1. Clonar el repositorio

```powershell
git clone https://github.com/mpastrana/nutrIplantA.git
cd nutrIplantA
```

### 2. Crear archivo de variables de entorno

```powershell
Copy-Item .env.example .env
```

Edita `.env` y cambia los valores marcados como `CHANGEME`.

### 3. Levantar el stack

```powershell
docker-compose up -d
```

La primera vez tomará varios minutos descargando imágenes.

### 4. Verificar que todo está arriba

```powershell
docker-compose ps
```

Debes ver tres servicios en estado `Up`:

- `nutriplanta-postgres`
- `nutriplanta-minio`
- `nutriplanta-gateway`

### 5. Probar el endpoint de salud

```powershell
curl http://localhost:8080/api/v1/health
```

Respuesta esperada:

```json
{"status": "ok", "version": "0.1.0", "service": "nutrI-plantA gateway"}
```

### 6. Acceder a la consola de MinIO

Abrir en el navegador: http://localhost:9001

Credenciales por defecto (cambiar antes de producción):

- Usuario: `minioadmin`
- Contraseña: `minioadmin`

## Comandos útiles (Makefile)

Si tienes `make` instalado en Windows (vía Chocolatey o WSL):

```bash
make up        # Levantar el stack
make down      # Detener el stack
make logs      # Ver logs en tiempo real
make ps        # Estado de los servicios
make clean     # Detener y borrar volúmenes (datos perdidos)
```

Sin `make`, los comandos equivalentes están documentados en `Makefile`.

## Estructura del repositorio

```
nutrIplantA/
├── .github/              # Workflows CI/CD y plantillas
├── docs/                 # Documentación (arquitectura, backlog, ADRs)
├── gateway/              # API Gateway (FastAPI)
├── services/             # Servicios backend
│   ├── auth-service/     # (Sprint 2)
│   └── diagnostico-service/  # (Sprint 4)
├── frontend/             # SPA React (Sprint 6)
├── scripts/dev/          # Utilidades de desarrollo
├── docker-compose.yml    # Orquestación local
├── .env.example          # Plantilla de variables de entorno
├── README.md
├── CONTRIBUTING.md       # Flujo de ramas y proceso de PR
└── Makefile              # Comandos de desarrollo
```

## Flujo de trabajo

Ver `CONTRIBUTING.md` para el detalle. Resumen:

1. Trabajar en rama `mpastrana` (rama personal del director).
2. Validar localmente: tests, linter, type checker.
3. Push a `mpastrana`.
4. Abrir PR a `develop`. CI ejecuta pipeline y Qodo Merge revisa.
5. Atender hallazgos de Qodo y revisar diff manualmente.
6. Mergear a `develop`.
7. Al cerrar sprint, PR de `develop` a `main` con tag semántico.

## Estado del proyecto

| Sprint | Estado | Descripción |
|---|---|---|
| S0 | En curso | Infraestructura base, hello-world |
| S1 | Pendiente | docker-compose con todos los servicios |
| S2 | Pendiente | auth-service: registro, login, roles |
| S3 | Pendiente | Gateway con validación JWT |
| S4 | Pendiente | diagnostico-service: estructura base |
| S5 | Pendiente | Endpoint diagnóstico con MockVisionProvider |
| S6-S12 | Pendiente | Ver `docs/backlog/` |

## Créditos

- Director del proyecto: Manuel
- Universidad del Valle, Escuela de Ingeniería de Sistemas y Computación
- Unicamacho

## Licencia

MIT — ver `LICENSE`.
