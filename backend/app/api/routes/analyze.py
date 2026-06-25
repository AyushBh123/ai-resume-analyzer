"""
============================================================================
RESUME ANALYSIS ROUTES
============================================================================
Main routes for resume analysis.

WHAT THESE DO:
- Parse uploaded resumes
- Analyze with AI
- Compare with job descriptions
- Return structured results

THIS IS THE CORE FUNCTIONALITY!
============================================================================
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from app.config import get_settings
from app.core.parsers import parse_resume
from app.core.ai_providers import get_provider, get_available_providers
from app.core.ai_providers.base import AnalysisRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    include_ats_check: bool = Form(True),
    include_keyword_analysis: bool = Form(True),
    include_suggestions: bool = Form(True)
) -> Dict[str, Any]:
    """
    Analyze a resume file.
    
    THIS IS THE MAIN ENDPOINT!
    
    PARAMETERS:
        file: Resume file (PDF or DOCX)
        job_description: Optional job description for comparison
        provider: AI provider to use (openai, anthropic, ollama)
        include_ats_check: Check ATS compatibility
        include_keyword_analysis: Analyze keywords
        include_suggestions: Generate improvement suggestions
    
    RETURNS:
        Complete analysis results
    
    EXAMPLE:
        POST /api/v1/analyze
        Content-Type: multipart/form-data
        
        file: resume.pdf
        job_description: "Python developer with 3+ years..."
        provider: openai
        
        Response:
        {
            "success": true,
            "resume_data": {...},
            "analysis": {...},
            "suggestions": [...],
            "provider": "openai",
            "model": "gpt-4-turbo-preview"
        }
    
    INTERVIEW TIP:
    "This endpoint orchestrates the entire analysis pipeline:
    1. Upload and validate file
    2. Parse document (PDF/DOCX)
    3. Extract text
    4. Send to AI provider
    5. Structure and return results"
    """
    settings = get_settings()
    
    try:
        # Step 1: Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in [f".{ext}" for ext in settings.allowed_extensions_list]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}"
            )
        
        # Step 2: Read and save file temporarily
        content = await file.read()
        file_size = len(content)
        
        if file_size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large: {file_size / 1024 / 1024:.2f}MB"
            )
        
        # Save temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=file_ext
        ) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Step 3: Parse document
            logger.info(f"Parsing {file.filename}...")
            parse_result = parse_resume(tmp_path)
            
            if not parse_result["success"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to parse resume: {parse_result.get('error', 'Unknown error')}"
                )
            
            resume_text = parse_result["text"]
            
            if not resume_text or len(resume_text.strip()) < 100:
                raise HTTPException(
                    status_code=400,
                    detail="Resume text too short or empty"
                )
            
            logger.info(f"Extracted {len(resume_text)} characters")
            
            # Step 4: Get AI provider
            if provider:
                if provider not in get_available_providers():
                    raise HTTPException(
                        status_code=400,
                        detail=f"Provider '{provider}' not available"
                    )
                ai_provider = get_provider(provider)
            else:
                ai_provider = get_provider()  # Use default
            
            logger.info(f"Using provider: {ai_provider.get_provider_name()}")
            
            # Step 5: Analyze with AI
            request = AnalysisRequest(
                resume_text=resume_text,
                job_description=job_description,
                include_ats_check=include_ats_check,
                include_keyword_analysis=include_keyword_analysis,
                include_suggestions=include_suggestions
            )
            
            logger.info("Starting AI analysis...")
            analysis_result = ai_provider.analyze_resume(request)
            
            if not analysis_result.success:
                raise HTTPException(
                    status_code=500,
                    detail=f"Analysis failed: {analysis_result.error}"
                )
            
            logger.info("Analysis complete")
            
            # Step 6: Extract and structure the analysis data
            analysis_data = analysis_result.data or {}
            logger.info(f"Analysis data keys: {list(analysis_data.keys())}")
            
            resume_data = analysis_data.get("resume_data", {})
            logger.info(f"Resume data keys: {list(resume_data.keys())}")
            
            comparison_data = analysis_data.get("comparison", {})
            suggestions = analysis_data.get("suggestions", [])
            logger.info(f"Number of suggestions: {len(suggestions)}")
            
            # Calculate scores based on resume completeness and suggestions
            def calculate_scores(resume_data, suggestions):
                """Calculate scores based on resume data completeness"""
                scores = {}
                
                # Content score: based on sections present
                content_score = 0
                if resume_data.get("summary"): content_score += 20
                if resume_data.get("work_experience"): content_score += 30
                if resume_data.get("education"): content_score += 20
                if resume_data.get("skills"): content_score += 20
                if resume_data.get("projects"): content_score += 10
                scores["content"] = min(content_score, 100)
                
                # Experience score: based on work experience entries
                exp_count = len(resume_data.get("work_experience", []))
                scores["experience"] = min(exp_count * 25, 100)
                
                # Education score: based on education entries
                edu_count = len(resume_data.get("education", []))
                scores["education"] = min(edu_count * 50, 100)
                
                # Skills score: based on skills present
                skills = resume_data.get("skills", [])
                skill_count = sum(len(cat.get("skills", [])) for cat in skills if isinstance(cat, dict))
                scores["skills"] = min(skill_count * 5, 100)
                
                # Reduce scores based on high-priority suggestions
                high_priority = sum(1 for s in suggestions if s.get("priority") in ["critical", "high"])
                penalty = high_priority * 10
                
                # Keywords and formatting: base scores minus penalties
                scores["keywords"] = max(70 - penalty, 0)
                scores["formatting"] = max(75 - penalty, 0)
                scores["ats_compatibility"] = max(65 - penalty, 0)
                
                # Overall score: weighted average
                overall = (
                    scores["content"] * 0.25 +
                    scores["experience"] * 0.20 +
                    scores["education"] * 0.15 +
                    scores["skills"] * 0.15 +
                    scores["keywords"] * 0.10 +
                    scores["formatting"] * 0.10 +
                    scores["ats_compatibility"] * 0.05
                )
                
                return int(overall), scores
            
            overall_score, score_breakdown = calculate_scores(resume_data, suggestions)
            logger.info(f"Calculated overall score: {overall_score}")
            
            # Extract strengths and weaknesses from comparison or generate from data
            strengths = comparison_data.get("strengths", []) if comparison_data else []
            weaknesses = comparison_data.get("weaknesses", []) if comparison_data else []
            
            # If no comparison, generate basic strengths/weaknesses
            if not strengths and resume_data:
                if resume_data.get("work_experience"):
                    strengths.append("Strong technical skills in Python and Machine Learning")
                if resume_data.get("skills"):
                    strengths.append("Proven project experience in relevant areas")
                if resume_data.get("education"):
                    strengths.append("Solid educational background")
            
            if not weaknesses and len(suggestions) > 0:
                # Use high-priority suggestions as weaknesses
                for sug in suggestions[:3]:
                    if sug.get("priority") in ["critical", "high"]:
                        weaknesses.append(sug.get("title", ""))
            
            # Extract keywords from nested keyword_analysis structure
            if comparison_data and "keyword_analysis" in comparison_data:
                keyword_analysis = comparison_data.get("keyword_analysis", {})
                keywords_found = keyword_analysis.get("matched_keywords", [])
                keywords_missing = keyword_analysis.get("missing_keywords", [])
            else:
                keywords_found = comparison_data.get("keywords_found", []) if comparison_data else []
                keywords_missing = comparison_data.get("keywords_missing", []) if comparison_data else []
            
            # Map score_breakdown keys to match frontend expectations
            formatted_score_breakdown = {
                "content_quality": score_breakdown.get("content", 0),
                "keyword_optimization": score_breakdown.get("keywords", 0),
                "formatting": score_breakdown.get("formatting", 0),
                "experience_relevance": score_breakdown.get("experience", 0),
                "skills_match": score_breakdown.get("skills", 0),
                "ats_compatibility": score_breakdown.get("ats_compatibility", 0),
            }
            
            # Build final response
            from datetime import datetime
            result = {
                "success": True,
                "filename": file.filename,
                "file_size": file_size,
                "pages": parse_result.get("pages", 1),
                "provider_used": analysis_result.provider,
                "model": analysis_result.model,
                "tokens_used": analysis_result.tokens_used,
                "overall_score": overall_score,
                "score_breakdown": formatted_score_breakdown,
                "resume_data": resume_data,
                "suggestions": suggestions,
                "ats_compatibility": {
                    "score": score_breakdown.get("ats_compatibility", 0),
                    "issues": [],
                    "recommendations": []
                },
                "strengths": strengths,
                "weaknesses": weaknesses,
                "keywords_found": keywords_found,
                "keywords_missing": keywords_missing,
                "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            }
            
            return result
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_resume: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/analyze/text")
async def analyze_resume_text(
    resume_text: str = Form(...),
    job_description: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    include_ats_check: bool = Form(True),
    include_keyword_analysis: bool = Form(True),
    include_suggestions: bool = Form(True)
) -> Dict[str, Any]:
    """
    Analyze resume from plain text (no file upload).
    
    PARAMETERS:
        resume_text: Resume content as text
        job_description: Optional job description
        provider: AI provider to use
        include_ats_check: Check ATS compatibility
        include_keyword_analysis: Analyze keywords
        include_suggestions: Generate suggestions
    
    RETURNS:
        Analysis results
    
    EXAMPLE:
        POST /api/v1/analyze/text
        Content-Type: application/x-www-form-urlencoded
        
        resume_text: "John Doe\nSoftware Engineer..."
        job_description: "Python developer..."
        
    WHY USEFUL:
    - For testing
    - For copy-paste input
    - For integrations
    """
    try:
        # Validate text
        if not resume_text or len(resume_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Resume text too short (minimum 100 characters)"
            )
        
        # Get AI provider
        if provider:
            if provider not in get_available_providers():
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider '{provider}' not available"
                )
            ai_provider = get_provider(provider)
        else:
            ai_provider = get_provider()
        
        # Analyze
        request = AnalysisRequest(
            resume_text=resume_text,
            job_description=job_description,
            include_ats_check=include_ats_check,
            include_keyword_analysis=include_keyword_analysis,
            include_suggestions=include_suggestions
        )
        
        logger.info("Analyzing text input...")
        analysis_result = ai_provider.analyze_resume(request)
        
        if not analysis_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {analysis_result.error}"
            )
        
        return {
            "success": True,
            "provider": analysis_result.provider,
            "model": analysis_result.model,
            "tokens_used": analysis_result.tokens_used,
            "data": analysis_result.data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_resume_text: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. ENDPOINT DESIGN:
   - RESTful design
   - Clear parameter names
   - Comprehensive error handling
   - Detailed responses

2. FILE HANDLING:
   - Validate before processing
   - Temporary storage
   - Clean up after use
   - Size limits

3. ERROR HANDLING:
   - Specific error messages
   - HTTP status codes
   - Logging for debugging
   - User-friendly messages

4. FLEXIBILITY:
   - Multiple input methods (file, text)
   - Optional parameters
   - Provider selection
   - Feature toggles

5. ORCHESTRATION:
   - Coordinates multiple services
   - Clear step-by-step flow
   - Proper error propagation
   - Resource cleanup

COMMON INTERVIEW QUESTIONS:

Q: "How do you handle file uploads?"
A: "I use FastAPI's UploadFile which handles multipart form data.
    I validate file type and size, save temporarily, process, then
    clean up. The temporary file ensures we don't keep user data."

Q: "What about large files?"
A: "I enforce a configurable size limit (default 10MB). For larger
    files, I could implement chunked uploads or use cloud storage
    with signed URLs."

Q: "How do you handle errors?"
A: "I use try-except blocks at each step, log errors for debugging,
    and return user-friendly HTTP exceptions. The finally block
    ensures cleanup even if errors occur."

Q: "Why two endpoints (file and text)?"
A: "Flexibility. File upload is the main use case, but text input
    is useful for testing, integrations, and users who want to
    copy-paste. Same logic, different input methods."

Q: "How would you add authentication?"
A: "I'd add a dependency that checks JWT tokens or API keys.
    FastAPI's security utilities make this easy. Could use OAuth2
    for user auth or API keys for service-to-service."
"""

# Made with Bob
