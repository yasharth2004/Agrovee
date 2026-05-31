#!/bin/bash
# Simple startup script for Agrovee full stack
# Usage: bash start-app.sh

set -e

PROJECT_ROOT="/Users/yasharthkesarwani/Downloads/Agrovee"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_PYTHON="$PROJECT_ROOT/venv/bin/python"

echo "╔════════════════════════════════════════════════╗"
echo "║  🌾 Agrovee - Full Stack Startup              ║"
echo "╚════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -f "$VENV_PYTHON" ]; then
  echo -e "${YELLOW}⚠ Virtual environment not found at $PROJECT_ROOT/venv${NC}"
  echo "Please run: python3.12 -m venv $PROJECT_ROOT/venv"
  exit 1
fi

echo -e "${BLUE}📦 Environment Verified${NC}"
echo "  ✓ Python: $VENV_PYTHON"
echo ""

# Start Backend
echo -e "${BLUE}🚀 Starting Backend API (Port 8000)...${NC}"
cd "$BACKEND_DIR"
PYTHONPATH="$BACKEND_DIR" "$VENV_PYTHON" -m uvicorn app.main:app \
  --host 127.0.0.1 --port 8000 > /tmp/agrovee-backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "  📡 API: http://127.0.0.1:8000"
echo "  📚 Docs: http://127.0.0.1:8000/api/docs"
sleep 2

# Start Frontend
echo ""
echo -e "${BLUE}🌐 Starting Frontend (Port 3000)...${NC}"
cd "$FRONTEND_DIR"
npm run dev > /tmp/agrovee-frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "  🌐 Web: http://localhost:3000"
echo ""

echo "╔════════════════════════════════════════════════╗"
echo -e "${GREEN}✅ All servers running!${NC}"
echo "╚════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}Access your app:${NC}"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://127.0.0.1:8000"
echo "  API Docs: http://127.0.0.1:8000/api/docs"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "  Backend:  tail -f /tmp/agrovee-backend.log"
echo "  Frontend: tail -f /tmp/agrovee-frontend.log"
echo ""
echo -e "${YELLOW}To stop servers:${NC}"
echo "  kill $BACKEND_PID   # Stop backend"
echo "  kill $FRONTEND_PID  # Stop frontend"
echo ""
echo "Happy coding! 🚀"
