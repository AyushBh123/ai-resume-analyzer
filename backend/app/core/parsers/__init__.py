"""
============================================================================
PARSERS MODULE
============================================================================
This module provides document parsing functionality for resumes.

SUPPORTED FORMATS:
- PDF (.pdf)
- Microsoft Word (.docx)

USAGE:
    from app.core.parsers import parse_resume
    
    result = parse_resume("resume.pdf")
    if result["success"]:
        print(result["text"])
============================================================================
"""

from .pdf_parser import PDFParser, parse_pdf
from .docx_parser import DOCXParser, parse_docx
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume file (auto-detects format).
    
    WHAT IT DOES:
    - Detects file format from extension
    - Routes to appropriate parser
    - Returns standardized result
    
    PARAMETERS:
        file_path: Path to the resume file
    
    RETURNS:
        Dictionary with:
        - success: bool
        - text: str (extracted text)
        - error: str (if failed)
        - metadata: dict (file info)
    
    EXAMPLE:
        result = parse_resume("resume.pdf")
        if result["success"]:
            text = result["text"]
            # Process text...
    
    INTERVIEW TIP:
    "I created a unified interface that auto-detects file format
    and routes to the appropriate parser. This makes it easy to
    add support for new formats in the future."
    """
    file_path_obj = Path(file_path)
    
    # Check if file exists
    if not file_path_obj.exists():
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "text": "",
            "metadata": {}
        }
    
    # Get file extension
    extension = file_path_obj.suffix.lower()
    
    # Route to appropriate parser
    if extension == ".pdf":
        logger.info(f"Parsing PDF: {file_path}")
        return parse_pdf(file_path)
    
    elif extension == ".docx":
        logger.info(f"Parsing DOCX: {file_path}")
        return parse_docx(file_path)
    
    else:
        return {
            "success": False,
            "error": f"Unsupported file format: {extension}. Supported: .pdf, .docx",
            "text": "",
            "metadata": {}
        }


def get_supported_extensions() -> list:
    """
    Get list of supported file extensions.
    
    RETURNS:
        List of extensions: [".pdf", ".docx"]
    
    WHY USEFUL:
    - For validation in API endpoints
    - For displaying to users
    - For file upload restrictions
    """
    return [".pdf", ".docx"]


def is_supported_format(file_path: str) -> bool:
    """
    Check if file format is supported.
    
    PARAMETERS:
        file_path: Path to file
    
    RETURNS:
        True if format is supported, False otherwise
    
    EXAMPLE:
        if is_supported_format("resume.pdf"):
            result = parse_resume("resume.pdf")
    """
    extension = Path(file_path).suffix.lower()
    return extension in get_supported_extensions()


# Export main classes and functions
__all__ = [
    "PDFParser",
    "DOCXParser",
    "parse_pdf",
    "parse_docx",
    "parse_resume",
    "get_supported_extensions",
    "is_supported_format",
]

# Made with Bob
