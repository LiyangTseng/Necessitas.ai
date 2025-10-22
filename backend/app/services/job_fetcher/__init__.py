"""
Job Fetcher Service

Unified service for fetching job postings from Adzuna API.
"""

from .service import JobFetcher
from .adapters import AdzunaJobAdapter
from ..models.job import JobPosting, JobSearchResult

__all__ = [
    "JobFetcher",
    "AdzunaJobAdapter",
    "JobPosting",
    "JobSearchResult"
]
