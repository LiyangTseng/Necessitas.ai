"""
Resume Processing Router

Handles resume upload, parsing, and analysis.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uuid
from datetime import datetime

from app.services.resume_parser import ResumeParser
from backend.app.agents.resume_analyzer.resume_analyzer import ResumeAnalyzer
from app.models.user_profile import UserProfile

router = APIRouter()


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), user_id: str = None
) -> Dict[str, Any]:
    """
    Upload and process a resume.

    Args:
        file: Resume file (PDF, DOCX, or TXT)
        user_id: Optional user ID for tracking

    Returns:
        Processing results and extracted information
    """
    try:
        # Validate file type
        if not file.content_type in [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Generate session ID if not provided
        if not user_id:
            user_id = str(uuid.uuid4())

        # Initialize resume parser
        parser = ResumeParser()

        # Save file temporarily
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file.filename.split('.')[-1]}"
        ) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Parse resume content
            resume_data = await parser.parse_resume(temp_path)
        finally:
            # Clean up temporary file
            os.unlink(temp_path)

        # Create user profile from parsed resume data
        user_profile = UserProfile(
            user_id=user_id,
            skills=resume_data.skills,
            experience=[exp.__dict__ for exp in resume_data.experience],
            education=[edu.__dict__ for edu in resume_data.education],
            preferences={
                "target_roles": [],
                "industries": [],
                "location": resume_data.personal_info.location,
                "salary_range": "",
            },
            created_at=datetime.now(),
        )

        return {
            "user_id": user_id,
            "status": "success",
            "resume_data": {
                "personal_info": resume_data.personal_info.__dict__,
                "summary": resume_data.summary,
                "skills": resume_data.skills,
                "experience": [exp.__dict__ for exp in resume_data.experience],
                "education": [edu.__dict__ for edu in resume_data.education],
                "certifications": [
                    cert.__dict__ for cert in resume_data.certifications
                ],
                "languages": resume_data.languages,
                "projects": resume_data.projects,
                "confidence_score": resume_data.confidence_score,
            },
            "user_profile": user_profile.dict(),
            "message": "Resume processed successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Resume processing failed: {str(e)}"
        )


@router.get("/analysis/{user_id}")
async def get_resume_analysis(user_id: str) -> Dict[str, Any]:
    """
    Get resume analysis results for a user.

    Args:
        user_id: User ID

    Returns:
        Analysis results
    """
    try:
        # This would typically fetch from database
        # For now, return mock data
        return {
            "user_id": user_id,
            "skills": ["Python", "FastAPI", "AWS", "Machine Learning"],
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2 years",
                    "description": "Developed web applications using Python and FastAPI",
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "University of Technology",
                    "year": "2022",
                }
            ],
            "preferences": {
                "target_roles": ["Senior Software Engineer", "Tech Lead"],
                "industries": ["Technology", "Fintech"],
                "location": "Remote",
                "salary_range": "$80,000 - $120,000",
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")


@router.post("/analyze-linkedin")
async def analyze_linkedin_profile(
    linkedin_url: str, user_id: str = None
) -> Dict[str, Any]:
    """
    Analyze LinkedIn profile.

    Args:
        linkedin_url: LinkedIn profile URL
        user_id: Optional user ID

    Returns:
        Analysis results
    """
    try:
        if not user_id:
            user_id = str(uuid.uuid4())

        # Initialize resume parser
        parser = ResumeParser()

        # Parse LinkedIn profile
        resume_data = await parser.parse_resume_from_url(linkedin_url)

        # Create user profile from parsed data
        user_profile = UserProfile(
            user_id=user_id,
            skills=resume_data.skills,
            experience=[exp.__dict__ for exp in resume_data.experience],
            education=[edu.__dict__ for edu in resume_data.education],
            preferences={
                "target_roles": [],
                "industries": [],
                "location": resume_data.personal_info.location,
                "salary_range": "",
            },
            created_at=datetime.now(),
        )

        return {
            "user_id": user_id,
            "linkedin_url": linkedin_url,
            "status": "success",
            "resume_data": {
                "personal_info": resume_data.personal_info.__dict__,
                "summary": resume_data.summary,
                "skills": resume_data.skills,
                "experience": [exp.__dict__ for exp in resume_data.experience],
                "education": [edu.__dict__ for edu in resume_data.education],
                "certifications": [
                    cert.__dict__ for cert in resume_data.certifications
                ],
                "languages": resume_data.languages,
                "projects": resume_data.projects,
                "confidence_score": resume_data.confidence_score,
            },
            "user_profile": user_profile.dict(),
            "message": "LinkedIn profile analyzed successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"LinkedIn analysis failed: {str(e)}"
        )
