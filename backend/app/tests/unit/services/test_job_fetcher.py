"""
Unit tests for JobFetcher service using unittest.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.job_fetcher.service import JobFetcher
from app.models.job import JobPosting, WorkType, ExperienceLevel
from app.tests.unit.utils.test_utils import AsyncTestCase, MockDataFactory


class TestJobFetcher(AsyncTestCase):
    """Test cases for JobFetcher service."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.job_fetcher = None
        self.mock_adapter = None

    def create_job_fetcher(self):
        """Create JobFetcher instance for testing."""
        with patch("services.job_fetcher.service.AdzunaJobAdapter") as mock_adapter_class:
            self.mock_adapter = Mock()
            self.mock_adapter.is_available = True
            self.mock_adapter.source_name = "adzuna"
            mock_adapter_class.return_value = self.mock_adapter

            self.job_fetcher = JobFetcher()
            return self.job_fetcher

    def create_mock_job_posting(self, job_id="test_123", title="Software Engineer",
                               company="Test Company", location="San Francisco"):
        """Create a mock JobPosting object."""
        return JobPosting(
            job_id=job_id,
            title=title,
            company=company,
            location=location,
            description="Test job description",
            requirements=["Python", "JavaScript"],
            work_type=WorkType.FULL_TIME,
            experience_level=ExperienceLevel.MID,
            posted_date=datetime.now(),
            source="adzuna"
        )

    def test_search_jobs_success(self):
        """Test successful job search."""
        job_fetcher = self.create_job_fetcher()

        # Mock adapter response
        mock_jobs = [
            self.create_mock_job_posting("job_1", "Python Developer", "Company A"),
            self.create_mock_job_posting("job_2", "JavaScript Developer", "Company B")
        ]
        self.mock_adapter.search_jobs = Mock(return_value=mock_jobs)

        # Test search
        result = job_fetcher.search_jobs("Python Developer", "San Francisco", 10, 1)

        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "Python Developer")
        self.assertEqual(result[1].title, "JavaScript Developer")

        # Verify adapter was called correctly
        self.mock_adapter.search_jobs.assert_called_once_with("Python Developer", "San Francisco", 10, 1)

if __name__ == "__main__":
    unittest.main()
