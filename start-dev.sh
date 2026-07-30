#!/usr/bin/env bash
# ───────────────────────────────────────────────────────────────
# start-dev.sh – Launch Python backend + Next.js dev server
# ───────────────────────────────────────────────────────────────
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cleanup() {
  echo -e "\n${YELLOW}Shutting down...${NC}"
  kill $BACKEND_PID 2>/dev/null || true
  kill $NEXT_PID 2>/dev/null || true
  wait
  echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT INT TERM

# ── 1. Python backend ──────────────────────────────────────
echo -e "${CYAN}🔧 Seeding database...${NC}"
cd "$ROOT_DIR"
python3 -c "from backend.seed import seed_database; seed_database()"

echo -e "${CYAN}🚀 Starting Python backend on http://0.0.0.0:8000${NC}"
cd "$ROOT_DIR"
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for Python backend...${NC}"
for i in $(seq 1 30); do
  if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Python backend is ready${NC}"
    break
  fi
  if [ "$i" = "30" ]; then
    echo -e "${YELLOW}⚠️  Backend didn't respond in time, continuing anyway...${NC}"
  fi
  sleep 1
done

# ── 2. Next.js dev server ──────────────────────────────────
echo -e "${CYAN}🚀 Starting Next.js dev server on http://localhost:3000${NC}"
cd "$ROOT_DIR"
bun run dev &
NEXT_PID=$!

# ── 3. Show status ─────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Dashboard is running!${NC}"
echo -e "${GREEN}  Frontend : http://localhost:3000${NC}"
echo -e "${GREEN}  Backend  : http://localhost:8000${NC}"
echo -e "${GREEN}  API Docs : http://localhost:8000/docs${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Press Ctrl+C to stop both servers."

# Wait for any process to exit
wait
