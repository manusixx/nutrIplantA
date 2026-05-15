# nutrI-plantA

Plataforma Lab-to-Land para diagnóstico nutricional y fitosanitario en cultivos de vid (*Vitis vinifera*) mediante visión por computador e inteligencia artificial.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Sprint%2014%20%E2%80%94%20V1.0-green.svg)]()
[![CI](https://github.com/manusixx/nutrIplantA/actions/workflows/ci.yml/badge.svg?branch=develop)]()
[![Quality Gate](https://img.shields.io/badge/quality%20gate-passed-brightgreen.svg)]()
[![Coverage auth](https://img.shields.io/badge/coverage%20auth-81%25-brightgreen.svg)]()
[![Coverage diagnostico](https://img.shields.io/badge/coverage%20diagnostico-86%25-brightgreen.svg)]()

## Descripción

nutrI-plantA permite a agricultores e investigadores analizar fotografías de hojas de vid para detectar deficiencias nutricionales y patologías. El sistema entrega diagnósticos con confianza calibrada, planes de abono ajustados al cultivo, y recordatorios de aplicación programados.

**Lab-to-Land:** dos roles complementarios sobre la misma plataforma.
- **Investigador (Lab):** acceso técnico a diagnósticos y datos históricos.
- **Agricultor (Land):** UX simplificada con flujo guiado de captura y diagnóstico.
- **Admin:** gestión completa de usuarios y aprobación de accesos.

## Arquitectura

Monorepo con microservicios independientes, API Gateway como punto único de entrada, almacenamiento de imágenes en MinIO y frontend SPA en React.

```
Internet / Navegador
        ↓
   Gateway   ←── punto de entrada único (JWT validation + routing)
     ↙         ↘
auth-service  diagnostico-service
             
        ↘         ↙
       PostgreSQL 
       MinIO      
```

Documentos de referencia:

- `docs/arquitectura/nutrIplantA_Arquitectura_V1.docx` — arquitectura completa con diagramas, ADRs y stack tecnológico.
- `docs/backlog/nutrIplantA_ProductBacklog_V1.0.docx` — historias de usuario con criterios de aceptación.
- `docs/adrs/` — ADR-07 refresh tokens, ADR-08 gateway proxy JWT.
- `docs/bitacora/` — bitácoras de sprint S0–S4.

## Stack tecnológico

### Backend

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Framework API | FastAPI ≥0.115 + Uvicorn |
| ORM | SQLAlchemy 2 async + Alembic |
| Autenticación | PyJWT + pwdlib (Argon2id) |
| Storage | miniopy-async (MinIO) |
| Base de datos | PostgreSQL 16 (asyncpg + psycopg2) |
| Inyección de dependencias | dependency-injector |

### Frontend

| Capa | Tecnología |
|---|---|
| Framework | React 18 + TypeScript 5.6 |
| Build tool | Vite 5.4 |
| Estilos | Tailwind CSS 3.4 |
| Routing | React Router 6 |
| HTTP | Axios 1.7 |

### Infraestructura

| Componente | Tecnología |
|---|---|
| Orquestación local | Docker Compose v2 |
| Object storage | MinIO 2024-12 |
| Servidor web (prod) | Nginx alpine |
| CI/CD | GitHub Actions + Qodo |

## Requisitos previos

- Docker Desktop 4.20 o superior.
- Git 2.40 o superior.
- Node.js 20 o superior (solo para desarrollo frontend local).
- Python 3.12 (solo para desarrollo backend local).
- VS Code (recomendado).

## Inicio rápido

### 1. Clonar el repositorio

```bash
git clone https://github.com/manusixx/nutrIplantA.git
cd nutrIplantA
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y cambia los valores marcados como `CHANGEME`:

```env
POSTGRES_PASSWORD=CHANGEME
JWT_SECRET_KEY=CHANGEME_min32chars
MINIO_ROOT_PASSWORD=CHANGEME
```

### 3. Construir las imágenes Docker

```bash
docker build -t nutriplanta-auth-service \
  -f services/auth-service/Dockerfile services/auth-service/

docker build -t nutriplanta-diagnostico-service \
  -f services/diagnostico-service/Dockerfile services/diagnostico-service/
```

### 4. Levantar el stack completo

```bash
docker-compose up -d
```

### 5. Verificar que todo está corriendo

```bash
docker-compose ps
```

Debes ver todos los servicios en estado `Up (healthy)`:

| Servicio | Puerto |
|---|---|
| nutriplanta-gateway 
| nutriplanta-auth 
| nutriplanta-diagnostico 
| nutriplanta-postgres 
| nutriplanta-minio 

### 6. Verificar endpoints de salud

```bash
curl http://localhost:puerto/api/v1/auth/health
curl http://localhost:puerto/api/v1/diagnostico/health
```

### 7. Levantar el frontend

```bash
cd frontend
npm install
npm run dev
```

Accede en: **http://localhost:3000**

### 8. Crear usuario administrador

```bash
# Registrar usuario
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@tudominio.com","full_name":"Admin","password":"MiP@ssw0rd!"}'

# Aprobar como ADMIN directamente en BD
docker exec -it nutriplanta-postgres psql -U nutriplanta -d nutriplanta \
  -c "UPDATE auth.users SET status='APROBADO', role='ADMIN' WHERE email='admin@tudominio.com';"
```

### 9. Acceder a la consola de MinIO

Abre: **http://localhost:9001**

- Usuario: `minioadmin`
- Contraseña: valor de `MINIO_ROOT_PASSWORD` en `.env`

## Comandos útiles

```bash
# Ver logs de un servicio
docker logs nutriplanta-diagnostico -f
docker logs nutriplanta-auth -f

# Reiniciar un servicio tras rebuild
docker build -t nutriplanta-auth-service \
  -f services/auth-service/Dockerfile services/auth-service/
docker-compose up -d auth-service

# Ver usuarios en BD
docker exec -it nutriplanta-postgres psql -U nutriplanta -d nutriplanta \
  -c "SELECT email, status, role FROM auth.users;"

# Ver tablas del diagnostico-service
docker exec -it nutriplanta-postgres psql -U nutriplanta -d nutriplanta \
  -c "\dt diagnostico.*"

# Correr tests (auth-service)
cd services/auth-service
source .venv/Scripts/activate  # Windows
export PYTHONPATH=src
pytest --cov=auth --cov-report=term-missing

# Correr tests (diagnostico-service)
cd services/diagnostico-service
source .venv/Scripts/activate
export PYTHONPATH=src
pytest --cov=diagnostico --cov-report=term-missing

# Linter y type checker
ruff check src tests
mypy src
```

## Estructura del repositorio

```
nutrIplantA/
├── .github/
│   └── workflows/          # CI/CD — pipeline de PR a develop y main
├── docs/
│   ├── arquitectura/       # Documento de arquitectura v2.1
│   ├── backlog/            # Product backlog con HUs
│   ├── adrs/               # ADR-07, ADR-08
│   └── bitacora/           # Bitácoras S0–S4
├── gateway/                # API Gateway — proxy JWT + routing
├── services/
│   ├── auth-service/       # Registro, login, refresh tokens, admin
│   └── diagnostico-service/# Cultivos, diagnósticos, planes, MinIO
├── frontend/               # React + Vite + Tailwind CSS
├── docker-compose.yml
├── .env.example
├── Makefile
├── CONTRIBUTING.md
└── README.md
```

## Flujo de trabajo

Ver `CONTRIBUTING.md` para el detalle completo. Resumen:

1. Trabajar en rama personal (`mpastrana`).
2. Validar localmente: `ruff`, `mypy`, `import-linter`, `pytest --cov`.
3. Push y PR a `develop`. CI ejecuta pipeline y Qodo revisa.
4. Atender hallazgos, mergear a `develop`.
5. Al cerrar sprint, PR de `develop` a `main` con tag semántico.

## Estado del proyecto

| Sprint | Estado | Descripción |
|---|---|---|
| S0 | ✅ Completado | Infraestructura base, Docker Compose, CI/CD |
| S1 | ✅ Completado | auth-service: registro con Argon2id |
| S2 | ✅ Completado | auth-service: login JWT, refresh tokens rotantes |
| S3 | ✅ Completado | API Gateway con proxy real y validación JWT |
| S4 | ✅ Completado | diagnostico-service: estructura hexagonal base |
| S5 | ✅ Completado | CRUD cultivos de vid |
| S6 | ✅ Completado | Diagnóstico nutricional con MockVisionProvider |
| S7 | ✅ Completado | Plan de abono y recordatorios |
| S8 | ✅ Completado | Gestión de usuarios admin, endpoint /me |
| S9 | ✅ Completado | Persistencia real PostgreSQL (repos SQLAlchemy) |
| S10 | ✅ Completado | Frontend: login, registro, dashboard |
| S11 | ✅ Completado | Frontend: cultivos y diagnóstico |
| S12 | ✅ Completado | Frontend: historial y plan de abono |
| S13 | ✅ Completado | Frontend: panel de administración |
| S14 | ✅ Completado | Upload real de imágenes a MinIO |
| S15+ | 🔜 Fase 2 | Modelo de visión real, reportes, modo offline |

## Cobertura de tests

| Servicio | Cobertura | Estado |
|---|---|---|
| auth-service | 81% | ✅ Supera umbral 80% |
| diagnostico-service | 86% | ✅ Supera umbral 80% |

## Créditos

- Dirección de desarrollo: Manuel Alejandro Pastrana Pardo, PhD.
- Universidad del Valle — Escuela de Ingeniería de Sistemas y Computación.

## Licencia

MIT — ver `LICENSE`.
