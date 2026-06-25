"""
============================================================================
ANALYSIS RESULT MODELS
============================================================================
This module defines data structures for resume analysis results.

KEY CONCEPTS TO UNDERSTAND:
1. Analysis Results: Structured output from AI analysis
2. Scoring System: How we rate different aspects of a resume
3. Suggestions: Actionable feedback for improvement
4. Job Matching: Comparing resume against job requirements

INTERVIEW TALKING POINTS:
- "I designed a comprehensive scoring system with multiple dimensions"
- "The analysis model provides structured, actionable feedback"
- "Results are easily serializable for API responses"
============================================================================
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ScoreLevel(str, Enum):
    """
    Score level categories.
    
    WHY USE THIS:
    - Provides human-readable score interpretation
    - Makes it easy to display color-coded results in UI
    """
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"           # 75-89
    FAIR = "fair"           # 60-74
    POOR = "poor"           # 40-59
    VERY_POOR = "very_poor" # 0-39


class SuggestionPriority(str, Enum):
    """Priority level for improvement suggestions."""
    CRITICAL = "critical"  # Must fix
    HIGH = "high"         # Should fix
    MEDIUM = "medium"     # Nice to fix
    LOW = "low"          # Optional


class SuggestionCategory(str, Enum):
    """Categories of improvement suggestions."""
    CONTENT = "content"           # Content quality
    FORMATTING = "formatting"     # Layout and structure
    KEYWORDS = "keywords"         # Missing keywords
    EXPERIENCE = "experience"     # Experience section
    EDUCATION = "education"       # Education section
    SKILLS = "skills"            # Skills section
    ATS = "ats"                  # ATS compatibility


# ============================================================================
# SCORE COMPONENTS
# ============================================================================

class ScoreBreakdown(BaseModel):
    """
    Detailed score breakdown for one aspect.
    
    EXAMPLE:
        ScoreBreakdown(
            category="Skills",
            score=85,
            max_score=100,
            weight=0.3,
            details="Strong technical skills, missing some trending technologies"
        )
    """
    
    category: str = Field(
        ...,
        description="Score category name",
        max_length=50
    )
    
    score: float = Field(
        ...,
        description="Score for this category (0-100)",
        ge=0,
        le=100
    )
    
    max_score: float = Field(
        default=100,
        description="Maximum possible score",
        ge=0
    )
    
    weight: float = Field(
        ...,
        description="Weight of this category in overall score (0-1)",
        ge=0,
        le=1
    )
    
    details: Optional[str] = Field(
        None,
        description="Detailed explanation of the score"
    )
    
    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0
    
    @property
    def weighted_score(self) -> float:
        """Get weighted contribution to overall score."""
        return self.score * self.weight
    
    @property
    def level(self) -> ScoreLevel:
        """
        Get score level based on percentage.
        
        SCORING RUBRIC:
        - 90-100: Excellent
        - 75-89: Good
        - 60-74: Fair
        - 40-59: Poor
        - 0-39: Very Poor
        """
        pct = self.percentage
        if pct >= 90:
            return ScoreLevel.EXCELLENT
        elif pct >= 75:
            return ScoreLevel.GOOD
        elif pct >= 60:
            return ScoreLevel.FAIR
        elif pct >= 40:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.VERY_POOR


# ============================================================================
# IMPROVEMENT SUGGESTIONS
# ============================================================================

class Suggestion(BaseModel):
    """
    Single improvement suggestion.
    
    WHAT IT CONTAINS:
    - What to improve
    - Why it matters
    - How to fix it
    - Priority level
    """
    
    category: SuggestionCategory = Field(
        ...,
        description="Suggestion category"
    )
    
    priority: SuggestionPriority = Field(
        ...,
        description="Priority level"
    )
    
    title: str = Field(
        ...,
        description="Short title of the suggestion",
        max_length=100
    )
    
    description: str = Field(
        ...,
        description="Detailed description of the issue"
    )
    
    recommendation: str = Field(
        ...,
        description="How to fix the issue"
    )
    
    impact: Optional[str] = Field(
        None,
        description="Expected impact of implementing this suggestion"
    )
    
    examples: List[str] = Field(
        default_factory=list,
        description="Example improvements"
    )


# ============================================================================
# KEYWORD ANALYSIS
# ============================================================================

class KeywordMatch(BaseModel):
    """
    Keyword matching results.
    
    USED FOR:
    - Comparing resume keywords with job description
    - Identifying missing important keywords
    - ATS optimization
    """
    
    keyword: str = Field(
        ...,
        description="The keyword",
        max_length=100
    )
    
    found: bool = Field(
        ...,
        description="Whether keyword was found in resume"
    )
    
    frequency: int = Field(
        default=0,
        description="How many times keyword appears",
        ge=0
    )
    
    importance: float = Field(
        default=1.0,
        description="Importance weight (0-1)",
        ge=0,
        le=1
    )
    
    context: Optional[str] = Field(
        None,
        description="Where the keyword was found"
    )


class KeywordAnalysis(BaseModel):
    """
    Complete keyword analysis results.
    """
    
    total_keywords: int = Field(
        ...,
        description="Total keywords analyzed",
        ge=0
    )
    
    matched_keywords: int = Field(
        ...,
        description="Number of keywords found",
        ge=0
    )
    
    missing_keywords: int = Field(
        ...,
        description="Number of keywords missing",
        ge=0
    )
    
    match_percentage: float = Field(
        ...,
        description="Percentage of keywords matched",
        ge=0,
        le=100
    )
    
    keywords: List[KeywordMatch] = Field(
        default_factory=list,
        description="Detailed keyword matches"
    )
    
    @property
    def matched_keyword_list(self) -> List[str]:
        """Get list of matched keywords."""
        return [kw.keyword for kw in self.keywords if kw.found]
    
    @property
    def missing_keyword_list(self) -> List[str]:
        """Get list of missing keywords."""
        return [kw.keyword for kw in self.keywords if not kw.found]


# ============================================================================
# ATS COMPATIBILITY
# ============================================================================

class ATSCompatibility(BaseModel):
    """
    ATS (Applicant Tracking System) compatibility analysis.
    
    WHY THIS MATTERS:
    - Most companies use ATS to filter resumes
    - Poor formatting can cause resume to be rejected automatically
    - This helps optimize for ATS parsing
    """
    
    overall_score: float = Field(
        ...,
        description="Overall ATS compatibility score (0-100)",
        ge=0,
        le=100
    )
    
    has_contact_info: bool = Field(
        ...,
        description="Contact information is present and parseable"
    )
    
    has_clear_sections: bool = Field(
        ...,
        description="Resume has clear, standard section headers"
    )
    
    uses_standard_fonts: bool = Field(
        default=True,
        description="Uses ATS-friendly fonts"
    )
    
    avoids_tables: bool = Field(
        default=True,
        description="Avoids complex tables (ATS can't parse them well)"
    )
    
    avoids_headers_footers: bool = Field(
        default=True,
        description="Avoids headers/footers (ATS often ignores them)"
    )
    
    has_keywords: bool = Field(
        ...,
        description="Contains relevant keywords"
    )
    
    file_format_compatible: bool = Field(
        default=True,
        description="File format is ATS-compatible (PDF or DOCX)"
    )
    
    issues: List[str] = Field(
        default_factory=list,
        description="List of ATS compatibility issues found"
    )
    
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommendations to improve ATS compatibility"
    )


# ============================================================================
# MAIN ANALYSIS RESULT
# ============================================================================

class ResumeAnalysis(BaseModel):
    """
    Complete resume analysis result.
    
    THIS IS THE MAIN OUTPUT:
    - Overall score and breakdown
    - Improvement suggestions
    - Keyword analysis
    - ATS compatibility
    - AI-generated insights
    
    USAGE:
        analysis = ResumeAnalysis(
            overall_score=78.5,
            score_breakdown=[...],
            suggestions=[...],
            ...
        )
    """
    
    # ========================================================================
    # OVERALL SCORE
    # ========================================================================
    
    overall_score: float = Field(
        ...,
        description="Overall resume score (0-100)",
        ge=0,
        le=100
    )
    
    score_level: ScoreLevel = Field(
        ...,
        description="Score level category"
    )
    
    # ========================================================================
    # DETAILED SCORES
    # ========================================================================
    
    score_breakdown: List[ScoreBreakdown] = Field(
        default_factory=list,
        description="Detailed score breakdown by category"
    )
    
    # ========================================================================
    # SUGGESTIONS
    # ========================================================================
    
    suggestions: List[Suggestion] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )
    
    # ========================================================================
    # KEYWORD ANALYSIS
    # ========================================================================
    
    keyword_analysis: Optional[KeywordAnalysis] = Field(
        None,
        description="Keyword matching results (if job description provided)"
    )
    
    # ========================================================================
    # ATS COMPATIBILITY
    # ========================================================================
    
    ats_compatibility: Optional[ATSCompatibility] = Field(
        None,
        description="ATS compatibility analysis"
    )
    
    # ========================================================================
    # AI INSIGHTS
    # ========================================================================
    
    strengths: List[str] = Field(
        default_factory=list,
        description="Key strengths identified"
    )
    
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Areas needing improvement"
    )
    
    summary: Optional[str] = Field(
        None,
        description="AI-generated summary of the analysis"
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the analysis was performed"
    )
    
    ai_provider: str = Field(
        ...,
        description="AI provider used for analysis"
    )
    
    ai_model: str = Field(
        ...,
        description="AI model used"
    )
    
    processing_time_seconds: Optional[float] = Field(
        None,
        description="Time taken to analyze (in seconds)",
        ge=0
    )
    
    # ========================================================================
    # COMPUTED PROPERTIES
    # ========================================================================
    
    @property
    def critical_suggestions(self) -> List[Suggestion]:
        """Get only critical priority suggestions."""
        return [s for s in self.suggestions if s.priority == SuggestionPriority.CRITICAL]
    
    @property
    def high_priority_suggestions(self) -> List[Suggestion]:
        """Get critical and high priority suggestions."""
        return [
            s for s in self.suggestions 
            if s.priority in [SuggestionPriority.CRITICAL, SuggestionPriority.HIGH]
        ]
    
    @property
    def suggestions_by_category(self) -> Dict[str, List[Suggestion]]:
        """Group suggestions by category."""
        result: Dict[str, List[Suggestion]] = {}
        for suggestion in self.suggestions:
            category = suggestion.category.value
            if category not in result:
                result[category] = []
            result[category].append(suggestion)
        return result
    
    @validator("score_level", pre=True, always=True)
    def set_score_level(cls, v, values):
        """
        Automatically set score_level based on overall_score.
        
        WHY: Ensures consistency between score and level
        """
        if v is not None:
            return v
        
        score = values.get("overall_score", 0)
        if score >= 90:
            return ScoreLevel.EXCELLENT
        elif score >= 75:
            return ScoreLevel.GOOD
        elif score >= 60:
            return ScoreLevel.FAIR
        elif score >= 40:
            return ScoreLevel.POOR
        else:
            return ScoreLevel.VERY_POOR
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "overall_score": 78.5,
                "score_level": "good",
                "score_breakdown": [
                    {
                        "category": "Skills",
                        "score": 85,
                        "max_score": 100,
                        "weight": 0.3,
                        "details": "Strong technical skills"
                    }
                ],
                "suggestions": [
                    {
                        "category": "keywords",
                        "priority": "high",
                        "title": "Add missing keywords",
                        "description": "Your resume is missing key terms from the job description",
                        "recommendation": "Include: Python, AWS, Docker"
                    }
                ],
                "strengths": [
                    "Strong technical background",
                    "Clear career progression"
                ],
                "weaknesses": [
                    "Missing quantifiable achievements",
                    "Could improve formatting"
                ],
                "analyzed_at": "2024-01-15T10:30:00Z",
                "ai_provider": "openai",
                "ai_model": "gpt-4-turbo-preview"
            }
        }


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. COMPREHENSIVE ANALYSIS:
   - Multiple scoring dimensions
   - Actionable suggestions
   - ATS compatibility check
   - Keyword matching

2. STRUCTURED OUTPUT:
   - Easy to display in UI
   - Can be stored in database
   - Serializes to JSON automatically

3. PRIORITY SYSTEM:
   - Helps users focus on important issues
   - Critical issues highlighted
   - Categorized for easy navigation

4. COMPUTED PROPERTIES:
   - Derived data calculated on-the-fly
   - No redundant storage
   - Always consistent

5. EXTENSIBILITY:
   - Easy to add new score categories
   - Can add new suggestion types
   - Flexible for future enhancements

COMMON INTERVIEW QUESTIONS:

Q: "How do you calculate the overall score?"
A: "I use a weighted average of category scores. Each category has 
    a weight (e.g., skills 30%, experience 40%, education 20%, 
    formatting 10%). The overall score is the sum of weighted scores."

Q: "How do you prioritize suggestions?"
A: "I use a priority system (critical, high, medium, low) based on 
    impact on ATS success and hiring decisions. Critical issues 
    could cause automatic rejection, while low priority are nice-to-haves."

Q: "How would you improve the scoring algorithm?"
A: "I could add machine learning to learn from successful resumes, 
    incorporate industry-specific scoring, add role-level adjustments, 
    and use historical data to refine weights."
"""

# Made with Bob
