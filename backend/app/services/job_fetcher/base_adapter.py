"""
Base Adapter for Job Data Sources

Abstract base class for job data adapters.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from models import JobPosting


class JobDataAdapter(ABC):
    """Abstract adapter for job data sources."""

    @abstractmethod
    def search_jobs(
        self, query: str, location: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> List[JobPosting]:
        """Search for jobs."""
        pass

    @abstractmethod
    def get_job_details(self, job_id: str) -> JobPosting:
        """Get detailed job information."""
        pass

    @abstractmethod
    def get_company_jobs(
        self, company_name: str, limit: int = 10
    ) -> List[JobPosting]:
        """Get jobs from a specific company."""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Get the name of this data source."""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this adapter is available."""
        pass
