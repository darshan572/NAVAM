# =============================================================================
# NAVAM — Root Makefile
# Near-real-time Analysis of Vulnerability and Adaptive Migration
#
# Usage:
#   make help       — list all targets
#   make up         — start full dev stack
#   make demo       — start minimal demo stack
# =============================================================================

.PHONY: help up demo down down-v logs lint test train-ml db-migrate db-seed \
        db-reset health score open build push clean fmt

# Default target
.DEFAULT_GOAL := help

# ─── Compose files ─────────────────────────────────────────────────────────
COMPOSE_FILE      := docker-compose.yml
COMPOSE_DEMO_FILE := docker-compose.demo.yml
COMPOSE           := docker compose -f $(COMPOSE_FILE)
COMPOSE_DEMO      := docker compose -f $(COMPOSE_DEMO_FILE)

# ─── App paths ─────────────────────────────────────────────────────────────
API_DIR      := apps/api
WORKER_DIR   := apps/worker
WEB_DIR      := apps/web
ML_DIR       := services/ml
SERVING_DIR  := services/ml/serving

# ─── Colours ───────────────────────────────────────────────────────────────
BOLD  := \033[1m
RESET := \033[0m
GREEN := \033[32m
CYAN  := \033[36m

# ─── Target: help ──────────────────────────────────────────────────────────
help: ## Show this help message
	@echo ""
	@echo "$(BOLD)NAVAM — Infrastructure Commands$(RESET)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ \
	  { printf "  $(CYAN)%-18s$(RESET) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ─── Docker Compose ────────────────────────────────────────────────────────

up: ## Start the full development stack (all services)
	@echo "$(BOLD)Starting full dev stack...$(RESET)"
	$(COMPOSE) up -d --build
	@echo ""
	@echo "$(GREEN)Services ready:$(RESET)"
	@echo "  API        → http://localhost:8000/docs"
	@echo "  Grafana    → http://localhost:3001"
	@echo "  Prometheus → http://localhost:9090"
	@echo "  MLflow     → http://localhost:5001"
	@echo "  Keycloak   → http://localhost:8080"
	@echo "  Airflow    → http://localhost:8082"
	@echo "  Martin     → http://localhost:3000/catalog"

demo: ## Start minimal demo stack (8 services, boots < 60s)
	@echo "$(BOLD)Starting demo stack...$(RESET)"
	$(COMPOSE_DEMO) up -d --build
	@echo ""
	@echo "$(GREEN)Demo stack ready:$(RESET)"
	@echo "  Dashboard  → http://localhost:5173"
	@echo "  API        → http://localhost:8000/docs"
	@echo "  Grafana    → http://localhost:3001"
	@echo "  Martin     → http://localhost:3000/catalog"

down: ## Stop all containers (preserve volumes)
	@echo "$(BOLD)Stopping containers...$(RESET)"
	$(COMPOSE) down --remove-orphans
	$(COMPOSE_DEMO) down --remove-orphans 2>/dev/null || true

down-v: ## Stop all containers AND delete volumes (destructive!)
	@echo "$(BOLD)$(RESET)WARNING: This will delete all data volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
	    $(COMPOSE) down --volumes --remove-orphans; \
	    $(COMPOSE_DEMO) down --volumes --remove-orphans 2>/dev/null || true; \
	fi

logs: ## Tail logs from API and ML serving
	$(COMPOSE) logs -f api ml-serving

logs-all: ## Tail logs from all services
	$(COMPOSE) logs -f

# ─── Database ──────────────────────────────────────────────────────────────

db-migrate: ## Run Alembic migrations (upgrade head)
	@echo "$(BOLD)Running database migrations...$(RESET)"
	cd $(API_DIR) && alembic upgrade head

db-seed: ## Seed synthetic data for development/demo
	@echo "$(BOLD)Seeding database...$(RESET)"
	python infra/scripts/seed_data.py

db-reset: ## Drop, recreate, migrate, and seed the database (destructive!)
	@echo "$(BOLD)Resetting database...$(RESET)"
	$(COMPOSE) exec postgres psql -U navam -c "DROP DATABASE IF EXISTS navam;" 2>/dev/null || true
	$(COMPOSE) exec postgres psql -U navam -c "CREATE DATABASE navam;" 2>/dev/null || true
	$(MAKE) db-migrate
	$(MAKE) db-seed
	@echo "$(GREEN)Database reset complete$(RESET)"

db-shell: ## Open a psql shell in the postgres container
	$(COMPOSE) exec postgres psql -U navam -d navam

# ─── Testing ───────────────────────────────────────────────────────────────

test: ## Run all tests (Python + JavaScript)
	@echo "$(BOLD)Running Python tests...$(RESET)"
	pytest $(API_DIR)/tests/ $(ML_DIR)/tests/ -v --tb=short
	@echo ""
	@echo "$(BOLD)Running frontend tests...$(RESET)"
	cd $(WEB_DIR) && npm test -- --watchAll=false

test-api: ## Run only API tests
	pytest $(API_DIR)/tests/ -v --tb=short

test-ml: ## Run only ML tests
	pytest $(ML_DIR)/tests/ -v --tb=short

test-web: ## Run only frontend tests
	cd $(WEB_DIR) && npm test -- --watchAll=false

test-cov: ## Run Python tests with coverage report
	pytest $(API_DIR)/tests/ $(ML_DIR)/tests/ \
	    --cov=$(API_DIR)/src \
	    --cov=$(ML_DIR) \
	    --cov-report=term-missing \
	    --cov-report=html:htmlcov

# ─── Linting & Formatting ──────────────────────────────────────────────────

lint: ## Run ruff (Python) + ESLint (JS/TS)
	@echo "$(BOLD)Linting Python...$(RESET)"
	ruff check $(API_DIR)/src/ $(ML_DIR)/
	@echo "$(BOLD)Linting frontend...$(RESET)"
	cd $(WEB_DIR) && npm run lint

fmt: ## Auto-format Python (ruff) + Prettier (JS/TS)
	@echo "$(BOLD)Formatting Python...$(RESET)"
	ruff format $(API_DIR)/src/ $(ML_DIR)/
	@echo "$(BOLD)Formatting frontend...$(RESET)"
	cd $(WEB_DIR) && npm run format

typecheck: ## Run pyright + tsc
	@echo "$(BOLD)Type checking Python...$(RESET)"
	pyright $(API_DIR)/src/
	@echo "$(BOLD)Type checking frontend...$(RESET)"
	cd $(WEB_DIR) && npm run type-check

# ─── ML ────────────────────────────────────────────────────────────────────

train-ml: ## Train ML models (evacuation priority + route optimisation)
	@echo "$(BOLD)Starting ML training pipeline...$(RESET)"
	python $(ML_DIR)/training/train.py

serve-ml: ## Start ML serving locally (outside Docker)
	@echo "$(BOLD)Starting ML serving...$(RESET)"
	cd $(SERVING_DIR) && uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# ─── Health checks ─────────────────────────────────────────────────────────

health: ## Deep health check of the API
	@echo "$(BOLD)API deep health check:$(RESET)"
	curl -sf http://localhost:8000/health/deep | python -m json.tool

health-all: ## Health check all services
	@echo "$(BOLD)Health checks:$(RESET)"
	@echo -n "  API:        "; curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8000/health || echo "DOWN"
	@echo -n "  ML serving: "; curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8001/health || echo "DOWN"
	@echo -n "  Martin:     "; curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:3000/catalog || echo "DOWN"
	@echo -n "  Prometheus: "; curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:9090/-/healthy || echo "DOWN"
	@echo -n "  Grafana:    "; curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:3001/api/health || echo "DOWN"
	@echo -n "  Keycloak:   "; curl -sf -o /dev/null -w "%{http_code}\n" http://localhost:8080/health/ready || echo "DOWN"

# ─── Scoring endpoint ──────────────────────────────────────────────────────

## Usage: make score HABITATION_ID=<uuid>
HABITATION_ID ?= 00000000-0000-0000-0000-000000000001

score: ## Score a habitation by ID (usage: make score HABITATION_ID=<uuid>)
	@echo "$(BOLD)Scoring habitation: $(HABITATION_ID)$(RESET)"
	curl -sf http://localhost:8001/score/$(HABITATION_ID) | python -m json.tool

# ─── Browser shortcuts ─────────────────────────────────────────────────────

open: ## Open dashboard, Grafana, and Prometheus in browser
	@echo "$(BOLD)Opening browser tabs...$(RESET)"
	@python -m webbrowser http://localhost:5173  2>/dev/null || start http://localhost:5173
	@python -m webbrowser http://localhost:3001  2>/dev/null || start http://localhost:3001
	@python -m webbrowser http://localhost:9090  2>/dev/null || start http://localhost:9090

# ─── Build helpers ─────────────────────────────────────────────────────────

build: ## Build all Docker images locally
	$(COMPOSE) build

build-api: ## Build only the API image
	$(COMPOSE) build api

build-ml: ## Build only the ML serving image
	$(COMPOSE) build ml-serving

# ─── Cleanup ───────────────────────────────────────────────────────────────

clean: ## Remove Python caches, build artefacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleaned$(RESET)"
