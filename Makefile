# ============================================================
# nutrI-plantA — Makefile
# ============================================================
# Comandos comunes de desarrollo. Si no tienes 'make' en Windows
# nativo, instala con: choco install make
# o usa los comandos equivalentes documentados en cada target.
# ============================================================

.PHONY: help up down restart logs ps clean build test lint typecheck

# --- Por defecto: mostrar ayuda ---
help:
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  make up         Levantar el stack (postgres + minio + gateway)"
	@echo "  make down       Detener el stack (preserva datos)"
	@echo "  make restart    Reiniciar el stack"
	@echo "  make logs       Ver logs en tiempo real"
	@echo "  make ps         Ver estado de los servicios"
	@echo "  make clean      Detener y borrar volúmenes (datos perdidos)"
	@echo "  make build      Reconstruir imágenes (tras cambios en Dockerfile)"
	@echo "  make health     Probar el endpoint de salud"
	@echo ""
	@echo "Comandos de calidad (sprints posteriores):"
	@echo "  make test       Ejecutar tests"
	@echo "  make lint       Ejecutar ruff"
	@echo "  make typecheck  Ejecutar mypy"
	@echo ""

# --- Docker Compose ---
up:
	docker-compose up -d
	@echo ""
	@echo "Stack levantado. Verificando..."
	@sleep 5
	@$(MAKE) ps

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

ps:
	docker-compose ps

clean:
	docker-compose down -v
	@echo "Volúmenes borrados. Datos perdidos."

build:
	docker-compose build --no-cache

# --- Smoke tests ---
health:
	@echo "Probando endpoint de salud..."
	@curl -sf http://localhost:8080/api/v1/health | python -m json.tool || echo "Gateway no responde"

# --- Calidad (placeholders, se implementan desde Sprint 2) ---
test:
	@echo "Tests configurados desde Sprint 2"

lint:
	@echo "Linter configurado desde Sprint 2"

typecheck:
	@echo "Type checker configurado desde Sprint 2"
