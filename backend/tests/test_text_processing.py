"""
Unit Tests for Text Processing Utilities

Tests for email extraction, phone extraction, URL extraction,
and other text processing functions.
"""

import pytest
from app.utils.text_processing import (
    extract_emails,
    extract_phone_numbers,
    extract_urls,
    extract_keywords,
    clean_text,
    identify_sections,
)


class TestEmailExtraction:
    """Test email extraction functionality"""

    def test_extract_single_email(self):
        text = "Contact me at john.doe@example.com for more info"
        emails = extract_emails(text)
        assert len(emails) == 1
        assert "john.doe@example.com" in emails

    def test_extract_multiple_emails(self):
        text = "Email: john@example.com or jane@company.org"
        emails = extract_emails(text)
        assert len(emails) == 2
        assert "john@example.com" in emails
        assert "jane@company.org" in emails

    def test_extract_no_emails(self):
        text = "No email addresses in this text"
        emails = extract_emails(text)
        assert len(emails) == 0

    def test_extract_email_with_special_chars(self):
        text = "Contact: john.doe+test@example.co.uk"
        emails = extract_emails(text)
        assert len(emails) == 1
        assert "john.doe+test@example.co.uk" in emails


class TestPhoneExtraction:
    """Test phone number extraction functionality"""

    def test_extract_us_phone(self):
        text = "Call me at (555) 123-4567"
        phones = extract_phone_numbers(text)
        assert len(phones) >= 1

    def test_extract_international_phone(self):
        text = "Phone: +1-555-123-4567"
        phones = extract_phone_numbers(text)
        assert len(phones) >= 1

    def test_extract_multiple_phones(self):
        text = "Mobile: 555-123-4567, Office: (555) 987-6543"
        phones = extract_phone_numbers(text)
        assert len(phones) >= 2

    def test_extract_no_phones(self):
        text = "No phone numbers here"
        phones = extract_phone_numbers(text)
        assert len(phones) == 0


class TestURLExtraction:
    """Test URL extraction functionality"""

    def test_extract_http_url(self):
        text = "Visit http://example.com for more"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert "http://example.com" in urls

    def test_extract_https_url(self):
        text = "Portfolio: https://johndoe.com"
        urls = extract_urls(text)
        assert len(urls) == 1
        assert "https://johndoe.com" in urls

    def test_extract_multiple_urls(self):
        text = "GitHub: https://github.com/user LinkedIn: https://linkedin.com/in/user"
        urls = extract_urls(text)
        assert len(urls) == 2

    def test_extract_no_urls(self):
        text = "No URLs in this text"
        urls = extract_urls(text)
        assert len(urls) == 0


class TestKeywordExtraction:
    """Test keyword extraction functionality"""

    def test_extract_keywords_basic(self):
        text = "Python developer with experience in Django and Flask"
        keywords = extract_keywords(text)
        assert len(keywords) > 0
        assert any("python" in k.lower() for k in keywords)

    def test_extract_keywords_technical(self):
        text = "Skills: React, TypeScript, Node.js, AWS, Docker"
        keywords = extract_keywords(text)
        assert len(keywords) > 0

    def test_extract_keywords_empty(self):
        text = ""
        keywords = extract_keywords(text)
        assert len(keywords) == 0

    def test_extract_keywords_with_stopwords(self):
        text = "I am a software engineer with experience in Python"
        keywords = extract_keywords(text)
        # Should filter out common words like "I", "am", "a", "with", "in"
        assert "python" in [k.lower() for k in keywords]


class TestTextCleaning:
    """Test text cleaning functionality"""

    def test_clean_text_whitespace(self):
        text = "  Multiple   spaces   here  "
        cleaned = clean_text(text)
        assert "  " not in cleaned
        assert cleaned.strip() == cleaned

    def test_clean_text_newlines(self):
        text = "Line 1\n\n\nLine 2"
        cleaned = clean_text(text)
        assert "\n\n\n" not in cleaned

    def test_clean_text_special_chars(self):
        text = "Text with •bullets and —dashes"
        cleaned = clean_text(text)
        assert len(cleaned) > 0

    def test_clean_text_empty(self):
        text = ""
        cleaned = clean_text(text)
        assert cleaned == ""


class TestSectionIdentification:
    """Test resume section identification"""

    def test_identify_experience_section(self):
        text = """
        EXPERIENCE
        Software Engineer at Company
        2020 - Present
        """
        sections = identify_sections(text)
        assert len(sections) > 0

    def test_identify_education_section(self):
        text = """
        EDUCATION
        Bachelor of Science in Computer Science
        University Name, 2020
        """
        sections = identify_sections(text)
        assert "education" in sections or "education" in str(sections).lower()

    def test_identify_skills_section(self):
        text = """
        SKILLS
        Python, JavaScript, React, Node.js
        """
        sections = identify_sections(text)
        assert "skills" in sections or "skills" in str(sections).lower()

    def test_identify_multiple_sections(self):
        text = """
        EXPERIENCE
        Software Engineer
        
        EDUCATION
        BS Computer Science
        
        SKILLS
        Python, Java
        """
        sections = identify_sections(text)
        assert len(sections) >= 2


# Fixtures for test data
@pytest.fixture
def sample_resume_text():
    return """
    John Doe
    john.doe@example.com | (555) 123-4567
    https://github.com/johndoe | https://linkedin.com/in/johndoe
    
    PROFESSIONAL SUMMARY
    Experienced software engineer with 5+ years in full-stack development.
    
    WORK EXPERIENCE
    Senior Software Engineer | Tech Company | 2020 - Present
    - Developed scalable web applications using React and Node.js
    - Led team of 5 developers
    
    EDUCATION
    Bachelor of Science in Computer Science
    University Name | 2015 - 2019
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL
    """


@pytest.fixture
def sample_job_description():
    return """
    We are looking for a Senior Software Engineer with:
    - 5+ years of experience in full-stack development
    - Strong knowledge of React, Node.js, and TypeScript
    - Experience with AWS and Docker
    - Excellent communication skills
    """


def test_full_text_processing_pipeline(sample_resume_text):
    """Test complete text processing pipeline"""
    # Extract all information
    emails = extract_emails(sample_resume_text)
    phones = extract_phone_numbers(sample_resume_text)
    urls = extract_urls(sample_resume_text)
    keywords = extract_keywords(sample_resume_text)
    sections = identify_sections(sample_resume_text)
    
    # Verify extractions
    assert len(emails) > 0
    assert len(phones) > 0
    assert len(urls) > 0
    assert len(keywords) > 0
    assert len(sections) > 0
    
    # Verify specific content
    assert "john.doe@example.com" in emails
    assert any("github" in url.lower() for url in urls)
    assert any("python" in k.lower() for k in keywords)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
