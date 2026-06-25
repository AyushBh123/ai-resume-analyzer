"""
============================================================================
HEALTH CHECK ROUTES
============================================================================
Health check and status endpoints.

WHAT THESE DO:
- Check if API is running
- Check if AI providers are available
- System status information

WHY NEEDED:
- Load balancers need health checks
- Monitoring systems need status
- Users can check availability
============================================================================
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.config import get_settings
from app.core.ai_providers import list_providers, is_provider_available

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint with provider status.
    
    RETURNS:
        Status information including AI provider availability
    
    EXAMPLE:
        GET /api/v1/health
        
        Response:
        {
            "status": "healthy",
            "version": "1.0.0",
            "providers": {
                "openai": {"available": true},
                "anthropic": {"available": false},
                "ollama": {"available": true}
            }
        }
    """
    # Check provider availability
    providers_status = {}
    for provider in list_providers():
        try:
            available = is_provider_available(provider)
            providers_status[provider] = {"available": available}
        except Exception as e:
            logger.error(f"Error checking {provider}: {e}")
            providers_status[provider] = {"available": False}
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "providers": providers_status
    }


@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with provider status.
    
    RETURNS:
        Detailed status including AI provider availability
    
    EXAMPLE:
        GET /api/v1/health/detailed
        
        Response:
        {
            "status": "healthy",
            "version": "1.0.0",
            "providers": {
                "openai": true,
                "anthropic": false,
                "ollama": true
            },
            "config": {
                "default_provider": "openai",
                "max_file_size_mb": 10
            }
        }
    """
    settings = get_settings()
    
    # Check provider availability
    providers_status = {}
    for provider in list_providers():
        try:
            providers_status[provider] = is_provider_available(provider)
        except Exception as e:
            logger.error(f"Error checking {provider}: {e}")
            providers_status[provider] = False
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "providers": providers_status,
        "config": {
            "default_provider": settings.default_ai_provider,
            "max_file_size_mb": settings.max_file_size_mb,
            "allowed_extensions": settings.allowed_extensions_list,
            "environment": settings.environment
        }
    }


@router.get("/providers")
async def list_available_providers() -> Dict[str, Any]:
    """
    List all available AI providers.
    
    RETURNS:
        List of providers and their status
    
    EXAMPLE:
        GET /api/v1/providers
        
        Response:
        {
            "providers": [
                {
                    "name": "openai",
                    "available": true,
                    "models": ["gpt-4-turbo-preview", "gpt-3.5-turbo"]
                },
                {
                    "name": "anthropic",
                    "available": false,
                    "models": ["claude-3-opus", "claude-3-sonnet"]
                }
            ],
            "default": "openai"
        }
    """
    settings = get_settings()
    
    providers_info = []
    for provider in list_providers():
        available = is_provider_available(provider)
        
        # Get available models for each provider
        models = []
        if provider == "openai":
            models = ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"]
        elif provider == "anthropic":
            models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        elif provider == "ollama":
            models = ["llama2", "mistral", "codellama", "llama2:13b"]
        
        providers_info.append({
            "name": provider,
            "available": available,
            "models": models
        })
    
    return {
        "providers": providers_info,
        "default": settings.default_ai_provider
    }

# Made with Bob
