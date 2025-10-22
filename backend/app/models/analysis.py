from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from models.base import WorkType, ExperienceLevel, LocationPreference, CompanySize, Industry
from models.user import UserProfile
from models.job import JobPosting

@dataclass
class DetailedScores:
    """Detailed scoring breakdown for job matching."""
    skills: float
    experience: float
    location: float
    salary: float
    company_fit: float
    work_type: float

    def calculate_overall_score(self, weights: Dict[str, float]) -> float:
        """Calculate overall score."""
        total_score = (
            self.skills * weights["skills"] +
            self.experience * weights["experience"] +
            self.location * weights["location"] +
            self.salary * weights["salary"] +
            self.company_fit * weights["company_fit"] +
            self.work_type * weights["work_type"]
        )
        return total_score

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format."""
        return {
            "skills": self.skills,
            "experience": self.experience,
            "location": self.location,
            "salary": self.salary,
            "company_fit": self.company_fit,
            "work_type": self.work_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'DetailedScores':
        """Create from dictionary format."""
        return cls(
            skills=data.get('skills', 0.0),
            experience=data.get('experience', 0.0),
            location=data.get('location', 0.0),
            salary=data.get('salary', 0.0),
            company_fit=data.get('company_fit', 0.0),
            work_type=data.get('work_type', 0.0),
        )

@dataclass
class MatchAnalysis:
    """Detailed match analysis between user and job."""
    overall_score: float
    detailed_scores: DetailedScores
    skill_matches: List[str]
    skill_gaps: List[str]
    reasons: List[str]
    salary_fit: bool
    location_fit: bool
    experience_fit: bool
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

    def __eq__(self, other: 'MatchAnalysis') -> bool:
        return (
            self.__dict__ == other.__dict__
        )

    def __str__(self) -> str:
        return f"""MatchAnalysis(
            overall_score={self.overall_score},
            detailed_scores={self.detailed_scores},
            skill_matches={self.skill_matches},
            skill_gaps={self.skill_gaps},
            reasons={self.reasons},
            salary_fit={self.salary_fit},
            location_fit={self.location_fit},
            experience_fit={self.experience_fit},
            strengths={self.strengths},
            weaknesses={self.weaknesses},
            recommendations={self.recommendations})
        """



@dataclass
class SkillGapAnalysis:
    """Analysis of skills gap between user and job requirements."""
    missing_skills: List[str]
    learning_recommendations: List[str]
    skill_priority: Dict[str, int]  # skill -> priority (1-5)
    estimated_learning_time: Dict[str, str]  # skill -> time estimate
    resources: Dict[str, List[str]]  # skill -> list of learning resources

    def __post_init__(self):
        if self.missing_skills is None:
            self.missing_skills = []
        if self.learning_recommendations is None:
            self.learning_recommendations = []
        if self.skill_priority is None:
            self.skill_priority = {}
        if self.estimated_learning_time is None:
            self.estimated_learning_time = {}
        if self.resources is None:
            self.resources = {}


@dataclass
class CareerRoadmap:
    """Career development roadmap for user."""
    target_role: str
    skill_development_plan: List['SkillDevelopmentStep']
    timeline: List['TimelineMilestone']
    estimated_completion_time: str
    success_metrics: List[str]

    def __post_init__(self):
        if self.skill_development_plan is None:
            self.skill_development_plan = []
        if self.timeline is None:
            self.timeline = []
        if self.success_metrics is None:
            self.success_metrics = []


@dataclass
class SkillDevelopmentStep:
    """Individual step in skill development plan."""
    skill: str
    priority: int  # 1-5
    learning_method: str  # "course", "practice", "project", etc.
    estimated_time: str
    prerequisites: List[str]
    resources: List[str]

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.resources is None:
            self.resources = []


@dataclass
class TimelineMilestone:
    """Milestone in career development timeline."""
    milestone: str
    target_date: str
    skills_to_achieve: List[str]
    success_criteria: List[str]

    def __post_init__(self):
        if self.skills_to_achieve is None:
            self.skills_to_achieve = []
        if self.success_criteria is None:
            self.success_criteria = []


# ========== Insights API Models ==========

@dataclass
class SkillGapRequest:
    """Request model for skill gap analysis."""
    user_profile: Dict[str, Any]
    target_role: Optional[str] = None


@dataclass
class SkillGapResponse:
    """Response model for skill gap analysis."""
    success: bool
    analysis: Optional[SkillGapAnalysis] = None
    error: Optional[str] = None


@dataclass
class CareerRoadmapRequest:
    """Request model for career roadmap generation."""
    user_profile: Dict[str, Any]
    target_role: str
    timeline_months: Optional[int] = None


@dataclass
class CareerRoadmapResponse:
    """Response model for career roadmap generation."""
    success: bool
    roadmap: Optional[CareerRoadmap] = None
    error: Optional[str] = None


@dataclass
class MatchAnalysisRequest:
    """Request model for job match analysis."""
    user_profile: Dict[str, Any]
    job_posting: Dict[str, Any]


@dataclass
class MatchAnalysisResponse:
    """Response model for job match analysis."""
    success: bool
    analysis: Optional[MatchAnalysis] = None
    error: Optional[str] = None
