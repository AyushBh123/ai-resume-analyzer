"""
============================================================================
CONFIGURATION MODULE
============================================================================
This module handles all application configuration using environment variables.

KEY CONCEPTS TO UNDERSTAND:
1. Environment Variables: Values stored outside code (in .env file)
2. Pydantic Settings: Type-safe configuration with validation
3. Singleton Pattern: One config instance for entire app
4. Security: Keeps secrets out of code

INTERVIEW TALKING POINTS:
- "I use Pydantic Settings for type-safe configuration"
- "Environment variables keep secrets secure and allow different configs per environment"
- "The Config class validates all settings on startup, catching errors early"
============================================================================
"""

from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    HOW IT WORKS:
    1. Pydantic reads from .env file automatically
    2. Type hints ensure correct data types
    3. Field() provides defaults and validation
    4. Validators can add custom logic
    
    EXAMPLE USAGE:
        from app.config import get_settings
        settings = get_settings()
        api_key = settings.openai_api_key
    """
    
    # ========================================================================
    # SERVER CONFIGURATION
    # ========================================================================
    
    backend_port: int = Field(
        default=8000,
        description="Port for backend server"
    )
    
    frontend_port: int = Field(
        default=3000,
        description="Port for frontend server"
    )
    
    environment: str = Field(
        default="development",
        description="Environment: development, staging, or production"
    )
    
    debug: bool = Field(
        default=True,
        description="Enable debug mode (detailed errors)"
    )
    
    # ========================================================================
    # AI PROVIDER API KEYS
    # ========================================================================
    # These are Optional because user might only have one provider
    
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for GPT models"
    )
    
    openai_base_url: Optional[str] = Field(
        default=None,
        description="OpenAI API base URL (for OpenRouter or custom endpoints)"
    )
    
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for Claude models"
    )
    
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama API (local LLM)"
    )
    
    # ========================================================================
    # DEFAULT AI PROVIDER
    # ========================================================================
    
    default_ai_provider: str = Field(
        default="openai",
        description="Default AI provider: openai, anthropic, or ollama"
    )
    
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="Default OpenAI model"
    )
    
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Default Anthropic model"
    )
    
    ollama_model: str = Field(
        default="llama2",
        description="Default Ollama model"
    )
    
    # ========================================================================
    # FILE UPLOAD SETTINGS
    # ========================================================================
    
    max_file_size_mb: int = Field(
        default=10,
        description="Maximum file size in megabytes"
    )
    
    allowed_extensions: str = Field(
        default="pdf,docx",
        description="Comma-separated list of allowed file extensions"
    )
    
    upload_dir: str = Field(
        default="./uploads",
        description="Directory for temporary file storage"
    )
    
    # ========================================================================
    # ANALYSIS SETTINGS
    # ========================================================================
    
    enable_ats_check: bool = Field(
        default=True,
        description="Enable ATS compatibility checking"
    )
    
    enable_skill_matching: bool = Field(
        default=True,
        description="Enable skill matching against job descriptions"
    )
    
    enable_experience_analysis: bool = Field(
        default=True,
        description="Enable experience level assessment"
    )
    
    enable_education_analysis: bool = Field(
        default=True,
        description="Enable education verification"
    )
    
    min_passing_score: int = Field(
        default=60,
        description="Minimum passing score (0-100)"
    )
    
    # ========================================================================
    # CORS SETTINGS
    # ========================================================================
    
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # ========================================================================
    # LOGGING
    # ========================================================================
    
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    log_file: Optional[str] = Field(
        default=None,
        description="Log file path (None = console only)"
    )
    
    # ========================================================================
    # VALIDATORS
    # ========================================================================
    # Custom validation logic for settings
    
    @validator("default_ai_provider")
    def validate_provider(cls, v):
        """
        Ensure default_ai_provider is valid.
        
        WHAT THIS DOES:
        - Checks if provider is one of the allowed values
        - Raises error if invalid
        - Runs automatically when Settings is created
        """
        allowed = ["openai", "anthropic", "ollama"]
        if v not in allowed:
            raise ValueError(f"default_ai_provider must be one of {allowed}")
        return v
    
    @validator("min_passing_score")
    def validate_score(cls, v):
        """
        Ensure min_passing_score is between 0 and 100.
        """
        if not 0 <= v <= 100:
            raise ValueError("min_passing_score must be between 0 and 100")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """
        Ensure log_level is valid.
        """
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v
    
    # ========================================================================
    # COMPUTED PROPERTIES
    # ========================================================================
    # Properties derived from settings
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """
        Convert comma-separated extensions to list.
        
        EXAMPLE:
            "pdf,docx" -> ["pdf", "docx"]
        """
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """
        Convert comma-separated origins to list.
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """
        Convert MB to bytes for file size checking.
        
        WHY: File sizes in Python are in bytes, but MB is more user-friendly
        """
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def upload_path(self) -> Path:
        """
        Get upload directory as Path object.
        
        WHY: Path objects are better than strings for file operations
        """
        return Path(self.upload_dir)
    
    def ensure_upload_dir(self):
        """
        Create upload directory if it doesn't exist.
        
        WHEN TO CALL: On application startup
        """
        self.upload_path.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # PYDANTIC CONFIGURATION
    # ========================================================================
    
    class Config:
        """
        Pydantic configuration.
        
        KEY SETTINGS:
        - env_file: Load from .env file
        - case_sensitive: Environment variables are case-insensitive
        - env_file_encoding: UTF-8 encoding for .env file
        """
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


# ============================================================================
# SINGLETON PATTERN
# ============================================================================
# Create one instance and reuse it everywhere
# WHY: Avoid reading .env file multiple times, ensure consistency

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton).
    
    HOW IT WORKS:
    1. First call: Creates Settings instance, reads .env
    2. Subsequent calls: Returns cached instance
    
    USAGE:
        from app.config import get_settings
        settings = get_settings()
        print(settings.openai_api_key)
    
    INTERVIEW TIP:
    "I use a singleton pattern for configuration to avoid reading 
    the .env file multiple times and ensure all parts of the app 
    use the same settings."
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        # Create upload directory on first access
        _settings.ensure_upload_dir()
    return _settings


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def get_ai_provider_config(provider: str) -> dict:
    """
    Get configuration for specific AI provider.
    
    PARAMETERS:
        provider: "openai", "anthropic", or "ollama"
    
    RETURNS:
        Dictionary with provider-specific config
    
    EXAMPLE:
        config = get_ai_provider_config("openai")
        # Returns: {"api_key": "sk-...", "model": "gpt-4-turbo-preview"}
    """
    settings = get_settings()
    
    if provider == "openai":
        return {
            "api_key": settings.openai_api_key,
            "model": settings.openai_model,
            "base_url": settings.openai_base_url
        }
    elif provider == "anthropic":
        return {
            "api_key": settings.anthropic_api_key,
            "model": settings.anthropic_model
        }
    elif provider == "ollama":
        return {
            "base_url": settings.ollama_base_url,
            "model": settings.ollama_model
        }
    else:
        raise ValueError(f"Unknown provider: {provider}")


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. SECURITY:
   - API keys stored in .env, never in code
   - .env is in .gitignore, never committed
   - Different .env files for dev/staging/production

2. TYPE SAFETY:
   - Pydantic validates types automatically
   - Catches configuration errors on startup
   - Better IDE autocomplete

3. FLEXIBILITY:
   - Easy to add new settings
   - Can override with environment variables
   - Different configs per environment

4. BEST PRACTICES:
   - Singleton pattern for efficiency
   - Validators for custom logic
   - Computed properties for derived values
   - Clear documentation

5. TESTING:
   - Can mock settings in tests
   - Can create test-specific settings
   - Validates configuration before running

COMMON INTERVIEW QUESTIONS:

Q: "Why use environment variables?"
A: "Security (keep secrets out of code), flexibility (different configs 
    per environment), and following 12-factor app principles."

Q: "Why Pydantic Settings?"
A: "Type safety, automatic validation, great IDE support, and it's 
    the recommended way for FastAPI applications."

Q: "How do you handle different environments?"
A: "Different .env files (.env.development, .env.production) or 
    environment-specific variables in deployment platforms."
"""

# Made with Bob
