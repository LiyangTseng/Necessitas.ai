"""
Insights API Router

Provides REST API endpoints for career insights and analysis.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
logger = logging.getLogger(__name__)

from services.job_matching_engine import JobMatchingEngine
from models import UserProfile, MatchAnalysis

router = APIRouter()

# Initialize service
job_matcher = JobMatchingEngine()


class SkillGapRequest(BaseModel):
    """Request model for skill gap analysis."""
    user_profile: Dict[str, Any]  # UserProfile as dict
    target_role: Optional[str] = None


class SkillGapResponse(BaseModel):
    """Response model for skill gap analysis."""
    success: bool
    current_skills: List[str] = []
    required_skills: List[str] = []
    missing_skills: List[str] = []
    strong_skills: List[str] = []
    recommendations: List[str] = []
    error: Optional[str] = None


class CareerRoadmapRequest(BaseModel):
    """Request model for career roadmap generation."""
    user_profile: Dict[str, Any]  # UserProfile as dict
    target_role: str
    timeline_months: int = 12


class CareerRoadmapResponse(BaseModel):
    """Response model for career roadmap."""
    success: bool
    target_role: str = ""
    current_position: str = ""
    timeline_months: int = 12
    milestones: List[Dict[str, Any]] = []
    skill_development_plan: List[Dict[str, Any]] = []
    networking_goals: List[str] = []
    certification_goals: List[str] = []
    experience_goals: List[str] = []
    error: Optional[str] = None


class MatchAnalysisRequest(BaseModel):
    """Request model for job match analysis."""
    user_profile: Dict[str, Any]  # UserProfile as dict
    job_posting: Dict[str, Any]  # JobPosting as dict


class MatchAnalysisResponse(BaseModel):
    """Response model for job match analysis."""
    success: bool
    overall_score: float = 0.0
    detailed_scores: Dict[str, float] = {}
    skill_matches: List[str] = []
    skill_gaps: List[str] = []
    reasons: List[str] = []
    salary_fit: bool = False
    location_fit: bool = False
    experience_fit: bool = False
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []
    error: Optional[str] = None


@router.post("/skill-gap", response_model=SkillGapResponse)
async def analyze_skill_gap(request: SkillGapRequest):
    """
    Analyze skill gaps for a user's career development.

    Args:
        request: User profile and optional target role

    Returns:
        Skill gap analysis with recommendations
    """
    try:
        # Convert dict to UserProfile object
        user_profile = UserProfile(**request.user_profile)

        # This would typically use the job_matcher.analyze_skill_gap method
        # For now, we'll provide a basic implementation
        current_skills = [skill.name.lower() for skill in user_profile.skills]

        # Mock required skills based on target role or general tech skills
        if request.target_role:
            required_skills = _get_role_requirements(request.target_role)
        else:
            required_skills = ["python", "javascript", "react", "aws", "docker"]

        missing_skills = list(set(required_skills) - set(current_skills))
        strong_skills = list(set(current_skills) & set(required_skills))

        recommendations = _generate_skill_recommendations(missing_skills)

        return SkillGapResponse(
            success=True,
            current_skills=current_skills,
            required_skills=required_skills,
            missing_skills=missing_skills,
            strong_skills=strong_skills,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Failed to analyze skill gap: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze skill gap: {str(e)}")


@router.post("/career-roadmap", response_model=CareerRoadmapResponse)
async def generate_career_roadmap(request: CareerRoadmapRequest):
    """
    Generate a career roadmap for reaching a target role.

    Args:
        request: User profile, target role, and timeline

    Returns:
        Career roadmap with milestones and learning path
    """
    try:
        # Convert dict to UserProfile object
        user_profile = UserProfile(**request.user_profile)

        # Get current position from user profile
        current_position = "Entry Level"
        if user_profile.experience:
            current_position = user_profile.experience[0].title

        # Generate roadmap milestones
        milestones = _create_roadmap_milestones(request.target_role, request.timeline_months)

        # Generate skill development plan
        skill_plan = _create_skill_development_plan(request.target_role)

        # Generate goals
        networking_goals = _generate_networking_goals(request.target_role)
        certification_goals = _generate_certification_goals(request.target_role)
        experience_goals = _generate_experience_goals(request.target_role)

        return CareerRoadmapResponse(
            success=True,
            target_role=request.target_role,
            current_position=current_position,
            timeline_months=request.timeline_months,
            milestones=milestones,
            skill_development_plan=skill_plan,
            networking_goals=networking_goals,
            certification_goals=certification_goals,
            experience_goals=experience_goals
        )

    except Exception as e:
        logger.error(f"Failed to generate career roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate career roadmap: {str(e)}")


@router.post("/match-analysis", response_model=MatchAnalysisResponse)
async def analyze_job_match(request: MatchAnalysisRequest):
    """
    Analyze match between user profile and job posting.

    Args:
        request: User profile and job posting

    Returns:
        Detailed match analysis
    """
    try:
        # Convert dicts to objects
        user_profile = UserProfile(**request.user_profile)
        # Note: JobPosting conversion would need to be implemented based on the model

        # This would use the job_matcher.analyze_match method
        # For now, return a mock analysis
        return MatchAnalysisResponse(
            success=True,
            overall_score=0.75,
            detailed_scores={
                "skills": 0.8,
                "experience": 0.7,
                "location": 0.9,
                "salary": 0.6
            },
            skill_matches=["python", "javascript"],
            skill_gaps=["aws", "docker"],
            reasons=["Strong skill alignment", "Experience level matches"],
            salary_fit=True,
            location_fit=True,
            experience_fit=True,
            strengths=["Strong in Python and JavaScript"],
            weaknesses=["Missing AWS experience"],
            recommendations=["Consider learning AWS fundamentals"]
        )

    except Exception as e:
        logger.error(f"Failed to analyze job match: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze job match: {str(e)}")


# Helper functions
def _get_role_requirements(target_role: str) -> List[str]:
    """Get requirements for a target role."""
    role_requirements = {
        "Senior Software Engineer": ["python", "javascript", "react", "aws", "docker"],
        "Data Scientist": ["python", "machine learning", "sql", "statistics", "pandas"],
        "Product Manager": ["product management", "agile", "user research", "analytics"],
        "DevOps Engineer": ["aws", "docker", "kubernetes", "terraform", "jenkins"],
        "Frontend Developer": ["javascript", "react", "html", "css", "typescript"],
        "Backend Developer": ["python", "java", "sql", "rest api", "microservices"]
    }

    return role_requirements.get(target_role, ["python", "javascript", "communication"])


def _generate_skill_recommendations(missing_skills: List[str]) -> List[str]:
    """Generate recommendations for skill development."""
    recommendations = []

    skill_learning_map = {
        "python": "Take Python programming course",
        "javascript": "Learn JavaScript fundamentals",
        "machine learning": "Study ML algorithms and frameworks",
        "aws": "Get AWS certification",
        "docker": "Learn containerization with Docker",
        "react": "Build projects with React",
        "kubernetes": "Learn container orchestration"
    }

    for skill in missing_skills[:3]:  # Top 3 missing skills
        if skill in skill_learning_map:
            recommendations.append(skill_learning_map[skill])

    return recommendations


def _create_roadmap_milestones(target_role: str, timeline_months: int) -> List[Dict[str, Any]]:
    """Create roadmap milestones."""
    milestones = []
    months_per_skill = timeline_months / 4  # Assume 4 main skills

    skills = _get_role_requirements(target_role)[:4]

    for i, skill in enumerate(skills):
        month = int((i + 1) * months_per_skill)
        milestones.append({
            "milestone": f"Master {skill}",
            "target_month": month,
            "description": f"Complete learning and practice in {skill}",
            "success_criteria": f"Build project using {skill}"
        })

    return milestones


def _create_skill_development_plan(target_role: str) -> List[Dict[str, Any]]:
    """Create detailed skill development plan."""
    skills = _get_role_requirements(target_role)[:5]

    return [
        {
            "skill": skill,
            "learning_approach": "Online courses + hands-on projects",
            "timeline": "4-6 weeks",
            "resources": [f"Course for {skill}", f"Practice with {skill}"]
        }
        for skill in skills
    ]


def _generate_networking_goals(target_role: str) -> List[str]:
    """Generate networking goals for target role."""
    return [
        f"Connect with {target_role}s on LinkedIn",
        f"Join {target_role} professional groups",
        f"Attend {target_role} meetups and conferences"
    ]


def _generate_certification_goals(target_role: str) -> List[str]:
    """Generate certification goals."""
    cert_map = {
        "Senior Software Engineer": ["AWS Certified Developer", "Google Cloud Professional"],
        "Data Scientist": ["AWS Machine Learning", "Google Data Analytics"],
        "Product Manager": ["Certified Scrum Master", "Google Analytics"],
        "DevOps Engineer": ["AWS Certified DevOps Engineer", "Kubernetes Administrator"]
    }

    return cert_map.get(target_role, ["Industry-relevant certification"])


def _generate_experience_goals(target_role: str) -> List[str]:
    """Generate experience goals."""
    return [
        f"Gain hands-on experience in {target_role} projects",
        f"Lead a {target_role} initiative",
        f"Build portfolio showcasing {target_role} skills"
    ]


@router.get("/health")
async def health_check():
    """Health check for insights service."""
    return {"status": "healthy", "service": "insights"}
