"""
User Profile Models

Data models for user profiles, skills, and career preferences.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class SkillCategory(str, Enum):
    """Skill category enumeration."""
    
    PROGRAMMING = "Programming"
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    CLOUD = "Cloud"
    DATABASE = "Database"
    AI_ML = "AI/ML"
    DEVOPS = "DevOps"
    MOBILE = "Mobile"
    DATA_SCIENCE = "Data Science"
    SOFT_SKILLS = "Soft Skills"
    TOOLS = "Tools"
    LANGUAGES = "Languages"


@dataclass
class Skill:
    """Individual skill representation."""
    
    name: str
    level: int  # 1-5 scale
    category: SkillCategory
    years_experience: Optional[int] = None
    last_used: Optional[datetime] = None
    certifications: List[str] = field(default_factory=list)


@dataclass
class CareerPreference:
    """Career preferences and goals."""
    
    target_roles: List[str] = field(default_factory=list)
    target_industries: List[str] = field(default_factory=list)
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    location_preference: Optional[str] = None
    remote_work: Optional[bool] = None
    company_size: Optional[str] = None
    work_environment: Optional[str] = None


@dataclass
class Experience:
    """Work experience entry."""
    
    title: str
    company: str
    location: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    current: bool = False
    description: str = ""
    skills_used: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)


@dataclass
class Education:
    """Education entry."""
    
    degree: str
    field: str
    school: str
    location: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    gpa: Optional[float] = None
    honors: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    """Complete user profile."""
    
    user_id: str
    skills: List[Skill] = field(default_factory=list)
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    preferences: CareerPreference = field(default_factory=CareerPreference)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "skills": [
                {
                    "name": skill.name,
                    "level": skill.level,
                    "category": skill.category.value,
                    "years_experience": skill.years_experience,
                    "last_used": skill.last_used.isoformat() if skill.last_used else None,
                    "certifications": skill.certifications,
                }
                for skill in self.skills
            ],
            "experience": [
                {
                    "title": exp.title,
                    "company": exp.company,
                    "location": exp.location,
                    "start_date": exp.start_date.isoformat() if exp.start_date else None,
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "current": exp.current,
                    "description": exp.description,
                    "skills_used": exp.skills_used,
                    "achievements": exp.achievements,
                }
                for exp in self.experience
            ],
            "education": [
                {
                    "degree": edu.degree,
                    "field": edu.field,
                    "school": edu.school,
                    "location": edu.location,
                    "start_date": edu.start_date.isoformat() if edu.start_date else None,
                    "end_date": edu.end_date.isoformat() if edu.end_date else None,
                    "gpa": edu.gpa,
                    "honors": edu.honors,
                }
                for edu in self.education
            ],
            "preferences": {
                "target_roles": self.preferences.target_roles,
                "target_industries": self.preferences.target_industries,
                "salary_range_min": self.preferences.salary_range_min,
                "salary_range_max": self.preferences.salary_range_max,
                "location_preference": self.preferences.location_preference,
                "remote_work": self.preferences.remote_work,
                "company_size": self.preferences.company_size,
                "work_environment": self.preferences.work_environment,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class JobPosting:
    """Job posting representation."""
    
    job_id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    employment_type: str = "full_time"
    experience_level: str = "mid"
    posted_date: Optional[datetime] = None
    application_url: Optional[str] = None
    company_info: Optional[Dict[str, Any]] = None


@dataclass
class JobRecommendation:
    """Job recommendation with matching score."""
    
    job: JobPosting
    match_score: float
    matching_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class SkillGapAnalysis:
    """Skill gap analysis results."""
    
    user_id: str
    target_role: str
    current_skills: List[Skill] = field(default_factory=list)
    required_skills: List[Skill] = field(default_factory=list)
    missing_skills: List[Skill] = field(default_factory=list)
    skill_gaps: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    priority_skills: List[str] = field(default_factory=list)


@dataclass
class CareerRoadmap:
    """Career roadmap with milestones and goals."""
    
    user_id: str
    target_role: str
    current_position: str
    timeline_months: int
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    skill_development_plan: List[Dict[str, Any]] = field(default_factory=list)
    networking_goals: List[str] = field(default_factory=list)
    certification_goals: List[str] = field(default_factory=list)
    experience_goals: List[str] = field(default_factory=list)
    estimated_salary_progression: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
