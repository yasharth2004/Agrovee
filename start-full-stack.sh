#!/bin/bash
# Agrovee Full Stack Startup Script

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Agrovee Full Stack${NC}"
echo ""

# 1. Activate virtual environment
echo -e "${YELLOW}1. Activating Python environment...${NC}"
source venv/bin/activate

# 2. Start Backend
echo -e "${YELLOW}2. Starting Backend API on port 8000...${NC}"
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "  📡 API: http://127.0.0.1:8000"
echo -e "  📚 Docs: http://127.0.0.1:8000/api/docs"
sleep 2

# 3. Start Frontend
echo -e "${YELLOW}3. Starting Frontend on port 3000...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "  🌐 Web: http://localhost:3000"
echo ""

echo -e "${GREEN}✅ All servers running!${NC}"
echo ""
echo -e "${YELLOW}To stop:${NC}"
echo "  kill $BACKEND_PID    # Stop backend"
echo "  kill $FRONTEND_PID   # Stop frontend"
echo ""

# Keep the script running
wait
