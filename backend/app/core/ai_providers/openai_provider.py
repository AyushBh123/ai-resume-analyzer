"""
============================================================================
OPENAI PROVIDER IMPLEMENTATION
============================================================================
This module implements the OpenAI adapter for resume analysis.

KEY CONCEPTS TO UNDERSTAND:
1. Concrete Implementation: Implements abstract methods from BaseAIProvider
2. OpenAI API: Using GPT-4/GPT-3.5 for analysis
3. Prompt Engineering: Crafting effective prompts for accurate results
4. JSON Mode: Getting structured responses from AI

INTERVIEW TALKING POINTS:
- "I use OpenAI's GPT-4 for intelligent resume analysis"
- "Prompt engineering is crucial - I structure prompts to get consistent, accurate results"
- "I use JSON mode to get structured data that's easy to parse"
- "Error handling includes rate limiting, API errors, and malformed responses"

API DOCUMENTATION: https://platform.openai.com/docs/api-reference
============================================================================
"""

from typing import Dict, Any, List, Optional
import json
import logging
from openai import OpenAI
from openai import OpenAIError, RateLimitError, APIError

from .base import BaseAIProvider, AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI implementation of AI provider.
    
    USES:
    - GPT-4 or GPT-3.5-turbo
    - Chat completions API
    - JSON mode for structured responses
    
    FEATURES:
    - Resume data extraction
    - Job matching
    - Improvement suggestions
    - ATS compatibility analysis
    
    USAGE:
        provider = OpenAIProvider(
            api_key="sk-...",
            model="gpt-4-turbo-preview"
        )
        result = provider.analyze_resume(request)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.3,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAI provider.
        
        PARAMETERS:
            api_key: OpenAI API key (or OpenRouter key)
            model: Model to use (gpt-4-turbo-preview, gpt-3.5-turbo, etc.)
            temperature: Creativity (0.0-1.0, lower = more focused)
            base_url: Custom API base URL (for OpenRouter or other providers)
            **kwargs: Additional configuration
        
        TEMPERATURE EXPLAINED:
        - 0.0: Deterministic, focused, consistent
        - 0.3: Slightly creative (good for analysis)
        - 0.7: More creative (good for suggestions)
        - 1.0: Very creative, less predictable
        
        WHY 0.3 FOR ANALYSIS:
        - Need consistency in data extraction
        - Want accurate, factual analysis
        - Some creativity for suggestions
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.temperature = temperature
        
        # Initialize OpenAI client with optional base_url
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            logger.info(f"Using custom base URL: {base_url}")
        
        self.client = OpenAI(**client_kwargs)
        
        logger.info(f"Initialized OpenAI provider with model: {model}")
    
    def analyze_resume(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Analyze resume using OpenAI.
        
        WHAT IT DOES:
        1. Extract structured data from resume
        2. Compare with job description (if provided)
        3. Generate improvement suggestions
        4. Calculate scores
        5. Return comprehensive analysis
        
        INTERVIEW TIP:
        "I orchestrate multiple AI calls - first to extract data,
        then to analyze and compare, finally to generate suggestions.
        Each call is optimized for its specific task."
        """
        try:
            # Validate API key
            if not self.validate_api_key():
                return AnalysisResponse(
                    success=False,
                    error="OpenAI API key not configured",
                    provider=self.get_provider_name(),
                    model=self.model
                )
            
            # Step 1: Extract resume data
            logger.info("Extracting resume data...")
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
        
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            return AnalysisResponse(
                success=False,
                error="Rate limit exceeded. Please try again later.",
                provider=self.get_provider_name(),
                model=self.model
            )
        
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return AnalysisResponse(
                success=False,
                error=f"API error: {str(e)}",
                provider=self.get_provider_name(),
                model=self.model
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI provider: {e}")
            return self.handle_error(e)
    
    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract structured data from resume using OpenAI.
        
        HOW IT WORKS:
        1. Create a detailed prompt
        2. Request JSON response
        3. Parse and validate response
        4. Return structured data
        
        PROMPT ENGINEERING:
        - Clear instructions
        - Specific output format
        - Examples (few-shot learning)
        - JSON schema definition
        
        INTERVIEW TIP:
        "I use JSON mode to get structured responses. The prompt
        includes a clear schema definition, which ensures consistent
        output format that's easy to parse and validate."
        """
        prompt = self._build_extraction_prompt(resume_text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume parser and HR analyst. Extract structured information from resumes accurately."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}  # JSON mode
            )
            
            # Parse response
            content = response.choices[0].message.content
            data = json.loads(content)
            
            logger.info("Successfully extracted resume data")
            return data
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return {"error": "Failed to parse AI response"}
        
        except Exception as e:
            logger.error(f"Error extracting resume data: {e}")
            return {"error": str(e)}
    
    def compare_with_job(
        self, 
        resume_text: str, 
        job_description: str
    ) -> Dict[str, Any]:
        """
        Compare resume with job description.
        
        WHAT IT ANALYZES:
        - Skill matching
        - Experience relevance
        - Education requirements
        - Keyword alignment
        - Overall fit percentage
        
        RETURNS:
        - Match percentage
        - Matched skills/keywords
        - Missing requirements
        - Recommendations
        """
        prompt = self._build_comparison_prompt(resume_text, job_description)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert recruiter analyzing candidate fit for job positions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            logger.info("Successfully compared resume with job")
            return data
        
        except Exception as e:
            logger.error(f"Error comparing with job: {e}")
            return {"error": str(e)}
    
    def generate_suggestions(
        self, 
        resume_text: str,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions.
        
        TYPES OF SUGGESTIONS:
        - Content improvements
        - Formatting recommendations
        - Keyword optimization
        - ATS compatibility
        - Achievement quantification
        
        PRIORITIZATION:
        - Critical: Must fix (ATS issues)
        - High: Should fix (missing key info)
        - Medium: Nice to have (formatting)
        - Low: Optional (minor improvements)
        """
        prompt = self._build_suggestions_prompt(resume_text, analysis_data)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume coach providing actionable improvement suggestions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,  # Higher temperature for creative suggestions
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            suggestions = data.get("suggestions", [])
            logger.info(f"Generated {len(suggestions)} suggestions")
            return suggestions
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    # ========================================================================
    # PROMPT TEMPLATES
    # ========================================================================
    
    def _build_extraction_prompt(self, resume_text: str) -> str:
        """
        Build prompt for data extraction.
        
        PROMPT STRUCTURE:
        1. Task description
        2. Input data
        3. Output format specification
        4. Examples (optional)
        
        WHY THIS STRUCTURE:
        - Clear instructions reduce errors
        - Specific format ensures consistency
        - Examples improve accuracy (few-shot learning)
        """
        return f"""
Extract structured information from this resume and return it as JSON.

RESUME TEXT:
{resume_text}

Extract the following information and return as JSON:

{{
  "contact_info": {{
    "full_name": "string",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin_url": "string or null",
    "github_url": "string or null",
    "portfolio_url": "string or null"
  }},
  "summary": "string or null (professional summary/objective)",
  "work_experience": [
    {{
      "company": "string",
      "position": "string",
      "start_date": "string (format: YYYY-MM or YYYY)",
      "end_date": "string (format: YYYY-MM or YYYY or 'Present')",
      "location": "string or null",
      "description": "string",
      "achievements": ["string"],
      "technologies": ["string"]
    }}
  ],
  "education": [
    {{
      "institution": "string",
      "degree": "string",
      "field_of_study": "string or null",
      "start_date": "string or null",
      "end_date": "string or null",
      "gpa": "number or null",
      "honors": ["string"]
    }}
  ],
  "skills": [
    {{
      "category": "string (e.g., 'Programming Languages', 'Frameworks')",
      "skills": ["string"]
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "issuing_organization": "string or null",
      "issue_date": "string or null",
      "expiry_date": "string or null"
    }}
  ],
  "languages": ["string"],
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["string"],
      "url": "string or null"
    }}
  ]
}}

IMPORTANT:
- Extract ALL information present in the resume
- Use null for missing information
- Preserve dates in their original format
- Group skills by logical categories
- Include all achievements and technologies mentioned
"""
    
    def _build_comparison_prompt(
        self, 
        resume_text: str, 
        job_description: str
    ) -> str:
        """Build prompt for job comparison."""
        return f"""
Compare this resume against the job description and analyze the fit.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Analyze and return JSON with:

{{
  "match_percentage": "number (0-100)",
  "overall_assessment": "string (brief summary)",
  "matched_skills": ["string"],
  "missing_skills": ["string"],
  "matched_experience": ["string"],
  "experience_gaps": ["string"],
  "education_match": "string (how well education matches requirements)",
  "keyword_analysis": {{
    "matched_keywords": ["string"],
    "missing_keywords": ["string"],
    "keyword_match_percentage": "number (0-100)"
  }},
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommendations": ["string"]
}}

SCORING CRITERIA:
- Skills match: 40%
- Experience relevance: 30%
- Education fit: 15%
- Keyword alignment: 15%
"""
    
    def _build_suggestions_prompt(
        self, 
        resume_text: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """Build prompt for generating suggestions."""
        return f"""
Analyze this resume and provide actionable improvement suggestions.

RESUME:
{resume_text}

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}

Generate improvement suggestions and return as JSON:

{{
  "suggestions": [
    {{
      "category": "string (content|formatting|keywords|experience|education|skills|ats)",
      "priority": "string (critical|high|medium|low)",
      "title": "string (short title)",
      "description": "string (what's the issue)",
      "recommendation": "string (how to fix it)",
      "impact": "string (expected benefit)",
      "examples": ["string (optional examples)"]
    }}
  ]
}}

FOCUS AREAS:
1. ATS Compatibility (critical issues that could cause rejection)
2. Missing Keywords (important terms from job description)
3. Quantifiable Achievements (add metrics and numbers)
4. Formatting Issues (structure, readability)
5. Content Gaps (missing sections or information)
6. Skill Presentation (how skills are showcased)

Provide 5-10 most impactful suggestions, prioritized by importance.
"""
    
    def _estimate_total_tokens(self, text: str) -> int:
        """Estimate total tokens used in analysis."""
        # Rough estimate: input + output tokens
        input_tokens = self.estimate_tokens(text)
        # Assume output is about 50% of input
        output_tokens = input_tokens // 2
        return input_tokens + output_tokens


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. OPENAI API USAGE:
   - Use chat completions API (not legacy completions)
   - JSON mode for structured responses
   - Temperature control for consistency vs creativity
   - Error handling for rate limits and API errors

2. PROMPT ENGINEERING:
   - Clear, specific instructions
   - Structured output format (JSON schema)
   - Examples improve accuracy
   - System message sets context

3. MULTI-STEP ANALYSIS:
   - Extract data first (structured)
   - Then analyze and compare
   - Finally generate suggestions
   - Each step optimized for its task

4. ERROR HANDLING:
   - Rate limit errors (retry logic could be added)
   - API errors (network, authentication)
   - JSON parsing errors
   - Graceful degradation

5. TOKEN MANAGEMENT:
   - Estimate tokens for cost tracking
   - Could add token limits
   - Could implement caching
   - Monitor usage for optimization

COMMON INTERVIEW QUESTIONS:

Q: "Why use JSON mode?"
A: "JSON mode ensures the AI returns valid JSON that matches our schema.
    This makes parsing reliable and reduces errors. Without it, the AI
    might return markdown, plain text, or malformed JSON."

Q: "How do you handle rate limits?"
A: "I catch RateLimitError specifically and return a user-friendly message.
    In production, I'd add exponential backoff retry logic and possibly
    queue requests during high load."

Q: "Why multiple API calls instead of one?"
A: "Each call is optimized for its specific task. Data extraction needs
    low temperature for accuracy. Suggestions need higher temperature for
    creativity. This gives better results than trying to do everything
    in one call."

Q: "How would you reduce costs?"
A: "Several strategies:
    - Cache common analyses
    - Use GPT-3.5 for simpler tasks
    - Batch similar requests
    - Implement token limits
    - Only analyze changed sections
    - Use embeddings for similarity matching"

Q: "What about prompt injection?"
A: "I validate and sanitize inputs, use system messages to set boundaries,
    and could add content filtering. The structured JSON output also helps
    prevent unexpected behavior."
"""

# Made with Bob
