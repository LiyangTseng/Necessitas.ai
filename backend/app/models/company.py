"""
Company Models

Data models for company information, funding, and company-related functionality.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from .base import CompanySize, Industry


@dataclass
class CompanyInfo:
    """Standardized company information."""
    company_id: str
    name: str
    description: str
    website: str
    founded_year: Optional[str] = None
    employee_count: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    categories: List[str] = None
    funding_total: Optional[int] = None
    last_funding_date: Optional[str] = None
    status: Optional[str] = None
    social_links: Dict[str, str] = None
    key_people: List[Dict[str, str]] = None
    technologies: List[str] = None
    company_size: Optional[str] = None
    growth_stage: Optional[str] = None
    revenue_range: Optional[str] = None
    headquarters: Optional[str] = None
    remote_policy: Optional[str] = None
    benefits: List[str] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.social_links is None:
            self.social_links = {}
        if self.key_people is None:
            self.key_people = []
        if self.technologies is None:
            self.technologies = []
        if self.benefits is None:
            self.benefits = []


@dataclass
class FundingRound:
    """Standardized funding information."""
    round_name: str
    announced_date: str
    money_raised: int
    money_raised_currency: str = "USD"
    investors: List[str] = None
    round_type: str = ""
    valuation: Optional[int] = None

    def __post_init__(self):
        if self.investors is None:
            self.investors = []


@dataclass
class CompanySearchResult:
    """Company search result with metadata."""
    companies: List[CompanyInfo]
    total_count: int
    page: int
    limit: int
    sources_used: List[str]
    search_time_ms: float


@dataclass
class CompanyReview:
    """Company review from employees or external sources."""
    review_id: str
    company_id: str
    rating: float  # 1-5 stars
    title: str
    review_text: str
    reviewer_role: str = ""
    reviewer_experience: str = ""  # e.g., "2 years"
    pros: List[str] = None
    cons: List[str] = None
    work_life_balance: float = 0.0
    culture: float = 0.0
    management: float = 0.0
    compensation: float = 0.0
    career_opportunities: float = 0.0
    source: str = "unknown"
    review_date: datetime = None

    def __post_init__(self):
        if self.pros is None:
            self.pros = []
        if self.cons is None:
            self.cons = []
        if self.review_date is None:
            self.review_date = datetime.now()


@dataclass
class CompanyCulture:
    """Company culture and values information."""
    company_id: str
    values: List[str] = None
    mission: str = ""
    vision: str = ""
    culture_description: str = ""
    diversity_initiatives: List[str] = None
    work_environment: str = ""
    remote_work_policy: str = ""
    flexible_hours: bool = False
    team_size: str = ""
    collaboration_style: str = ""

    def __post_init__(self):
        if self.values is None:
            self.values = []
        if self.diversity_initiatives is None:
            self.diversity_initiatives = []


@dataclass
class CompanyBenefits:
    """Company benefits and perks."""
    company_id: str
    health_insurance: bool = False
    dental_insurance: bool = False
    vision_insurance: bool = False
    retirement_401k: bool = False
    stock_options: bool = False
    paid_time_off: int = 0
    sick_leave: int = 0
    parental_leave: int = 0
    flexible_schedule: bool = False
    remote_work: bool = False
    professional_development: bool = False
    gym_membership: bool = False
    free_meals: bool = False
    transportation: bool = False
    other_perks: List[str] = None

    def __post_init__(self):
        if self.other_perks is None:
            self.other_perks = []


@dataclass
class CompanyNews:
    """Company news and updates."""
    news_id: str
    company_id: str
    title: str
    content: str
    published_date: datetime
    source: str
    url: str = ""
    category: str = ""  # funding, product, hiring, etc.
    sentiment: str = "neutral"  # positive, negative, neutral
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
