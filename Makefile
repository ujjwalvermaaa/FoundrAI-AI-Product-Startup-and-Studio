# ============================================
# FoundrAI — Project Makefile
# From Idea to Startup, Powered by AI
# ============================================

.PHONY: help dev db-up db-down migrate migrate-down migrate-history \
        test test-backend test-frontend test-ai lint lint-backend lint-frontend \
        format build clean setup seed logs shell-backend shell-db \
        docker-build docker-up docker-down docker-logs \
        eval install-backend install-frontend ollama-setup

# Default target
.DEFAULT_GOAL := help

# ============================================
# COLORS
# ============================================
CYAN  := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED   := \033[0;31m
RESET := \033[0m

# ============================================
# VARIABLES
# ============================================
BACKEND_DIR := backend
FRONTEND_DIR := frontend
AI_DIR := ai
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_PROD := docker compose -f docker-compose.prod.yml
PYTHON := python3
POETRY := poetry
PNPM := pnpm

# ============================================
# HELP
# ============================================
help: ## Show this help message
	@echo ""
	@echo "$(CYAN)FoundrAI — Development Commands$(RESET)"
	@echo "$(CYAN)=================================$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-25s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ============================================
# DEVELOPMENT
# ============================================
dev: db-up ## Start full development stack (DB + backend + frontend)
	@echo "$(CYAN)Starting FoundrAI development stack...$(RESET)"
	@make -j2 dev-backend dev-frontend

dev-backend: ## Start backend development server
	@echo "$(CYAN)Starting FastAPI backend on :8000...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run uvicorn app.main:app \
		--reload \
		--host 0.0.0.0 \
		--port 8000 \
		--log-level info

dev-frontend: ## Start Next.js frontend on :3000
	@echo "$(CYAN)Starting Next.js frontend on :3000...$(RESET)"
	@cd $(FRONTEND_DIR) && $(PNPM) dev

# ============================================
# DATABASE
# ============================================
db-up: ## Start PostgreSQL via Docker
	@echo "$(CYAN)Starting PostgreSQL...$(RESET)"
	@$(DOCKER_COMPOSE) up -d postgres
	@echo "$(GREEN)PostgreSQL ready on localhost:5432$(RESET)"

db-down: ## Stop PostgreSQL
	@echo "$(YELLOW)Stopping PostgreSQL...$(RESET)"
	@$(DOCKER_COMPOSE) down

db-reset: ## Drop and recreate database (DESTRUCTIVE)
	@echo "$(RED)WARNING: This will destroy all data!$(RESET)"
	@read -p "Are you sure? [y/N]: " confirm; \
	if [ "$$confirm" = "y" ]; then \
		$(DOCKER_COMPOSE) down -v; \
		$(DOCKER_COMPOSE) up -d postgres; \
		sleep 3; \
		make migrate; \
	fi

migrate: ## Run all pending Alembic migrations
	@echo "$(CYAN)Running database migrations...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run alembic upgrade head
	@echo "$(GREEN)Migrations complete$(RESET)"

migrate-down: ## Roll back last migration
	@echo "$(YELLOW)Rolling back last migration...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run alembic downgrade -1

migrate-history: ## Show migration history
	@cd $(BACKEND_DIR) && $(POETRY) run alembic history --verbose

migrate-create: ## Create new migration (usage: make migrate-create MSG="add users table")
	@cd $(BACKEND_DIR) && $(POETRY) run alembic revision --autogenerate -m "$(MSG)"

# ============================================
# TESTING
# ============================================
test: test-backend test-ai ## Run all tests
	@echo "$(GREEN)All tests passed!$(RESET)"

test-backend: ## Run backend tests
	@echo "$(CYAN)Running backend tests...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run pytest tests/ -v \
		--tb=short \
		--cov=app \
		--cov-report=term-missing \
		--cov-fail-under=70

test-frontend: ## Run frontend tests
	@echo "$(CYAN)Running frontend tests...$(RESET)"
	@cd $(FRONTEND_DIR) && $(PNPM) test --run

test-ai: ## Run AI unit tests
	@echo "$(CYAN)Running AI tests...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run pytest tests/ai/ -v --tb=short

test-watch: ## Run tests in watch mode
	@cd $(BACKEND_DIR) && $(POETRY) run pytest tests/ -v --tb=short -f

# ============================================
# LINTING & FORMATTING
# ============================================
lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend Python code
	@echo "$(CYAN)Linting backend...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run ruff check .
	@cd $(BACKEND_DIR) && $(POETRY) run mypy app/ --ignore-missing-imports

lint-frontend: ## Lint frontend TypeScript code
	@echo "$(CYAN)Linting frontend...$(RESET)"
	@cd $(FRONTEND_DIR) && $(PNPM) lint

format: format-backend format-frontend ## Format all code

format-backend: ## Format backend Python code
	@echo "$(CYAN)Formatting backend...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run ruff format .
	@cd $(BACKEND_DIR) && $(POETRY) run ruff check --fix .

format-frontend: ## Format frontend TypeScript code
	@echo "$(CYAN)Formatting frontend...$(RESET)"
	@cd $(FRONTEND_DIR) && $(PNPM) format

# ============================================
# INSTALLATION
# ============================================
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python dependencies
	@echo "$(CYAN)Installing backend dependencies...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) install

install-frontend: ## Install Node.js dependencies
	@echo "$(CYAN)Installing frontend dependencies...$(RESET)"
	@cd $(FRONTEND_DIR) && $(PNPM) install

# ============================================
# BUILD
# ============================================
build: ## Build both frontend and backend for production
	@make build-frontend
	@make build-backend

build-frontend: ## Build Next.js for production
	@echo "$(CYAN)Building frontend...$(RESET)"
	@cd $(FRONTEND_DIR) && $(PNPM) build

build-backend: ## Build backend (type check + lint)
	@echo "$(CYAN)Building backend...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run mypy app/

# ============================================
# SETUP
# ============================================
setup: ## Complete first-time project setup
	@echo "$(CYAN)Setting up FoundrAI...$(RESET)"
	@cp -n .env.example .env || true
	@make install
	@make db-up
	@sleep 3
	@make migrate
	@make seed
	@echo "$(GREEN)Setup complete! Run 'make dev' to start.$(RESET)"

seed: ## Seed database with initial data
	@echo "$(CYAN)Seeding database...$(RESET)"
	@cd $(BACKEND_DIR) && $(POETRY) run python -m app.database.seed

seed-knowledge: ## Build FAISS knowledge base index
	@echo "$(CYAN)Building knowledge base index...$(RESET)"
	@$(PYTHON) scripts/build_index.py

# ============================================
# OLLAMA
# ============================================
ollama-setup: ## Install and configure Ollama with Qwen 3 8B
	@echo "$(CYAN)Setting up Ollama...$(RESET)"
	@which ollama || (echo "$(RED)Ollama not found. Install from https://ollama.ai$(RESET)" && exit 1)
	@echo "$(CYAN)Pulling qwen3:8b model (this may take several minutes)...$(RESET)"
	@ollama pull qwen3:8b
	@echo "$(GREEN)Ollama ready with qwen3:8b$(RESET)"

ollama-check: ## Check if Ollama is running and model is available
	@curl -s http://localhost:11434/api/tags | grep -q "qwen3:8b" \
		&& echo "$(GREEN)✓ Ollama running with qwen3:8b$(RESET)" \
		|| echo "$(RED)✗ Ollama not running or qwen3:8b not available$(RESET)"

# ============================================
# EVALUATION
# ============================================
eval: ## Run AI agent evaluation suite
	@echo "$(CYAN)Running AI evaluation suite...$(RESET)"
	@$(PYTHON) scripts/run_evals.py

# ============================================
# DOCKER
# ============================================
docker-build: ## Build Docker images
	@echo "$(CYAN)Building Docker images...$(RESET)"
	@$(DOCKER_COMPOSE_PROD) build

docker-up: ## Start production Docker stack
	@echo "$(CYAN)Starting production stack...$(RESET)"
	@$(DOCKER_COMPOSE_PROD) up -d

docker-down: ## Stop production Docker stack
	@echo "$(YELLOW)Stopping production stack...$(RESET)"
	@$(DOCKER_COMPOSE_PROD) down

docker-logs: ## Tail production Docker logs
	@$(DOCKER_COMPOSE_PROD) logs -f

# ============================================
# UTILITIES
# ============================================
logs: ## Tail all development logs
	@tail -f logs/*.log 2>/dev/null || echo "No log files found"

shell-backend: ## Open Python shell with app context
	@cd $(BACKEND_DIR) && $(POETRY) run python -c "import asyncio; from app.database.session import get_db; print('Shell ready')"

shell-db: ## Open PostgreSQL shell
	@$(DOCKER_COMPOSE) exec postgres psql -U foundrai -d foundrai

clean: ## Clean build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf $(FRONTEND_DIR)/.next $(FRONTEND_DIR)/out 2>/dev/null || true
	@echo "$(GREEN)Clean complete$(RESET)"

status: ## Show status of all services
	@echo "$(CYAN)Service Status:$(RESET)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@make ollama-check

reset-dev: ## Full dev environment reset (DESTRUCTIVE)
	@$(PYTHON) scripts/reset_dev.py
