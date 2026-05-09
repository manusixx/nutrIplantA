# Guía paso a paso para Windows — Sprint 0

Esta guía te lleva desde un repositorio vacío hasta tener el stack levantado y el primer PR a `develop`. Todos los comandos son para **PowerShell** en Windows.

## Prerrequisitos verificados

Antes de empezar, abre PowerShell y verifica:

```powershell
# Docker debe estar corriendo
docker --version
# Esperado: Docker version 24.x o superior

docker compose version
# Esperado: Docker Compose version v2.x o superior

# Git debe estar configurado
git --version
# Esperado: git version 2.x

git config user.name
# Debe mostrar tu nombre

git config user.email
# Debe mostrar tu correo
```

Si alguno falla, instala lo que falte antes de continuar.

## Paso 1: Crear el repositorio en GitHub

1. Ir a https://github.com/new
2. Nombre del repositorio: `nutrIplantA`
3. Descripción: `Plataforma Lab-to-Land para diagnóstico nutricional en cultivos de vid`
4. Visibilidad: **Public**
5. **NO** marcar "Initialize this repository with: README, .gitignore, license". Vamos a subir los archivos desde local.
6. Click en `Create repository`.

## Paso 2: Inicializar el repositorio local

Crear una carpeta donde vivirá el proyecto. Recomiendo `C:\dev\nutrIplantA` (rutas sin espacios ni acentos para evitar problemas con Docker).

```powershell
# Crear carpeta y entrar
New-Item -ItemType Directory -Path "C:\dev\nutrIplantA" -Force
Set-Location "C:\dev\nutrIplantA"
```

Descomprimir el contenido del paquete del Sprint 0 que te entregué en esta carpeta. Después debes tener algo como:

```
C:\dev\nutrIplantA\
  ├── .github\
  ├── docs\
  ├── gateway\
  ├── scripts\
  ├── services\
  ├── frontend\
  ├── docker-compose.yml
  ├── .env.example
  └── ...
```

## Paso 3: Configurar Git e inicializar

```powershell
# Inicializar repo
git init

# Configurar branch principal como main
git branch -M main

# Conectar con el remoto (cambia mpastrana por tu usuario real)
git remote add origin https://github.com/mpastrana/nutrIplantA.git

# Crear el archivo .env desde el ejemplo
Copy-Item .env.example .env
```

Edita `.env` con tu editor favorito y cambia los valores `CHANGEME`. Para generar el secret de JWT:

```powershell
# Genera un secret aleatorio de 64 caracteres hex
-join ((1..32) | ForEach-Object { '{0:x2}' -f (Get-Random -Maximum 256) })
```

Copia la salida y pégala en `JWT_SECRET_KEY` dentro de `.env`.

## Paso 4: Primer commit a main

```powershell
# Verificar qué se va a commitear
git status

# Añadir todo (el .gitignore filtra lo que no debe ir)
git add .

# Verificar de nuevo, asegúrate que .env NO aparezca como agregado
git status

# Si .env aparece, abortar y revisar .gitignore
# Si NO aparece, continuar:

git commit -m "chore: scaffolding inicial del Sprint 0

- Estructura monorepo con services/, frontend/, gateway/
- docker-compose con postgres, minio y gateway hello-world
- Documentación: README, CONTRIBUTING, arquitectura, backlog
- CI: workflow para PR a develop
- Plantillas de PR e issues
- Configuración de Qodo Merge"

# Push inicial
git push -u origin main
```

## Paso 5: Crear las ramas develop y mpastrana

```powershell
# Crear develop a partir de main
git checkout -b develop
git push -u origin develop

# Crear mpastrana a partir de develop
git checkout -b mpastrana
git push -u origin mpastrana
```

## Paso 6: Configurar protección de ramas en GitHub

En el navegador, ir al repositorio:

1. Settings → Branches → Add branch protection rule
2. Branch name pattern: `main`
3. Marcar:
   - Require a pull request before merging
   - Require approvals: 1
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include administrators (sí, también tú)
4. Save changes

Repetir para `develop` con las mismas reglas.

`mpastrana` queda sin protección (es tu área de trabajo).

## Paso 7: Verificar Docker Desktop

Abrir Docker Desktop. Debe mostrar el icono verde de "Docker Desktop is running". Si no:

```powershell
# Iniciar Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
# Esperar 30-60 segundos hasta que esté listo
```

## Paso 8: Levantar el stack

```powershell
# Estás en C:\dev\nutrIplantA y en rama mpastrana
# Levantar el stack
docker-compose up -d

# La primera vez tarda varios minutos descargando imágenes
# Verás algo como:
# [+] Running 4/4
#  ✔ Container nutriplanta-postgres     Started
#  ✔ Container nutriplanta-minio        Started
#  ✔ Container nutriplanta-minio-init   Started
#  ✔ Container nutriplanta-gateway      Started

# Verificar estado
docker-compose ps
```

Salida esperada (todos en estado `Up` o `running`, con `healthy` para los que tienen healthcheck):

```
NAME                       STATUS                       PORTS
nutriplanta-gateway        Up X seconds (healthy)       0.0.0.0:8080->8080/tcp
nutriplanta-minio          Up X seconds (healthy)       0.0.0.0:9000-9001->...
nutriplanta-postgres       Up X seconds (healthy)       0.0.0.0:5432->5432/tcp
```

## Paso 9: Verificar los criterios de aceptación

```powershell
# Test 1: endpoint de salud
curl http://localhost:8080/api/v1/health
# Esperado: {"status":"ok","version":"0.1.0","service":"nutrI-plantA gateway"}
```

```powershell
# Test 2: documentación OpenAPI
# Abrir en navegador: http://localhost:8080/api/v1/docs
# Debe mostrar Swagger UI con el endpoint /health listado
Start-Process "http://localhost:8080/api/v1/docs"
```

```powershell
# Test 3: consola MinIO
# Abrir en navegador: http://localhost:9001
# Login: minioadmin / [el password que configuraste en .env]
# Debe mostrar el bucket "diagnosticos" creado automáticamente
Start-Process "http://localhost:9001"
```

```powershell
# Test 4: PostgreSQL
# Verificar que los esquemas auth y diagnostico existen
docker exec -it nutriplanta-postgres psql -U nutriplanta -d nutriplanta -c "\dn"
# Esperado: lista que incluya 'auth' y 'diagnostico'
```

Si los 4 tests pasan, el Sprint 0 está completo localmente.

## Paso 10: Probar el pipeline CI con un PR de prueba

Para validar que CI funciona, hacemos un cambio mínimo y abrimos un PR.

```powershell
# Verificar que estamos en mpastrana
git status
# On branch mpastrana

# Hacer un cambio menor en README
# (puedes añadir tu nombre en la sección de créditos, por ejemplo)
# Guardar el cambio

git add README.md
git commit -m "docs: añade nombre del director en créditos"
git push origin mpastrana
```

Ir a GitHub:

1. Verás un banner: `mpastrana had recent pushes`. Click en `Compare & pull request`.
2. Base: `develop`. Compare: `mpastrana`.
3. Llena la plantilla de PR (en este caso es trivial, solo describe el cambio).
4. Click en `Create pull request`.
5. Esperar a que el pipeline corra. Debería ver:
   - ✅ Gateway · linter y build
   - ✅ Docker Compose · validar configuración

Si el pipeline pasa, todo está funcionando.

## Paso 11: Configurar Qodo Merge

0. Ir a https://github.com/marketplace/qodo-merge-pro
1. Click en el botón verde Add (arriba a la derecha)
Es el que aparece en tu captura, al lado de "By qodo-ai · 27.173 installs".
2. Te lleva a la página de planes
Verás dos opciones de plan:

Free / Developer — gratuito, con límites mensuales (30 reviews por mes aproximadamente).
Team / Pro — de pago.

Selecciona el plan Free. Click en Install it for free o el botón equivalente que aparezca debajo del plan gratuito.
3. Pantalla de "Order summary"
GitHub te muestra un resumen del "pedido" (aunque sea gratis, GitHub usa este flujo). Click en Complete order and begin installation.
No te pedirá tarjeta de crédito porque es el plan gratuito.
4. Pantalla "Install Qodo"
Aquí vienen las decisiones clave:
Pregunta 1: ¿Para qué cuenta?
Si solo tienes tu usuario <TU_USUARIO_GITHUB>, aparece directamente. Si tienes organizaciones, elige <TU_USUARIO_GITHUB> (tu cuenta personal).
Pregunta 2: Repository access
Tienes dos opciones:

⚪ All repositories (todos los actuales y futuros) — NO uses esta
⚫ Only select repositories — usa esta

Selecciona Only select repositories.
Pregunta 3: Selecciona el repositorio
En el dropdown que aparece, escribe nutrIplantA y selecciónalo.
5. Permisos
GitHub te muestra qué permisos otorgarás a Qodo (lectura de código, escritura de comentarios en PRs, etc.). Click en Install.
6. Confirmación de Qodo
Te redirige al sitio de Qodo (app.qodo.ai o similar). Es posible que te pida iniciar sesión con tu cuenta de GitHub. Acepta.
7. Verificar que está funcionando
Vuelve a tu repositorio en GitHub:
Settings → GitHub Apps (en el menú lateral izquierdo, sección "Integrations") → debes ver Qodo listado como instalado en este repositorio.
Volver al PR de prueba que creaste. Qodo debería empezar a comentar automáticamente en menos de 2 minutos. Si no lo hace, comentar en el PR `/review` para forzarlo.

## Paso 12: Mergear y crear tag v0.1.0

Una vez que CI pasa y revisaste las observaciones de Qodo:

1. En GitHub, click en `Merge pull request`.
2. Seleccionar `Squash and merge`.
3. Confirmar.

Después, mergear `develop` a `main`:

```powershell
# En local
git checkout main
git pull origin main
git merge --no-ff develop
git tag -a v0.1.0 -m "Sprint 0: infraestructura base levantada"
git push origin main --tags
```

## Paso 13: Cerrar la bitácora del Sprint 0

Editar `docs/bitacora/sprint-00.md` y completar:

- Marcar todas las tareas como `[x]`.
- Marcar todos los criterios de aceptación como `[x]`.
- Llenar la sección de retrospectiva con tu experiencia.
- Commit y push.

## Detener el stack al final del día

```powershell
# Detener pero preservar datos
docker-compose down

# Detener y borrar datos (úsalo solo si quieres empezar limpio)
docker-compose down -v
```

## Solución de problemas comunes

### Error: "port is already allocated"

Otro servicio está usando el puerto. Cambia el puerto en `.env` o detén el servicio en conflicto:

```powershell
# Ver qué proceso usa un puerto (ejemplo: 8080)
netstat -ano | findstr :8080
```

### Error: "Cannot connect to the Docker daemon"

Docker Desktop no está corriendo. Iniciarlo y esperar.

### El gateway no levanta

```powershell
# Ver los logs
docker-compose logs gateway

# Reconstruir la imagen
docker-compose build --no-cache gateway
docker-compose up -d gateway
```

### Cambios en código no se reflejan

Para Sprint 0 esto es esperado: no hay hot-reload aún (se añade en Sprint 2). Cualquier cambio requiere `docker-compose build` + `docker-compose up -d`.

## Próximo paso

Cuando este sprint esté cerrado, abrir conversación nueva o continuar y avanzar a Sprint 1: profundizar en la estructura de servicios y preparar todo para empezar `auth-service` en Sprint 2.
