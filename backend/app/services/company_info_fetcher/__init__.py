"""
Company Info Fetcher Service

Unified service for fetching company information from multiple sources.
Uses adapter pattern to support different data providers.
"""

from .service import CompanyInfoFetcher
from .adapters import (
    CrunchbaseCompanyAdapter,
    MockCompanyAdapter,
)
from models import CompanyInfo, FundingRound

__all__ = [
    "CompanyInfoFetcher",
    "CrunchbaseCompanyAdapter",
    "MockCompanyAdapter",
    "CompanyInfo",
    "FundingRound",
]
