"""
============================================================================
AI PROVIDER BASE CLASS (ADAPTER PATTERN)
============================================================================
This module defines the base interface for AI providers.

KEY CONCEPTS TO UNDERSTAND:
1. Adapter Pattern: Provides a unified interface for different implementations
2. Abstract Base Class (ABC): Defines contract that all providers must follow
3. Polymorphism: Different providers, same interface
4. Dependency Inversion: Depend on abstraction, not concrete implementations

INTERVIEW TALKING POINTS:
- "I use the Adapter pattern to support multiple AI providers with a unified interface"
- "This makes it easy to add new providers or switch between them without changing core logic"
- "The abstract base class ensures all providers implement required methods"

DESIGN PATTERN: ADAPTER
Why: Different AI APIs have different interfaces. The adapter pattern
     provides a consistent interface regardless of the underlying provider.
============================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalysisRequest(BaseModel):
    """
    Request for resume analysis.
    
    WHAT IT CONTAINS:
    - Resume text to analyze
    - Optional job description for comparison
    - Analysis options/preferences
    
    WHY PYDANTIC:
    - Automatic validation
    - Type safety
    - Easy serialization
    """
    
    resume_text: str
    job_description: Optional[str] = None
    include_ats_check: bool = True
    include_keyword_analysis: bool = True
    include_suggestions: bool = True


class AnalysisResponse(BaseModel):
    """
    Response from AI analysis.
    
    WHAT IT CONTAINS:
    - Extracted resume data
    - Analysis results
    - Suggestions
    - Metadata
    """
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    provider: str
    model: str
    tokens_used: Optional[int] = None


# ============================================================================
# BASE AI PROVIDER (ABSTRACT CLASS)
# ============================================================================

class BaseAIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    WHAT IS AN ABSTRACT CLASS:
    - Cannot be instantiated directly
    - Defines methods that subclasses MUST implement
    - Ensures consistent interface across providers
    
    WHY USE IT:
    - Enforces contract for all providers
    - Makes code more maintainable
    - Enables polymorphism (treat all providers the same)
    
    SUBCLASSES MUST IMPLEMENT:
    - analyze_resume()
    - extract_resume_data()
    - compare_with_job()
    - generate_suggestions()
    
    USAGE:
        # Cannot do this (abstract class):
        # provider = BaseAIProvider()  # ERROR!
        
        # Must use concrete implementation:
        provider = OpenAIProvider(api_key="...")
        result = provider.analyze_resume(request)
    
    INTERVIEW TIP:
    "I use an abstract base class to define the contract that all
    AI providers must follow. This ensures consistency and makes
    it easy to add new providers."
    """
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the AI provider.
        
        PARAMETERS:
            api_key: API key for the provider (if needed)
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    def analyze_resume(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Analyze a resume and return comprehensive results.
        
        THIS IS THE MAIN METHOD:
        - Takes resume text (and optional job description)
        - Performs AI analysis
        - Returns structured results
        
        PARAMETERS:
            request: AnalysisRequest with resume text and options
        
        RETURNS:
            AnalysisResponse with analysis results
        
        MUST BE IMPLEMENTED BY SUBCLASSES.
        
        EXAMPLE IMPLEMENTATION:
            def analyze_resume(self, request):
                # 1. Call AI API
                # 2. Parse response
                # 3. Structure data
                # 4. Return AnalysisResponse
                pass
        """
        pass
    
    @abstractmethod
    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract structured data from resume text.
        
        WHAT IT EXTRACTS:
        - Contact information
        - Work experience
        - Education
        - Skills
        - Certifications
        
        PARAMETERS:
            resume_text: Raw resume text
        
        RETURNS:
            Dictionary with extracted data
        
        EXAMPLE RETURN:
            {
                "contact": {"name": "John Doe", "email": "..."},
                "experience": [...],
                "education": [...],
                "skills": [...]
            }
        """
        pass
    
    @abstractmethod
    def compare_with_job(
        self, 
        resume_text: str, 
        job_description: str
    ) -> Dict[str, Any]:
        """
        Compare resume against job description.
        
        WHAT IT DOES:
        - Identify matching skills/experience
        - Find gaps
        - Calculate match percentage
        - Suggest improvements
        
        PARAMETERS:
            resume_text: Resume content
            job_description: Job posting content
        
        RETURNS:
            Dictionary with comparison results
        
        EXAMPLE RETURN:
            {
                "match_percentage": 75,
                "matched_skills": ["Python", "React"],
                "missing_skills": ["AWS", "Docker"],
                "recommendations": [...]
            }
        """
        pass
    
    @abstractmethod
    def generate_suggestions(
        self, 
        resume_text: str,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions.
        
        WHAT IT GENERATES:
        - Content improvements
        - Formatting suggestions
        - Keyword recommendations
        - ATS optimization tips
        
        PARAMETERS:
            resume_text: Resume content
            analysis_data: Previous analysis results
        
        RETURNS:
            List of suggestions
        
        EXAMPLE RETURN:
            [
                {
                    "category": "content",
                    "priority": "high",
                    "title": "Add quantifiable achievements",
                    "description": "...",
                    "recommendation": "..."
                },
                ...
            ]
        """
        pass
    
    # ========================================================================
    # HELPER METHODS (OPTIONAL TO OVERRIDE)
    # ========================================================================
    
    def validate_api_key(self) -> bool:
        """
        Validate that API key is set and valid.
        
        WHY NEEDED:
        - Fail fast if API key is missing
        - Better error messages
        - Avoid wasted API calls
        
        RETURNS:
            True if valid, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        RETURNS:
            Provider name (e.g., "openai", "anthropic")
        
        WHY USEFUL:
        - For logging
        - For user display
        - For analytics
        """
        return self.__class__.__name__.replace("Provider", "").lower()
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        WHY IMPORTANT:
        - API costs based on tokens
        - Rate limiting
        - Context window limits
        
        ROUGH ESTIMATE:
        - 1 token ≈ 4 characters
        - 1 token ≈ 0.75 words
        
        PARAMETERS:
            text: Text to estimate
        
        RETURNS:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4
    
    def build_prompt(
        self, 
        template: str, 
        **variables
    ) -> str:
        """
        Build a prompt from template and variables.
        
        WHY USEFUL:
        - Consistent prompt formatting
        - Easy to modify prompts
        - Variable substitution
        
        PARAMETERS:
            template: Prompt template with {variables}
            **variables: Values to substitute
        
        RETURNS:
            Formatted prompt
        
        EXAMPLE:
            template = "Analyze this resume: {resume_text}"
            prompt = self.build_prompt(template, resume_text=text)
        """
        return template.format(**variables)
    
    def handle_error(self, error: Exception) -> AnalysisResponse:
        """
        Handle errors and return standardized error response.
        
        WHY NEEDED:
        - Consistent error handling
        - Better error messages
        - Easier debugging
        
        PARAMETERS:
            error: Exception that occurred
        
        RETURNS:
            AnalysisResponse with error details
        """
        return AnalysisResponse(
            success=False,
            data=None,
            error=str(error),
            provider=self.get_provider_name(),
            model="unknown"
        )


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. ADAPTER PATTERN:
   - Provides unified interface for different AI providers
   - Makes it easy to add new providers
   - Core logic doesn't need to know which provider is used
   - Follows Open/Closed Principle (open for extension, closed for modification)

2. ABSTRACT BASE CLASS:
   - Defines contract that all providers must follow
   - Cannot be instantiated directly
   - Enforces implementation of required methods
   - Provides optional helper methods

3. TYPE SAFETY:
   - Pydantic models for requests/responses
   - Type hints throughout
   - Catches errors at development time

4. EXTENSIBILITY:
   - Easy to add new providers (just implement abstract methods)
   - Easy to add new features (add methods to base class)
   - Backward compatible

5. BEST PRACTICES:
   - Separation of concerns
   - Single Responsibility Principle
   - Dependency Inversion Principle
   - Clear documentation

COMMON INTERVIEW QUESTIONS:

Q: "Why use the Adapter pattern?"
A: "Different AI providers have different APIs and response formats. 
    The Adapter pattern provides a consistent interface, so the rest 
    of the application doesn't need to know which provider is being used. 
    This makes it easy to switch providers or add new ones."

Q: "Why use an abstract base class instead of just an interface?"
A: "Python doesn't have interfaces like Java. Abstract base classes 
    serve the same purpose - they define a contract. Plus, they can 
    provide default implementations of helper methods, reducing code 
    duplication across providers."

Q: "How would you add a new AI provider?"
A: "Create a new class that inherits from BaseAIProvider, implement 
    the four required methods (analyze_resume, extract_resume_data, 
    compare_with_job, generate_suggestions), and that's it! The rest 
    of the application will work with it automatically."

Q: "What about error handling?"
A: "Each provider handles its own API-specific errors, but they all 
    return the same AnalysisResponse format. The base class provides 
    a handle_error() method for consistent error responses."

Q: "How do you handle different pricing models?"
A: "I track tokens_used in the response. Each provider can implement 
    its own token counting logic. This allows for cost tracking and 
    optimization regardless of the provider."

DESIGN PATTERNS DEMONSTRATED:
1. Adapter Pattern - Unified interface for different implementations
2. Template Method Pattern - Base class provides structure, subclasses fill in details
3. Strategy Pattern - Different providers are different strategies
4. Factory Pattern - (Will be used to create providers)
"""

# Made with Bob
