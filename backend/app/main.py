"""
============================================================================
FASTAPI APPLICATION - MAIN ENTRY POINT
============================================================================
This is the main FastAPI application file.

KEY CONCEPTS TO UNDERSTAND:
1. FastAPI Application: ASGI web framework
2. Middleware: CORS, error handling
3. Routers: Modular route organization
4. Lifespan Events: Startup/shutdown hooks
5. Auto Documentation: Swagger UI, ReDoc

INTERVIEW TALKING POINTS:
- "I use FastAPI for its automatic API documentation and type safety"
- "CORS middleware allows frontend to communicate with backend"
- "Modular router structure keeps code organized"
- "Automatic validation with Pydantic models"

RUN WITH:
    uvicorn app.main:app --reload
    
ACCESS:
    - API: http://localhost:8000
    - Docs: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc
============================================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.routes import analyze, upload, health

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    
    WHAT IT DOES:
    - Runs code on application startup
    - Runs code on application shutdown
    - Manages resources (connections, etc.)
    
    WHY NEEDED:
    - Initialize resources once
    - Clean up on shutdown
    - Better than deprecated @app.on_event
    """
    # Startup
    logger.info("Starting AI Resume Analyzer API...")
    settings = get_settings()
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Default AI Provider: {settings.default_ai_provider}")
    
    # Ensure upload directory exists
    settings.ensure_upload_dir()
    logger.info(f"Upload directory: {settings.upload_dir}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Resume Analyzer API...")


# ============================================================================
# CREATE FASTAPI APPLICATION
# ============================================================================

settings = get_settings()

app = FastAPI(
    title="AI Resume Analyzer API",
    description="""
    Intelligent resume analysis powered by multiple AI providers.
    
    ## Features
    
    * **Multi-Format Support**: Parse PDF and DOCX resumes
    * **AI-Powered Analysis**: Use OpenAI, Anthropic, or Ollama
    * **Job Matching**: Compare resumes against job descriptions
    * **ATS Compatibility**: Check Applicant Tracking System compatibility
    * **Improvement Suggestions**: Get actionable feedback
    * **Keyword Analysis**: Identify missing keywords
    
    ## Providers
    
    * **OpenAI**: GPT-4, GPT-3.5-turbo
    * **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
    * **Ollama**: Local LLMs (Llama, Mistral, etc.)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler.
    
    WHAT IT DOES:
    - Catches all unhandled exceptions
    - Returns consistent error format
    - Logs errors for debugging
    
    WHY NEEDED:
    - Prevents server crashes
    - Provides user-friendly errors
    - Helps with debugging
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Health check routes
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

# Upload routes
app.include_router(
    upload.router,
    prefix="/api/v1",
    tags=["Upload"]
)

# Analysis routes
app.include_router(
    analyze.router,
    prefix="/api/v1",
    tags=["Analysis"]
)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information.
    
    RETURNS:
        Basic API information and links
    """
    return {
        "name": "AI Resume Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. FASTAPI BENEFITS:
   - Automatic API documentation (Swagger, ReDoc)
   - Type safety with Pydantic
   - Async support for better performance
   - Built-in validation
   - Modern Python features

2. MIDDLEWARE:
   - CORS for frontend communication
   - Could add authentication middleware
   - Could add rate limiting
   - Could add request logging

3. ERROR HANDLING:
   - Global exception handler
   - Consistent error format
   - Debug mode for development
   - Production-safe errors

4. MODULAR STRUCTURE:
   - Routes organized by feature
   - Easy to add new endpoints
   - Clear separation of concerns
   - Scalable architecture

5. DOCUMENTATION:
   - Auto-generated from code
   - Interactive testing in browser
   - Type hints become API schema
   - Examples in docstrings

COMMON INTERVIEW QUESTIONS:

Q: "Why FastAPI over Flask or Django?"
A: "FastAPI provides automatic API documentation, built-in validation
    with Pydantic, async support, and better performance. It's more
    modern and has better type safety than Flask, while being lighter
    than Django for API-only applications."

Q: "How do you handle CORS?"
A: "I use FastAPI's CORS middleware, configured with allowed origins
    from environment variables. In development, I allow localhost.
    In production, I'd restrict to the actual frontend domain."

Q: "What about authentication?"
A: "For this project, I focused on core functionality. To add auth,
    I'd use FastAPI's security utilities with JWT tokens, OAuth2,
    or API keys. Could add a middleware to check tokens on protected
    routes."

Q: "How do you handle file uploads?"
A: "FastAPI has built-in support for file uploads with UploadFile.
    I validate file type and size, save temporarily, process, then
    clean up. Could add virus scanning for production."

Q: "What about rate limiting?"
A: "Could add slowapi or custom middleware to limit requests per IP.
    Important for preventing abuse and managing costs with AI APIs.
    Would track by IP or API key."
"""

# Made with Bob
