FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels \
    "fastapi==0.115.6" \
    "uvicorn[standard]==0.34.0" \
    "pydantic==2.10.4" \
    "pydantic-settings==2.7.0" \
    "pydantic[email]==2.10.4" \
    "sqlalchemy[asyncio]==2.0.36" \
    "asyncpg==0.30.0" \
    "psycopg2-binary==2.9.10" \
    "alembic==1.14.0" \
    "pyjwt==2.10.1" \
    "dependency-injector==4.43.0" \
    "structlog==24.4.0"

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app app

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

COPY src ./src
COPY alembic ./alembic
COPY alembic.ini .

ENV PYTHONPATH=/app/src

RUN chown -R app:app /app
USER app

EXPOSE 8002

CMD ["uvicorn", "diagnostico.main:app", "--host", "0.0.0.0", "--port", "8002"]