#!/bin/bash

# --- Uniwatch One-Click Startup Script ---
# This script orchestrates the Prometheus server, Django backend, and React frontend.

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔭 Starting Uniwatch Infrastructure...${NC}"

# Add Homebrew to PATH for Mac users
export PATH=$PATH:/opt/homebrew/bin:/usr/local/bin

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${RED}🛑 Shutting down services...${NC}"
    kill $PROMETHEUS_PID $DJANGO_PID $VITE_PID 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# 1. Start Prometheus
echo -e "${GREEN}🔥 Starting Prometheus...${NC}"
prometheus --config.file=prometheus/prometheus.yml > prometheus.log 2>&1 &
PROMETHEUS_PID=$!

# 2. Start Django Backend
echo -e "${GREEN}🐍 Starting Django Backend...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}⚠️ No virtual environment found. Running with system python...${NC}"
fi
python3 manage.py runserver 8000 > django.log 2>&1 &
DJANGO_PID=$!

# 3. Start React Frontend
echo -e "${GREEN}⚛️ Starting React Frontend...${NC}"
cd react_dashboard
npm run dev > ../vite.log 2>&1 &
VITE_PID=$!
cd ..

echo -e "\n${BLUE}✨ Uniwatch is warming up!${NC}"
echo -e "----------------------------------------"
echo -e "📊 Prometheus Dashboard: ${BLUE}http://localhost:9090${NC}"
echo -e "🖥️ Django Admin/API:    ${BLUE}http://localhost:8000${NC}"
echo -e "🚀 React Dashboard:     ${BLUE}http://localhost:5173${NC}"
echo -e "----------------------------------------"
echo -e "Press ${RED}Ctrl+C${NC} to stop all services.\n"

# Keep the script running to maintain child processes
wait
