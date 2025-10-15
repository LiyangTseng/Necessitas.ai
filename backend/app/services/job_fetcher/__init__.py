"""
Job Fetcher Service

Unified service for fetching job postings from multiple sources.
Uses adapter pattern to support different job platforms.
"""

from .service import JobFetcher
from .adapters import (
    IndeedJobAdapter,
    LinkedInJobAdapter,
    GreenhouseJobAdapter,
    MockJobAdapter,
)
from .models import JobPosting, JobSearchResult

__all__ = [
    "JobFetcher",
    "IndeedJobAdapter",
    "LinkedInJobAdapter",
    "GreenhouseJobAdapter",
    "MockJobAdapter",
    "JobPosting",
    "JobSearchResult",
]
