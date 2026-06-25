# AI Resume Analyzer

An intelligent resume analysis tool powered by multiple AI providers. Upload a PDF or DOCX resume, optionally paste a job description, and get an instant AI-powered score, keyword analysis, ATS compatibility check, and actionable improvement suggestions.

[![CI/CD](https://github.com/AyushBh123/ai-resume-analyzer/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/AyushBh123/ai-resume-analyzer/actions/workflows/ci-cd.yml)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-19+-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-6+-3178C6.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Live Demo

| | URL |
|---|---|
| **App** | https://ai-resume-analyzer-ayush.vercel.app |
| **API** | https://ai-resume-analyzer-api-h9aw.onrender.com |
| **API Docs** | https://ai-resume-analyzer-api-h9aw.onrender.com/docs |

> **Note:** The backend runs on Render's free tier and may take ~30 seconds to wake up after inactivity.

## Features

- **Multi-Format Support** — Upload PDF or DOCX resumes
- **AI-Powered Analysis** — Extracts structured data and scores your resume using GPT-4 / Claude / local LLMs
- **Job Matching** — Paste a job description to get a tailored match score and missing keywords
- **ATS Compatibility** — Checks if your resume will pass Applicant Tracking Systems
- **Improvement Suggestions** — Prioritised, actionable feedback (critical → low)
- **Multi-Provider** — Switch between OpenAI, Anthropic Claude, or Ollama (local)

## Architecture

```
┌─────────────────────────────────────────┐
│           Frontend (React + Vite)        │
│   FileUpload → Analyze → Results Dashboard│
└──────────────────┬──────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────┐
│           Backend (FastAPI)              │
│  ┌────────────┐  ┌──────────────────┐   │
│  │  Parsers   │  │   AI Providers   │   │
│  │ PDF / DOCX │  │ OpenAI (OpenRouter│   │
│  └────────────┘  │ Anthropic / Ollama│   │
│                  └──────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │     Analysis Engine              │   │
│  │  Scoring · Matching · Suggestions│   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript 6, Vite, Tailwind CSS, Recharts |
| Backend | Python 3.11, FastAPI, Pydantic v2, Uvicorn |
| AI | OpenAI / OpenRouter, Anthropic Claude, Ollama |
| Parsing | pdfplumber, PyPDF2, python-docx |
| Deployment | Vercel (frontend), Render (backend) |
| CI/CD | GitHub Actions (test → lint → docker build → deploy) |

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- An API key from [OpenAI](https://platform.openai.com/api-keys), [Anthropic](https://console.anthropic.com/), or [OpenRouter](https://openrouter.ai/keys)

### Setup

**1. Clone**
```bash
git clone https://github.com/AyushBh123/ai-resume-analyzer.git
cd ai-resume-analyzer
```

**2. Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Environment**
```bash
cp .env.example .env
# Edit .env — add at minimum:
# OPENAI_API_KEY=sk-...
# DEFAULT_AI_PROVIDER=openai
```

**4. Run backend**
```bash
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs
```

**5. Frontend** (new terminal)
```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Using OpenRouter (instead of direct OpenAI)
Add these to your `.env`:
```env
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini
```

## Project Structure

```
ai-resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/routes/         # analyze.py · upload.py · health.py
│   │   ├── core/
│   │   │   ├── ai_providers/   # base.py · openai · anthropic · ollama
│   │   │   └── parsers/        # pdf_parser.py · docx_parser.py
│   │   ├── models/             # resume.py · analysis.py (Pydantic)
│   │   ├── utils/              # text_processing.py
│   │   ├── config.py           # Settings (singleton)
│   │   └── main.py             # FastAPI app entry point
│   ├── tests/                  # 37 unit + integration tests
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/         # FileUpload · AnalysisResults · ScoreCard · SuggestionsList
│       ├── services/api.ts     # All HTTP calls to backend
│       └── types/api.ts        # TypeScript type definitions
├── render.yaml                 # Render deployment config
├── Procfile                    # Heroku fallback
├── docker-compose.yml          # Local full-stack Docker setup
└── .github/workflows/ci-cd.yml # CI pipeline
```

## Key Design Patterns

**Adapter Pattern** — All AI providers implement the same `BaseAIProvider` interface:
```python
class OpenAIProvider(BaseAIProvider):
    def analyze_resume(self, request: AnalysisRequest) -> AnalysisResponse: ...
    def extract_resume_data(self, text: str) -> dict: ...
    def compare_with_job(self, resume: str, jd: str) -> dict: ...
    def generate_suggestions(self, text: str, data: dict) -> list: ...
```
Adding a new AI provider = create one class, implement four methods.

**Singleton Pattern** — Config loaded once from `.env`, reused everywhere:
```python
settings = get_settings()   # reads .env once, cached globally
```

**Strategy Pattern** — Weighted scoring across independent dimensions:
```
Overall Score = content×25% + experience×20% + education×15%
              + skills×15% + keywords×10% + formatting×10% + ats×5%
```

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v          # run all 37 tests
```

## Docker

```bash
docker compose up -d       # start both services
docker compose logs -f     # tail logs
docker compose down        # stop
```

## Deployment

| Service | Platform | Auto-deploy |
|---|---|---|
| Frontend | Vercel | ✅ on push to `main` |
| Backend | Render | ✅ on push to `main` |

Every `git push origin main` deploys both automatically.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes (one of three) | OpenAI or OpenRouter key |
| `OPENAI_BASE_URL` | No | Set to `https://openrouter.ai/api/v1` for OpenRouter |
| `OPENAI_MODEL` | No | Default: `gpt-4-turbo-preview` |
| `ANTHROPIC_API_KEY` | Yes (one of three) | Anthropic Claude key |
| `OLLAMA_BASE_URL` | Yes (one of three) | Default: `http://localhost:11434` |
| `DEFAULT_AI_PROVIDER` | Yes | `openai`, `anthropic`, or `ollama` |
| `CORS_ORIGINS` | Yes | Comma-separated frontend URLs |
| `MAX_FILE_SIZE_MB` | No | Default: `10` |

## Author

**Ayush Bhardwaj**
- GitHub: [@AyushBh123](https://github.com/AyushBh123)
- Email: ayushcar4@gmail.com

---

⭐ If you find this project useful, please give it a star!
