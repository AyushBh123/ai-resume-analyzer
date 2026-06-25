# 🚀 AI Resume Analyzer - Setup Guide

Complete guide to set up and run the AI Resume Analyzer locally.

## 📋 Prerequisites

### Required
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/) (for frontend, optional)
- **Git** - [Download](https://git-scm.com/)

### Optional
- **Docker** - [Download](https://www.docker.com/) (for containerized deployment)
- **Ollama** - [Download](https://ollama.ai/) (for local LLM support)

### AI Provider (Choose at least one)
- **OpenAI API Key** - [Get Key](https://platform.openai.com/api-keys)
- **Anthropic API Key** - [Get Key](https://console.anthropic.com/)
- **Ollama** - Free, runs locally

## 🔧 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Required Configuration:**

```env
# Add at least ONE AI provider API key
OPENAI_API_KEY=sk-...                    # Get from OpenAI
ANTHROPIC_API_KEY=sk-ant-...             # Get from Anthropic
OLLAMA_BASE_URL=http://localhost:11434   # If using Ollama

# Choose default provider
DEFAULT_AI_PROVIDER=openai  # or anthropic, ollama
```

### Step 4: Run Backend

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload

# Server will start at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## 🐳 Docker Setup (Alternative)

If you prefer Docker:

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## 🧪 Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Try the `/api/v1/health` endpoint
3. Upload a resume using `/api/v1/analyze`

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# List providers
curl http://localhost:8000/api/v1/providers

# Analyze resume
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "file=@/path/to/resume.pdf" \
  -F "provider=openai"
```

### Using Python

```python
import requests

# Analyze resume
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/analyze',
        files={'file': f},
        data={'provider': 'openai'}
    )

result = response.json()
print(result)
```

## 🔍 Troubleshooting

### Issue: "OpenAI API key not configured"

**Solution:** Make sure you've set `OPENAI_API_KEY` in your `.env` file.

```bash
# Check if .env exists
ls -la .env

# Verify content
cat .env | grep OPENAI_API_KEY
```

### Issue: "Cannot connect to Ollama"

**Solution:** Make sure Ollama is running.

```bash
# Start Ollama
ollama serve

# Pull a model
ollama pull llama2

# Test
curl http://localhost:11434/api/tags
```

### Issue: "Module not found"

**Solution:** Make sure virtual environment is activated and dependencies are installed.

```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution:** Change the port or kill the process.

```bash
# Use different port
uvicorn app.main:app --port 8001

# Or find and kill process
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

## 📊 Verifying Installation

Run this checklist:

```bash
# 1. Check Python version
python --version  # Should be 3.11+

# 2. Check if venv is activated
which python  # Should point to venv

# 3. Test imports
python -c "import fastapi; import pydantic; print('OK')"

# 4. Check API
curl http://localhost:8000/api/v1/health

# 5. Check providers
curl http://localhost:8000/api/v1/providers
```

## 🎯 Next Steps

### For Development

1. **Read the code**: Start with `backend/app/main.py`
2. **Check documentation**: Every file has extensive comments
3. **Try examples**: Use the Swagger UI at `/docs`
4. **Modify prompts**: Edit AI provider files to customize analysis

### For Production

1. **Set environment to production**:
   ```env
   ENVIRONMENT=production
   DEBUG=false
   ```

2. **Use production-grade server**:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Set up monitoring**: Add logging, metrics, alerts

4. **Configure CORS**: Update `CORS_ORIGINS` for your domain

5. **Add authentication**: Implement JWT or API keys

## 🔐 Security Checklist

- [ ] Never commit `.env` file
- [ ] Use strong API keys
- [ ] Set `DEBUG=false` in production
- [ ] Configure CORS properly
- [ ] Use HTTPS in production
- [ ] Implement rate limiting
- [ ] Add authentication
- [ ] Validate all inputs
- [ ] Scan uploaded files
- [ ] Monitor API usage

## 📚 Additional Resources

### Documentation
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **README**: See main README.md
- **Learning Guide**: See LEARNING_GUIDE.md

### AI Providers
- **OpenAI**: https://platform.openai.com/docs
- **Anthropic**: https://docs.anthropic.com
- **Ollama**: https://ollama.ai/

### Frameworks
- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/

## 💡 Tips for Interviews

When discussing this project:

1. **Start with architecture**: "I built a full-stack application with FastAPI backend..."

2. **Highlight design patterns**: "I used the adapter pattern for AI providers..."

3. **Discuss challenges**: "Parsing different resume formats was challenging..."

4. **Show extensibility**: "Adding a new AI provider is easy - just implement four methods..."

5. **Mention best practices**: "I use type hints, comprehensive error handling, and Docker for deployment..."

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: Look at console output for errors
2. **Read error messages**: They're designed to be helpful
3. **Check configuration**: Verify `.env` file
4. **Test components**: Try each endpoint individually
5. **Review code comments**: Every file has detailed explanations

## ✅ Success Indicators

You're ready when:

- ✅ Backend starts without errors
- ✅ Health check returns "healthy"
- ✅ At least one AI provider is available
- ✅ You can upload and analyze a resume
- ✅ API documentation loads at `/docs`

---

**Ready to build something amazing? Let's go! 🚀**