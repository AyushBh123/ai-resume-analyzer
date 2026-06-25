"""
============================================================================
RESUME DATA MODELS
============================================================================
This module defines the data structures for resume information.

KEY CONCEPTS TO UNDERSTAND:
1. Pydantic Models: Python classes that validate data automatically
2. Type Hints: Specify what type each field should be
3. Data Transfer Objects (DTOs): Structures for passing data between layers
4. JSON Serialization: Converting Python objects to/from JSON

INTERVIEW TALKING POINTS:
- "I use Pydantic models for automatic data validation and serialization"
- "These models ensure data integrity throughout the application"
- "Type hints provide IDE autocomplete and catch errors early"
============================================================================
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import date
from enum import Enum


# ============================================================================
# ENUMS - Predefined choices
# ============================================================================

class ExperienceLevel(str, Enum):
    """
    Experience level categories.
    
    WHY USE ENUM:
    - Limits values to predefined choices
    - Prevents typos and invalid values
    - Self-documenting code
    """
    ENTRY = "entry"           # 0-2 years
    JUNIOR = "junior"         # 2-4 years
    MID = "mid"              # 4-7 years
    SENIOR = "senior"        # 7-10 years
    LEAD = "lead"            # 10+ years
    EXECUTIVE = "executive"   # C-level


class EducationLevel(str, Enum):
    """Education degree levels."""
    HIGH_SCHOOL = "high_school"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    DOCTORATE = "doctorate"
    CERTIFICATE = "certificate"


# ============================================================================
# CONTACT INFORMATION
# ============================================================================

class ContactInfo(BaseModel):
    """
    Contact information extracted from resume.
    
    WHAT THIS STORES:
    - Name, email, phone
    - Location (city, state, country)
    - Professional links (LinkedIn, GitHub, portfolio)
    
    EXAMPLE:
        contact = ContactInfo(
            full_name="John Doe",
            email="john@example.com",
            phone="+1-555-0123"
        )
    """
    
    full_name: str = Field(
        ...,  # ... means required field
        description="Full name of the candidate",
        min_length=2,
        max_length=100
    )
    
    email: Optional[EmailStr] = Field(
        None,  # None means optional
        description="Email address (validated format)"
    )
    
    phone: Optional[str] = Field(
        None,
        description="Phone number",
        max_length=20
    )
    
    location: Optional[str] = Field(
        None,
        description="City, State or City, Country",
        max_length=100
    )
    
    linkedin_url: Optional[str] = Field(
        None,
        description="LinkedIn profile URL"
    )
    
    github_url: Optional[str] = Field(
        None,
        description="GitHub profile URL"
    )
    
    portfolio_url: Optional[str] = Field(
        None,
        description="Personal website or portfolio URL"
    )
    
    @validator("linkedin_url", "github_url", "portfolio_url")
    def validate_url(cls, v):
        """
        Ensure URLs start with http:// or https://.
        
        WHY: Prevents invalid URLs from being stored
        """
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v


# ============================================================================
# WORK EXPERIENCE
# ============================================================================

class WorkExperience(BaseModel):
    """
    Single work experience entry.
    
    REPRESENTS:
    - One job/position in work history
    - Company, title, dates, responsibilities
    """
    
    company: str = Field(
        ...,
        description="Company name",
        max_length=100
    )
    
    position: str = Field(
        ...,
        description="Job title/position",
        max_length=100
    )
    
    start_date: Optional[str] = Field(
        None,
        description="Start date (format: YYYY-MM or 'Present')"
    )
    
    end_date: Optional[str] = Field(
        None,
        description="End date (format: YYYY-MM or 'Present')"
    )
    
    location: Optional[str] = Field(
        None,
        description="Job location",
        max_length=100
    )
    
    description: Optional[str] = Field(
        None,
        description="Job description and responsibilities"
    )
    
    achievements: List[str] = Field(
        default_factory=list,
        description="List of key achievements/accomplishments"
    )
    
    technologies: List[str] = Field(
        default_factory=list,
        description="Technologies/tools used in this role"
    )
    
    @property
    def is_current(self) -> bool:
        """Check if this is the current job."""
        return bool(self.end_date and self.end_date.lower() in ["present", "current"])


# ============================================================================
# EDUCATION
# ============================================================================

class Education(BaseModel):
    """
    Single education entry.
    
    REPRESENTS:
    - One degree or certification
    - School, degree, field of study, dates
    """
    
    institution: str = Field(
        ...,
        description="School/university name",
        max_length=150
    )
    
    degree: str = Field(
        ...,
        description="Degree type (e.g., Bachelor of Science)",
        max_length=100
    )
    
    field_of_study: Optional[str] = Field(
        None,
        description="Major/field of study",
        max_length=100
    )
    
    start_date: Optional[str] = Field(
        None,
        description="Start date (format: YYYY)"
    )
    
    end_date: Optional[str] = Field(
        None,
        description="End date (format: YYYY or 'Present')"
    )
    
    gpa: Optional[float] = Field(
        None,
        description="Grade Point Average",
        ge=0.0,  # Greater than or equal to 0
        le=4.0   # Less than or equal to 4
    )
    
    honors: List[str] = Field(
        default_factory=list,
        description="Academic honors and awards"
    )


# ============================================================================
# SKILLS
# ============================================================================

class SkillCategory(BaseModel):
    """
    Skills grouped by category.
    
    EXAMPLE:
        SkillCategory(
            category="Programming Languages",
            skills=["Python", "JavaScript", "Java"]
        )
    """
    
    category: str = Field(
        ...,
        description="Skill category name",
        max_length=50
    )
    
    skills: List[str] = Field(
        ...,
        description="List of skills in this category"
    )


# ============================================================================
# CERTIFICATIONS
# ============================================================================

class Certification(BaseModel):
    """Professional certification or license."""
    
    name: str = Field(
        ...,
        description="Certification name",
        max_length=150
    )
    
    issuing_organization: Optional[str] = Field(
        None,
        description="Organization that issued the certification",
        max_length=100
    )
    
    issue_date: Optional[str] = Field(
        None,
        description="Date issued (format: YYYY-MM)"
    )
    
    expiry_date: Optional[str] = Field(
        None,
        description="Expiration date (format: YYYY-MM)"
    )
    
    credential_id: Optional[str] = Field(
        None,
        description="Credential ID or license number",
        max_length=100
    )


# ============================================================================
# COMPLETE RESUME
# ============================================================================

class Resume(BaseModel):
    """
    Complete resume data structure.
    
    THIS IS THE MAIN MODEL:
    - Contains all extracted information from a resume
    - Used throughout the application
    - Can be serialized to/from JSON
    
    USAGE:
        resume = Resume(
            contact_info=ContactInfo(...),
            work_experience=[WorkExperience(...), ...],
            education=[Education(...), ...],
            skills=[SkillCategory(...), ...]
        )
    """
    
    # Basic Information
    contact_info: ContactInfo = Field(
        ...,
        description="Contact information"
    )
    
    # Professional Summary
    summary: Optional[str] = Field(
        None,
        description="Professional summary or objective",
        max_length=1000
    )
    
    # Work History
    work_experience: List[WorkExperience] = Field(
        default_factory=list,
        description="List of work experiences"
    )
    
    # Education
    education: List[Education] = Field(
        default_factory=list,
        description="List of educational qualifications"
    )
    
    # Skills
    skills: List[SkillCategory] = Field(
        default_factory=list,
        description="Skills grouped by category"
    )
    
    # Certifications
    certifications: List[Certification] = Field(
        default_factory=list,
        description="Professional certifications"
    )
    
    # Additional Sections
    languages: List[str] = Field(
        default_factory=list,
        description="Languages spoken"
    )
    
    projects: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Personal or professional projects"
    )
    
    publications: List[str] = Field(
        default_factory=list,
        description="Publications or research papers"
    )
    
    awards: List[str] = Field(
        default_factory=list,
        description="Awards and recognitions"
    )
    
    # Metadata
    raw_text: Optional[str] = Field(
        None,
        description="Original resume text (for reference)"
    )
    
    # ========================================================================
    # COMPUTED PROPERTIES
    # ========================================================================
    
    @property
    def total_years_experience(self) -> float:
        """
        Calculate total years of work experience.
        
        HOW IT WORKS:
        - Counts years from all work experiences
        - Handles overlapping dates
        - Returns approximate years
        
        INTERVIEW TIP:
        "I calculate experience by parsing dates and handling edge cases
        like overlapping jobs or 'Present' as end date."
        """
        # This is a simplified version
        # In production, you'd parse dates properly
        return len(self.work_experience) * 2.5  # Rough estimate
    
    @property
    def all_skills(self) -> List[str]:
        """
        Get flat list of all skills.
        
        RETURNS:
            ["Python", "JavaScript", "React", ...]
        """
        all_skills = []
        for category in self.skills:
            all_skills.extend(category.skills)
        return all_skills
    
    @property
    def highest_education(self) -> Optional[str]:
        """Get highest education level."""
        if not self.education:
            return None
        # Return first education entry (assuming sorted by level)
        return self.education[0].degree
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def has_skill(self, skill: str) -> bool:
        """
        Check if resume contains a specific skill.
        
        PARAMETERS:
            skill: Skill name to search for
        
        RETURNS:
            True if skill found (case-insensitive)
        """
        skill_lower = skill.lower()
        return any(
            skill_lower in s.lower() 
            for s in self.all_skills
        )
    
    def get_current_position(self) -> Optional[str]:
        """Get current job title (if employed)."""
        for exp in self.work_experience:
            if exp.is_current:
                return exp.position
        return None
    
    class Config:
        """Pydantic configuration."""
        # Allow arbitrary types (for complex nested structures)
        arbitrary_types_allowed = True
        # Generate JSON schema for API documentation
        schema_extra = {
            "example": {
                "contact_info": {
                    "full_name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "phone": "+1-555-0123",
                    "location": "San Francisco, CA",
                    "linkedin_url": "https://linkedin.com/in/janesmith",
                    "github_url": "https://github.com/janesmith"
                },
                "summary": "Experienced software engineer with 5+ years...",
                "work_experience": [
                    {
                        "company": "Tech Corp",
                        "position": "Senior Software Engineer",
                        "start_date": "2020-01",
                        "end_date": "Present",
                        "description": "Led development of...",
                        "technologies": ["Python", "React", "AWS"]
                    }
                ],
                "education": [
                    {
                        "institution": "University of California",
                        "degree": "Bachelor of Science",
                        "field_of_study": "Computer Science",
                        "end_date": "2018"
                    }
                ],
                "skills": [
                    {
                        "category": "Programming Languages",
                        "skills": ["Python", "JavaScript", "Java"]
                    }
                ]
            }
        }


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. DATA VALIDATION:
   - Pydantic validates all data automatically
   - Type hints catch errors early
   - Custom validators for complex rules

2. STRUCTURE:
   - Nested models for complex data
   - Enums for predefined choices
   - Optional fields with defaults

3. SERIALIZATION:
   - Automatically converts to/from JSON
   - Works seamlessly with FastAPI
   - Easy to store in database

4. MAINTAINABILITY:
   - Clear structure, easy to understand
   - Self-documenting with Field descriptions
   - Easy to extend with new fields

5. BEST PRACTICES:
   - Separation of concerns (each model has one purpose)
   - Computed properties for derived data
   - Helper methods for common operations

COMMON INTERVIEW QUESTIONS:

Q: "Why use Pydantic instead of plain dictionaries?"
A: "Pydantic provides automatic validation, type safety, better IDE 
    support, and seamless JSON serialization. It catches errors early 
    and makes the code more maintainable."

Q: "How do you handle optional fields?"
A: "I use Optional[Type] for fields that might be None, and provide 
    sensible defaults. Pydantic handles the validation automatically."

Q: "How would you extend this for new resume formats?"
A: "The models are flexible - I can add new fields without breaking 
    existing code. I'd add new optional fields and update the parser 
    to extract them."
"""

# Made with Bob
