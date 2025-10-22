"""
Jobs API Router

Provides REST API endpoints for job search and matching.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
import logging
logger = logging.getLogger(__name__)

from services.job_fetcher import JobFetcher
from services.job_matching_engine import JobMatchingEngine
from models import (
    JobSearchResponse,
    JobSearchRequest,
    JobMatchResponse,
    JobMatchRequest,
    UserProfile,
    MatchAnalysis,
    CareerPreference
)

router = APIRouter()

job_fetcher = JobFetcher()
job_matcher = JobMatchingEngine()

@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    """
    Search for jobs based on query and location.

    Args:
        request: Job search parameters

    Returns:
        List of matching job postings
    """
    try:
        logger.info(f"Searching jobs: {request.query} in {request.location or 'all locations'}")

        # Search jobs using the service
        jobs = job_fetcher.search_jobs(
            query=request.query,
            location=request.location,
            limit=request.limit,
            page=request.page
        )

        return JobSearchResponse(
            success=True,
            jobs=jobs,
            total_count=len(jobs),
            page=request.page,
            limit=request.limit
        )

    except Exception as e:
        logger.error(f"Failed to search jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search jobs: {str(e)}")


@router.get("/search", response_model=JobSearchResponse)
async def search_jobs_get(
    query: str = Query(..., description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    limit: int = Query(20, description="Number of results"),
    page: int = Query(1, description="Page number")
):
    """
    Search for jobs using GET method.

    Args:
        query: Search query
        location: Optional location filter
        limit: Number of results
        page: Page number

    Returns:
        List of matching job postings
    """
    try:
        logger.info(f"Searching jobs: {query} in {location or 'all locations'}")

        # Search jobs using the service
        jobs = job_fetcher.search_jobs(
            query=query,
            location=location,
            limit=limit,
            page=page
        )

        return JobSearchResponse(
            success=True,
            jobs=jobs,
            total_count=len(jobs),
            page=page,
            limit=limit
        )

    except Exception as e:
        logger.error(f"Failed to search jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search jobs: {str(e)}")


@router.get("/{job_id}")
async def get_job_details(job_id: str):
    """
    Get detailed information about a specific job.

    Args:
        job_id: Job identifier

    Returns:
        Detailed job information
    """
    try:
        job = job_fetcher.get_job_details(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"success": True, "job": job}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get job details: {str(e)}")


@router.get("/company/{company_name}")
async def get_company_jobs(
    company_name: str,
    limit: int = Query(10, description="Number of jobs to return")
):
    """
    Get jobs from a specific company.

    Args:
        company_name: Name of the company
        limit: Number of jobs to return

    Returns:
        List of jobs from the company
    """
    try:
        jobs = job_fetcher.get_company_jobs(company_name, limit)

        return {
            "success": True,
            "company": company_name,
            "jobs": jobs,
            "count": len(jobs)
        }

    except Exception as e:
        logger.error(f"Failed to get company jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company jobs: {str(e)}")


@router.post("/match", response_model=JobMatchResponse)
async def match_jobs(request: JobMatchRequest):
    """
    Find job matches for a user profile using resume as a filtering mechanism.

    Args:
        request: User profile and matching criteria

    Returns:
        List of job matches with analysis
    """
    try:
        # Convert dict to UserProfile object, filtering out extra fields
        user_profile_data = request.user_profile.copy()

        # Extract only the fields that UserProfile expects
        user_profile_fields = {
            'user_id': user_profile_data.get('user_id', 'temp_user'),
            'personal_info': user_profile_data.get('personal_info', {}),
            'skills': user_profile_data.get('skills', []),
            'experience': user_profile_data.get('experience', []),
            'education': user_profile_data.get('education', []),
            'certifications': user_profile_data.get('certifications', []),
        }

        # Create CareerPreference object from dict
        preferences_data = user_profile_data.get('preferences', {})
        preferences = CareerPreference(**preferences_data)
        user_profile_fields['preferences'] = preferences

        user_profile = UserProfile(**user_profile_fields)

        # Extract job search criteria from request
        job_criteria = request.job_criteria or {}
        query = job_criteria.get("query", "")
        location = job_criteria.get("location")
        search_limit = job_criteria.get("limit", 50)

        # Debug logging
        logger.info(f"Job match request - job_criteria: {job_criteria}")
        logger.info(f"Job match request - query: '{query}'")
        print(user_profile)

        # If no query in job_criteria, try to use a default based on user profile
        if not query:
            # Try to extract a default query from user profile skills
            user_skills = [skill.get('name', '') for skill in user_profile_data.get('skills', [])]
            if user_skills:
                query = f"{user_skills[0]} developer"  # Use first skill as default
                logger.info(f"Using default query based on skills: '{query}'")
            else:
                query = "software engineer"  # Fallback default
                logger.info(f"Using fallback default query: '{query}'")

        # Search for jobs using the provided criteria
        available_jobs = job_fetcher.search_jobs(
            query=query,
            location=location,
            limit=search_limit
        )

        if not available_jobs:
            return JobMatchResponse(
                success=True,
                matches=[],
                total_count=0
            )

        # Find matches using the matching engine - this acts as a filtering mechanism
        # The resume/profile is used to filter and score the job search results
        matches = job_matcher.find_matches(
            user_profile=user_profile,
            job_postings=available_jobs,
            limit=request.limit,
            min_score=request.min_score
        )

        # Convert matches to serializable format
        match_results = []
        for job, match_analysis in matches:
            match_results.append({
                "job": job.dict() if hasattr(job, 'dict') else job,
                "match_analysis": match_analysis.dict() if hasattr(match_analysis, 'dict') else match_analysis,
                "score": match_analysis.overall_score
            })

        return JobMatchResponse(
            success=True,
            matches=match_results,
            total_count=len(match_results)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to match jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to match jobs: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for jobs service."""
    return {"status": "healthy", "service": "job_fetcher"}
