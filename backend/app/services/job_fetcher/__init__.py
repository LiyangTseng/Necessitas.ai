"""
Job Fetcher Service

Unified service for fetching job postings from Adzuna API.
"""

from .service import JobFetcher
from .adapters import AdzunaJobAdapter
from .models import JobPosting

__all__ = [
    "JobFetcher",
    "AdzunaJobAdapter",
    "JobPosting",
]
