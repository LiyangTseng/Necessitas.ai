"""
Job Recommendations Router

Handles job search, matching, and recommendations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.job_fetcher import JobFetcher
from app.services.company_info_fetcher import CompanyInfoFetcher
from app.services.job_recommender import JobRecommender

router = APIRouter()


@router.get("/recommendations")
async def get_job_recommendations(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(10, description="Number of recommendations"),
    location: Optional[str] = Query(None, description="Job location filter"),
    industry: Optional[str] = Query(None, description="Industry filter"),
) -> Dict[str, Any]:
    """
    Get personalized job recommendations for a user.

    Args:
        user_id: User ID
        limit: Number of recommendations to return
        location: Optional location filter
        industry: Optional industry filter

    Returns:
        Job recommendations with matching scores
    """
    try:
        # Initialize job recommender
        job_recommender = JobRecommender()

        # Get job recommendations
        recommendations = await job_recommender.get_recommendations(
            user_id=user_id, limit=limit, location=location, industry=industry
        )

        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "filters": {"location": location, "industry": industry},
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/search")
async def search_jobs(
    query: str = Query(..., description="Search query"),
    location: Optional[str] = Query(None, description="Job location"),
    limit: int = Query(20, description="Number of results"),
    page: int = Query(1, description="Page number"),
) -> Dict[str, Any]:
    """
    Search for jobs across multiple platforms.

    Args:
        query: Search query
        location: Optional location filter
        limit: Number of results per page
        page: Page number

    Returns:
        Search results from multiple job platforms
    """
    try:
        # Initialize job fetcher
        job_fetcher = JobFetcher()

        # Search jobs
        search_results = await job_fetcher.search_jobs(
            query=query, location=location, limit=limit, page=page
        )

        return {
            "query": query,
            "results": search_results,
            "total_count": len(search_results),
            "page": page,
            "limit": limit,
            "searched_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")


@router.get("/company/{company_id}")
async def get_company_info(company_id: str) -> Dict[str, Any]:
    """
    Get detailed company information.

    Args:
        company_id: Company identifier

    Returns:
        Company information and insights
    """
    try:
        # Initialize company info fetcher
        company_fetcher = CompanyInfoFetcher()

        # Get company information
        company_info = await company_fetcher.get_company_info(company_id)

        return {
            "company_id": company_id,
            "company_info": company_info,
            "retrieved_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get company info: {str(e)}"
        )


@router.get("/salary-insights")
async def get_salary_insights(
    job_title: str = Query(..., description="Job title"),
    location: Optional[str] = Query(None, description="Location"),
    experience_level: Optional[str] = Query(None, description="Experience level"),
) -> Dict[str, Any]:
    """
    Get salary insights for a specific role.

    Args:
        job_title: Job title
        location: Optional location
        experience_level: Optional experience level

    Returns:
        Salary insights and market data
    """
    try:
        # This would typically fetch from salary databases
        # For now, return mock data
        return {
            "job_title": job_title,
            "location": location,
            "experience_level": experience_level,
            "salary_data": {
                "min_salary": 80000,
                "max_salary": 120000,
                "median_salary": 95000,
                "percentile_25": 85000,
                "percentile_75": 110000,
                "currency": "USD",
            },
            "market_insights": [
                "Salary range is competitive for the role",
                "Remote positions typically offer 10-15% higher salaries",
                "Senior level positions show 20% salary growth",
            ],
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get salary insights: {str(e)}"
        )


@router.post("/apply")
async def apply_to_job(
    job_id: str, user_id: str, cover_letter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply to a job position.

    Args:
        job_id: Job ID
        user_id: User ID
        cover_letter: Optional cover letter

    Returns:
        Application status
    """
    try:
        # This would typically handle job application
        # For now, return mock response
        return {
            "job_id": job_id,
            "user_id": user_id,
            "status": "applied",
            "application_id": f"app_{job_id}_{user_id}",
            "applied_at": datetime.now().isoformat(),
            "message": "Application submitted successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job application failed: {str(e)}")
