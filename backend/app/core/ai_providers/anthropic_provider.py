"""
============================================================================
ANTHROPIC CLAUDE PROVIDER IMPLEMENTATION
============================================================================
This module implements the Anthropic Claude adapter for resume analysis.

KEY CONCEPTS TO UNDERSTAND:
1. Alternative AI Provider: Shows flexibility of adapter pattern
2. Claude API: Different from OpenAI but same interface to our app
3. Prompt Engineering: Similar but adapted for Claude's strengths
4. Tool Use: Claude's approach to structured outputs

INTERVIEW TALKING POINTS:
- "Adding Anthropic was easy thanks to the adapter pattern"
- "Claude excels at detailed analysis and following complex instructions"
- "The adapter pattern means the rest of the app doesn't know which provider is used"
- "I can easily switch providers or use multiple for different tasks"

API DOCUMENTATION: https://docs.anthropic.com/claude/reference
============================================================================
"""

from typing import Dict, Any, List, Optional
import json
import logging
from anthropic import Anthropic, APIError, RateLimitError

from .base import BaseAIProvider, AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic Claude implementation of AI provider.
    
    USES:
    - Claude 3 (Opus, Sonnet, or Haiku)
    - Messages API
    - System prompts for context
    
    CLAUDE STRENGTHS:
    - Excellent at following complex instructions
    - Strong reasoning capabilities
    - Good at structured analysis
    - Longer context window (200K tokens)
    
    USAGE:
        provider = AnthropicProvider(
            api_key="sk-ant-...",
            model="claude-3-sonnet-20240229"
        )
        result = provider.analyze_resume(request)
    
    INTERVIEW TIP:
    "Claude and GPT have different strengths. Claude is better at
    detailed analysis and following complex instructions, while GPT
    is faster and cheaper. The adapter pattern lets me use the best
    tool for each task."
    """
    
    def __init__(
        self, 
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 4096,
        temperature: float = 0.3,
        **kwargs
    ):
        """
        Initialize Anthropic provider.
        
        PARAMETERS:
            api_key: Anthropic API key
            model: Claude model (opus, sonnet, haiku)
            max_tokens: Maximum tokens in response
            temperature: Creativity (0.0-1.0)
            **kwargs: Additional configuration
        
        CLAUDE MODELS:
        - claude-3-opus: Most capable, expensive
        - claude-3-sonnet: Balanced (recommended)
        - claude-3-haiku: Fast, cheap
        
        MAX_TOKENS:
        - Claude requires explicit max_tokens
        - 4096 is good for most analyses
        - Can go up to 200K for context
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key)
        
        logger.info(f"Initialized Anthropic provider with model: {model}")
    
    def analyze_resume(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Analyze resume using Claude.
        
        SAME INTERFACE AS OPENAI:
        - Takes AnalysisRequest
        - Returns AnalysisResponse
        - Rest of app doesn't know the difference
        
        THIS IS THE POWER OF THE ADAPTER PATTERN!
        """
        try:
            # Validate API key
            if not self.validate_api_key():
                return AnalysisResponse(
                    success=False,
                    error="Anthropic API key not configured",
                    provider=self.get_provider_name(),
                    model=self.model
                )
            
            # Step 1: Extract resume data
            logger.info("Extracting resume data with Claude...")
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
            logger.error(f"Anthropic rate limit exceeded: {e}")
            return AnalysisResponse(
                success=False,
                error="Rate limit exceeded. Please try again later.",
                provider=self.get_provider_name(),
                model=self.model
            )
        
        except APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return AnalysisResponse(
                success=False,
                error=f"API error: {str(e)}",
                provider=self.get_provider_name(),
                model=self.model
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in Anthropic provider: {e}")
            return self.handle_error(e)
    
    def extract_resume_data(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract structured data using Claude.
        
        CLAUDE'S APPROACH:
        - Uses system prompt for context
        - User message contains task
        - Explicitly request JSON format
        - Parse response
        
        DIFFERENCE FROM OPENAI:
        - No native JSON mode (yet)
        - Need to explicitly request JSON
        - Usually follows instructions well
        """
        system_prompt = """You are an expert resume parser and HR analyst. 
Your task is to extract structured information from resumes accurately.
Always respond with valid JSON only, no additional text."""
        
        user_prompt = self._build_extraction_prompt(resume_text)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            # Extract text from response
            content = response.content[0].text
            
            # Parse JSON
            try:
                data = json.loads(content)
                logger.info("Successfully extracted resume data with Claude")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                # Try to extract JSON from response
                return self._extract_json_from_text(content)
        
        except Exception as e:
            logger.error(f"Error extracting resume data: {e}")
            return {"error": str(e)}
    
    def compare_with_job(
        self, 
        resume_text: str, 
        job_description: str
    ) -> Dict[str, Any]:
        """
        Compare resume with job description using Claude.
        
        CLAUDE'S STRENGTH:
        - Excellent at detailed comparison
        - Good at identifying nuances
        - Strong reasoning about fit
        """
        system_prompt = """You are an expert recruiter analyzing candidate fit 
for job positions. Provide detailed, accurate analysis in JSON format only."""
        
        user_prompt = self._build_comparison_prompt(resume_text, job_description)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            content = response.content[0].text
            
            try:
                data = json.loads(content)
                logger.info("Successfully compared resume with job using Claude")
                return data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return self._extract_json_from_text(content)
        
        except Exception as e:
            logger.error(f"Error comparing with job: {e}")
            return {"error": str(e)}
    
    def generate_suggestions(
        self, 
        resume_text: str,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate improvement suggestions using Claude.
        
        CLAUDE'S STRENGTH:
        - Thoughtful, detailed suggestions
        - Good at explaining reasoning
        - Actionable recommendations
        """
        system_prompt = """You are an expert resume coach providing actionable 
improvement suggestions. Be specific, practical, and prioritize by impact.
Respond with JSON only."""
        
        user_prompt = self._build_suggestions_prompt(resume_text, analysis_data)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,  # Higher for creative suggestions
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            content = response.content[0].text
            
            try:
                data = json.loads(content)
                suggestions = data.get("suggestions", [])
                logger.info(f"Generated {len(suggestions)} suggestions with Claude")
                return suggestions
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                data = self._extract_json_from_text(content)
                return data.get("suggestions", [])
        
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    # ========================================================================
    # PROMPT TEMPLATES (Same as OpenAI for consistency)
    # ========================================================================
    
    def _build_extraction_prompt(self, resume_text: str) -> str:
        """Build prompt for data extraction (same as OpenAI)."""
        return f"""
Extract structured information from this resume and return it as JSON.

RESUME TEXT:
{resume_text}

Extract the following information and return ONLY valid JSON (no markdown, no additional text):

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
  "summary": "string or null",
  "work_experience": [
    {{
      "company": "string",
      "position": "string",
      "start_date": "string",
      "end_date": "string",
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
      "category": "string",
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

Return ONLY the JSON object, nothing else.
"""
    
    def _build_comparison_prompt(
        self, 
        resume_text: str, 
        job_description: str
    ) -> str:
        """Build prompt for job comparison (same as OpenAI)."""
        return f"""
Compare this resume against the job description and analyze the fit.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Analyze and return ONLY valid JSON (no markdown, no additional text):

{{
  "match_percentage": number,
  "overall_assessment": "string",
  "matched_skills": ["string"],
  "missing_skills": ["string"],
  "matched_experience": ["string"],
  "experience_gaps": ["string"],
  "education_match": "string",
  "keyword_analysis": {{
    "matched_keywords": ["string"],
    "missing_keywords": ["string"],
    "keyword_match_percentage": number
  }},
  "strengths": ["string"],
  "weaknesses": ["string"],
  "recommendations": ["string"]
}}

Return ONLY the JSON object, nothing else.
"""
    
    def _build_suggestions_prompt(
        self, 
        resume_text: str,
        analysis_data: Dict[str, Any]
    ) -> str:
        """Build prompt for generating suggestions (same as OpenAI)."""
        return f"""
Analyze this resume and provide actionable improvement suggestions.

RESUME:
{resume_text}

ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}

Generate improvement suggestions and return ONLY valid JSON (no markdown, no additional text):

{{
  "suggestions": [
    {{
      "category": "string",
      "priority": "string",
      "title": "string",
      "description": "string",
      "recommendation": "string",
      "impact": "string",
      "examples": ["string"]
    }}
  ]
}}

Provide 5-10 most impactful suggestions, prioritized by importance.
Return ONLY the JSON object, nothing else.
"""
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from text that might contain markdown or other content.
        
        WHY NEEDED:
        - Claude sometimes wraps JSON in markdown code blocks
        - Need to extract just the JSON part
        - Fallback for when JSON parsing fails
        """
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
        """Estimate total tokens used (same as OpenAI)."""
        input_tokens = self.estimate_tokens(text)
        output_tokens = input_tokens // 2
        return input_tokens + output_tokens


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. ADAPTER PATTERN IN ACTION:
   - Same interface as OpenAI provider
   - Different implementation details
   - Rest of app doesn't know the difference
   - Easy to add new providers

2. CLAUDE VS GPT:
   - Claude: Better at detailed analysis, longer context
   - GPT: Faster, cheaper, JSON mode
   - Can use both for different tasks
   - Adapter pattern makes this easy

3. API DIFFERENCES:
   - Claude uses system + messages
   - OpenAI uses messages with roles
   - Claude needs explicit max_tokens
   - Different error types

4. JSON HANDLING:
   - Claude doesn't have JSON mode (yet)
   - Need to explicitly request JSON
   - Sometimes wraps in markdown
   - Added fallback extraction

5. FLEXIBILITY:
   - Can switch providers easily
   - Can use multiple providers
   - Can A/B test providers
   - Can optimize costs

COMMON INTERVIEW QUESTIONS:

Q: "How easy was it to add Anthropic after OpenAI?"
A: "Very easy! The adapter pattern meant I just needed to implement
    the four abstract methods. The prompts are similar, just adapted
    for Claude's API format. Took maybe 2-3 hours including testing."

Q: "Why support multiple providers?"
A: "Several reasons:
    - Redundancy (if one is down)
    - Cost optimization (use cheaper for simple tasks)
    - Feature differences (Claude's longer context)
    - Avoid vendor lock-in
    - A/B testing for quality"

Q: "How do you decide which provider to use?"
A: "Could be:
    - User preference (settings)
    - Task type (Claude for analysis, GPT for speed)
    - Cost constraints (Haiku for simple tasks)
    - Availability (fallback if one fails)
    - A/B testing (compare results)"

Q: "What about consistency between providers?"
A: "I use the same prompts and output format for both. The adapter
    pattern ensures consistent interface. Results might vary slightly,
    but structure is the same. Could add validation layer to ensure
    consistency."

Q: "How would you add a third provider?"
A: "Just create a new class inheriting from BaseAIProvider, implement
    the four methods, and it works! Could add Cohere, Gemini, or even
    local models like Llama. The pattern scales well."
"""

# Made with Bob
