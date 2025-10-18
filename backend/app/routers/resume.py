"""
Resume API Router

Provides REST API endpoints for resume parsing and analysis.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

from services.resume_parser import ResumeParser, ResumeData
from models import PersonalInfo, Experience, Education, Certification

router = APIRouter()

# Initialize service
resume_parser = ResumeParser()


class ResumeParseResponse(BaseModel):
    """Response model for resume parsing."""
    success: bool
    data: Optional[ResumeData] = None
    error: Optional[str] = None
    confidence_score: Optional[float] = None


class ResumeParseRequest(BaseModel):
    """Request model for resume parsing from text."""
    resume_text: str


@router.post("/parse/file", response_model=ResumeParseResponse)
async def parse_resume_file(file: UploadFile = File(...)):
    """
    Parse resume from uploaded file.

    Args:
        file: Uploaded resume file (PDF, DOCX, etc.)

    Returns:
        Parsed resume data with confidence score
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Parse resume
            resume_data = await resume_parser.parse_resume(temp_file_path)

            return ResumeParseResponse(
                success=True,
                data=resume_data,
                confidence_score=resume_data.confidence_score
            )
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Failed to parse resume file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.post("/parse/text", response_model=ResumeParseResponse)
async def parse_resume_text(request: ResumeParseRequest):
    """
    Parse resume from text content.

    Args:
        request: Resume text content

    Returns:
        Parsed resume data with confidence score
    """
    try:
        # Create temporary file with text content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_file:
            temp_file.write(request.resume_text)
            temp_file_path = temp_file.name

        try:
            # Parse resume
            resume_data = await resume_parser.parse_resume(temp_file_path)

            return ResumeParseResponse(
                success=True,
                data=resume_data,
                confidence_score=resume_data.confidence_score
            )
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

    except Exception as e:
        logger.error(f"Failed to parse resume text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")


@router.post("/parse/url", response_model=ResumeParseResponse)
async def parse_resume_url(url: str):
    """
    Parse resume from URL (e.g., LinkedIn profile).

    Args:
        url: URL to resume or profile

    Returns:
        Parsed resume data with confidence score
    """
    try:
        # Parse resume from URL
        resume_data = await resume_parser.parse_resume_from_url(url)

        return ResumeParseResponse(
            success=True,
            data=resume_data,
            confidence_score=resume_data.confidence_score
        )

    except Exception as e:
        logger.error(f"Failed to parse resume from URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse resume from URL: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for resume service."""
    return {"status": "healthy", "service": "resume_parser"}
