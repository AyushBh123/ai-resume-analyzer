# 🚀 Quick Start Guide

Get your AI Resume Analyzer up and running in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- OpenAI API key OR Anthropic API key OR Ollama installed locally

## Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
./setup.sh

# Edit backend/.env and add your API key
nano backend/.env

# Start backend (Terminal 1)
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start frontend (Terminal 2)
cd frontend && npm run dev
```

## Option 2: Docker (Easiest)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 2. Start everything
docker-compose up -d

# 3. Access the app
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Option 3: Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

## Configuration

### Backend (.env)

```env
# Required: Choose at least one AI provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434

# Optional
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Verify Installation

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Frontend Access**
   - Open http://localhost:5173 in your browser
   - You should see the AI Resume Analyzer interface

3. **API Documentation**
   - Visit http://localhost:8000/docs
   - Interactive API documentation with Swagger UI

## First Analysis

1. Open http://localhost:5173
2. Drag and drop a resume (PDF or DOCX)
3. Optionally add a job description
4. Select AI provider (OpenAI, Anthropic, or Ollama)
5. Click "Analyze Resume"
6. View comprehensive results!

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API connection error
- Ensure backend is running on port 8000
- Check VITE_API_BASE_URL in frontend/.env
- Verify CORS settings in backend

### AI provider errors
- Verify API keys in backend/.env
- Check API key permissions
- Ensure sufficient API credits
- For Ollama: ensure it's running (`ollama serve`)

## Next Steps

- Read [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) for full project overview
- Check [LEARNING_GUIDE.md](LEARNING_GUIDE.md) to understand the code
- Review [PORTFOLIO_HIGHLIGHTS.md](PORTFOLIO_HIGHLIGHTS.md) for interview prep
- See [SETUP.md](SETUP.md) for detailed setup instructions

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review error messages in terminal
3. Check backend logs
4. Verify all prerequisites are installed
5. Ensure API keys are valid

## Quick Commands Reference

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Docker
docker-compose up -d
docker-compose down
docker-compose logs -f

# Health check
curl http://localhost:8000/health

# Build frontend for production
cd frontend && npm run build
```

Happy analyzing! 🎉