"""
Jobs API Router

Provides REST API endpoints for job search and matching.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
logger = logging.getLogger(__name__)

from services.job_fetcher.service import JobFetcher
from services.job_matching_engine import JobMatchingEngine
from models import JobPosting, JobSearchResult, UserProfile, MatchAnalysis

router = APIRouter()

# Initialize services
job_fetcher = JobFetcher()
job_matcher = JobMatchingEngine()


class JobSearchRequest(BaseModel):
    """Request model for job search."""
    query: str
    location: Optional[str] = None
    limit: int = 20
    page: int = 1


class JobSearchResponse(BaseModel):
    """Response model for job search."""
    success: bool
    jobs: List[JobPosting] = []
    total_count: int = 0
    page: int = 1
    limit: int = 20
    error: Optional[str] = None


class JobMatchRequest(BaseModel):
    """Request model for job matching."""
    user_profile: Dict[str, Any]  # UserProfile as dict
    job_criteria: Dict[str, Any] = {}
    limit: int = 10
    min_score: float = 0.5


class JobMatchResponse(BaseModel):
    """Response model for job matching."""
    success: bool
    matches: List[Dict[str, Any]] = []  # List of (job, match_analysis) pairs
    total_count: int = 0
    error: Optional[str] = None


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
    Find job matches for a user profile.

    Args:
        request: User profile and matching criteria

    Returns:
        List of job matches with analysis
    """
    try:
        # Convert dict to UserProfile object
        user_profile = UserProfile(**request.user_profile)

        # Get available jobs (this would typically come from a job database)
        # For now, we'll search for jobs first
        available_jobs = job_fetcher.search_jobs(
            query=request.job_criteria.get("query", "software engineer"),
            location=request.job_criteria.get("location"),
            limit=50  # Get more jobs for matching
        )

        # Find matches using the matching engine
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

    except Exception as e:
        logger.error(f"Failed to match jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to match jobs: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for jobs service."""
    return {"status": "healthy", "service": "job_fetcher"}
