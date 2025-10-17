"""
Job Fetcher Service
Handles job data retrieval from the Adzuna API.
"""

from typing import List, Optional
from datetime import datetime
from loguru import logger

from .adapters import AdzunaJobAdapter
from .models import JobPosting, JobMatchScore


class JobFetcher:
    """Service for retrieving job data from Adzuna."""

    def __init__(self):
        """Initialize the Adzuna adapter."""
        try:
            self.adapter = AdzunaJobAdapter()
            if not self.adapter.is_available:
                logger.warning("Adzuna adapter not available - missing credentials.")
        except Exception as e:
            logger.error(f"Failed to initialize Adzuna adapter: {e}")
            raise

    async def search_jobs(
        self, query: str, location: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> List[JobPosting]:
        """
        Search for jobs using the Adzuna API.

        Args:
            query: Search keyword (e.g., "software engineer").
            location: Optional location filter.
            limit: Number of results to return.
            page: Page number.

        Returns:
            A list of JobPosting objects.
        """
        start_time = datetime.now()
        try:
            logger.info(f"Searching Adzuna for '{query}' in {location or 'all locations'}")
            jobs = await self.adapter.search_jobs(query, location, limit, page)
            logger.info(f"Fetched {len(jobs)} jobs from Adzuna in {(datetime.now() - start_time).total_seconds()*1000:.2f} ms")
            return self._deduplicate_jobs(jobs)[:limit]
        except Exception as e:
            logger.error(f"Failed to search jobs from Adzuna: {str(e)}")
            return []

    async def get_job_details(self, job_id: str) -> Optional[JobPosting]:
        """
        Get detailed job information by job ID.

        Args:
            job_id: Unique job identifier (e.g., "adzuna_123456").

        Returns:
            A single JobPosting object, or None if not found.
        """
        try:
            logger.info(f"Fetching Adzuna job details for ID: {job_id}")
            return await self.adapter.get_job_details(job_id)
        except Exception as e:
            logger.error(f"Failed to fetch job details from Adzuna: {str(e)}")
            return None

    async def get_company_jobs(self, company_name: str, limit: int = 10) -> List[JobPosting]:
        """
        Get job postings from a specific company.

        Args:
            company_name: Name of the company.
            limit: Number of job postings to return.

        Returns:
            A list of JobPosting objects.
        """
        try:
            logger.info(f"Fetching Adzuna jobs for company: {company_name}")
            jobs = await self.adapter.get_company_jobs(company_name, limit)
            return self._deduplicate_jobs(jobs)[:limit]
        except Exception as e:
            logger.error(f"Failed to get company jobs from Adzuna: {str(e)}")
            return []

    async def calculate_job_match_score(
        self, user_skills: List[str], job_requirements: List[str]
    ) -> JobMatchScore:
        """
        Calculate how well a user's skills match a job's requirements.

        Args:
            user_skills: List of user's skills.
            job_requirements: List of required skills from job description.

        Returns:
            JobMatchScore object with match percentage and analysis.
        """
        try:
            user_skills_lower = [s.lower() for s in user_skills]
            job_requirements_lower = [r.lower() for r in job_requirements]

            matched = list(set(user_skills_lower) & set(job_requirements_lower))
            missing = list(set(job_requirements_lower) - set(user_skills_lower))

            score = len(matched) / len(job_requirements_lower) if job_requirements_lower else 0.0

            reasons = []
            if matched:
                reasons.append(f"Matched skills: {', '.join(matched)}")
            if missing:
                reasons.append(f"Missing: {', '.join(missing[:3])}")

            return JobMatchScore(
                job_id="",
                match_score=score,
                skill_matches=matched,
                skill_gaps=missing,
                location_match=True,
                salary_match=True,
                experience_match=True,
                reasons=reasons,
            )
        except Exception as e:
            logger.error(f"Failed to calculate match score: {str(e)}")
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
        """Remove duplicate jobs based on (title, company) key."""
        seen = set()
        unique_jobs = []
        for job in jobs:
            key = (job.title.lower().strip(), (job.company or "").lower().strip())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        return unique_jobs
