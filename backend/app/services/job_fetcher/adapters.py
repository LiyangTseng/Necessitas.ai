"""
Job Data Adapters

Concrete implementations of job data adapters for different sources.
"""

import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from .base_adapter import JobDataAdapter
from .models import JobPosting, WorkType, ExperienceLevel
from app.core.config import settings


class IndeedJobAdapter(JobDataAdapter):
    """Indeed job data adapter."""

    def __init__(self, api_key: str = None):
        """Initialize Indeed adapter."""
        self.api_key = api_key or settings.indeed_api_key
        self.base_url = "https://api.indeed.com/v1"
        self.headers = (
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            if self.api_key
            else {}
        )

    @property
    def source_name(self) -> str:
        return "indeed"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    async def search_jobs(
        self, query: str, location: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> List[JobPosting]:
        """Search jobs on Indeed."""
        if not self.is_available:
            raise Exception("Indeed API key not configured")

        try:
            params = {
                "q": query,
                "l": location or "",
                "limit": limit,
                "start": (page - 1) * limit,
                "fromage": 30,  # Last 30 days
                "sort": "date",
                "format": "json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobs",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_jobs(data)
                else:
                    logger.error(f"Indeed API error: {response.status_code}")
                    raise Exception(f"Indeed API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to search jobs on Indeed: {str(e)}")
            raise

    async def get_job_details(self, job_id: str) -> JobPosting:
        """Get detailed job information from Indeed."""
        if not self.is_available:
            raise Exception("Indeed API key not configured")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobs/{job_id}", headers=self.headers, timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_job_details(data)
                else:
                    logger.error(
                        f"Indeed job details API error: {response.status_code}"
                    )
                    raise Exception(
                        f"Indeed job details API error: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"Failed to get job details from Indeed: {str(e)}")
            raise

    async def get_company_jobs(
        self, company_name: str, limit: int = 10
    ) -> List[JobPosting]:
        """Get jobs from a specific company on Indeed."""
        return await self.search_jobs(f"company:{company_name}", limit=limit)

    def _parse_jobs(self, data: Dict[str, Any]) -> List[JobPosting]:
        """Parse job data from Indeed API response."""
        try:
            results = data.get("results", [])
            jobs = []

            for result in results:
                job = JobPosting(
                    job_id=f"indeed_{result.get('jobkey', '')}",
                    title=result.get("jobtitle", ""),
                    company=result.get("company", ""),
                    location=result.get("formattedLocation", ""),
                    remote="remote" in result.get("formattedLocation", "").lower(),
                    description=result.get("snippet", ""),
                    requirements=self._extract_requirements(result.get("snippet", "")),
                    work_type=WorkType.FULL_TIME,  # Default
                    experience_level=ExperienceLevel.MID,  # Default
                    posted_date=datetime.now() - timedelta(days=1),
                    application_url=result.get("url", ""),
                    source="indeed",
                )
                jobs.append(job)

            return jobs
        except Exception as e:
            logger.error(f"Failed to parse Indeed jobs: {str(e)}")
            return []

    def _parse_job_details(self, data: Dict[str, Any]) -> JobPosting:
        """Parse detailed job information from Indeed."""
        try:
            return JobPosting(
                job_id=f"indeed_{data.get('jobkey', '')}",
                title=data.get("jobtitle", ""),
                company=data.get("company", ""),
                location=data.get("formattedLocation", ""),
                remote="remote" in data.get("formattedLocation", "").lower(),
                description=data.get("snippet", ""),
                requirements=self._extract_requirements(data.get("snippet", "")),
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.MID,
                posted_date=datetime.now(),
                application_url=data.get("url", ""),
                source="indeed",
            )
        except Exception as e:
            logger.error(f"Failed to parse Indeed job details: {str(e)}")
            raise

    def _extract_requirements(self, description: str) -> List[str]:
        """Extract job requirements from description."""
        common_requirements = [
            "Python",
            "JavaScript",
            "React",
            "Node.js",
            "AWS",
            "Docker",
            "Kubernetes",
            "SQL",
            "MongoDB",
            "PostgreSQL",
            "Git",
            "Agile",
            "Machine Learning",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
        ]

        requirements = []
        description_lower = description.lower()

        for req in common_requirements:
            if req.lower() in description_lower:
                requirements.append(req)

        return requirements


class LinkedInJobAdapter(JobDataAdapter):
    """LinkedIn job data adapter."""

    def __init__(self, api_key: str = None):
        """Initialize LinkedIn adapter."""
        self.api_key = api_key or settings.linkedin_api_key
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = (
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            if self.api_key
            else {}
        )

    @property
    def source_name(self) -> str:
        return "linkedin"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    async def search_jobs(
        self, query: str, location: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> List[JobPosting]:
        """Search jobs on LinkedIn."""
        if not self.is_available:
            raise Exception("LinkedIn API key not configured")

        try:
            params = {
                "keywords": query,
                "locationName": location or "",
                "count": limit,
                "start": (page - 1) * limit,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobSearch",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_linkedin_jobs(data)
                else:
                    logger.error(f"LinkedIn API error: {response.status_code}")
                    raise Exception(f"LinkedIn API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to search jobs on LinkedIn: {str(e)}")
            raise

    async def get_job_details(self, job_id: str) -> JobPosting:
        """Get detailed job information from LinkedIn."""
        if not self.is_available:
            raise Exception("LinkedIn API key not configured")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobs/{job_id}", headers=self.headers, timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_linkedin_job_details(data)
                else:
                    logger.error(
                        f"LinkedIn job details API error: {response.status_code}"
                    )
                    raise Exception(
                        f"LinkedIn job details API error: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"Failed to get job details from LinkedIn: {str(e)}")
            raise

    async def get_company_jobs(
        self, company_name: str, limit: int = 10
    ) -> List[JobPosting]:
        """Get jobs from a specific company on LinkedIn."""
        return await self.search_jobs(f"company:{company_name}", limit=limit)

    def _parse_linkedin_jobs(self, data: Dict[str, Any]) -> List[JobPosting]:
        """Parse job data from LinkedIn API response."""
        try:
            elements = data.get("elements", [])
            jobs = []

            for element in elements:
                job_data = element.get("jobPosting", {})

                job = JobPosting(
                    job_id=f"linkedin_{element.get('id', '')}",
                    title=job_data.get("title", ""),
                    company=job_data.get("companyDetails", {})
                    .get("company", {})
                    .get("name", ""),
                    location=job_data.get("formattedLocation", ""),
                    remote="remote" in job_data.get("formattedLocation", "").lower(),
                    description=job_data.get("description", {}).get("text", ""),
                    requirements=self._extract_requirements(
                        job_data.get("description", {}).get("text", "")
                    ),
                    work_type=self._parse_work_type(job_data.get("employmentType", "")),
                    experience_level=self._parse_experience_level(
                        job_data.get("experienceLevel", "")
                    ),
                    posted_date=datetime.now(),
                    application_url=job_data.get("applyMethod", {}).get(
                        "companyApplyUrl", ""
                    ),
                    source="linkedin",
                )
                jobs.append(job)

            return jobs
        except Exception as e:
            logger.error(f"Failed to parse LinkedIn jobs: {str(e)}")
            return []

    def _parse_linkedin_job_details(self, data: Dict[str, Any]) -> JobPosting:
        """Parse detailed job information from LinkedIn."""
        try:
            job_data = data.get("jobPosting", {})

            return JobPosting(
                job_id=f"linkedin_{data.get('id', '')}",
                title=job_data.get("title", ""),
                company=job_data.get("companyDetails", {})
                .get("company", {})
                .get("name", ""),
                location=job_data.get("formattedLocation", ""),
                remote="remote" in job_data.get("formattedLocation", "").lower(),
                description=job_data.get("description", {}).get("text", ""),
                requirements=self._extract_requirements(
                    job_data.get("description", {}).get("text", "")
                ),
                work_type=self._parse_work_type(job_data.get("employmentType", "")),
                experience_level=self._parse_experience_level(
                    job_data.get("experienceLevel", "")
                ),
                posted_date=datetime.now(),
                application_url=job_data.get("applyMethod", {}).get(
                    "companyApplyUrl", ""
                ),
                source="linkedin",
            )
        except Exception as e:
            logger.error(f"Failed to parse LinkedIn job details: {str(e)}")
            raise

    def _extract_requirements(self, description: str) -> List[str]:
        """Extract job requirements from description."""
        common_requirements = [
            "Python",
            "JavaScript",
            "React",
            "Node.js",
            "AWS",
            "Docker",
            "Kubernetes",
            "SQL",
            "MongoDB",
            "PostgreSQL",
            "Git",
            "Agile",
            "Machine Learning",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
        ]

        requirements = []
        description_lower = description.lower()

        for req in common_requirements:
            if req.lower() in description_lower:
                requirements.append(req)

        return requirements

    def _parse_work_type(self, employment_type: str) -> WorkType:
        """Parse work type from employment type string."""
        if not employment_type:
            return WorkType.FULL_TIME

        employment_type_lower = employment_type.lower()

        if "part" in employment_type_lower:
            return WorkType.PART_TIME
        elif "contract" in employment_type_lower:
            return WorkType.CONTRACT
        elif "freelance" in employment_type_lower:
            return WorkType.FREELANCE
        elif "intern" in employment_type_lower:
            return WorkType.INTERNSHIP
        else:
            return WorkType.FULL_TIME

    def _parse_experience_level(self, experience_level: str) -> ExperienceLevel:
        """Parse experience level from string."""
        if not experience_level:
            return ExperienceLevel.MID

        experience_lower = experience_level.lower()

        if "entry" in experience_lower or "junior" in experience_lower:
            return ExperienceLevel.ENTRY
        elif "senior" in experience_lower:
            return ExperienceLevel.SENIOR
        elif "lead" in experience_lower:
            return ExperienceLevel.LEAD
        elif "principal" in experience_lower:
            return ExperienceLevel.PRINCIPAL
        elif "executive" in experience_lower:
            return ExperienceLevel.EXECUTIVE
        else:
            return ExperienceLevel.MID


class GreenhouseJobAdapter(JobDataAdapter):
    """Greenhouse job data adapter."""

    def __init__(self, api_key: str = None):
        """Initialize Greenhouse adapter."""
        self.api_key = api_key or settings.greenhouse_api_key
        self.base_url = "https://boards-api.greenhouse.io/v1"
        self.headers = (
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            if self.api_key
            else {}
        )

    @property
    def source_name(self) -> str:
        return "greenhouse"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    async def search_jobs(
        self, query: str, location: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> List[JobPosting]:
        """Search jobs on Greenhouse."""
        if not self.is_available:
            raise Exception("Greenhouse API key not configured")

        try:
            params = {
                "q": query,
                "location": location or "",
                "limit": limit,
                "offset": (page - 1) * limit,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobs",
                    headers=self.headers,
                    params=params,
                    timeout=10.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_greenhouse_jobs(data)
                else:
                    logger.error(f"Greenhouse API error: {response.status_code}")
                    raise Exception(f"Greenhouse API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to search jobs on Greenhouse: {str(e)}")
            raise

    async def get_job_details(self, job_id: str) -> JobPosting:
        """Get detailed job information from Greenhouse."""
        if not self.is_available:
            raise Exception("Greenhouse API key not configured")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobs/{job_id}", headers=self.headers, timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return self._parse_greenhouse_job_details(data)
                else:
                    logger.error(
                        f"Greenhouse job details API error: {response.status_code}"
                    )
                    raise Exception(
                        f"Greenhouse job details API error: {response.status_code}"
                    )

        except Exception as e:
            logger.error(f"Failed to get job details from Greenhouse: {str(e)}")
            raise

    async def get_company_jobs(
        self, company_name: str, limit: int = 10
    ) -> List[JobPosting]:
        """Get jobs from a specific company on Greenhouse."""
        return await self.search_jobs(f"company:{company_name}", limit=limit)

    def _parse_greenhouse_jobs(self, data: Dict[str, Any]) -> List[JobPosting]:
        """Parse job data from Greenhouse API response."""
        try:
            jobs_data = data.get("jobs", [])
            jobs = []

            for job_data in jobs_data:
                job = JobPosting(
                    job_id=f"greenhouse_{job_data.get('id', '')}",
                    title=job_data.get("title", ""),
                    company=job_data.get("company", {}).get("name", ""),
                    location=job_data.get("location", {}).get("name", ""),
                    remote=job_data.get("remote", False),
                    description=job_data.get("content", ""),
                    requirements=self._extract_requirements(
                        job_data.get("content", "")
                    ),
                    work_type=WorkType.FULL_TIME,  # Default
                    experience_level=ExperienceLevel.MID,  # Default
                    posted_date=datetime.now(),
                    application_url=job_data.get("absolute_url", ""),
                    source="greenhouse",
                )
                jobs.append(job)

            return jobs
        except Exception as e:
            logger.error(f"Failed to parse Greenhouse jobs: {str(e)}")
            return []

    def _parse_greenhouse_job_details(self, data: Dict[str, Any]) -> JobPosting:
        """Parse detailed job information from Greenhouse."""
        try:
            return JobPosting(
                job_id=f"greenhouse_{data.get('id', '')}",
                title=data.get("title", ""),
                company=data.get("company", {}).get("name", ""),
                location=data.get("location", {}).get("name", ""),
                remote=data.get("remote", False),
                description=data.get("content", ""),
                requirements=self._extract_requirements(data.get("content", "")),
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.MID,
                posted_date=datetime.now(),
                application_url=data.get("absolute_url", ""),
                source="greenhouse",
            )
        except Exception as e:
            logger.error(f"Failed to parse Greenhouse job details: {str(e)}")
            raise

    def _extract_requirements(self, description: str) -> List[str]:
        """Extract job requirements from description."""
        common_requirements = [
            "Python",
            "JavaScript",
            "React",
            "Node.js",
            "AWS",
            "Docker",
            "Kubernetes",
            "SQL",
            "MongoDB",
            "PostgreSQL",
            "Git",
            "Agile",
            "Machine Learning",
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
        ]

        requirements = []
        description_lower = description.lower()

        for req in common_requirements:
            if req.lower() in description_lower:
                requirements.append(req)

        return requirements


class MockJobAdapter(JobDataAdapter):
    """Mock job data adapter for testing."""

    @property
    def source_name(self) -> str:
        return "mock"

    @property
    def is_available(self) -> bool:
        return True

    async def search_jobs(
        self, query: str, location: Optional[str] = None, limit: int = 20, page: int = 1
    ) -> List[JobPosting]:
        """Get mock job search results."""
        return [
            JobPosting(
                job_id=f"mock_{i}",
                title=f"Mock {query} Position {i}",
                company=f"Mock Company {i}",
                location=location or "San Francisco, CA",
                remote=i % 2 == 0,
                salary_min=80000 + (i * 10000),
                salary_max=120000 + (i * 10000),
                description=f"Mock job description for {query} position {i}",
                requirements=["Python", "JavaScript", "React", "AWS"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.MID,
                posted_date=datetime.now() - timedelta(days=i),
                application_url=f"https://mockcompany{i}.com/jobs/{i}",
                source="mock",
            )
            for i in range(1, limit + 1)
        ]

    async def get_job_details(self, job_id: str) -> JobPosting:
        """Get mock job details."""
        return JobPosting(
            job_id=job_id,
            title="Mock Software Engineer",
            company="Mock Company",
            location="San Francisco, CA",
            remote=True,
            salary_min=100000,
            salary_max=150000,
            description="Mock job description for software engineer position",
            requirements=["Python", "JavaScript", "React", "AWS"],
            work_type=WorkType.FULL_TIME,
            experience_level=ExperienceLevel.MID,
            posted_date=datetime.now(),
            application_url="https://mockcompany.com/jobs/1",
            source="mock",
        )

    async def get_company_jobs(
        self, company_name: str, limit: int = 10
    ) -> List[JobPosting]:
        """Get mock company jobs."""
        return await self.search_jobs(f"company:{company_name}", limit=limit)
