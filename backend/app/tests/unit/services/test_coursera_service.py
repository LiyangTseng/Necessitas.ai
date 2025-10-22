"""
Unit tests for Coursera service.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.services.coursera_service import CourseraService
from app.models.coursera import CourseSearchRequest, CertificationSearchRequest


class TestCourseraService(unittest.TestCase):
    """Test cases for Coursera service."""

    def setUp(self):
        self.coursera_service = CourseraService()

    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        self.assertIsNotNone(self.coursera_service)
        self.assertIsNotNone(self.coursera_service.base_url)
        self.assertIsNotNone(self.coursera_service.headers)

    def test_service_availability(self):
        """Test service availability check."""
        # Service should be available if RapidAPI key is set
        # In test environment, it might not be available
        self.assertIsInstance(self.coursera_service.is_available, bool)

    @patch('app.services.coursera_service.httpx.AsyncClient')
    async def test_search_courses_mock(self, mock_client):
        """Test course search with mocked API response."""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'courses': [
                {
                    'id': 'test-1',
                    'title': 'Test Course',
                    'description': 'A test course',
                    'url': 'https://coursera.org/test',
                    'institution': 'Test University',
                    'level': 'beginner',
                    'type': 'course',
                    'language': 'en',
                    'skills': ['python', 'programming'],
                    'is_free': True
                }
            ],
            'total': 1
        }
        mock_response.raise_for_status.return_value = None
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        # Test the search
        request = CourseSearchRequest(
            query="python",
            skills=["programming"],
            limit=5
        )
        
        response = await self.coursera_service.search_courses(request)
        
        self.assertIsNotNone(response)
        self.assertEqual(len(response.courses), 1)
        self.assertEqual(response.courses[0].title, "Test Course")

    async def test_search_courses_mock_data(self):
        """Test course search with mock data (when API is not available)."""
        request = CourseSearchRequest(
            query="python",
            skills=["programming"],
            limit=2
        )
        
        response = await self.coursera_service.search_courses(request)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response.courses, list)
        # Should return mock data when API is not available
        if not self.coursera_service.is_available:
            self.assertGreater(len(response.courses), 0)

    async def test_search_certifications_mock_data(self):
        """Test certification search with mock data."""
        request = CertificationSearchRequest(
            query="data science",
            skills=["python", "machine learning"],
            limit=2
        )
        
        response = await self.coursera_service.search_certifications(request)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response.certifications, list)

    async def test_get_learning_recommendations(self):
        """Test learning recommendations generation."""
        user_id = "test_user"
        skill_gaps = ["python", "machine learning", "data analysis"]
        target_role = "Data Scientist"
        
        recommendations = await self.coursera_service.get_learning_recommendations(
            user_id=user_id,
            skill_gaps=skill_gaps,
            target_role=target_role
        )
        
        self.assertIsNotNone(recommendations)
        self.assertEqual(recommendations.user_id, user_id)
        self.assertEqual(recommendations.target_role, target_role)
        self.assertEqual(recommendations.skill_gaps, skill_gaps)
        self.assertIsInstance(recommendations.recommended_courses, list)
        self.assertIsInstance(recommendations.recommended_certifications, list)

    def test_parse_courses(self):
        """Test course parsing from API response."""
        raw_courses = [
            {
                'id': 'test-1',
                'title': 'Test Course',
                'description': 'A test course',
                'url': 'https://coursera.org/test',
                'institution': 'Test University',
                'level': 'beginner',
                'type': 'course',
                'language': 'en',
                'skills': ['python'],
                'is_free': True
            }
        ]
        
        courses = self.coursera_service._parse_courses(raw_courses)
        
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0].title, "Test Course")
        self.assertEqual(courses[0].institution, "Test University")

    def test_parse_certifications(self):
        """Test certification parsing from API response."""
        raw_certs = [
            {
                'id': 'cert-1',
                'name': 'Test Certification',
                'description': 'A test certification',
                'url': 'https://coursera.org/cert',
                'institution': 'Test University',
                'type': 'professional_certificate',
                'skills': ['python', 'data science'],
                'is_free': False,
                'price': 49.0
            }
        ]
        
        certifications = self.coursera_service._parse_certifications(raw_certs)
        
        self.assertEqual(len(certifications), 1)
        self.assertEqual(certifications[0].name, "Test Certification")
        self.assertEqual(certifications[0].institution, "Test University")

    def test_create_learning_path(self):
        """Test learning path creation."""
        skill_gaps = ["python", "machine learning", "data analysis"]
        courses = []
        certifications = []
        
        learning_path = self.coursera_service._create_learning_path(
            skill_gaps, courses, certifications
        )
        
        self.assertIsInstance(learning_path, list)

    def test_estimate_completion_time(self):
        """Test completion time estimation."""
        courses = []
        certifications = []
        
        time_weeks = self.coursera_service._estimate_completion_time(courses, certifications)
        
        self.assertIsInstance(time_weeks, int)
        self.assertGreaterEqual(time_weeks, 0)


if __name__ == '__main__':
    # Run async tests
    async def run_async_tests():
        test_instance = TestCourseraService()
        test_instance.setUp()
        
        await test_instance.test_search_courses_mock_data()
        await test_instance.test_search_certifications_mock_data()
        await test_instance.test_get_learning_recommendations()
        
        print("All async tests passed!")
    
    asyncio.run(run_async_tests())
