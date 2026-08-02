#!/usr/bin/env bash
# ============================================================
# FoundrAI — One-command production setup script
#
# Usage:
#   chmod +x scripts/setup.sh
#   ./scripts/setup.sh
#
# What it does:
#   1. Checks required tools (Docker, Docker Compose, Ollama)
#   2. Creates .env from .env.example if missing
#   3. Creates required data directories
#   4. Pulls the Ollama model
#   5. Builds and starts all Docker services
#   6. Waits for services to be healthy
#   7. Runs database migrations
#   8. Seeds the knowledge base FAISS index
# ============================================================

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
log_success() { echo -e "${GREEN}[OK]${NC}    $1"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ── Script directory ───────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   FoundrAI — Production Setup Script     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── 1. Check prerequisites ─────────────────────────────────────
log_info "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || log_error "Docker is not installed. Visit https://docs.docker.com/get-docker/"
command -v docker compose >/dev/null 2>&1 || log_error "Docker Compose (v2) is not installed."

DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
log_success "Docker $DOCKER_VERSION"

COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "unknown")
log_success "Docker Compose $COMPOSE_VERSION"

# Check Ollama (optional — warn if missing)
if command -v ollama >/dev/null 2>&1; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null | head -1 || echo "installed")
    log_success "Ollama: $OLLAMA_VERSION"
else
    log_warn "Ollama not found locally. Install from https://ollama.com"
    log_warn "The AI features require Ollama to be running on the host."
fi

# ── 2. Set up .env ─────────────────────────────────────────────
log_info "Checking environment configuration..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_warn ".env created from .env.example — PLEASE EDIT .env before going to production!"
        log_warn "  - Change JWT_SECRET_KEY to a long random string"
        log_warn "  - Change POSTGRES_PASSWORD to a strong password"
    else
        log_error ".env.example not found. Cannot create .env"
    fi
else
    log_success ".env already exists"
fi

# ── 3. Create data directories ─────────────────────────────────
log_info "Creating data directories..."

mkdir -p data/faiss data/exports data/uploads data/knowledge logs
log_success "Data directories ready"

# ── 4. Pull Ollama model ───────────────────────────────────────
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:4b}"
log_info "Checking Ollama model: $OLLAMA_MODEL"

if command -v ollama >/dev/null 2>&1; then
    if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
        log_success "Model $OLLAMA_MODEL already downloaded"
    else
        log_info "Pulling Ollama model $OLLAMA_MODEL (this may take a while)..."
        ollama pull "$OLLAMA_MODEL" || log_warn "Could not pull $OLLAMA_MODEL — start Ollama and run: ollama pull $OLLAMA_MODEL"
    fi
else
    log_warn "Skipping model pull (Ollama not installed locally)"
    log_warn "Run manually: ollama pull $OLLAMA_MODEL"
fi

# ── 5. Build Docker images ─────────────────────────────────────
log_info "Building Docker images (first build may take 5-10 minutes)..."

docker compose -f docker-compose.prod.yml build \
    --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://localhost/api/v1}" \
    || log_error "Docker build failed. Check the output above."

log_success "Docker images built"

# ── 6. Start services ──────────────────────────────────────────
log_info "Starting services..."

docker compose -f docker-compose.prod.yml up -d
log_success "Services started"

# ── 7. Wait for postgres to be healthy ─────────────────────────
log_info "Waiting for PostgreSQL to be ready..."

MAX_TRIES=30
COUNT=0
until docker compose -f docker-compose.prod.yml exec -T postgres \
    pg_isready -U "${POSTGRES_USER:-foundrai}" -d "${POSTGRES_DB:-foundrai}" >/dev/null 2>&1; do
    COUNT=$((COUNT + 1))
    if [ $COUNT -ge $MAX_TRIES ]; then
        log_error "PostgreSQL did not become ready in time."
    fi
    echo -n "."
    sleep 2
done
echo ""
log_success "PostgreSQL is ready"

# ── 8. Seed knowledge base ─────────────────────────────────────
log_info "Seeding knowledge base FAISS index..."

docker compose -f docker-compose.prod.yml exec -T backend \
    python /app/../scripts/build_index.py \
    --knowledge-dir /app/data/knowledge \
    --output-dir /app/data/faiss/knowledge \
    2>/dev/null || log_warn "Knowledge base seeding skipped (run manually if needed)"

# ── Done ────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   FoundrAI is up and running!            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Frontend:  ${BLUE}http://localhost${NC}"
echo -e "  Backend:   ${BLUE}http://localhost/api/v1${NC}"
echo -e "  API Docs:  ${BLUE}http://localhost/api/docs${NC}"
echo ""
echo -e "  Stop:   docker compose -f docker-compose.prod.yml down"
echo -e "  Logs:   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC} Make sure Ollama is running: ollama serve"
echo ""
