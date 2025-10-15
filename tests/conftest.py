"""
Pytest configuration and fixtures for CareerCompassAI tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from datetime import datetime, date


# Test fixtures for common objects
@pytest.fixture
def mock_user_profile():
    """Mock user profile for testing."""
    return {
        "user_id": "test_user_123",
        "skills": ["Python", "React", "AWS", "Machine Learning"],
        "experience_years": 5,
        "location": "San Francisco, CA",
        "preferred_locations": ["San Francisco", "Remote"],
        "salary_min": 120000,
        "salary_max": 150000,
        "remote_preference": True,
        "target_roles": ["Senior Software Engineer", "Tech Lead"],
        "industries": ["Technology", "Fintech"],
    }


@pytest.fixture
def mock_job_posting():
    """Mock job posting for testing."""
    return {
        "job_id": "job_123",
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "remote": True,
        "salary_min": 130000,
        "salary_max": 160000,
        "description": "We're looking for a senior software engineer...",
        "requirements": ["Python", "React", "AWS", "Machine Learning"],
        "preferred_skills": ["Docker", "Kubernetes", "Leadership"],
        "work_type": "full_time",
        "experience_level": "senior",
        "posted_date": datetime.now(),
        "application_url": "https://techcorp.com/jobs/123",
    }


@pytest.fixture
def mock_company_info():
    """Mock company information for testing."""
    return {
        "company_id": "techcorp_123",
        "name": "TechCorp",
        "description": "Leading technology company",
        "website": "https://techcorp.com",
        "founded_year": "2015",
        "employee_count": "100-500",
        "location": "San Francisco, CA",
        "industry": "Technology",
        "categories": ["Software", "AI"],
        "funding_total": 50000000,
        "last_funding_date": "2023-01-01",
        "status": "Operating",
    }


@pytest.fixture
def mock_resume_data():
    """Mock resume data for testing."""
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-123-4567",
            "location": "San Francisco, CA",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "github_url": "https://github.com/johndoe",
        },
        "summary": "Experienced software engineer with 5+ years in Python and React",
        "skills": ["Python", "React", "AWS", "Machine Learning", "Docker"],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "start_date": date(2021, 1, 1),
                "end_date": None,
                "current": True,
                "description": "Led development of microservices architecture",
                "skills_used": ["Python", "React", "AWS", "Docker"],
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Computer Science",
                "field": "Computer Science",
                "school": "University of Technology",
                "location": "San Francisco, CA",
                "start_date": date(2018, 9, 1),
                "end_date": date(2022, 5, 1),
                "gpa": 3.8,
            }
        ],
        "certifications": [
            {
                "name": "AWS Solutions Architect",
                "issuer": "Amazon Web Services",
                "date_earned": date(2023, 6, 1),
                "credential_id": "AWS-SA-123456",
            }
        ],
        "languages": ["English", "Spanish"],
        "projects": [
            {
                "name": "ML Recommendation System",
                "description": "Built a machine learning recommendation system",
                "technologies": ["Python", "TensorFlow", "AWS"],
                "url": "https://github.com/johndoe/ml-recommendation",
            }
        ],
        "confidence_score": 0.85,
    }


@pytest.fixture
def mock_skill_gap_analysis():
    """Mock skill gap analysis for testing."""
    return {
        "user_id": "test_user_123",
        "target_role": "Senior Software Engineer",
        "current_skills": ["Python", "React", "AWS"],
        "required_skills": ["Python", "React", "AWS", "Leadership", "System Design"],
        "missing_skills": ["Leadership", "System Design"],
        "developing_skills": [],
        "strong_skills": ["Python", "React", "AWS"],
        "skill_priorities": [
            {
                "skill": "Leadership",
                "priority": "high",
                "type": "required",
                "estimated_time": "2-3 months",
            },
            {
                "skill": "System Design",
                "priority": "high",
                "type": "required",
                "estimated_time": "2-3 months",
            },
        ],
        "learning_path": [
            {
                "phase": "Phase 1",
                "skill": "Leadership",
                "priority": "high",
                "resources": [
                    "Online course for Leadership",
                    "Practice projects with Leadership",
                    "Community forums for Leadership",
                ],
                "timeline": "2-3 months",
                "milestones": [
                    "Complete Leadership fundamentals",
                    "Build project using Leadership",
                    "Get certified in Leadership",
                ],
            }
        ],
        "estimated_time_months": 6,
        "confidence_score": 0.6,
    }


@pytest.fixture
def mock_job_recommendation():
    """Mock job recommendation for testing."""
    return {
        "job_id": "job_123",
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "location": "San Francisco, CA",
        "match_score": {
            "overall_score": 0.85,
            "skill_score": 0.9,
            "location_score": 1.0,
            "salary_score": 0.8,
            "experience_score": 0.9,
            "skill_matches": ["Python", "React", "AWS"],
            "skill_gaps": ["Leadership"],
            "match_reasons": [
                "Strong match in skills: Python, React, AWS",
                "Remote work opportunity",
                "Salary meets expectations",
            ],
            "confidence": 0.85,
        },
        "salary_range": {"min": 130000, "max": 160000},
        "benefits": ["Health Insurance", "401k", "Stock Options"],
        "remote_friendly": True,
        "growth_potential": 0.8,
        "company_rating": 4.5,
        "recommended_at": datetime.now(),
    }


# Async test fixtures
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock API responses
@pytest.fixture
def mock_crunchbase_response():
    """Mock Crunchbase API response."""
    return {
        "entities": [
            {
                "properties": {
                    "identifier": {"value": "techcorp"},
                    "name": "TechCorp",
                    "short_description": "Leading technology company",
                    "website": {"value": "https://techcorp.com"},
                    "founded_on": {"value": "2015"},
                    "num_employees_enum": {"value": "100-500"},
                    "location_identifiers": [{"value": "San Francisco, CA"}],
                    "categories": [{"value": "Software"}, {"value": "AI"}],
                }
            }
        ]
    }


@pytest.fixture
def mock_indeed_response():
    """Mock Indeed API response."""
    return {
        "results": [
            {
                "jobkey": "indeed_123",
                "jobtitle": "Senior Software Engineer",
                "company": "TechCorp",
                "formattedLocation": "San Francisco, CA",
                "snippet": "We're looking for a senior software engineer...",
                "url": "https://indeed.com/viewjob?jk=indeed_123",
            }
        ]
    }


@pytest.fixture
def mock_linkedin_response():
    """Mock LinkedIn API response."""
    return {
        "elements": [
            {
                "id": "linkedin_123",
                "jobPosting": {
                    "title": "Senior Software Engineer",
                    "companyDetails": {"company": {"name": "TechCorp"}},
                    "formattedLocation": "San Francisco, CA",
                    "description": {
                        "text": "We're looking for a senior software engineer..."
                    },
                    "applyMethod": {"companyApplyUrl": "https://techcorp.com/jobs/123"},
                },
            }
        ]
    }


# Mock AWS services
@pytest.fixture
def mock_textract_response():
    """Mock AWS Textract response."""
    return {
        "Blocks": [
            {"BlockType": "LINE", "Text": "John Doe"},
            {"BlockType": "LINE", "Text": "Senior Software Engineer"},
            {"BlockType": "LINE", "Text": "Python, React, AWS, Machine Learning"},
        ]
    }


# Test utilities
@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for API calls."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_response
        )
        yield mock_client


@pytest.fixture
def mock_boto3_client():
    """Mock boto3 client for AWS services."""
    with patch("boto3.client") as mock_client:
        mock_textract = Mock()
        mock_textract.analyze_document.return_value = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "John Doe"},
                {"BlockType": "LINE", "Text": "Senior Software Engineer"},
            ]
        }
        mock_client.return_value = mock_textract
        yield mock_client
