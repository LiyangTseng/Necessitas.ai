"""
Job Data Adapters

Concrete implementations of job data adapters for different sources.
"""

# app/services/job_fetcher/adapters/adzuna_adapter.py
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from services.job_fetcher.base_adapter import JobDataAdapter
from models.job import JobPosting, WorkType, ExperienceLevel
from core.config import settings

logger = logging.getLogger(__name__)

class AdzunaJobAdapter(JobDataAdapter):
    """Adzuna job data adapter."""

    def __init__(self, app_id: str = None, app_key: str = None, country: str = "us"):
        """Initialize Adzuna adapter."""
        self.app_id = app_id or settings.adzuna_app_id
        self.app_key = app_key or settings.adzuna_app_key
        self.country = country
        self.base_url = f"https://api.adzuna.com/v1/api/jobs/us"
        self.headers = {"Content-Type": "application/json"}

    @property
    def source_name(self) -> str:
        return "adzuna"

    @property
    def is_available(self) -> bool:
        return bool(self.app_id and self.app_key)

    def search_jobs(
        self, query: str, location: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> List[JobPosting]:
        """Search jobs on Adzuna."""
        if not self.is_available:
            raise Exception("Adzuna API credentials not configured")

        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": limit,
            "what": query,
            # "page": page,
            # "content-type": "application/json",
        }
        if location:
            params["where"] = location

        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/search/{page}", params=params, timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_adzuna_jobs(data)
                else:
                    logger.error(f"Adzuna API error {response.status_code}: {response.text}")
                    raise Exception(f"Adzuna API error {response.status_code}: {response.text}")

        except Exception as e:
            logger.error(f"Failed to fetch jobs from Adzuna: {str(e)}")
            raise

    def get_job_details(self, job_id: str) -> JobPosting:
        """Adzuna doesn't provide a dedicated job details endpoint; simulate by search."""
        try:
            search_id = job_id.replace("adzuna_", "")
            jobs = self.search_jobs(search_id)
            return jobs[0] if jobs else None
        except Exception as e:
            logger.error(f"Failed to get Adzuna job details: {str(e)}")
            raise

    def get_company_jobs(
        self, company_name: str, limit: int = 10
    ) -> List[JobPosting]:
        """Get jobs from a specific company."""
        return self.search_jobs(query=f"company:{company_name}", limit=limit)

    def _parse_adzuna_jobs(self, data: Dict[str, Any]) -> List[JobPosting]:
        """Parse Adzuna API job data into JobPosting models."""
        jobs = []
        try:
            for item in data.get("results", []):
                job = JobPosting(
                    job_id=f"adzuna_{item.get('id', '')}",
                    title=item.get("title", ""),
                    company=item.get("company", {}).get("display_name", ""),
                    location=item.get("location", {}).get("display_name", ""),
                    remote=self._detect_remote(item),
                    description=item.get("description", ""),
                    requirements=self._extract_requirements(item.get("description", "")),
                    work_type=self._parse_work_type(item.get("contract_type", "")),
                    experience_level=self._parse_experience_level(
                        item.get("category", {}).get("label", "")
                    ),
                    posted_date=datetime.fromtimestamp(
                        item.get("created", datetime.now().timestamp())
                    )
                    if isinstance(item.get("created"), (int, float))
                    else datetime.now(),
                    application_url=item.get("redirect_url", ""),
                    source="adzuna",
                )
                jobs.append(job)
        except Exception as e:
            logger.error(f"Failed to parse Adzuna jobs: {str(e)}")

        return jobs

    def _detect_remote(self, item: Dict[str, Any]) -> bool:
        """Detect if the job may be remote based on description."""
        desc = (item.get("description") or "").lower()
        loc = (item.get("location", {}).get("display_name") or "").lower()
        return "remote" in desc or "remote" in loc

    def _extract_requirements(self, description: str) -> List[str]:
        """Extract skills from job description."""
        common_requirements = [
            "Python", "Java", "C++", "JavaScript", "React", "Node.js",
            "AWS", "Docker", "Kubernetes", "SQL", "Linux", "TensorFlow", "PyTorch"
        ]

        found = []
        desc_lower = description.lower()
        for skill in common_requirements:
            if skill.lower() in desc_lower:
                found.append(skill)
        return found

    def _parse_work_type(self, contract_type: str) -> WorkType:
        """Map Adzuna contract type to internal WorkType enum."""
        if not contract_type:
            return WorkType.FULL_TIME
        lower = contract_type.lower()
        if "part" in lower:
            return WorkType.PART_TIME
        elif "contract" in lower:
            return WorkType.CONTRACT
        elif "intern" in lower:
            return WorkType.INTERNSHIP
        elif "freelance" in lower:
            return WorkType.FREELANCE
        return WorkType.FULL_TIME

    def _parse_experience_level(self, category_label: str) -> ExperienceLevel:
        """Estimate experience level from category or label."""
        if not category_label:
            return ExperienceLevel.MID
        label = category_label.lower()
        if "junior" in label or "entry" in label:
            return ExperienceLevel.ENTRY
        elif "senior" in label:
            return ExperienceLevel.SENIOR
        elif "lead" in label:
            return ExperienceLevel.LEAD
        elif "executive" in label:
            return ExperienceLevel.EXECUTIVE
        return ExperienceLevel.MID
