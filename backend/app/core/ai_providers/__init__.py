"""
============================================================================
AI PROVIDERS MODULE
============================================================================
This module provides a unified interface for all AI providers.

KEY CONCEPTS TO UNDERSTAND:
1. Factory Pattern: Creates provider instances based on configuration
2. Provider Registry: Maps provider names to classes
3. Dependency Injection: Providers are created with configuration
4. Abstraction: Rest of app doesn't know which provider is used

INTERVIEW TALKING POINTS:
- "I use the Factory pattern to create providers dynamically"
- "The registry makes it easy to add new providers"
- "Configuration-driven provider selection"
- "Supports multiple providers simultaneously"

USAGE:
    from app.core.ai_providers import get_provider, list_providers
    
    # Get configured provider
    provider = get_provider("openai")
    
    # Or get default provider
    provider = get_provider()
    
    # List all available providers
    providers = list_providers()
============================================================================
"""

from typing import Dict, Type, Optional, List
import logging

from .base import BaseAIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


# ============================================================================
# PROVIDER REGISTRY
# ============================================================================

# Maps provider name to provider class
PROVIDER_REGISTRY: Dict[str, Type[BaseAIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def get_provider(
    provider_name: Optional[str] = None,
    **kwargs
) -> BaseAIProvider:
    """
    Get an AI provider instance (Factory Pattern).
    
    WHAT IT DOES:
    1. Determines which provider to use
    2. Gets configuration for that provider
    3. Creates and returns provider instance
    
    PARAMETERS:
        provider_name: Provider to use (openai, anthropic, ollama)
                      If None, uses default from config
        **kwargs: Override configuration (api_key, model, etc.)
    
    RETURNS:
        Configured provider instance
    
    RAISES:
        ValueError: If provider not found or not configured
    
    EXAMPLE:
        # Use default provider
        provider = get_provider()
        
        # Use specific provider
        provider = get_provider("anthropic")
        
        # Override configuration
        provider = get_provider("openai", model="gpt-3.5-turbo")
    
    INTERVIEW TIP:
    "The factory pattern centralizes provider creation. This makes
    it easy to add caching, connection pooling, or other cross-cutting
    concerns in one place."
    """
    from app.config import get_settings, get_ai_provider_config
    
    settings = get_settings()
    
    # Determine provider name
    if provider_name is None:
        provider_name = settings.default_ai_provider
    
    provider_name = provider_name.lower()
    
    # Check if provider exists
    if provider_name not in PROVIDER_REGISTRY:
        available = ", ".join(PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {available}"
        )
    
    # Get provider class
    provider_class = PROVIDER_REGISTRY[provider_name]
    
    # Get configuration
    config = get_ai_provider_config(provider_name)
    
    # Override with kwargs
    config.update(kwargs)
    
    # Create provider instance
    try:
        if provider_name == "openai":
            if not config.get("api_key"):
                raise ValueError("OpenAI API key not configured")
            provider = provider_class(
                api_key=config["api_key"],
                model=config.get("model", settings.openai_model),
                base_url=config.get("base_url", settings.openai_base_url)
            )
        
        elif provider_name == "anthropic":
            if not config.get("api_key"):
                raise ValueError("Anthropic API key not configured")
            provider = provider_class(
                api_key=config["api_key"],
                model=config.get("model", settings.anthropic_model)
            )
        
        elif provider_name == "ollama":
            provider = provider_class(
                base_url=config.get("base_url", settings.ollama_base_url),
                model=config.get("model", settings.ollama_model)
            )
        
        else:
            # Generic provider creation
            provider = provider_class(**config)
        
        logger.info(f"Created {provider_name} provider")
        return provider
    
    except Exception as e:
        logger.error(f"Failed to create {provider_name} provider: {e}")
        raise


def list_providers() -> List[str]:
    """
    Get list of available provider names.
    
    RETURNS:
        List of provider names
    
    EXAMPLE:
        providers = list_providers()
        # Returns: ["openai", "anthropic", "ollama"]
    
    WHY USEFUL:
    - For UI dropdown menus
    - For validation
    - For documentation
    """
    return list(PROVIDER_REGISTRY.keys())


def register_provider(
    name: str, 
    provider_class: Type[BaseAIProvider]
) -> None:
    """
    Register a new provider (for extensibility).
    
    PARAMETERS:
        name: Provider name
        provider_class: Provider class (must inherit from BaseAIProvider)
    
    EXAMPLE:
        class MyCustomProvider(BaseAIProvider):
            # Implementation...
            pass
        
        register_provider("custom", MyCustomProvider)
    
    WHY USEFUL:
    - Allows plugins/extensions
    - Can add providers at runtime
    - Doesn't require modifying core code
    
    INTERVIEW TIP:
    "This function demonstrates the Open/Closed Principle - the
    system is open for extension but closed for modification."
    """
    if not issubclass(provider_class, BaseAIProvider):
        raise ValueError(
            f"{provider_class} must inherit from BaseAIProvider"
        )
    
    PROVIDER_REGISTRY[name.lower()] = provider_class
    logger.info(f"Registered provider: {name}")


def is_provider_available(provider_name: str) -> bool:
    """
    Check if a provider is available and configured.
    
    PARAMETERS:
        provider_name: Provider to check
    
    RETURNS:
        True if provider is available and configured
    
    EXAMPLE:
        if is_provider_available("openai"):
            provider = get_provider("openai")
    
    WHY USEFUL:
    - Check before attempting to use
    - Provide better error messages
    - Enable/disable UI options
    """
    from app.config import get_settings
    
    provider_name = provider_name.lower()
    
    # Check if provider exists
    if provider_name not in PROVIDER_REGISTRY:
        return False
    
    # Check if configured
    settings = get_settings()
    
    if provider_name == "openai":
        return settings.openai_api_key is not None
    elif provider_name == "anthropic":
        return settings.anthropic_api_key is not None
    elif provider_name == "ollama":
        # Ollama doesn't need API key, just check if it's running
        try:
            provider = get_provider("ollama")
            return provider.validate_api_key()
        except:
            return False
    
    return True


def get_available_providers() -> List[str]:
    """
    Get list of providers that are actually available (configured).
    
    RETURNS:
        List of available provider names
    
    EXAMPLE:
        available = get_available_providers()
        # Returns: ["openai", "ollama"] (if only these are configured)
    
    DIFFERENCE FROM list_providers():
    - list_providers(): All registered providers
    - get_available_providers(): Only configured/available providers
    """
    return [
        name for name in list_providers()
        if is_provider_available(name)
    ]


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def analyze_resume_with_provider(
    resume_text: str,
    job_description: Optional[str] = None,
    provider_name: Optional[str] = None,
    **kwargs
):
    """
    Convenience function to analyze resume with specified provider.
    
    PARAMETERS:
        resume_text: Resume content
        job_description: Optional job description
        provider_name: Provider to use (None = default)
        **kwargs: Additional options
    
    RETURNS:
        Analysis response
    
    EXAMPLE:
        result = analyze_resume_with_provider(
            resume_text="...",
            job_description="...",
            provider_name="openai"
        )
    """
    from .base import AnalysisRequest
    
    provider = get_provider(provider_name)
    
    request = AnalysisRequest(
        resume_text=resume_text,
        job_description=job_description,
        **kwargs
    )
    
    return provider.analyze_resume(request)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Base class
    "BaseAIProvider",
    
    # Provider classes
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    
    # Factory functions
    "get_provider",
    "list_providers",
    "register_provider",
    "is_provider_available",
    "get_available_providers",
    
    # Convenience
    "analyze_resume_with_provider",
]


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. FACTORY PATTERN:
   - Centralizes object creation
   - Hides complexity from clients
   - Easy to add caching, pooling, etc.
   - Configuration-driven

2. PROVIDER REGISTRY:
   - Maps names to classes
   - Easy to add new providers
   - Runtime registration possible
   - Supports plugins

3. CONFIGURATION:
   - Providers configured via environment
   - Can override at runtime
   - Validates configuration
   - Clear error messages

4. AVAILABILITY CHECKING:
   - Check if provider is configured
   - Check if provider is reachable
   - Graceful degradation
   - Better UX

5. EXTENSIBILITY:
   - Easy to add new providers
   - No core code changes needed
   - Plugin architecture
   - Open/Closed Principle

COMMON INTERVIEW QUESTIONS:

Q: "Why use a factory pattern?"
A: "The factory pattern centralizes provider creation, making it easy
    to add cross-cutting concerns like caching, logging, or connection
    pooling. It also hides complexity from the rest of the application."

Q: "How do you handle multiple providers?"
A: "The registry pattern maps provider names to classes. Users can
    specify which provider to use, or we use the default from config.
    All providers implement the same interface, so they're interchangeable."

Q: "What if a provider isn't configured?"
A: "I check availability before creating providers and return clear
    error messages. The UI can use get_available_providers() to only
    show configured options."

Q: "How would you add a new provider?"
A: "Three steps:
    1. Create class inheriting from BaseAIProvider
    2. Implement the four required methods
    3. Add to PROVIDER_REGISTRY or use register_provider()
    That's it! The factory handles the rest."

Q: "What about provider-specific features?"
A: "The base interface covers common functionality. For provider-specific
    features, I could add optional methods or use the kwargs parameter
    to pass provider-specific options."
"""

# Made with Bob
