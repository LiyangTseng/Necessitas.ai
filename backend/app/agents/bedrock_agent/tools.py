from strands import tool
import httpx
import json
from typing import Dict, Any, List
import logging
logger = logging.getLogger(__name__)

# API base URL - in production this would be configurable
API_BASE_URL = "http://localhost:8000/api"

async def _make_api_request(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make HTTP request to API endpoint."""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_BASE_URL}{endpoint}"

            if method.upper() == "GET":
                response = await client.get(url, params=data)
            elif method.upper() == "POST":
                response = await client.post(url, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

    except httpx.HTTPError as e:
        logger.error(f"HTTP error calling {endpoint}: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Error calling {endpoint}: {str(e)}")
        return {"success": False, "error": str(e)}


@tool
def find_job_matches(user_profile_data: dict, job_criteria: dict) -> dict:
    """Find matching jobs for a user profile."""
    try:
        # Prepare request data
        request_data = {
            "user_profile": user_profile_data,
            "job_criteria": job_criteria,
            "limit": 10,
            "min_score": 0.5
        }

        # Call API endpoint
        import asyncio
        result = asyncio.run(_make_api_request("/jobs/match", "POST", request_data))

        if result.get("success"):
            return result
        else:
            logger.error(f"Job matching failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "matches": [], "error": result.get("error")}

    except Exception as e:
        logger.error(f"Failed to find job matches: {str(e)}")
        return {"success": False, "matches": [], "error": str(e)}


@tool
def parse_resume(resume_text: str) -> dict:
    """Parse resume text and extract structured information."""
    try:
        # Prepare request data
        request_data = {"resume_text": resume_text}

        # Call API endpoint
        import asyncio
        result = asyncio.run(_make_api_request("/resume/parse/text", "POST", request_data))

        if result.get("success"):
            return result
        else:
            logger.error(f"Resume parsing failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "data": None, "error": result.get("error")}

    except Exception as e:
        logger.error(f"Failed to parse resume: {str(e)}")
        return {"success": False, "data": None, "error": str(e)}


@tool
def search_jobs(query: str, location: str = None, limit: int = 10) -> dict:
    """Search for jobs based on query and location."""
    try:
        # Prepare request data
        request_data = {
            "query": query,
            "location": location,
            "limit": limit,
            "page": 1
        }

        # Call API endpoint
        import asyncio
        result = asyncio.run(_make_api_request("/jobs/search", "POST", request_data))

        if result.get("success"):
            return result
        else:
            logger.error(f"Job search failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "jobs": [], "error": result.get("error")}

    except Exception as e:
        logger.error(f"Failed to search jobs: {str(e)}")
        return {"success": False, "jobs": [], "error": str(e)}


@tool
def get_company_info(company_name: str) -> dict:
    """Get detailed company information."""
    try:
        # Call API endpoint
        import asyncio
        result = asyncio.run(_make_api_request(f"/company/{company_name}"))

        if result.get("success"):
            return result
        else:
            logger.error(f"Company info retrieval failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "company": None, "error": result.get("error")}

    except Exception as e:
        logger.error(f"Failed to get company info: {str(e)}")
        return {"success": False, "company": None, "error": str(e)}


@tool
def analyze_skill_gap(user_profile_data: dict, target_role: str = None) -> dict:
    """Analyze skill gaps for career development."""
    try:
        # Prepare request data
        request_data = {
            "user_profile": user_profile_data,
            "target_role": target_role
        }

        # Call API endpoint
        import asyncio
        result = asyncio.run(_make_api_request("/insights/skill-gap", "POST", request_data))

        if result.get("success"):
            return result
        else:
            logger.error(f"Skill gap analysis failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get("error")}

    except Exception as e:
        logger.error(f"Failed to analyze skill gap: {str(e)}")
        return {"success": False, "error": str(e)}


@tool
def generate_career_roadmap(user_profile_data: dict, target_role: str, timeline_months: int = 12) -> dict:
    """Generate a career roadmap for reaching a target role."""
    try:
        # Prepare request data
        request_data = {
            "user_profile": user_profile_data,
            "target_role": target_role,
            "timeline_months": timeline_months
        }

        # Call API endpoint
        import asyncio
        result = asyncio.run(_make_api_request("/insights/career-roadmap", "POST", request_data))

        if result.get("success"):
            return result
        else:
            logger.error(f"Career roadmap generation failed: {result.get('error', 'Unknown error')}")
            return {"success": False, "error": result.get("error")}

    except Exception as e:
        logger.error(f"Failed to generate career roadmap: {str(e)}")
        return {"success": False, "error": str(e)}
