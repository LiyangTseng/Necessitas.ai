"""
Job Fetcher Service

Unified service for fetching job postings from Adzuna API.
"""

from services.job_fetcher.service import JobFetcher
from services.job_fetcher.adapters import AdzunaJobAdapter
from models.job import JobPosting, JobSearchResult

__all__ = [
    "JobFetcher",
    "AdzunaJobAdapter",
    "JobPosting",
    "JobSearchResult"
]
