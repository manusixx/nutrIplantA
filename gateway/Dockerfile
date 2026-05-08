# ============================================================
# nutrI-plantA Gateway — Dockerfile
# ============================================================
# Multi-stage build para imagen mínima en producción.
# ============================================================

# --- Stage 1: builder ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y compilar dependencias en wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


# --- Stage 2: runtime ---
FROM python:3.12-slim

WORKDIR /app

# curl para healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para ejecutar la app
RUN groupadd -r app && useradd -r -g app app

# Instalar dependencias desde los wheels precompilados
COPY --from=builder /build/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copiar código de la aplicación
COPY app ./app

# Cambiar ownership al usuario app
RUN chown -R app:app /app
USER app

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
