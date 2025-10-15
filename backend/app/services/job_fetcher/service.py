"""
Job Fetcher Service

Main service class that orchestrates job data retrieval from multiple sources.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from .base_adapter import JobDataAdapter
from .adapters import (
    IndeedJobAdapter,
    LinkedInJobAdapter,
    GreenhouseJobAdapter,
    MockJobAdapter,
)
from .models import JobPosting, JobSearchResult, JobMatchScore
from app.core.config import settings


class JobFetcher:
    """Unified service for job data retrieval."""

    def __init__(self):
        """Initialize the job fetcher."""
        self.adapters: Dict[str, JobDataAdapter] = {}
        self._setup_adapters()

    def _setup_adapters(self):
        """Setup available adapters."""
        # Add Indeed adapter
        try:
            indeed_adapter = IndeedJobAdapter()
            if indeed_adapter.is_available:
                self.adapters["indeed"] = indeed_adapter
                logger.info("Indeed adapter initialized")
            else:
                logger.warning("Indeed adapter not available - API key missing")
        except Exception as e:
            logger.warning(f"Failed to setup Indeed adapter: {e}")

        # Add LinkedIn adapter
        try:
            linkedin_adapter = LinkedInJobAdapter()
            if linkedin_adapter.is_available:
                self.adapters["linkedin"] = linkedin_adapter
                logger.info("LinkedIn adapter initialized")
            else:
                logger.warning("LinkedIn adapter not available - API key missing")
        except Exception as e:
            logger.warning(f"Failed to setup LinkedIn adapter: {e}")

        # Add Greenhouse adapter
        try:
            greenhouse_adapter = GreenhouseJobAdapter()
            if greenhouse_adapter.is_available:
                self.adapters["greenhouse"] = greenhouse_adapter
                logger.info("Greenhouse adapter initialized")
            else:
                logger.warning("Greenhouse adapter not available - API key missing")
        except Exception as e:
            logger.warning(f"Failed to setup Greenhouse adapter: {e}")

        # Always add mock adapter as fallback
        self.adapters["mock"] = MockJobAdapter()
        logger.info("Mock adapter initialized as fallback")

    async def search_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
        sources: List[str] = None,
    ) -> JobSearchResult:
        """
        Search for jobs across multiple sources.

        Args:
            query: Search query
            location: Optional location filter
            limit: Number of results per page
            page: Page number
            sources: List of sources to search (None = all available)

        Returns:
            Job search results with metadata
        """
        start_time = datetime.now()

        try:
            if sources is None:
                # Use all available sources except mock
                sources = [
                    name for name, adapter in self.adapters.items() if name != "mock"
                ]
                if not sources:
                    sources = ["mock"]

            all_jobs = []
            sources_used = []

            for source in sources:
                if source in self.adapters:
                    try:
                        logger.info(f"Searching jobs on {source}")
                        jobs = await self.adapters[source].search_jobs(
                            query, location, limit // len(sources), page
                        )
                        all_jobs.extend(jobs)
                        sources_used.append(source)
                    except Exception as e:
                        logger.warning(f"Failed to search jobs on {source}: {e}")
                        continue

            # Deduplicate and limit results
            unique_jobs = self._deduplicate_jobs(all_jobs)[:limit]

            search_time = (datetime.now() - start_time).total_seconds() * 1000

            return JobSearchResult(
                jobs=unique_jobs,
                total_count=len(unique_jobs),
                page=page,
                limit=limit,
                sources_used=sources_used,
                search_time_ms=search_time,
                filters_applied={
                    "query": query,
                    "location": location,
                    "sources": sources,
                },
            )

        except Exception as e:
            logger.error(f"Failed to search jobs: {str(e)}")
            # Return empty result instead of raising
            return JobSearchResult(
                jobs=[],
                total_count=0,
                page=page,
                limit=limit,
                sources_used=[],
                search_time_ms=0,
                filters_applied={
                    "query": query,
                    "location": location,
                    "sources": sources,
                },
            )

    async def get_job_details(self, job_id: str, source: str = "primary") -> JobPosting:
        """
        Get detailed job information.

        Args:
            job_id: Job identifier
            source: Data source to use

        Returns:
            Detailed job information
        """
        try:
            if source == "primary":
                # Try to determine source from job_id
                if job_id.startswith("indeed_"):
                    source = "indeed"
                elif job_id.startswith("linkedin_"):
                    source = "linkedin"
                elif job_id.startswith("greenhouse_"):
                    source = "greenhouse"
                else:
                    source = "mock"

            if source in self.adapters:
                logger.info(f"Getting job details from {source}")
                return await self.adapters[source].get_job_details(job_id)
            else:
                raise Exception(f"Unknown job data source: {source}")

        except Exception as e:
            logger.error(f"Failed to get job details: {str(e)}")
            raise

    async def get_company_jobs(
        self, company_name: str, limit: int = 10, sources: List[str] = None
    ) -> List[JobPosting]:
        """
        Get jobs from a specific company.

        Args:
            company_name: Company name
            limit: Number of results
            sources: List of sources to search

        Returns:
            List of jobs from the company
        """
        try:
            if sources is None:
                sources = [
                    name for name, adapter in self.adapters.items() if name != "mock"
                ]
                if not sources:
                    sources = ["mock"]

            all_jobs = []

            for source in sources:
                if source in self.adapters:
                    try:
                        logger.info(f"Getting company jobs from {source}")
                        jobs = await self.adapters[source].get_company_jobs(
                            company_name, limit // len(sources)
                        )
                        all_jobs.extend(jobs)
                    except Exception as e:
                        logger.warning(f"Failed to get company jobs from {source}: {e}")
                        continue

            return self._deduplicate_jobs(all_jobs)[:limit]

        except Exception as e:
            logger.error(f"Failed to get company jobs: {str(e)}")
            return []

    async def calculate_job_match_score(
        self, user_skills: List[str], job_requirements: List[str]
    ) -> JobMatchScore:
        """
        Calculate match score between user skills and job requirements.

        Args:
            user_skills: List of user skills
            job_requirements: List of job requirements

        Returns:
            Job match score and analysis
        """
        try:
            user_skills_lower = [skill.lower() for skill in user_skills]
            job_requirements_lower = [req.lower() for req in job_requirements]

            # Calculate skill matches
            skill_matches = list(set(user_skills_lower) & set(job_requirements_lower))
            skill_gaps = list(set(job_requirements_lower) - set(user_skills_lower))

            # Calculate match score
            if not job_requirements_lower:
                match_score = 0.0
            else:
                match_score = len(skill_matches) / len(job_requirements_lower)

            # Generate reasons
            reasons = []
            if skill_matches:
                reasons.append(f"Strong match in skills: {', '.join(skill_matches)}")
            if skill_gaps:
                reasons.append(f"Missing skills: {', '.join(skill_gaps[:3])}")

            return JobMatchScore(
                job_id="",  # Will be set by caller
                match_score=match_score,
                skill_matches=skill_matches,
                skill_gaps=skill_gaps,
                location_match=True,  # Default
                salary_match=True,  # Default
                experience_match=True,  # Default
                reasons=reasons,
            )

        except Exception as e:
            logger.error(f"Failed to calculate job match score: {str(e)}")
            return JobMatchScore(
                job_id="",
                match_score=0.0,
                skill_matches=[],
                skill_gaps=[],
                location_match=False,
                salary_match=False,
                experience_match=False,
                reasons=["Error calculating match score"],
            )

    def _deduplicate_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove duplicate jobs based on title and company."""
        seen = set()
        unique_jobs = []

        for job in jobs:
            # Create a key based on title and company
            key = (job.title.lower().strip(), job.company.lower().strip())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs

    def get_available_sources(self) -> List[str]:
        """Get list of available data sources."""
        return [name for name, adapter in self.adapters.items() if adapter.is_available]

    def get_source_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available sources."""
        info = {}
        for name, adapter in self.adapters.items():
            info[name] = {
                "name": adapter.source_name,
                "available": adapter.is_available,
                "type": "external" if name != "mock" else "mock",
            }
        return info
