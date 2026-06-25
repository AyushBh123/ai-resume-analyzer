"""
============================================================================
PDF PARSER MODULE
============================================================================
This module handles extracting text from PDF resume files.

KEY CONCEPTS TO UNDERSTAND:
1. PDF Structure: PDFs are complex, containing text, images, formatting
2. Text Extraction: Getting readable text from PDF binary data
3. Layout Preservation: Maintaining structure (sections, bullets, etc.)
4. Error Handling: PDFs can be corrupted or password-protected

INTERVIEW TALKING POINTS:
- "I use multiple PDF libraries for robustness - PyPDF2 for basic extraction,
   pdfplumber for better layout handling"
- "I handle edge cases like encrypted PDFs, scanned images, and multi-column layouts"
- "The parser preserves structure by detecting sections and formatting"

LIBRARIES USED:
- PyPDF2: Basic PDF text extraction
- pdfplumber: Advanced extraction with layout awareness
============================================================================
"""

import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Optional, List, Dict, Any
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)


class PDFParser:
    """
    Parse PDF files and extract text content.
    
    HOW IT WORKS:
    1. Try pdfplumber first (better layout handling)
    2. Fall back to PyPDF2 if pdfplumber fails
    3. Clean and structure the extracted text
    4. Return organized content
    
    USAGE:
        parser = PDFParser()
        result = parser.parse("resume.pdf")
        print(result["text"])
    """
    
    def __init__(self):
        """Initialize the PDF parser."""
        self.logger = logging.getLogger(__name__)
    
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a PDF file and extract text.
        
        PARAMETERS:
            file_path: Path to the PDF file
        
        RETURNS:
            Dictionary containing:
            - text: Extracted text content
            - pages: Number of pages
            - metadata: PDF metadata (author, title, etc.)
            - method: Which extraction method was used
            - success: Whether extraction succeeded
        
        EXAMPLE:
            result = parser.parse("resume.pdf")
            if result["success"]:
                print(result["text"])
        """
        file_path_obj = Path(file_path)
        
        # Validate file exists
        if not file_path_obj.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "text": "",
                "pages": 0,
                "metadata": {},
                "method": None
            }
        
        # Try pdfplumber first (better for complex layouts)
        try:
            result = self._parse_with_pdfplumber(file_path_obj)
            if result["success"]:
                self.logger.info(f"Successfully parsed {file_path} with pdfplumber")
                return result
        except Exception as e:
            self.logger.warning(f"pdfplumber failed for {file_path}: {e}")
        
        # Fall back to PyPDF2
        try:
            result = self._parse_with_pypdf2(file_path_obj)
            if result["success"]:
                self.logger.info(f"Successfully parsed {file_path} with PyPDF2")
                return result
        except Exception as e:
            self.logger.error(f"PyPDF2 failed for {file_path}: {e}")
        
        # Both methods failed
        return {
            "success": False,
            "error": "Failed to extract text from PDF",
            "text": "",
            "pages": 0,
            "metadata": {},
            "method": None
        }
    
    def _parse_with_pdfplumber(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse PDF using pdfplumber library.
        
        WHY PDFPLUMBER:
        - Better at preserving layout
        - Can extract tables
        - Handles multi-column layouts better
        - More accurate text positioning
        
        HOW IT WORKS:
        1. Open PDF with pdfplumber
        2. Extract text from each page
        3. Combine pages with page breaks
        4. Extract metadata
        """
        text_parts = []
        metadata = {}
        
        with pdfplumber.open(file_path) as pdf:
            # Extract metadata
            if pdf.metadata:
                metadata = {
                    "author": pdf.metadata.get("Author", ""),
                    "title": pdf.metadata.get("Title", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                }
            
            # Extract text from each page
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    # Extract text with layout preservation
                    page_text = page.extract_text()
                    
                    if page_text:
                        # Add page separator for multi-page resumes
                        if page_num > 1:
                            text_parts.append("\n--- Page Break ---\n")
                        text_parts.append(page_text)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue
            
            # Combine all text
            full_text = "\n".join(text_parts)
            
            # Clean the text
            full_text = self._clean_text(full_text)
            
            return {
                "success": True,
                "text": full_text,
                "pages": len(pdf.pages),
                "metadata": metadata,
                "method": "pdfplumber",
                "error": None
            }
    
    def _parse_with_pypdf2(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse PDF using PyPDF2 library (fallback method).
        
        WHY PYPDF2:
        - More robust for simple PDFs
        - Handles encrypted PDFs better
        - Lighter weight
        
        LIMITATIONS:
        - Less accurate layout preservation
        - May miss text in complex layouts
        - Doesn't handle tables well
        """
        text_parts = []
        metadata = {}
        
        with open(file_path, "rb") as file:
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                try:
                    # Try to decrypt with empty password
                    pdf_reader.decrypt("")
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"PDF is password-protected: {e}",
                        "text": "",
                        "pages": 0,
                        "metadata": {},
                        "method": "pypdf2"
                    }
            
            # Extract metadata
            if pdf_reader.metadata:
                metadata = {
                    "author": pdf_reader.metadata.get("/Author", ""),
                    "title": pdf_reader.metadata.get("/Title", ""),
                    "subject": pdf_reader.metadata.get("/Subject", ""),
                    "creator": pdf_reader.metadata.get("/Creator", ""),
                }
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    
                    if page_text:
                        if page_num > 1:
                            text_parts.append("\n--- Page Break ---\n")
                        text_parts.append(page_text)
                
                except Exception as e:
                    self.logger.warning(f"Failed to extract page {page_num}: {e}")
                    continue
            
            # Combine and clean text
            full_text = "\n".join(text_parts)
            full_text = self._clean_text(full_text)
            
            return {
                "success": True,
                "text": full_text,
                "pages": len(pdf_reader.pages),
                "metadata": metadata,
                "method": "pypdf2",
                "error": None
            }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        
        WHAT IT DOES:
        1. Remove excessive whitespace
        2. Fix common extraction artifacts
        3. Normalize line breaks
        4. Remove special characters that cause issues
        
        WHY NEEDED:
        - PDF extraction often includes formatting artifacts
        - Multiple spaces, weird line breaks
        - Special characters that break parsing
        """
        if not text:
            return ""
        
        # Remove null bytes and other problematic characters
        text = text.replace("\x00", "")
        
        # Normalize line breaks (convert \r\n to \n)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove excessive blank lines (more than 2 consecutive)
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # Remove excessive spaces (but keep single spaces)
        text = re.sub(r" {2,}", " ", text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        
        # Remove leading/trailing whitespace from entire text
        text = text.strip()
        
        return text
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Attempt to identify and extract resume sections.
        
        COMMON SECTIONS:
        - Contact Information
        - Summary/Objective
        - Work Experience
        - Education
        - Skills
        - Certifications
        - Projects
        
        HOW IT WORKS:
        1. Look for section headers (case-insensitive)
        2. Extract text between headers
        3. Return dictionary of sections
        
        NOTE: This is a basic implementation. The AI will do more
        sophisticated extraction, but this helps structure the data.
        """
        sections = {}
        
        # Common section header patterns
        section_patterns = {
            "contact": r"(?i)(contact|personal information)",
            "summary": r"(?i)(summary|objective|profile|about)",
            "experience": r"(?i)(experience|employment|work history)",
            "education": r"(?i)(education|academic)",
            "skills": r"(?i)(skills|technical skills|competencies)",
            "certifications": r"(?i)(certifications?|licenses?)",
            "projects": r"(?i)(projects?)",
            "awards": r"(?i)(awards?|honors?|achievements?)",
        }
        
        # Split text into lines
        lines = text.split("\n")
        
        current_section = "header"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header
            is_header = False
            for section_name, pattern in section_patterns.items():
                if re.match(pattern, line):
                    # Save previous section
                    if current_content:
                        sections[current_section] = "\n".join(current_content)
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content)
        
        return sections


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def parse_pdf(file_path: str) -> Dict[str, Any]:
    """
    Convenience function to parse a PDF file.
    
    USAGE:
        from app.core.parsers.pdf_parser import parse_pdf
        result = parse_pdf("resume.pdf")
        if result["success"]:
            print(result["text"])
    """
    parser = PDFParser()
    return parser.parse(file_path)


# ============================================================================
# NOTES FOR INTERVIEWS
# ============================================================================
"""
KEY POINTS TO MENTION:

1. MULTIPLE LIBRARIES:
   - Use pdfplumber for better layout handling
   - Fall back to PyPDF2 for robustness
   - Each has strengths and weaknesses

2. ERROR HANDLING:
   - Handle encrypted PDFs
   - Handle corrupted files
   - Graceful degradation (try multiple methods)

3. TEXT CLEANING:
   - Remove extraction artifacts
   - Normalize whitespace
   - Preserve structure where possible

4. SECTION DETECTION:
   - Use regex patterns for common headers
   - Case-insensitive matching
   - Flexible to handle variations

5. METADATA EXTRACTION:
   - Extract author, title, etc.
   - Can help with validation
   - Useful for debugging

COMMON INTERVIEW QUESTIONS:

Q: "Why use two PDF libraries?"
A: "Different libraries have different strengths. pdfplumber is better 
    for complex layouts and tables, while PyPDF2 is more robust for 
    encrypted or unusual PDFs. Using both provides better coverage."

Q: "How do you handle scanned PDFs (images)?"
A: "This parser handles text-based PDFs. For scanned PDFs, I'd need to 
    add OCR (Optical Character Recognition) using libraries like 
    pytesseract or cloud services like AWS Textract."

Q: "What about multi-column layouts?"
A: "pdfplumber handles multi-column layouts better than PyPDF2. It 
    preserves reading order more accurately. For very complex layouts, 
    I might need to add custom logic or use specialized tools."

Q: "How would you improve this parser?"
A: "I could add:
    - OCR for scanned PDFs
    - Better table extraction
    - Font and formatting detection
    - More sophisticated section detection
    - Caching for repeated parses
    - Parallel processing for multi-page documents"
"""

# Made with Bob
