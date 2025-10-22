"""
Company API Router

Provides REST API endpoints for company information retrieval.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
logger = logging.getLogger(__name__)

from ..services.company_info_fetcher.service import CompanyInfoFetcher
from ..models import CompanyInfo, CompanySearchResult

router = APIRouter()

# Initialize service
company_fetcher = CompanyInfoFetcher()


class CompanySearchRequest(BaseModel):
    """Request model for company search."""
    query: str
    limit: int = 10


class CompanySearchResponse(BaseModel):
    """Response model for company search."""
    success: bool
    companies: List[CompanySearchResult] = []
    total_count: int = 0
    error: Optional[str] = None


class CompanyInfoResponse(BaseModel):
    """Response model for company information."""
    success: bool
    company: Optional[CompanyInfo] = None
    error: Optional[str] = None


@router.get("/search", response_model=CompanySearchResponse)
async def search_companies(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Number of results")
):
    """
    Search for companies by name or description.

    Args:
        query: Search query
        limit: Number of results to return

    Returns:
        List of matching companies
    """
    try:
        logger.info(f"Searching companies: {query}")

        # Search companies using the service
        companies = company_fetcher.search_companies(query, limit)

        return CompanySearchResponse(
            success=True,
            companies=companies,
            total_count=len(companies)
        )

    except Exception as e:
        logger.error(f"Failed to search companies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search companies: {str(e)}")


@router.get("/{company_id}")
async def get_company_info(
    company_id: str,
    source: str = Query("primary", description="Data source preference")
):
    """
    Get detailed information about a specific company.

    Args:
        company_id: Company identifier
        source: Preferred data source (primary, crunchbase, linkedin, mock)

    Returns:
        Detailed company information
    """
    try:
        logger.info(f"Getting company info for: {company_id} from {source}")

        # Get company information using the service
        company_info = await company_fetcher.get_company_info(company_id, source)

        if not company_info:
            raise HTTPException(status_code=404, detail="Company not found")

        return CompanyInfoResponse(
            success=True,
            company=company_info
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get company info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company info: {str(e)}")


@router.get("/{company_id}/funding")
async def get_company_funding(company_id: str):
    """
    Get funding information for a company.

    Args:
        company_id: Company identifier

    Returns:
        Company funding rounds and information
    """
    try:
        logger.info(f"Getting funding info for: {company_id}")

        # Get company information first
        company_info = await company_fetcher.get_company_info(company_id)

        if not company_info:
            raise HTTPException(status_code=404, detail="Company not found")

        return {
            "success": True,
            "company_id": company_id,
            "funding_rounds": company_info.funding_rounds,
            "total_funding": sum(round.amount for round in company_info.funding_rounds if round.amount),
            "last_funding_date": max(round.date for round in company_info.funding_rounds) if company_info.funding_rounds else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get company funding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company funding: {str(e)}")


@router.get("/{company_id}/jobs")
async def get_company_jobs(
    company_id: str,
    limit: int = Query(10, description="Number of jobs to return")
):
    """
    Get jobs from a specific company.

    Args:
        company_id: Company identifier
        limit: Number of jobs to return

    Returns:
        List of jobs from the company
    """
    try:
        logger.info(f"Getting jobs for company: {company_id}")

        # Get company information first
        company_info = await company_fetcher.get_company_info(company_id)

        if not company_info:
            raise HTTPException(status_code=404, detail="Company not found")

        # This would typically integrate with the job service
        # For now, return company info with a note about job integration
        return {
            "success": True,
            "company_id": company_id,
            "company_name": company_info.name,
            "message": "Job integration with job service would be implemented here",
            "jobs": []  # Would be populated by job service integration
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get company jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company jobs: {str(e)}")


@router.get("/sources")
async def get_available_sources():
    """
    Get list of available data sources.

    Returns:
        List of available company data sources
    """
    try:
        sources = list(company_fetcher.adapters.keys())

        return {
            "success": True,
            "sources": sources,
            "default": "primary"
        }

    except Exception as e:
        logger.error(f"Failed to get available sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get available sources: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for company service."""
    return {"status": "healthy", "service": "company_info_fetcher"}
