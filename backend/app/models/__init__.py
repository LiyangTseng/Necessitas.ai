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

    # Resume API models
    ResumeParseRequest,
    ResumeParseResponse,
)

# Job models
from .job import (
    JobPosting,
    JobSearchResult,
    JobMatchScore,
    JobFilter,
    JobAlert,
    JobApplication,
    SalaryData,

    # Jobs API models
    JobSearchRequest,
    JobSearchResponse,
    JobMatchRequest,
    JobMatchResponse
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

    # Company API models
    CompanySearchRequest,
    CompanySearchResponse,
    CompanyInfoResponse
)

# Analysis models
from .analysis import (
    MatchAnalysis,
    DetailedScores,
    SkillGapAnalysis,
    CareerRoadmap,
    SkillDevelopmentStep,
    TimelineMilestone
)

# Chat models
from .chat import (
    ChatMessage,
    ChatRequest,
    ChatResponse
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

    # Resume API models
    "ResumeParseRequest",
    "ResumeParseResponse",

    # Job models
    "JobPosting",
    "JobSearchResult",
    "JobMatchScore",
    "JobFilter",
    "JobAlert",
    "JobApplication",
    "SalaryData",

    # Jobs API models
    "JobSearchRequest",
    "JobSearchResponse",
    "JobMatchRequest",
    "JobMatchResponse",

    # Analysis models
    "MatchAnalysis",
    "DetailedScores",
    "SkillGapAnalysis",
    "CareerRoadmap",
    "SkillDevelopmentStep",
    "TimelineMilestone",

    # Company models
    "CompanyInfo",
    "FundingRound",
    "CompanySearchResult",
    "CompanyReview",
    "CompanyCulture",
    "CompanyBenefits",
    "CompanyNews",

    # Company API models
    "CompanySearchRequest",
    "CompanySearchResponse",
    "CompanyInfoResponse",

    # Chat models
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
]
