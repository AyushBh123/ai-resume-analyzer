"""
============================================================================
FILE UPLOAD ROUTES
============================================================================
Handle resume file uploads.

WHAT THESE DO:
- Accept file uploads (PDF, DOCX)
- Validate file type and size
- Save files temporarily
- Return file information

WHY NEEDED:
- Users need to upload resumes
- Validation prevents issues
- Temporary storage for processing
============================================================================
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import logging
import os
import uuid
from pathlib import Path

from app.config import get_settings
from app.core.parsers import is_supported_format

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Upload a resume file.
    
    PARAMETERS:
        file: Resume file (PDF or DOCX)
    
    RETURNS:
        File information including ID and path
    
    RAISES:
        HTTPException: If file is invalid
    
    EXAMPLE:
        POST /api/v1/upload
        Content-Type: multipart/form-data
        
        file: resume.pdf
        
        Response:
        {
            "success": true,
            "file_id": "abc123...",
            "filename": "resume.pdf",
            "size": 102400,
            "content_type": "application/pdf"
        }
    """
    settings = get_settings()
    
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = Path(file.filename).suffix.lower()
    if not is_supported_format(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. "
                   f"Supported: {', '.join(settings.allowed_extensions_list)}"
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large: {file_size / 1024 / 1024:.2f}MB. "
                   f"Maximum: {settings.max_file_size_mb}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Save file
    upload_dir = settings.upload_path
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{file_id}{file_ext}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Uploaded file: {file.filename} ({file_size} bytes) -> {file_id}")
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "size": file_size,
            "content_type": file.content_type,
            "path": str(file_path)
        }
    
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")


@router.delete("/upload/{file_id}")
async def delete_uploaded_file(file_id: str) -> Dict[str, Any]:
    """
    Delete an uploaded file.
    
    PARAMETERS:
        file_id: File ID from upload response
    
    RETURNS:
        Success status
    
    EXAMPLE:
        DELETE /api/v1/upload/abc123...
        
        Response:
        {
            "success": true,
            "message": "File deleted"
        }
    """
    settings = get_settings()
    upload_dir = settings.upload_path
    
    # Find file with this ID (any extension)
    deleted = False
    for ext in settings.allowed_extensions_list:
        file_path = upload_dir / f"{file_id}.{ext}"
        if file_path.exists():
            try:
                os.remove(file_path)
                deleted = True
                logger.info(f"Deleted file: {file_id}")
                break
            except Exception as e:
                logger.error(f"Failed to delete file {file_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to delete file")
    
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "success": True,
        "message": "File deleted"
    }

# Made with Bob
