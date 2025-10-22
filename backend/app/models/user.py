"""
User Models

Data models for user profiles, skills, experience, education, and resume data.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional

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


    def __str__(self) -> str:
        return f"""ResumeData(
            personal_info={self.personal_info},
            summary={self.summary},
            experience={self.experience},
            education={self.education},
            certifications={self.certifications},
            skills={self.skills},
        )"""

# ========== User Profile Models ==========

@dataclass
class Skill:
    """Skill model."""
    name: str
    level: int = 1  # Skill level from 1-5
    category: str = ""
    years_experience: Optional[int] = None
    last_used: Optional[datetime] = None


@dataclass
class WorkExperience:
    """Work experience model."""
    title: str
    company: str
    location: str
    start_date: datetime
    end_date: Optional[datetime] = None
    current: bool = False
    description: str = ""
    achievements: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)
    work_type: WorkType = WorkType.FULL_TIME


@dataclass
class Education:
    """Education model."""
    degree: str
    institution: str
    graduation_date: datetime
    field_of_study: str = ""
    gpa: Optional[float] = None
    honors: List[str] = field(default_factory=list)
    relevant_courses: List[str] = field(default_factory=list)


@dataclass
class Certification:
    """Certification model."""
    name: str
    issuer: str
    issue_date: datetime
    expiry_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    verification_url: Optional[str] = None


@dataclass
class CareerPreference:
    """Career preference model."""
    target_roles: List[str] = field(default_factory=list)
    target_industries: List[str] = field(default_factory=list)
    target_companies: List[str] = field(default_factory=list)
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    location_preference: LocationPreference = LocationPreference.FLEXIBLE
    work_type_preference: WorkType = WorkType.FULL_TIME
    company_size_preference: Optional[str] = None
    remote_work_preference: bool = True


@dataclass
class UserProfile:
    """User profile model."""
    user_id: str
    personal_info: Dict[str, Any] = field(default_factory=dict)
    skills: List[Skill] = field(default_factory=list)
    experience: List[WorkExperience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    preferences: CareerPreference = field(default_factory=CareerPreference)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        # use multiple lines for better readability
        return f"""UserProfile(
            user_id={self.user_id},
            personal_info={self.personal_info},
            skills={self.skills},
            experience={self.experience},
            education={self.education},
            certifications={self.certifications},
            preferences={self.preferences},
            created_at={self.created_at},
            updated_at={self.updated_at}
        )"""


# ========== Resume API Models ==========

@dataclass
class ResumeParseResponse:
    """Response model for resume parsing."""
    success: bool
    data: Optional[ResumeData] = None
    error: Optional[str] = None
    confidence_score: Optional[float] = None


@dataclass
class ResumeParseRequest:
    """Request model for resume parsing from text."""
    resume_text: str
