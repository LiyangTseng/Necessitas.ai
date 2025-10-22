"""
Coursera API Router

Provides REST API endpoints for Coursera courses and certifications.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging

from ..services.coursera_service import CourseraService
from ..models.coursera import (
    CourseSearchRequest, CourseSearchResponse,
    CertificationSearchRequest, CertificationSearchResponse,
    LearningRecommendation, LearningPath
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize service
coursera_service = CourseraService()


@router.post("/courses/search", response_model=CourseSearchResponse)
async def search_courses(request: CourseSearchRequest):
    """
    Search for Coursera courses.

    Args:
        request: Course search parameters

    Returns:
        List of matching courses
    """
    try:
        logger.info(f"Searching courses: {request.query or 'all'} with skills: {request.skills}")
        
        response = await coursera_service.search_courses(request)
        return response

    except Exception as e:
        logger.error(f"Failed to search courses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search courses: {str(e)}")


@router.get("/courses/search", response_model=CourseSearchResponse)
async def search_courses_get(
    query: Optional[str] = Query(None, description="Search query"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    level: Optional[str] = Query(None, description="Course level (beginner, intermediate, advanced)"),
    course_type: Optional[str] = Query(None, description="Course type (course, specialization, etc.)"),
    language: Optional[str] = Query(None, description="Language code (en, es, fr, etc.)"),
    is_free: Optional[bool] = Query(None, description="Filter free courses"),
    institution: Optional[str] = Query(None, description="Institution filter"),
    limit: int = Query(10, description="Number of results", ge=1, le=50)
):
    """
    Search for Coursera courses using GET method.

    Args:
        query: Search query
        skills: Comma-separated skills
        level: Course level filter
        course_type: Course type filter
        language: Language filter
        is_free: Free courses filter
        institution: Institution filter
        limit: Number of results

    Returns:
        List of matching courses
    """
    try:
        # Parse skills from comma-separated string
        skills_list = []
        if skills:
            skills_list = [skill.strip() for skill in skills.split(",")]

        request = CourseSearchRequest(
            query=query,
            skills=skills_list,
            level=level,
            course_type=course_type,
            language=language,
            is_free=is_free,
            institution=institution,
            limit=limit
        )

        logger.info(f"Searching courses: {query or 'all'} with skills: {skills_list}")
        
        response = await coursera_service.search_courses(request)
        return response

    except Exception as e:
        logger.error(f"Failed to search courses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search courses: {str(e)}")


@router.post("/certifications/search", response_model=CertificationSearchResponse)
async def search_certifications(request: CertificationSearchRequest):
    """
    Search for Coursera certifications.

    Args:
        request: Certification search parameters

    Returns:
        List of matching certifications
    """
    try:
        logger.info(f"Searching certifications: {request.query or 'all'} with skills: {request.skills}")
        
        response = await coursera_service.search_certifications(request)
        return response

    except Exception as e:
        logger.error(f"Failed to search certifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search certifications: {str(e)}")


@router.get("/certifications/search", response_model=CertificationSearchResponse)
async def search_certifications_get(
    query: Optional[str] = Query(None, description="Search query"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    course_type: Optional[str] = Query(None, description="Course type (professional_certificate, etc.)"),
    language: Optional[str] = Query(None, description="Language code (en, es, fr, etc.)"),
    is_free: Optional[bool] = Query(None, description="Filter free certifications"),
    institution: Optional[str] = Query(None, description="Institution filter"),
    industry_recognition: Optional[bool] = Query(None, description="Industry recognition filter"),
    limit: int = Query(10, description="Number of results", ge=1, le=50)
):
    """
    Search for Coursera certifications using GET method.

    Args:
        query: Search query
        skills: Comma-separated skills
        course_type: Course type filter
        language: Language filter
        is_free: Free certifications filter
        institution: Institution filter
        industry_recognition: Industry recognition filter
        limit: Number of results

    Returns:
        List of matching certifications
    """
    try:
        # Parse skills from comma-separated string
        skills_list = []
        if skills:
            skills_list = [skill.strip() for skill in skills.split(",")]

        request = CertificationSearchRequest(
            query=query,
            skills=skills_list,
            course_type=course_type,
            language=language,
            is_free=is_free,
            institution=institution,
            industry_recognition=industry_recognition,
            limit=limit
        )

        logger.info(f"Searching certifications: {query or 'all'} with skills: {skills_list}")
        
        response = await coursera_service.search_certifications(request)
        return response

    except Exception as e:
        logger.error(f"Failed to search certifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search certifications: {str(e)}")


@router.get("/recommendations/{user_id}")
async def get_learning_recommendations(
    user_id: str,
    skill_gaps: Optional[str] = Query(None, description="Comma-separated skill gaps"),
    target_role: Optional[str] = Query(None, description="Target role for recommendations")
):
    """
    Get personalized learning recommendations for a user.

    Args:
        user_id: User identifier
        skill_gaps: Comma-separated list of skills the user needs to develop
        target_role: Optional target role

    Returns:
        Learning recommendations with courses and certifications
    """
    try:
        # Parse skill gaps from comma-separated string
        skill_gaps_list = []
        if skill_gaps:
            skill_gaps_list = [skill.strip() for skill in skill_gaps.split(",")]

        if not skill_gaps_list:
            raise HTTPException(
                status_code=400, 
                detail="skill_gaps parameter is required"
            )

        logger.info(f"Getting learning recommendations for user {user_id} with skill gaps: {skill_gaps_list}")
        
        recommendations = await coursera_service.get_learning_recommendations(
            user_id=user_id,
            skill_gaps=skill_gaps_list,
            target_role=target_role
        )
        
        return {
            "success": True,
            "recommendations": recommendations
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get learning recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get learning recommendations: {str(e)}")


@router.post("/recommendations/{user_id}")
async def get_learning_recommendations_post(
    user_id: str,
    request: Dict[str, Any]
):
    """
    Get personalized learning recommendations for a user using POST method.

    Args:
        user_id: User identifier
        request: Request body with skill_gaps and optional target_role

    Returns:
        Learning recommendations with courses and certifications
    """
    try:
        skill_gaps = request.get("skill_gaps", [])
        target_role = request.get("target_role")

        if not skill_gaps:
            raise HTTPException(
                status_code=400, 
                detail="skill_gaps is required in request body"
            )

        logger.info(f"Getting learning recommendations for user {user_id} with skill gaps: {skill_gaps}")
        
        recommendations = await coursera_service.get_learning_recommendations(
            user_id=user_id,
            skill_gaps=skill_gaps,
            target_role=target_role
        )
        
        return {
            "success": True,
            "recommendations": recommendations
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get learning recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get learning recommendations: {str(e)}")


@router.get("/courses/{course_id}")
async def get_course_details(course_id: str):
    """
    Get detailed information about a specific course.

    Args:
        course_id: Course identifier

    Returns:
        Detailed course information
    """
    try:
        # For now, return a placeholder response
        # In a real implementation, this would fetch from the API
        return {
            "success": True,
            "message": "Course details endpoint not yet implemented",
            "course_id": course_id
        }

    except Exception as e:
        logger.error(f"Failed to get course details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get course details: {str(e)}")


@router.get("/certifications/{certification_id}")
async def get_certification_details(certification_id: str):
    """
    Get detailed information about a specific certification.

    Args:
        certification_id: Certification identifier

    Returns:
        Detailed certification information
    """
    try:
        # For now, return a placeholder response
        # In a real implementation, this would fetch from the API
        return {
            "success": True,
            "message": "Certification details endpoint not yet implemented",
            "certification_id": certification_id
        }

    except Exception as e:
        logger.error(f"Failed to get certification details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get certification details: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for Coursera service."""
    return {
        "status": "healthy", 
        "service": "coursera",
        "api_available": coursera_service.is_available
    }
