"""
Coursera Models

Data models for Coursera courses, certifications, and learning recommendations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CourseLevel(str, Enum):
    """Course difficulty level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MIXED = "mixed"


class CourseType(str, Enum):
    """Course type enumeration."""
    COURSE = "course"
    SPECIALIZATION = "specialization"
    PROFESSIONAL_CERTIFICATE = "professional_certificate"
    MASTER_TRACK = "master_track"
    DEGREE = "degree"


class Language(str, Enum):
    """Language enumeration for courses."""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    CHINESE = "zh"
    PORTUGUESE = "pt"
    ARABIC = "ar"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    KOREAN = "ko"
    GERMAN = "de"
    ITALIAN = "it"


class Course(BaseModel):
    """Coursera course model."""
    id: str
    title: str
    description: str
    url: str
    institution: str
    instructor: Optional[str] = None
    level: CourseLevel = CourseLevel.BEGINNER
    course_type: CourseType = CourseType.COURSE
    language: Language = Language.ENGLISH
    duration_weeks: Optional[int] = None
    hours_per_week: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    enrollment_count: Optional[int] = None
    skills: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    learning_outcomes: List[str] = Field(default_factory=list)
    price: Optional[float] = None
    currency: str = "USD"
    is_free: bool = False
    certificate_available: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Certification(BaseModel):
    """Coursera certification model."""
    id: str
    name: str
    description: str
    url: str
    institution: str
    course_type: CourseType = CourseType.PROFESSIONAL_CERTIFICATE
    duration_weeks: Optional[int] = None
    skills: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    price: Optional[float] = None
    currency: str = "USD"
    is_free: bool = False
    industry_recognition: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LearningRecommendation(BaseModel):
    """Learning recommendation model."""
    user_id: str
    target_role: Optional[str] = None
    skill_gaps: List[str] = Field(default_factory=list)
    recommended_courses: List[Course] = Field(default_factory=list)
    recommended_certifications: List[Certification] = Field(default_factory=list)
    learning_path: List[Dict[str, Any]] = Field(default_factory=list)
    estimated_completion_time: Optional[int] = None  # in weeks
    priority_skills: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CourseSearchRequest(BaseModel):
    """Request model for course search."""
    query: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    level: Optional[CourseLevel] = None
    course_type: Optional[CourseType] = None
    language: Optional[Language] = None
    is_free: Optional[bool] = None
    institution: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=50)


class CourseSearchResponse(BaseModel):
    """Response model for course search."""
    courses: List[Course] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    limit: int = 10
    has_more: bool = False


class CertificationSearchRequest(BaseModel):
    """Request model for certification search."""
    query: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    course_type: Optional[CourseType] = None
    language: Optional[Language] = None
    is_free: Optional[bool] = None
    institution: Optional[str] = None
    industry_recognition: Optional[bool] = None
    limit: int = Field(default=10, ge=1, le=50)


class CertificationSearchResponse(BaseModel):
    """Response model for certification search."""
    certifications: List[Certification] = Field(default_factory=list)
    total_count: int = 0
    page: int = 1
    limit: int = 10
    has_more: bool = False


class LearningPathStep(BaseModel):
    """Individual step in a learning path."""
    step_number: int
    title: str
    description: str
    courses: List[Course] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    estimated_duration_weeks: int
    skills_covered: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)


class LearningPath(BaseModel):
    """Complete learning path model."""
    id: str
    title: str
    description: str
    target_role: str
    total_duration_weeks: int
    difficulty_level: CourseLevel
    steps: List[LearningPathStep] = Field(default_factory=list)
    skills_covered: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
