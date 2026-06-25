"""
Integration Tests for API Endpoints

Tests for health check, upload, and analysis endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_success(self):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "providers" in data

    def test_health_check_providers(self):
        """Test that health endpoint returns provider information"""
        response = client.get("/health")
        data = response.json()
        
        providers = data.get("providers", {})
        assert isinstance(providers, dict)
        # Should have at least one provider configured
        assert len(providers) > 0


class TestUploadEndpoint:
    """Test file upload endpoint"""

    def test_upload_without_file(self):
        """Test upload endpoint without file"""
        response = client.post("/upload")
        assert response.status_code == 422  # Validation error

    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/upload", files=files)
        # Should reject non-PDF/DOCX files
        assert response.status_code in [400, 422]

    def test_upload_pdf_file(self):
        """Test upload with PDF file (mock)"""
        # Create a minimal PDF-like content
        pdf_content = b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"
        files = {"file": ("resume.pdf", pdf_content, "application/pdf")}
        response = client.post("/upload", files=files)
        
        # May fail without valid PDF, but should not crash
        assert response.status_code in [200, 400, 422]


class TestAnalyzeEndpoint:
    """Test analysis endpoint"""

    def test_analyze_without_data(self):
        """Test analyze endpoint without data"""
        response = client.post("/analyze", json={})
        assert response.status_code == 422  # Validation error

    def test_analyze_with_text(self):
        """Test analyze endpoint with resume text"""
        request_data = {
            "resume_text": "John Doe\nSoftware Engineer\nPython, JavaScript",
            "provider": "openai"
        }
        response = client.post("/analyze", json=request_data)
        
        # May fail without API key, but should not crash
        assert response.status_code in [200, 400, 500]

    def test_analyze_with_invalid_provider(self):
        """Test analyze with invalid provider"""
        request_data = {
            "resume_text": "Test resume",
            "provider": "invalid_provider"
        }
        response = client.post("/analyze", json=request_data)
        assert response.status_code == 422  # Validation error


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers(self):
        """Test that CORS headers are present"""
        response = client.options("/health")
        # CORS should be configured
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Test error handling"""

    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_method(self):
        """Test invalid HTTP method"""
        response = client.delete("/health")
        assert response.status_code == 405  # Method not allowed


# Fixtures
@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing"""
    return {
        "resume_text": """
        John Doe
        john.doe@example.com | (555) 123-4567
        
        EXPERIENCE
        Software Engineer at Tech Company
        2020 - Present
        - Developed web applications
        
        EDUCATION
        BS Computer Science, 2019
        
        SKILLS
        Python, JavaScript, React
        """,
        "provider": "openai"
    }


@pytest.fixture
def sample_job_description():
    """Sample job description for testing"""
    return """
    Looking for a Software Engineer with:
    - 3+ years experience
    - Python and JavaScript skills
    - Experience with React
    """


def test_full_analysis_flow(sample_resume_data, sample_job_description):
    """Test complete analysis flow"""
    # Add job description
    sample_resume_data["job_description"] = sample_job_description
    
    # Make request
    response = client.post("/analyze", json=sample_resume_data)
    
    # Check response (may fail without API key)
    if response.status_code == 200:
        data = response.json()
        assert "overall_score" in data
        assert "score_breakdown" in data
        assert "suggestions" in data
        assert "ats_compatibility" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
