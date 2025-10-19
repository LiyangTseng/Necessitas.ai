"""
Tools for Test Agent
Provides tools to search jobs, parse resumes, analyze skills, and generate learning paths.
"""

from strands import tool
import sys
import os
from typing import Dict, Any, List, Optional
import logging
import httpx
from functools import wraps

logger = logging.getLogger(__name__)

# Global variable to track current agent (will be set by test_agent.py)
_current_agent = None

def set_current_agent(agent_name: str):
    """Set the current agent name for tracking."""
    global _current_agent
    _current_agent = agent_name

def track_tool_call(func):
    """Decorator to track tool calls."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        agent_name = _current_agent or "Unknown"

        # Import tool_tracker here to avoid circular import
        from test_agent import tool_tracker

        # Record the call in the tracker
        tool_tracker.record_call(agent_name, tool_name)

        # Log the call
        logger.info(f"[{agent_name}] Calling tool: {tool_name}")
        print(f"   🔧 [{agent_name}] → {tool_name}()")

        # Execute the tool
        result = func(*args, **kwargs)

        # Log the result
        success = result.get("success", False) if isinstance(result, dict) else True
        status = "✓" if success else "✗"
        print(f"      {status} {tool_name} completed")

        return result

    return wrapper

# API base URL - tools will call FastAPI endpoints instead of importing services
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

# Helper function to make API requests
async def _make_api_request(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Make HTTP request to API endpoint."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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
@track_tool_call
def search_jobs(query: str, location: str = None, limit: int = 10) -> Dict[str, Any]:
    """
    Search for jobs using Adzuna API based on query and location.

    Args:
        query: Job search keywords (e.g., "software engineer", "data scientist")
        location: Optional location filter (e.g., "San Francisco", "New York")
        limit: Maximum number of jobs to return (default: 10)

    Returns:
        Dictionary with success status and list of job postings

    Example:
        search_jobs("python developer", "San Francisco", 5)
    """
    try:
        logger.info(f"Searching jobs: {query} in {location or 'all locations'}")

        # Call FastAPI endpoint
        import asyncio
        result = asyncio.run(_make_api_request(
            "/jobs/search",
            "POST",
            {
                "query": query,
                "location": location,
                "limit": limit,
                "page": 1
            }
        ))

        if result.get("success"):
            return {
                "success": True,
                "jobs": result.get("jobs", []),
                "count": result.get("total_count", 0),
                "query": query,
                "location": location
            }
        else:
            logger.error(f"Job search failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "jobs": [],
                "count": 0
            }

    except Exception as e:
        logger.error(f"Failed to search jobs: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "jobs": [],
            "count": 0
        }


@tool
@track_tool_call
def parse_resume_text(resume_text: str) -> Dict[str, Any]:
    """
    Parse resume text and extract structured information including skills, experience, and education.

    Args:
        resume_text: Raw text content of the resume

    Returns:
        Dictionary with parsed resume data including personal info, skills, experience, education

    Example:
        parse_resume_text("John Doe\\nSoftware Engineer\\nSkills: Python, React...")
    """
    try:
        logger.info("Parsing resume text")

        # Call FastAPI endpoint
        import asyncio
        result = asyncio.run(_make_api_request(
            "/resume/parse/text",
            "POST",
            {"resume_text": resume_text}
        ))

        if result.get("success"):
            return result
        else:
            logger.error(f"Resume parsing failed: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "data": None
            }

    except Exception as e:
        logger.error(f"Failed to parse resume: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }


@tool
@track_tool_call
def analyze_skill_gap(user_skills: List[str], target_role: str) -> Dict[str, Any]:
    """
    Analyze skill gaps between user's current skills and target role requirements.

    Args:
        user_skills: List of user's current skills (e.g., ["Python", "JavaScript", "React"])
        target_role: Target job role (e.g., "Senior Software Engineer", "Data Scientist")

    Returns:
        Dictionary with skill gap analysis including missing skills and recommendations

    Example:
        analyze_skill_gap(["Python", "Django"], "Full Stack Developer")
    """
    try:
        logger.info(f"Analyzing skill gap for target role: {target_role}")

        # Define common role requirements (in production, this would come from a database or ML model)
        role_requirements = {
            "Senior Software Engineer": ["Python", "JavaScript", "React", "AWS", "Docker", "Kubernetes", "SQL", "Git"],
            "Data Scientist": ["Python", "Machine Learning", "SQL", "Statistics", "Pandas", "NumPy", "TensorFlow", "PyTorch"],
            "Full Stack Developer": ["JavaScript", "React", "Node.js", "Python", "SQL", "HTML", "CSS", "Git"],
            "DevOps Engineer": ["AWS", "Docker", "Kubernetes", "Terraform", "Jenkins", "Python", "Linux", "Git"],
            "Frontend Developer": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Webpack", "Git"],
            "Backend Developer": ["Python", "Java", "SQL", "REST API", "Docker", "Git", "Redis"],
            "Machine Learning Engineer": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "AWS", "Docker", "SQL"]
        }

        # Get requirements for target role (default to generic requirements)
        required_skills = role_requirements.get(target_role, ["Python", "Git", "SQL"])

        # Normalize skills to lowercase for comparison
        user_skills_lower = [skill.lower() for skill in user_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]

        # Calculate gaps
        matched_skills = []
        missing_skills = []

        for req_skill in required_skills:
            if req_skill.lower() in user_skills_lower:
                matched_skills.append(req_skill)
            else:
                missing_skills.append(req_skill)

        # Generate learning recommendations
        learning_recommendations = []
        for skill in missing_skills[:5]:  # Top 5 missing skills
            learning_recommendations.append({
                "skill": skill,
                "priority": "High" if missing_skills.index(skill) < 3 else "Medium",
                "estimated_learning_time": "2-4 weeks",
                "resources": [
                    f"Online course for {skill}",
                    f"Build a project using {skill}",
                    f"Join {skill} community forums"
                ]
            })

        match_percentage = (len(matched_skills) / len(required_skills)) * 100 if required_skills else 0

        return {
            "success": True,
            "target_role": target_role,
            "required_skills": required_skills,
            "user_skills": user_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_percentage": round(match_percentage, 2),
            "learning_recommendations": learning_recommendations,
            "readiness_level": "Ready" if match_percentage >= 80 else "Nearly Ready" if match_percentage >= 60 else "Needs Development"
        }

    except Exception as e:
        logger.error(f"Failed to analyze skill gap: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
@track_tool_call
def match_jobs_to_profile(user_skills: List[str], job_query: str, location: str = None, min_score: float = 0.5) -> Dict[str, Any]:
    """
    Find and rank jobs that match the user's skill profile.

    Args:
        user_skills: List of user's skills (e.g., ["Python", "React", "AWS"])
        job_query: Job search query (e.g., "software engineer")
        location: Optional location filter
        min_score: Minimum match score threshold (0.0 to 1.0)

    Returns:
        Dictionary with matched jobs ranked by compatibility score

    Example:
        match_jobs_to_profile(["Python", "Django", "SQL"], "backend developer", "Remote")
    """
    try:
        logger.info(f"Matching jobs for query: {job_query}")

        # First, search for jobs
        job_search_result = search_jobs(job_query, location, 20)

        if not job_search_result.get("success"):
            return {
                "success": False,
                "error": job_search_result.get("error", "Job search failed"),
                "matched_jobs": []
            }

        jobs = job_search_result.get("jobs", [])

        # Calculate match scores for each job
        matched_jobs = []
        user_skills_lower = [s.lower() for s in user_skills]

        for job in jobs:
            job_requirements = job.get("requirements", [])
            job_requirements_lower = [r.lower() for r in job_requirements]

            # Calculate match score
            matched = list(set(user_skills_lower) & set(job_requirements_lower))
            missing = list(set(job_requirements_lower) - set(user_skills_lower))

            match_score = len(matched) / len(job_requirements_lower) if job_requirements_lower else 0.0

            if match_score >= min_score:
                matched_jobs.append({
                    "job": {
                        "job_id": job.get("job_id"),
                        "title": job.get("title"),
                        "company": job.get("company"),
                        "location": job.get("location"),
                        "remote": job.get("remote"),
                        "description": job.get("description", "")[:300] + "..." if len(job.get("description", "")) > 300 else job.get("description", ""),
                        "requirements": job_requirements,
                        "application_url": job.get("application_url")
                    },
                    "match_score": round(match_score, 2),
                    "skill_matches": matched,
                    "skill_gaps": missing,
                    "reasons": [f"Matched skills: {', '.join(matched[:3])}" if matched else "Limited skill match"]
                })

        # Sort by match score
        matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)

        return {
            "success": True,
            "query": job_query,
            "location": location,
            "total_jobs_searched": len(jobs),
            "matched_jobs": matched_jobs[:10],  # Top 10 matches
            "match_count": len(matched_jobs),
            "average_match_score": round(sum(j["match_score"] for j in matched_jobs) / len(matched_jobs), 2) if matched_jobs else 0
        }

    except Exception as e:
        logger.error(f"Failed to match jobs: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "matched_jobs": []
        }


@tool
@track_tool_call
def generate_learning_path(target_role: str, user_skills: List[str], timeline_months: int = 6) -> Dict[str, Any]:
    """
    Generate a structured learning path to transition to a target role.

    Args:
        target_role: Desired job role (e.g., "Data Scientist", "Senior Software Engineer")
        user_skills: Current skills of the user
        timeline_months: Timeline for learning path in months (default: 6)

    Returns:
        Dictionary with structured learning path including milestones, resources, and timeline

    Example:
        generate_learning_path("Data Scientist", ["Python", "SQL"], 6)
    """
    try:
        logger.info(f"Generating learning path for: {target_role}")

        # Analyze skill gap first
        skill_gap_analysis = analyze_skill_gap(user_skills, target_role)

        if not skill_gap_analysis["success"]:
            return skill_gap_analysis

        missing_skills = skill_gap_analysis["missing_skills"]

        # Generate month-by-month learning plan
        learning_milestones = []
        skills_per_milestone = max(1, len(missing_skills) // timeline_months) if missing_skills else 0

        current_month = 1
        for i in range(0, len(missing_skills), max(1, skills_per_milestone)):
            skills_to_learn = missing_skills[i:i+skills_per_milestone]

            if current_month <= timeline_months and skills_to_learn:
                learning_milestones.append({
                    "month": current_month,
                    "milestone_title": f"Month {current_month}: Master {', '.join(skills_to_learn)}",
                    "skills_to_learn": skills_to_learn,
                    "learning_activities": [
                        f"Complete online course for {skill}" for skill in skills_to_learn
                    ] + [
                        f"Build hands-on project using {skills_to_learn[0]}" if skills_to_learn else "Practice coding"
                    ],
                    "practice_projects": [
                        f"Build a {skills_to_learn[0]} application" if skills_to_learn else "General project"
                    ],
                    "success_criteria": [
                        f"Complete certification or course for {skill}" for skill in skills_to_learn
                    ]
                })
                current_month += 1

        # Add final milestone
        if current_month <= timeline_months:
            learning_milestones.append({
                "month": timeline_months,
                "milestone_title": f"Month {timeline_months}: Portfolio & Job Applications",
                "skills_to_learn": ["Interview Skills", "Portfolio Development"],
                "learning_activities": [
                    "Build comprehensive portfolio showcasing all learned skills",
                    "Practice coding interviews",
                    "Update resume and LinkedIn profile",
                    "Start applying to target positions"
                ],
                "practice_projects": [
                    f"Capstone project for {target_role}"
                ],
                "success_criteria": [
                    "Complete portfolio with 3+ projects",
                    "Submit 10+ job applications"
                ]
            })

        # Generate resource recommendations
        resources = {
            "online_courses": [
                "Coursera - Role-specific specializations",
                "Udemy - Practical skill courses",
                "edX - University-level courses"
            ],
            "practice_platforms": [
                "LeetCode - Coding practice",
                "GitHub - Open source contributions",
                "Kaggle - Data science competitions (if applicable)"
            ],
            "communities": [
                "Stack Overflow - Technical Q&A",
                "LinkedIn Groups - Professional networking",
                f"{target_role} Slack/Discord communities"
            ],
            "books": [
                f"Essential reading for {target_role}",
                "Design patterns and best practices",
                "Interview preparation guides"
            ]
        }

        return {
            "success": True,
            "target_role": target_role,
            "current_skills": user_skills,
            "timeline_months": timeline_months,
            "skill_gap_summary": {
                "total_skills_needed": len(skill_gap_analysis["required_skills"]),
                "skills_you_have": len(skill_gap_analysis["matched_skills"]),
                "skills_to_learn": len(missing_skills),
                "readiness_level": skill_gap_analysis["readiness_level"]
            },
            "learning_milestones": learning_milestones,
            "resources": resources,
            "estimated_study_hours_per_week": 10 + (len(missing_skills) * 2),
            "networking_goals": [
                f"Connect with 5+ {target_role}s on LinkedIn",
                f"Attend 2+ {target_role} meetups or webinars",
                "Join professional communities and contribute"
            ],
            "certification_goals": [
                f"Relevant certification for {target_role}",
                "Industry-recognized credentials"
            ]
        }

    except Exception as e:
        logger.error(f"Failed to generate learning path: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@tool
@track_tool_call
def get_job_market_insights(role: str, location: str = None) -> Dict[str, Any]:
    """
    Get market insights for a specific job role including demand and trends.

    Args:
        role: Job role to analyze (e.g., "Data Scientist")
        location: Optional location filter

    Returns:
        Dictionary with job market insights including demand, salary trends, and popular skills

    Example:
        get_job_market_insights("Software Engineer", "San Francisco")
    """
    try:
        logger.info(f"Getting market insights for: {role}")

        # Search for jobs in this role
        job_search_result = search_jobs(role, location, 50)

        if not job_search_result.get("success"):
            return {
                "success": False,
                "error": job_search_result.get("error", "Job search failed")
            }

        jobs = job_search_result.get("jobs", [])

        # Analyze the market
        total_jobs = len(jobs)
        remote_jobs = sum(1 for job in jobs if job.get("remote", False))

        # Extract most common skills
        all_requirements = []
        for job in jobs:
            all_requirements.extend(job.get("requirements", []))

        skill_frequency = {}
        for skill in all_requirements:
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1

        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]

        # Analyze companies
        companies = [job.get("company") for job in jobs if job.get("company")]
        top_companies = list(set(companies))[:10]

        return {
            "success": True,
            "role": role,
            "location": location or "All locations",
            "total_job_postings": total_jobs,
            "remote_job_percentage": round((remote_jobs / total_jobs * 100), 2) if total_jobs > 0 else 0,
            "demand_level": "High" if total_jobs > 30 else "Medium" if total_jobs > 15 else "Low",
            "top_required_skills": [{"skill": skill, "frequency": freq} for skill, freq in top_skills],
            "top_hiring_companies": top_companies,
            "market_insights": {
                "trend": "Growing" if total_jobs > 20 else "Stable",
                "competition_level": "High" if total_jobs > 40 else "Medium",
                "recommendation": f"Good opportunity for {role} positions" if total_jobs > 15 else f"Limited openings for {role}, consider expanding location search"
            }
        }

    except Exception as e:
        logger.error(f"Failed to get market insights: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
