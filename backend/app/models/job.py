"""
Job Models

Data models for job postings, search results, and job-related functionality.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import WorkType, ExperienceLevel


@dataclass
class JobPosting:
    """Standardized job posting."""
    job_id: str
    title: str
    company: str
    location: str
    remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    currency: str = "USD"
    description: str = ""
    requirements: List[str] = None
    preferred_skills: List[str] = None
    benefits: List[str] = None
    work_type: WorkType = WorkType.FULL_TIME
    experience_level: ExperienceLevel = ExperienceLevel.MID
    posted_date: datetime = None
    application_deadline: Optional[datetime] = None
    application_url: Optional[str] = None
    source: str = "unknown"
    company_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.preferred_skills is None:
            self.preferred_skills = []
        if self.benefits is None:
            self.benefits = []
        if self.posted_date is None:
            self.posted_date = datetime.now()
        if self.company_info is None:
            self.company_info = {}


@dataclass
class JobSearchResult:
    """Job search result with metadata."""
    jobs: List[JobPosting]
    total_count: int
    page: int
    limit: int
    sources_used: List[str]
    search_time_ms: float
    filters_applied: Dict[str, Any] = None

    def __post_init__(self):
        if self.filters_applied is None:
            self.filters_applied = {}


@dataclass
class JobMatchScore:
    """Job matching score and analysis."""
    job_id: str
    match_score: float
    skill_matches: List[str]
    skill_gaps: List[str]
    location_match: bool
    salary_match: bool
    experience_match: bool
    reasons: List[str] = None

    def __post_init__(self):
        if self.reasons is None:
            self.reasons = []


@dataclass
class JobFilter:
    """Job search filter criteria."""
    keywords: List[str] = None
    location: str = ""
    remote_only: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    work_type: WorkType = None
    experience_level: ExperienceLevel = None
    company_size: str = ""
    industry: str = ""
    posted_within_days: Optional[int] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class JobAlert:
    """Job alert configuration."""
    alert_id: str
    user_id: str
    name: str
    filters: JobFilter
    frequency: str = "daily"  # daily, weekly, monthly
    is_active: bool = True
    created_at: datetime = None
    last_triggered: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class JobApplication:
    """Job application tracking."""
    application_id: str
    user_id: str
    job_id: str
    status: str = "applied"  # applied, reviewed, interviewed, rejected, offered
    applied_date: datetime = None
    notes: str = ""
    follow_up_date: Optional[datetime] = None
    interview_scheduled: Optional[datetime] = None

    def __post_init__(self):
        if self.applied_date is None:
            self.applied_date = datetime.now()


@dataclass
class SalaryData:
    """Salary information for a role."""
    role: str
    location: str
    salary_min: int
    salary_max: int
    experience_level: ExperienceLevel
    currency: str = "USD"
    company_size: str = ""
    industry: str = ""
    data_source: str = ""
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()
