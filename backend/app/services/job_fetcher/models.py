"""
Job Fetcher Models

Data models for job postings and search results.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class WorkType(str, Enum):
    """Work type enumeration."""

    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""

    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"


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
