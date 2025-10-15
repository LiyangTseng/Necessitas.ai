"""
Company Info Fetcher Models

Data models for company information and funding.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


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
