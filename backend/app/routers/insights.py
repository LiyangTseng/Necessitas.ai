"""
Career Insights Router

Handles skill gap analysis, career roadmaps, and personalized insights.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.agents.roadmap_generator import RoadmapGenerator
from app.services.job_recommender import JobRecommender

router = APIRouter()


@router.get("/skill-gap/{user_id}")
async def get_skill_gap_analysis(
    user_id: str,
    target_role: Optional[str] = Query(None, description="Target role for analysis"),
) -> Dict[str, Any]:
    """
    Get skill gap analysis for a user.

    Args:
        user_id: User ID
        target_role: Optional target role

    Returns:
        Skill gap analysis with recommendations
    """
    try:
        # Initialize job recommender
        job_recommender = JobRecommender()

        # Get skill gap analysis
        skill_gap = await job_recommender.analyze_skill_gap(
            user_id=user_id, target_role=target_role
        )

        return {
            "user_id": user_id,
            "target_role": target_role,
            "skill_gap": skill_gap,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Skill gap analysis failed: {str(e)}"
        )


@router.get("/roadmap/{user_id}")
async def get_career_roadmap(
    user_id: str,
    target_role: str = Query(..., description="Target role"),
    timeline_months: int = Query(12, description="Timeline in months"),
) -> Dict[str, Any]:
    """
    Generate a personalized career roadmap.

    Args:
        user_id: User ID
        target_role: Target role
        timeline_months: Timeline in months

    Returns:
        Career roadmap with milestones and recommendations
    """
    try:
        # Initialize roadmap generator
        roadmap_generator = RoadmapGenerator()

        # Generate roadmap
        roadmap = await roadmap_generator.generate_roadmap(
            user_id=user_id, target_role=target_role, timeline_months=timeline_months
        )

        return {
            "user_id": user_id,
            "target_role": target_role,
            "timeline_months": timeline_months,
            "roadmap": roadmap,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Roadmap generation failed: {str(e)}"
        )


@router.get("/market-trends")
async def get_market_trends(
    industry: Optional[str] = Query(None, description="Industry filter"),
    location: Optional[str] = Query(None, description="Location filter"),
) -> Dict[str, Any]:
    """
    Get market trends and insights.

    Args:
        industry: Optional industry filter
        location: Optional location filter

    Returns:
        Market trends and insights
    """
    try:
        # This would typically fetch from market data APIs
        # For now, return mock data
        return {
            "industry": industry,
            "location": location,
            "trends": [
                {
                    "trend": "AI/ML Skills in High Demand",
                    "growth_rate": 25,
                    "description": "Artificial Intelligence and Machine Learning skills are experiencing rapid growth",
                    "impact": "high",
                },
                {
                    "trend": "Remote Work Continues to Grow",
                    "growth_rate": 15,
                    "description": "Remote work opportunities are increasing across all industries",
                    "impact": "medium",
                },
                {
                    "trend": "Cloud Computing Skills Essential",
                    "growth_rate": 20,
                    "description": "Cloud computing skills are becoming essential for most tech roles",
                    "impact": "high",
                },
            ],
            "insights": [
                "Focus on developing AI/ML skills for competitive advantage",
                "Consider remote work opportunities for better work-life balance",
                "Cloud certifications can significantly boost career prospects",
            ],
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get market trends: {str(e)}"
        )


@router.get("/salary-projection/{user_id}")
async def get_salary_projection(
    user_id: str,
    target_role: str = Query(..., description="Target role"),
    years_experience: int = Query(..., description="Years of experience"),
) -> Dict[str, Any]:
    """
    Get salary projection for career progression.

    Args:
        user_id: User ID
        target_role: Target role
        years_experience: Years of experience

    Returns:
        Salary projection and career progression insights
    """
    try:
        # This would typically use ML models for salary prediction
        # For now, return mock data
        base_salary = 60000 + (years_experience * 8000)

        return {
            "user_id": user_id,
            "target_role": target_role,
            "years_experience": years_experience,
            "projections": {
                "current_level": {
                    "title": f"Junior {target_role}",
                    "salary_range": f"${base_salary - 10000} - ${base_salary + 5000}",
                    "requirements": ["Basic technical skills", "1-2 years experience"],
                },
                "next_level": {
                    "title": f"Senior {target_role}",
                    "salary_range": f"${base_salary + 10000} - ${base_salary + 25000}",
                    "requirements": [
                        "Advanced technical skills",
                        "Leadership experience",
                        "3-5 years experience",
                    ],
                },
                "senior_level": {
                    "title": f"Principal {target_role}",
                    "salary_range": f"${base_salary + 25000} - ${base_salary + 50000}",
                    "requirements": [
                        "Expert technical skills",
                        "Team leadership",
                        "5+ years experience",
                    ],
                },
            },
            "growth_potential": {
                "short_term": f"${base_salary + 5000} (6 months)",
                "medium_term": f"${base_salary + 15000} (2 years)",
                "long_term": f"${base_salary + 30000} (5 years)",
            },
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Salary projection failed: {str(e)}"
        )


@router.get("/competitor-analysis/{user_id}")
async def get_competitor_analysis(
    user_id: str, target_role: str = Query(..., description="Target role")
) -> Dict[str, Any]:
    """
    Get competitor analysis for job applications.

    Args:
        user_id: User ID
        target_role: Target role

    Returns:
        Competitor analysis and insights
    """
    try:
        # This would typically analyze job market competition
        # For now, return mock data
        return {
            "user_id": user_id,
            "target_role": target_role,
            "competition_analysis": {
                "market_saturation": "Medium",
                "average_applicants_per_job": 150,
                "top_skills_in_demand": [
                    "Python",
                    "AWS",
                    "Machine Learning",
                    "React",
                    "Docker",
                ],
                "skill_gaps": ["Kubernetes", "GraphQL", "Microservices Architecture"],
            },
            "recommendations": [
                "Focus on developing in-demand skills",
                "Consider obtaining relevant certifications",
                "Build a strong portfolio with real projects",
                "Network with industry professionals",
            ],
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Competitor analysis failed: {str(e)}"
        )
