"""
AWS Lambda Function: Company Researcher

Researches company information using Crunchbase and other APIs.
"""

import json
import boto3
import requests
from typing import Dict, Any, List
from datetime import datetime
import os

# Initialize AWS clients
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for company research.

    Args:
        event: Lambda event containing company information
        context: Lambda context

    Returns:
        Company research results
    """
    try:
        # Extract parameters
        company_name = event.get("company_name")
        company_id = event.get("company_id")
        user_id = event.get("user_id")

        if not company_name and not company_id:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Missing required parameters: company_name or company_id"}
                ),
            }

        # Research company information
        company_info = research_company(company_name or company_id)

        # Get company funding information
        funding_info = get_company_funding(company_name or company_id)

        # Get company job postings
        job_postings = get_company_jobs(company_name or company_id)

        # Combine all information
        research_results = {
            "company_info": company_info,
            "funding_info": funding_info,
            "job_postings": job_postings,
            "researched_at": datetime.now().isoformat(),
        }

        # Store results in DynamoDB
        store_company_research(user_id, research_results)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "user_id": user_id,
                    "company_name": company_name or company_id,
                    "research_results": research_results,
                    "message": "Company research completed successfully",
                }
            ),
        }

    except Exception as e:
        print(f"Error researching company: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to research company: {str(e)}"}),
        }


def research_company(company_identifier: str) -> Dict[str, Any]:
    """Research company information from multiple sources."""
    try:
        # For demo purposes, return mock data
        # In production, this would call Crunchbase API, LinkedIn API, etc.
        return get_mock_company_info(company_identifier)

    except Exception as e:
        print(f"Error researching company: {str(e)}")
        return {}


def get_company_funding(company_identifier: str) -> List[Dict[str, Any]]:
    """Get company funding information."""
    try:
        # For demo purposes, return mock data
        # In production, this would call Crunchbase API
        return get_mock_funding_info(company_identifier)

    except Exception as e:
        print(f"Error getting funding info: {str(e)}")
        return []


def get_company_jobs(company_identifier: str) -> List[Dict[str, Any]]:
    """Get company job postings."""
    try:
        # For demo purposes, return mock data
        # In production, this would call job APIs
        return get_mock_company_jobs(company_identifier)

    except Exception as e:
        print(f"Error getting company jobs: {str(e)}")
        return []


def get_mock_company_info(company_identifier: str) -> Dict[str, Any]:
    """Get mock company information for testing."""
    return {
        "company_id": company_identifier.lower().replace(" ", "-"),
        "name": company_identifier,
        "description": f"{company_identifier} is a leading technology company specializing in innovative solutions.",
        "website": f'https://{company_identifier.lower().replace(" ", "")}.com',
        "founded_year": "2015",
        "employee_count": "500-1000",
        "location": "San Francisco, CA",
        "industry": "Technology",
        "categories": ["Software", "Artificial Intelligence", "Cloud Computing"],
        "funding_total": 50000000,
        "last_funding_date": "2023-01-15",
        "status": "Operating",
        "social_links": {
            "linkedin": f'https://linkedin.com/company/{company_identifier.lower().replace(" ", "-")}',
            "twitter": f'https://twitter.com/{company_identifier.lower().replace(" ", "")}',
        },
        "key_people": [
            {"name": "John CEO", "title": "CEO"},
            {"name": "Jane CTO", "title": "CTO"},
        ],
        "technologies": ["Python", "React", "AWS", "Docker", "Kubernetes"],
        "company_size": "Mid-size (100-1000 employees)",
        "growth_stage": "Series B",
        "revenue_range": "$10M - $50M",
        "headquarters": "San Francisco, CA",
        "remote_policy": "Hybrid (2-3 days in office)",
        "benefits": [
            "Health Insurance",
            "Dental Insurance",
            "401k Matching",
            "Stock Options",
            "Flexible PTO",
            "Remote Work",
        ],
    }


def get_mock_funding_info(company_identifier: str) -> List[Dict[str, Any]]:
    """Get mock funding information for testing."""
    return [
        {
            "round_name": "Series B",
            "announced_date": "2023-01-15",
            "money_raised": 25000000,
            "money_raised_currency": "USD",
            "investors": ["VC Fund A", "VC Fund B", "Strategic Investor C"],
            "round_type": "Series B",
            "valuation": 200000000,
        },
        {
            "round_name": "Series A",
            "announced_date": "2021-06-01",
            "money_raised": 10000000,
            "money_raised_currency": "USD",
            "investors": ["VC Fund D", "Angel Investor E"],
            "round_type": "Series A",
            "valuation": 50000000,
        },
        {
            "round_name": "Seed Round",
            "announced_date": "2020-01-01",
            "money_raised": 2000000,
            "money_raised_currency": "USD",
            "investors": ["Seed Fund F"],
            "round_type": "Seed",
            "valuation": 10000000,
        },
    ]


def get_mock_company_jobs(company_identifier: str) -> List[Dict[str, Any]]:
    """Get mock company job postings for testing."""
    return [
        {
            "job_id": f"{company_identifier.lower()}_job_1",
            "title": "Senior Software Engineer",
            "location": "San Francisco, CA",
            "remote": True,
            "salary_min": 130000,
            "salary_max": 160000,
            "description": f"Join {company_identifier} as a Senior Software Engineer...",
            "requirements": ["Python", "React", "AWS", "Machine Learning"],
            "posted_date": datetime.now().isoformat(),
            "job_type": "Full-time",
            "experience_level": "Senior",
            "department": "Engineering",
        },
        {
            "job_id": f"{company_identifier.lower()}_job_2",
            "title": "Product Manager",
            "location": "San Francisco, CA",
            "remote": False,
            "salary_min": 120000,
            "salary_max": 150000,
            "description": f"Lead product development at {company_identifier}...",
            "requirements": ["Product Management", "Agile", "Analytics", "Leadership"],
            "posted_date": datetime.now().isoformat(),
            "job_type": "Full-time",
            "experience_level": "Mid-level",
            "department": "Product",
        },
        {
            "job_id": f"{company_identifier.lower()}_job_3",
            "title": "Data Scientist",
            "location": "Remote",
            "remote": True,
            "salary_min": 110000,
            "salary_max": 140000,
            "description": f"Build ML models at {company_identifier}...",
            "requirements": ["Python", "Machine Learning", "TensorFlow", "Statistics"],
            "posted_date": datetime.now().isoformat(),
            "job_type": "Full-time",
            "experience_level": "Mid-level",
            "department": "Data Science",
        },
    ]


def store_company_research(user_id: str, research_results: Dict[str, Any]) -> None:
    """Store company research results in DynamoDB."""
    try:
        table = dynamodb.Table("careercompass-ai-job-sessions")

        # Create session ID
        session_id = (
            f"company_research_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        table.put_item(
            Item={
                "session_id": session_id,
                "user_id": user_id,
                "research_type": "company_research",
                "research_results": research_results,
                "created_at": datetime.now().isoformat(),
                "ttl": int((datetime.now() + timedelta(days=7)).timestamp()),
            }
        )
    except Exception as e:
        print(f"Failed to store company research: {str(e)}")
        # Don't raise exception to avoid failing the entire process


def analyze_company_culture(company_info: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze company culture based on available information."""
    try:
        culture_analysis = {
            "work_environment": (
                "Hybrid" if company_info.get("remote_policy") else "On-site"
            ),
            "company_stage": company_info.get("growth_stage", "Unknown"),
            "benefits_score": len(company_info.get("benefits", [])) / 10.0,
            "technology_focus": company_info.get("technologies", []),
            "company_size_category": company_info.get("company_size", "Unknown"),
            "funding_stability": (
                "High" if company_info.get("funding_total", 0) > 10000000 else "Medium"
            ),
            "growth_potential": (
                "High"
                if company_info.get("growth_stage") in ["Series A", "Series B"]
                else "Medium"
            ),
        }

        return culture_analysis

    except Exception as e:
        print(f"Error analyzing company culture: {str(e)}")
        return {}


def calculate_company_match_score(
    user_preferences: Dict[str, Any], company_info: Dict[str, Any]
) -> float:
    """Calculate how well a company matches user preferences."""
    try:
        score = 0.0
        total_factors = 0

        # Location match
        if user_preferences.get("location_preference") == "remote" and company_info.get(
            "remote_policy"
        ):
            score += 1.0
        total_factors += 1

        # Company size match
        if user_preferences.get("company_size_preference"):
            if user_preferences["company_size_preference"] in company_info.get(
                "company_size", ""
            ):
                score += 1.0
        total_factors += 1

        # Industry match
        if user_preferences.get("target_industries"):
            user_industries = [
                ind.lower() for ind in user_preferences["target_industries"]
            ]
            company_industry = company_info.get("industry", "").lower()
            if any(ind in company_industry for ind in user_industries):
                score += 1.0
        total_factors += 1

        # Technology match
        if user_preferences.get("skills"):
            user_skills = [skill.lower() for skill in user_preferences["skills"]]
            company_technologies = [
                tech.lower() for tech in company_info.get("technologies", [])
            ]
            matching_technologies = len(set(user_skills) & set(company_technologies))
            if matching_technologies > 0:
                score += min(matching_technologies / len(company_technologies), 1.0)
        total_factors += 1

        return score / total_factors if total_factors > 0 else 0.0

    except Exception as e:
        print(f"Error calculating company match score: {str(e)}")
        return 0.0
