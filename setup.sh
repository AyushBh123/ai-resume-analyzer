#!/bin/bash

# AI Resume Analyzer - Quick Setup Script
# This script sets up both backend and frontend

set -e  # Exit on error

echo "🚀 AI Resume Analyzer - Quick Setup"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Setup Backend
echo -e "${BLUE}Setting up Backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your API keys${NC}"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
cd ..
echo ""

# Setup Frontend
echo -e "${BLUE}Setting up Frontend...${NC}"
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install --silent

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
cd ..
echo ""

# Final instructions
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your API keys (OpenAI, Anthropic, or setup Ollama)"
echo "2. Start the backend:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "Access the application:"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}Happy analyzing! 🚀${NC}"

# Made with Bob
