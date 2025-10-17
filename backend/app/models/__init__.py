"""
Centralized Model Imports

This module provides centralized access to all data models across the application.
Import from here instead of individual service model files.
"""

# Base models and enums
from .base import (
    WorkType,
    ExperienceLevel,
    LocationPreference,
    CompanySize,
    Industry,
)

# User and resume models
from .user import (
    # Resume data models
    PersonalInfo,
    Experience,
    Education,
    Certification,
    ResumeData,

    # User profile models
    Skill,
    WorkExperience,
    CareerPreference,
    UserProfile,
)

# Job models
from .job import (
    JobPosting,
    JobSearchResult,
    JobMatchScore,
    JobFilter,
    JobAlert,
    JobApplication,
    SalaryData
)

# Company models
from .company import (
    CompanyInfo,
    FundingRound,
    CompanySearchResult,
    CompanyReview,
    CompanyCulture,
    CompanyBenefits,
    CompanyNews,
)

# Analysis models
from .analysis import (
    MatchAnalysis,
    DetailedScores
)
# Re-export all models for easy importing
__all__ = [
    # Base enums
    "WorkType",
    "ExperienceLevel",
    "LocationPreference",
    "CompanySize",
    "Industry",

    # Resume data models
    "PersonalInfo",
    "Experience",
    "Education",
    "Certification",
    "ResumeData",

    # User profile models
    "Skill",
    "WorkExperience",
    "CareerPreference",
    "UserProfile",

    # Job models
    "JobPosting",
    "JobSearchResult",
    "JobMatchScore",
    "JobFilter",
    "JobAlert",
    "JobApplication",
    "SalaryData",

    # Analysis models
    "MatchAnalysis",
    "DetailedScores",
    "SkillGapAnalysis",
    "CareerRoadmap",

    # Company models
    "CompanyInfo",
    "FundingRound",
    "CompanySearchResult",
    "CompanyReview",
    "CompanyCulture",
    "CompanyBenefits",
    "CompanyNews",
]
