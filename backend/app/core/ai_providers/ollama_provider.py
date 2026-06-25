"""
============================================================================
OLLAMA PROVIDER IMPLEMENTATION
============================================================================
This module implements the Ollama adapter for local LLM resume analysis.

KEY CONCEPTS TO UNDERSTAND:
1. Local LLM: Runs on your machine, no API costs
2. Ollama: Easy way to run LLMs locally (Llama, Mistral, etc.)
3. HTTP API: Ollama provides REST API similar to OpenAI
4. Privacy: Data never leaves your machine

INTERVIEW TALKING POINTS:
- "Ollama support means users can run the app without API costs"
- "Great for privacy-sensitive use cases - data stays local"
- "Same adapter pattern makes it easy to add local LLM support"
- "Can use models like Llama 2, Mistral, CodeLlama, etc."

OLLAMA DOCUMENTATION: https://github.com/ollama/ollama
============================================================================
"""

from typing import Dict, Any, List, Optional
import json
import logging
import httpx

from .base import BaseAIProvider, AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """
    Ollama implementation for local LLM support.
    
    WHAT IS OLLAMA:
    - Runs LLMs locally on your machine
    - No API costs, no rate limits
    - Privacy-focused (data stays local)
    - Supports many models (Llama, Mistral, etc.)
    
    REQUIREMENTS:
    - Ollama installed and running
    - Model downloaded (e.g., llama2, mistral)
    
    USAGE:
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="llama2"
        )
        result = provider.analyze_resume(request)
    
    INTERVIEW TIP:
    "Adding Ollama support demonstrates understanding of different
    deployment scenarios. Some users prefer local processing for
    privacy or cost reasons. The adapter pattern makes this trivial."
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        temperature: float = 0.3,
        **kwargs
    ):
        """
        Initialize Ollama provider.
        
        PARAMETERS:
            base_url: Ollama server URL
            model: Model name (llama2, mistral, codellama, etc.)
            temperature: Creativity (0.0-1.0)
            **kwargs: Additional configuration
        
        POPULAR MODELS:
        - llama2: General purpose, good quality
        - mistral: Fast, efficient
        - codellama: Good for technical content
        - llama2:13b: Larger, better quality
        
        NO API KEY NEEDED!
        """
        super().__init__(api_key=None, **kwargs)
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        
        # HTTP client for API calls
        self.client = httpx.Client(timeout=120.0)  # Longer timeout for local LLMs
        
        logger.info(f"Initialized Ollama provider with model: {model}")
    
    def validate_api_key(self) -> bool:
        """
        Check if Ollama is running and model is available.
        
        OVERRIDE: Ollama doesn't use API keys
        Instead, check if server is reachable
        """
        try:
            response = self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check if our model is available
                if any(self.model in name for name in model_names):
                    logger.info(f"Ollama model {self.model} is available")
                    return True
                else:
                    logger.warning(f"Model {self.model} not found. Available: {model_names}")
                    return False
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def analyze_resume(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Analyze resume using local LLM.
        
        SAME INTERFACE:
        - Takes AnalysisRequest
        - Returns AnalysisResponse
        - Rest of app doesn't know it's local
        
        PERFORMANCE NOTE:
        - Local LLMs are slower than cloud APIs
        - But no cost and complete privacy
        """
        try:
            # Validate Ollama is running
            if not self.validate_api_key():
                return AnalysisResponse(
                    success=False,
                    error=f"Ollama not running or model {self.model} not available",
                    provider=self.get_provider_name(),
                    model=self.model
                )
            
            # Step 1: Extract resume data
            logger.info("Extracting resume data with Ollama...")
            resume_data = self.extract_resume_data(request.resume_text)
            
            # Step 2: Compare with job (if provided)
            comparison_data = None
            if request.job_description and request.include_keyword_analysis:
                logger.info("Comparing with job description...")
                comparison_data = self.compare_with_job(
                    request.resume_text,
                    request.job_description
                )
            
            # Step 3: Generate suggestions
            suggestions = []
            if request.include_suggestions:
                logger.info("Generating suggestions...")
                suggestions = self.generate_suggestions(
                    request.resume_text,
                    resume_data
                )
            
            # Combine all data
            analysis_data = {
                "resume_data": resume_data,
                "comparison": comparison_data,
                "suggestions": suggestions
            }
            
            return AnalysisResponse(
                success=True,
                data=analysis_data,
                provider=self.get_provider_name(),
                model=self.model,
                tokens_used=self._estimate_total_tokens(request.resume_text)
            )
        
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timeout: {e}")
            return AnalysisResponse(
                success=False,
                error="Request timeout. Local LLM might be slow or overloaded.",
                provider=self.get_provider_name(),
                model=self.model
            )
        
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to Ollama: {e}")
            return AnalysisResponse(
                success=False,
                error="Cannot connect to Ollama. Is it running?",
                provider=self.get_provider_name(),
                model=self.model
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in Ollama provider: {e}")
            return self.handle_error(e)
    
    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract structured data using local LLM.
        
        OLLAMA API:
        - POST to /api/generate
        - Send prompt and model
        - Get streaming or complete response
        """
        prompt = self._build_extraction_prompt(resume_text)
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,  # Get complete response
                    "temperature": self.temperature,
                    "format": "json"  # Request JSON format
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}
            
            # Parse response
            result = response.json()
            content = result.get("response", "")
            
            # Parse JSON from response
            try:
                data = json.loads(content)
                logger.info("Successfully extracted resume data with Ollama")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON: {e}")
                return self._extract_json_from_text(content)
        
        except Exception as e:
            logger.error(f"Error extracting resume data: {e}")
            return {"error": str(e)}
    
    def compare_with_job(
        self, 
        resume_text: str, 
        job_description: str
    ) -> Dict[str, Any]:
        """Compare resume with job description using local LLM."""
        prompt = self._build_comparison_prompt(resume_text, job_description)
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": self.temperature,
                    "format": "json"
                }
            )
            
            if response.status_code != 200:
                return {"error": f"API error: {response.status_code}"}
            
            result = response.json()
            content = result.get("response", "")
            
            try:
                data = json.loads(content)
                logger.info("Successfully compared resume with job using Ollama")
                return data
            except json.JSONDecodeError:
                return self._extract_json_from_text(content)
        
        except Exception as e:
            logger.error(f"Error comparing with job: {e}")
            return {"error": str(e)}
    
    def generate_suggestions(
        self, 
        resume_text: str,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate improvement suggestions using local LLM."""
        prompt = self._build_suggestions_prompt(resume_text, analysis_data)
        
        try:
            response = self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,  # Higher for creative suggestions
                    "format": "json"
                }
            )
            
            if response.status_code != 200:
                return []
            
            result = response.json()
            content = result.get("response", "")
            
            try:
                data = json.loads(content)
                suggestions = data.get("suggestions", [])
                logger.info(f"Generated {len(suggestions)} suggestions with Ollama")
                return suggestions
            except json.JSONDecodeError:
                data = self._extract_json_from_text(content)
                return data.get("suggestions", [])
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    # ========================================================================
    # PROMPT TEMPLATES (Same as other providers)
    # ========================================================================
    
    def _build_extraction_prompt(self, resume_text: str) -> str:
        """Build prompt for data extraction."""
        return f"""Extract structured information from this resume and return ONLY valid JSON.

RESUME TEXT:
{resume_text}

Return a JSON object with this exact structure:
{{
  "contact_info": {{"full_name": "string", "email": "string or null", "phone": "string or null", "location": "string or null", "linkedin_url": "string or null", "github_url": "string or null"}},
  "summary": "string or null",
  "work_experience": [{{"company": "string", "position": "string", "start_date": "string", "end_date": "string", "description": "string", "achievements": ["string"], "technologies": ["string"]}}],
  "education": [{{"institution": "string", "degree": "string", "field_of_study": "string or null", "end_date": "string or null"}}],
  "skills": [{{"category": "string", "skills": ["string"]}}],
  "certifications": [{{"name": "string", "issuing_organization": "string or null"}}],
  "languages": ["string"],
  "projects": [{{"name": "string", "description": "string", "technologies": ["string"]}}]
}}

Return ONLY the JSON, no other text."""
    
    def _build_comparison_prompt(
        self, 
        resume_text: str, 
        job_description: str
    ) -> str:
        """Build prompt for job comparison."""
        return f"""Compare this resume against the job description. Return ONLY valid JSON.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return a JSON object with:
{{
  "match_percentage": number,
  "overall_assessment": "string",
  "matched_skills": ["string"],
  "missing_skills": ["string"],
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommendations": ["string"]
}}

Return ONLY the JSON, no other text."""
    
    def _build_suggestions_prompt(
        self, 
        resume_text: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """Build prompt for generating suggestions."""
        return f"""Analyze this resume and provide improvement suggestions. Return ONLY valid JSON.

RESUME:
{resume_text}

Return a JSON object with:
{{
  "suggestions": [
    {{
      "category": "string",
      "priority": "string",
      "title": "string",
      "description": "string",
      "recommendation": "string"
    }}
  ]
}}

Provide 5-10 actionable suggestions. Return ONLY the JSON, no other text."""
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text (same as Anthropic provider)."""
        try:
            # Try to find JSON in markdown code block
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            
            # Try to find JSON object
            if "{" in text and "}" in text:
                start = text.find("{")
                end = text.rfind("}") + 1
                json_str = text[start:end]
                return json.loads(json_str)
            
            return {"error": "Could not extract JSON from response"}
        
        except Exception as e:
            logger.error(f"Failed to extract JSON: {e}")
            return {"error": "Failed to parse response"}
    
    def _estimate_total_tokens(self, text: str) -> int:
        """Estimate total tokens used."""
        input_tokens = self.estimate_tokens(text)
        output_tokens = input_tokens // 2
        return input_tokens + output_tokens
    
    def __del__(self):
        """Clean up HTTP client."""
        try:
            self.client.close()
        except:
            pass


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. LOCAL LLM BENEFITS:
   - No API costs
   - Complete privacy (data never leaves machine)
   - No rate limits
   - Works offline

2. OLLAMA ADVANTAGES:
   - Easy to install and use
   - Supports many models
   - Simple HTTP API
   - Good performance on modern hardware

3. TRADE-OFFS:
   - Slower than cloud APIs
   - Requires good hardware (GPU recommended)
   - Model quality varies
   - Need to download models (GBs)

4. ADAPTER PATTERN BENEFIT:
   - Same interface as cloud providers
   - Easy to switch between local/cloud
   - User can choose based on needs
   - No code changes needed

5. USE CASES:
   - Privacy-sensitive applications
   - Cost-conscious users
   - Offline scenarios
   - Development/testing

COMMON INTERVIEW QUESTIONS:

Q: "Why support local LLMs?"
A: "Different users have different needs. Some prioritize privacy,
    some want to avoid API costs, some need offline capability.
    The adapter pattern makes it easy to support all scenarios."

Q: "How does performance compare?"
A: "Local LLMs are slower (10-30s vs 5-10s for cloud APIs) but
    there's no cost and complete privacy. For many users, that's
    a worthwhile trade-off. We could add caching to improve this."

Q: "What about model quality?"
A: "Smaller local models (7B parameters) are less capable than
    GPT-4, but larger models (13B, 70B) can be competitive. Users
    can choose based on their hardware and quality needs."

Q: "How do you handle Ollama not being installed?"
A: "I check if Ollama is running and the model is available before
    processing. If not, I return a clear error message. Could add
    automatic fallback to cloud providers."

Q: "What about GPU requirements?"
A: "Ollama can run on CPU but it's slow. GPU (8GB+ VRAM) is
    recommended. Could add hardware detection and model
    recommendations based on available resources."
"""

# Made with Bob
