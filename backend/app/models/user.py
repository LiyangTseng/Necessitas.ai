"""
User Models

Data models for user profiles, skills, experience, education, and resume data.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .base import WorkType, ExperienceLevel, LocationPreference


# ========== Resume Data Models ==========

@dataclass
class PersonalInfo:
    """Personal information extracted from resume."""
    full_name: str
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    portfolio_url: str = ""


@dataclass
class Experience:
    """Work experience entry."""
    title: str
    company: str
    location: str
    start_date: str
    end_date: str = ""
    current: bool = False
    description: str = ""
    achievements: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)


@dataclass
class Education:
    """Education entry."""
    degree: str
    institution: str
    field_of_study: str = ""
    graduation_date: str = ""
    gpa: str = ""
    honors: List[str] = field(default_factory=list)


@dataclass
class Certification:
    """Certification entry."""
    name: str
    issuer: str
    issue_date: str = ""
    expiry_date: Optional[str] = None
    credential_id: str = ""


@dataclass
class ResumeData:
    """Complete resume data structure."""
    personal_info: PersonalInfo
    summary: str = ""
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    raw_text: str = ""
    confidence_score: float = 0.0
    parsed_at: datetime = field(default_factory=datetime.now)


# ========== User Profile Models ==========

class Skill(BaseModel):
    """Skill model."""
    name: str
    level: int = Field(ge=1, le=5, description="Skill level from 1-5")
    category: str
    years_experience: Optional[int] = None
    last_used: Optional[datetime] = None


class WorkExperience(BaseModel):
    """Work experience model."""
    title: str
    company: str
    location: str
    start_date: datetime
    end_date: Optional[datetime] = None
    current: bool = False
    description: str
    achievements: List[str] = []
    skills_used: List[str] = []
    work_type: WorkType = WorkType.FULL_TIME


class Education(BaseModel):
    """Education model."""
    degree: str
    institution: str
    field_of_study: str
    graduation_date: datetime
    gpa: Optional[float] = None
    honors: List[str] = []
    relevant_courses: List[str] = []


class Certification(BaseModel):
    """Certification model."""
    name: str
    issuer: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    verification_url: Optional[str] = None


class CareerPreference(BaseModel):
    """Career preference model."""
    target_roles: List[str] = []
    target_industries: List[str] = []
    target_companies: List[str] = []
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    location_preference: LocationPreference = LocationPreference.FLEXIBLE
    work_type_preference: WorkType = WorkType.FULL_TIME
    company_size_preference: Optional[str] = None
    remote_work_preference: bool = True


class UserProfile(BaseModel):
    """User profile model."""
    user_id: str
    personal_info: Dict[str, Any] = {}
    skills: List[Skill] = []
    experience: List[WorkExperience] = []
    education: List[Education] = []
    certifications: List[Certification] = []
    preferences: CareerPreference = CareerPreference()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========== AI/ML Models ==========

class JobRecommendation(BaseModel):
    """Job recommendation model."""
    job_posting: 'JobPosting'  # Forward reference
    match_score: float = Field(ge=0, le=100)
    match_reasons: List[str] = []
    skill_matches: List[str] = []
    skill_gaps: List[str] = []
    salary_fit: bool = True
    location_fit: bool = True
    experience_fit: bool = True


class SkillGapAnalysis(BaseModel):
    """Skill gap analysis model."""
    user_id: str
    target_role: str
    current_skills: List[str] = []
    required_skills: List[str] = []
    missing_skills: List[str] = []
    developing_skills: List[str] = []
    strong_skills: List[str] = []
    recommendations: List[str] = []
    priority_skills: List[str] = []
    learning_path: List[Dict[str, Any]] = []


class CareerRoadmap(BaseModel):
    """Career roadmap model."""
    user_id: str
    target_role: str
    current_position: str
    timeline_months: int
    milestones: List[Dict[str, Any]] = []
    skill_development_plan: List[Dict[str, Any]] = []
    networking_goals: List[str] = []
    certification_goals: List[str] = []
    experience_goals: List[str] = []
    estimated_salary_progression: List[Dict[str, Any]] = []


class MarketInsight(BaseModel):
    """Market insight model."""
    insight_id: str
    title: str
    description: str
    category: str
    relevance_score: float = Field(ge=0, le=1)
    source: str
    published_date: datetime
    tags: List[str] = []
    impact_level: str = "medium"  # low, medium, high
    actionable: bool = True
    related_skills: List[str] = []
    related_roles: List[str] = []
