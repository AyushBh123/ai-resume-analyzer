"""
============================================================================
TEXT PROCESSING UTILITIES
============================================================================
This module provides utilities for processing and cleaning text.

KEY CONCEPTS TO UNDERSTAND:
1. Text Normalization: Converting text to standard format
2. Regular Expressions: Pattern matching for text extraction
3. NLP Basics: Natural language processing techniques
4. Data Cleaning: Removing noise and artifacts

INTERVIEW TALKING POINTS:
- "I use regex patterns to extract structured data from unstructured text"
- "Text preprocessing is crucial for accurate AI analysis"
- "I handle edge cases like special characters, multiple languages, etc."
============================================================================
"""

import re
from typing import List, Dict, Optional, Set, Any
import string
from datetime import datetime


class TextProcessor:
    """
    Process and clean text extracted from resumes.
    
    WHAT IT DOES:
    - Clean and normalize text
    - Extract emails, phone numbers, URLs
    - Identify sections
    - Extract dates
    - Tokenize text
    
    USAGE:
        processor = TextProcessor()
        clean_text = processor.clean(raw_text)
        emails = processor.extract_emails(text)
    """
    
    def __init__(self):
        """Initialize text processor with common patterns."""
        
        # Email pattern (RFC 5322 simplified)
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone number patterns (various formats)
        self.phone_patterns = [
            re.compile(r'\+?1?\s*\(?(\d{3})\)?[\s.-]?(\d{3})[\s.-]?(\d{4})'),  # US
            re.compile(r'\+?\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}'),  # International
        ]
        
        # URL pattern
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # LinkedIn URL pattern
        self.linkedin_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        )
        
        # GitHub URL pattern
        self.github_pattern = re.compile(
            r'(?:https?://)?(?:www\.)?github\.com/[\w-]+'
        )
        
        # Date patterns
        self.date_patterns = [
            re.compile(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b', re.IGNORECASE),
            re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'),
            re.compile(r'\b\d{4}\b'),  # Just year
        ]
    
    def clean(self, text: str) -> str:
        """
        Clean and normalize text.
        
        WHAT IT DOES:
        1. Remove extra whitespace
        2. Normalize line breaks
        3. Remove special characters (optional)
        4. Fix common issues
        
        PARAMETERS:
            text: Raw text to clean
        
        RETURNS:
            Cleaned text
        
        EXAMPLE:
            clean_text = processor.clean(raw_text)
        """
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove leading/trailing whitespace from lines
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_emails(self, text: str) -> List[str]:
        """
        Extract email addresses from text.
        
        HOW IT WORKS:
        - Uses regex pattern to find email-like strings
        - Validates format
        - Returns unique emails
        
        EXAMPLE:
            emails = processor.extract_emails(text)
            # Returns: ["john@example.com", "jane@company.com"]
        """
        if not text:
            return []
        
        emails = self.email_pattern.findall(text)
        # Return unique emails, lowercase
        return list(set(email.lower() for email in emails))
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        Extract phone numbers from text.
        
        HANDLES:
        - US format: (123) 456-7890
        - International: +1-123-456-7890
        - Various separators: spaces, dashes, dots
        
        EXAMPLE:
            phones = processor.extract_phone_numbers(text)
            # Returns: ["+1-123-456-7890", "555-0123"]
        """
        if not text:
            return []
        
        phones = []
        for pattern in self.phone_patterns:
            matches = pattern.findall(text)
            phones.extend(matches)
        
        # Clean up phone numbers
        cleaned_phones = []
        for phone in phones:
            if isinstance(phone, tuple):
                # From grouped regex
                phone = ''.join(phone)
            # Remove non-digit characters for comparison
            digits = re.sub(r'\D', '', str(phone))
            if 10 <= len(digits) <= 15:  # Valid phone number length
                cleaned_phones.append(phone)
        
        return list(set(cleaned_phones))
    
    def extract_urls(self, text: str) -> Dict[str, List[str]]:
        """
        Extract URLs from text, categorized by type.
        
        RETURNS:
            Dictionary with:
            - linkedin: List of LinkedIn URLs
            - github: List of GitHub URLs
            - other: List of other URLs
        
        EXAMPLE:
            urls = processor.extract_urls(text)
            linkedin = urls["linkedin"]
        """
        if not text:
            return {"linkedin": [], "github": [], "other": []}
        
        linkedin_urls = self.linkedin_pattern.findall(text)
        github_urls = self.github_pattern.findall(text)
        all_urls = self.url_pattern.findall(text)
        
        # Other URLs (not LinkedIn or GitHub)
        other_urls = [
            url for url in all_urls 
            if 'linkedin.com' not in url.lower() and 'github.com' not in url.lower()
        ]
        
        return {
            "linkedin": list(set(linkedin_urls)),
            "github": list(set(github_urls)),
            "other": list(set(other_urls))
        }
    
    def extract_dates(self, text: str) -> List[str]:
        """
        Extract dates from text.
        
        FORMATS SUPPORTED:
        - Month Year: "January 2020", "Jan 2020"
        - MM/DD/YYYY: "01/15/2020"
        - Year only: "2020"
        
        EXAMPLE:
            dates = processor.extract_dates(text)
            # Returns: ["January 2020", "2019", "12/2018"]
        """
        if not text:
            return []
        
        dates = []
        for pattern in self.date_patterns:
            matches = pattern.findall(text)
            dates.extend(matches)
        
        return list(set(dates))
    
    def identify_sections(self, text: str) -> Dict[str, int]:
        """
        Identify resume sections and their positions.
        
        COMMON SECTIONS:
        - Summary/Objective
        - Experience
        - Education
        - Skills
        - Certifications
        - Projects
        
        RETURNS:
            Dictionary mapping section name to line number
        
        EXAMPLE:
            sections = processor.identify_sections(text)
            # Returns: {"experience": 10, "education": 45, ...}
        
        INTERVIEW TIP:
        "I use regex patterns to identify section headers, which helps
        structure the resume data before sending to AI for analysis."
        """
        sections = {}
        
        # Section header patterns
        patterns = {
            "summary": r'(?i)^(summary|objective|profile|about me)',
            "experience": r'(?i)^(experience|employment|work history|professional experience)',
            "education": r'(?i)^(education|academic background)',
            "skills": r'(?i)^(skills|technical skills|core competencies)',
            "certifications": r'(?i)^(certifications?|licenses?)',
            "projects": r'(?i)^(projects?|portfolio)',
            "awards": r'(?i)^(awards?|honors?|achievements?)',
            "publications": r'(?i)^(publications?|papers?)',
            "languages": r'(?i)^(languages?)',
        }
        
        lines = text.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            for section_name, pattern in patterns.items():
                if re.match(pattern, line):
                    sections[section_name] = line_num
                    break
        
        return sections
    
    def extract_section_content(self, text: str, section_name: str) -> Optional[str]:
        """
        Extract content of a specific section.
        
        PARAMETERS:
            text: Full resume text
            section_name: Section to extract (e.g., "experience")
        
        RETURNS:
            Section content or None if not found
        
        HOW IT WORKS:
        1. Find section header
        2. Extract text until next section or end
        3. Return cleaned content
        """
        sections = self.identify_sections(text)
        
        if section_name not in sections:
            return None
        
        lines = text.split('\n')
        start_line = sections[section_name]
        
        # Find next section
        next_line = len(lines)
        for other_section, line_num in sections.items():
            if line_num > start_line and line_num < next_line:
                next_line = line_num
        
        # Extract content
        content_lines = lines[start_line:next_line]
        content = '\n'.join(content_lines)
        
        return self.clean(content)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Split text into words (tokens).
        
        WHAT IT DOES:
        - Split on whitespace
        - Remove punctuation
        - Convert to lowercase
        - Remove empty tokens
        
        EXAMPLE:
            tokens = processor.tokenize("Hello, World!")
            # Returns: ["hello", "world"]
        """
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Split on whitespace
        tokens = text.split()
        
        # Remove empty tokens
        tokens = [t for t in tokens if t]
        
        return tokens
    
    def extract_keywords(self, text: str, min_length: int = 3) -> Set[str]:
        """
        Extract keywords from text.
        
        WHAT IT DOES:
        - Tokenize text
        - Remove common words (stopwords)
        - Filter by length
        - Return unique keywords
        
        PARAMETERS:
            text: Text to process
            min_length: Minimum keyword length
        
        RETURNS:
            Set of keywords
        
        EXAMPLE:
            keywords = processor.extract_keywords(text)
            # Returns: {"python", "javascript", "react", ...}
        """
        # Common stopwords (simplified list)
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        tokens = self.tokenize(text)
        
        # Filter keywords
        keywords = {
            token for token in tokens
            if len(token) >= min_length and token not in stopwords
        }
        
        return keywords
    
    def calculate_word_frequency(self, text: str) -> Dict[str, int]:
        """
        Calculate word frequency in text.
        
        RETURNS:
            Dictionary mapping word to frequency count
        
        EXAMPLE:
            freq = processor.calculate_word_frequency(text)
            # Returns: {"python": 5, "javascript": 3, ...}
        
        WHY USEFUL:
        - Identify most mentioned skills
        - Detect keyword stuffing
        - Analyze content focus
        """
        tokens = self.tokenize(text)
        
        frequency = {}
        for token in tokens:
            frequency[token] = frequency.get(token, 0) + 1
        
        return frequency


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def clean_text(text: str) -> str:
    """Clean text using default processor."""
    processor = TextProcessor()
    return processor.clean(text)


def extract_contact_info(text: str) -> Dict[str, Any]:
    """
    Extract contact information from text.
    
    RETURNS:
        Dictionary with emails, phones, URLs
    
    EXAMPLE:
        contact = extract_contact_info(resume_text)
        email = contact["emails"][0] if contact["emails"] else None
    """
    processor = TextProcessor()
    
    return {
        "emails": processor.extract_emails(text),
        "phones": processor.extract_phone_numbers(text),
        "urls": processor.extract_urls(text),
    }


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text."""
    return TextProcessor().extract_emails(text)


def extract_phone_numbers(text: str) -> List[str]:
    """Extract phone numbers from text."""
    return TextProcessor().extract_phone_numbers(text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text as a flat list."""
    urls_dict = TextProcessor().extract_urls(text)
    # flatten the dict of lists into a single list
    result = []
    for v in urls_dict.values():
        result.extend(v)
    return result


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text."""
    return list(TextProcessor().extract_keywords(text))


def identify_sections(text: str) -> Dict[str, Any]:
    """Identify resume sections in text."""
    return TextProcessor().identify_sections(text)


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. REGEX PATTERNS:
   - Use compiled patterns for performance
   - Handle various formats (phone, email, dates)
   - Case-insensitive matching where appropriate

2. TEXT CLEANING:
   - Remove artifacts from parsing
   - Normalize whitespace and line breaks
   - Preserve structure where needed

3. INFORMATION EXTRACTION:
   - Extract structured data from unstructured text
   - Handle edge cases and variations
   - Return consistent format

4. PERFORMANCE:
   - Compile regex patterns once
   - Use sets for uniqueness
   - Efficient string operations

5. EXTENSIBILITY:
   - Easy to add new patterns
   - Modular functions
   - Clear interfaces

COMMON INTERVIEW QUESTIONS:

Q: "Why use regex for extraction?"
A: "Regex is efficient for pattern matching in text. For contact info
    and dates, patterns are well-defined. For more complex extraction
    like job titles or skills, I use AI which understands context better."

Q: "How do you handle different date formats?"
A: "I use multiple regex patterns to match common formats. For ambiguous
    dates, I could add date parsing libraries like dateutil for better
    accuracy."

Q: "What about internationalization?"
A: "Current implementation focuses on English resumes. For international
    support, I'd add language detection, locale-specific patterns, and
    Unicode handling."

Q: "How would you improve this?"
A: "I could add:
    - NLP library integration (spaCy, NLTK)
    - Named entity recognition
    - Better stopword handling
    - Stemming/lemmatization
    - Language detection
    - More sophisticated keyword extraction"
"""

# Made with Bob
