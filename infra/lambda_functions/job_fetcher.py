"""
AWS Lambda Function: Job Fetcher

Fetches job data from external APIs and stores in DynamoDB.
"""

import json
import boto3
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
import os

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for job fetching.

    Args:
        event: Lambda event containing search parameters
        context: Lambda context

    Returns:
        Job search results
    """
    try:
        # Extract search parameters
        query = event.get("query", "software engineer")
        location = event.get("location")
        limit = event.get("limit", 20)
        user_id = event.get("user_id")

        # Fetch jobs from multiple sources
        all_jobs = []

        # Fetch from Indeed API
        indeed_jobs = fetch_indeed_jobs(query, location, limit // 2)
        all_jobs.extend(indeed_jobs)

        # Fetch from LinkedIn API
        linkedin_jobs = fetch_linkedin_jobs(query, location, limit // 2)
        all_jobs.extend(linkedin_jobs)

        # Remove duplicates
        unique_jobs = deduplicate_jobs(all_jobs)

        # Store in DynamoDB
        store_job_results(user_id, unique_jobs)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "user_id": user_id,
                    "jobs": unique_jobs,
                    "total_count": len(unique_jobs),
                    "message": "Jobs fetched successfully",
                }
            ),
        }

    except Exception as e:
        print(f"Error fetching jobs: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to fetch jobs: {str(e)}"}),
        }


def fetch_indeed_jobs(query: str, location: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch jobs from Indeed API."""
    try:
        # Indeed API parameters
        params = {
            "q": query,
            "l": location or "",
            "limit": limit,
            "fromage": 30,  # Last 30 days
            "sort": "date",
            "format": "json",
        }

        # Indeed API endpoint (this would be the actual API endpoint)
        # For demo purposes, we'll return mock data
        return get_mock_indeed_jobs(query, location, limit)

    except Exception as e:
        print(f"Error fetching Indeed jobs: {str(e)}")
        return []


def fetch_linkedin_jobs(query: str, location: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch jobs from LinkedIn API."""
    try:
        # LinkedIn API parameters
        params = {
            "keywords": query,
            "locationName": location or "",
            "count": limit,
            "start": 0,
        }

        # LinkedIn API endpoint (this would be the actual API endpoint)
        # For demo purposes, we'll return mock data
        return get_mock_linkedin_jobs(query, location, limit)

    except Exception as e:
        print(f"Error fetching LinkedIn jobs: {str(e)}")
        return []


def get_mock_indeed_jobs(query: str, location: str, limit: int) -> List[Dict[str, Any]]:
    """Get mock Indeed jobs for testing."""
    mock_jobs = [
        {
            "job_id": f"indeed_{i}",
            "title": f"Software Engineer - {query}",
            "company": f"Tech Company {i}",
            "location": location or "San Francisco, CA",
            "salary_min": 80000 + (i * 10000),
            "salary_max": 120000 + (i * 10000),
            "description": f"We are looking for a {query} to join our team...",
            "requirements": ["Python", "JavaScript", "React", "AWS"],
            "posted_date": (datetime.now() - timedelta(days=i)).isoformat(),
            "source": "indeed",
            "url": f"https://indeed.com/viewjob?jk=job{i}",
        }
        for i in range(1, limit + 1)
    ]

    return mock_jobs


def get_mock_linkedin_jobs(
    query: str, location: str, limit: int
) -> List[Dict[str, Any]]:
    """Get mock LinkedIn jobs for testing."""
    mock_jobs = [
        {
            "job_id": f"linkedin_{i}",
            "title": f"Senior {query}",
            "company": f"Startup {i}",
            "location": location or "Remote",
            "salary_min": 90000 + (i * 15000),
            "salary_max": 140000 + (i * 15000),
            "description": f"Join our fast-growing team as a {query}...",
            "requirements": ["Python", "React", "Node.js", "Docker"],
            "posted_date": (datetime.now() - timedelta(days=i)).isoformat(),
            "source": "linkedin",
            "url": f"https://linkedin.com/jobs/view/{i}",
        }
        for i in range(1, limit + 1)
    ]

    return mock_jobs


def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate jobs based on title and company."""
    seen = set()
    unique_jobs = []

    for job in jobs:
        key = (job.get("title", "").lower(), job.get("company", "").lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


def store_job_results(user_id: str, jobs: List[Dict[str, Any]]) -> None:
    """Store job search results in DynamoDB."""
    try:
        table = dynamodb.Table("careercompass-ai-job-sessions")

        # Create session ID
        session_id = f"job_search_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        table.put_item(
            Item={
                "session_id": session_id,
                "user_id": user_id,
                "jobs": jobs,
                "created_at": datetime.now().isoformat(),
                "ttl": int((datetime.now() + timedelta(days=7)).timestamp()),
            }
        )
    except Exception as e:
        print(f"Failed to store job results: {str(e)}")
        # Don't raise exception to avoid failing the entire process


def calculate_job_match_score(
    user_skills: List[str], job_requirements: List[str]
) -> float:
    """Calculate match score between user skills and job requirements."""
    if not job_requirements:
        return 0.0

    user_skills_lower = [skill.lower() for skill in user_skills]
    job_requirements_lower = [req.lower() for req in job_requirements]

    matches = len(set(user_skills_lower) & set(job_requirements_lower))
    total_requirements = len(job_requirements_lower)

    return matches / total_requirements if total_requirements > 0 else 0.0


def enrich_job_data(
    job: Dict[str, Any], user_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """Enrich job data with user-specific information."""
    try:
        # Calculate match score
        user_skills = user_profile.get("skills", [])
        job_requirements = job.get("requirements", [])
        match_score = calculate_job_match_score(user_skills, job_requirements)

        # Add enrichment data
        job["match_score"] = match_score
        job["skill_matches"] = list(
            set([skill.lower() for skill in user_skills])
            & set([req.lower() for req in job_requirements])
        )
        job["skill_gaps"] = list(
            set([req.lower() for req in job_requirements])
            - set([skill.lower() for skill in user_skills])
        )
        job["enriched_at"] = datetime.now().isoformat()

        return job

    except Exception as e:
        print(f"Error enriching job data: {str(e)}")
        return job
