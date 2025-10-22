"""
Unit tests for Coursera service integration.
"""

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.services.coursera_service import CourseraService
from app.models.coursera import CourseSearchRequest, CertificationSearchRequest, LearningRecommendation


class TestCourseraIntegration(unittest.TestCase):
    """Test cases for Coursera service integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.coursera_service = CourseraService()

    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        self.assertIsNotNone(self.coursera_service)
        self.assertIsNotNone(self.coursera_service.base_url)
        self.assertIsNotNone(self.coursera_service.headers)
        self.assertIsInstance(self.coursera_service.is_available, bool)

    async def test_search_courses_mock_data(self):
        """Test course search with mock data."""
        request = CourseSearchRequest(
            query="python programming",
            skills=["python", "programming"],
            limit=3
        )
        
        response = await self.coursera_service.search_courses(request)
        
        self.assertIsNotNone(response)
        self.assertIsInstance(response.courses, list)
        self.assertIsInstance(response.total_count, int)
        self.assertIsInstance(response.page, int)
        self.assertIsInstance(response.limit, int)
        self.assertIsInstance(response.has_more, bool)

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
        self.assertIsInstance(response.total_count, int)
        self.assertIsInstance(response.page, int)
        self.assertIsInstance(response.limit, int)
        self.assertIsInstance(response.has_more, bool)

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
        self.assertIsInstance(recommendations.learning_path, list)
        self.assertIsInstance(recommendations.estimated_completion_time, (int, type(None)))

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


# Async test runner
async def run_async_tests():
    """Run async tests."""
    test_instance = TestCourseraIntegration()
    test_instance.setUp()
    
    print("Running Coursera integration tests...")
    
    try:
        await test_instance.test_search_courses_mock_data()
        print("Course search test passed")
    except Exception as e:
        print(f"Course search test failed: {e}")
    
    try:
        await test_instance.test_search_certifications_mock_data()
        print("Certification search test passed")
    except Exception as e:
        print(f"Certification search test failed: {e}")
    
    try:
        await test_instance.test_get_learning_recommendations()
        print("Learning recommendations test passed")
    except Exception as e:
        print(f"Learning recommendations test failed: {e}")
    
    print("Coursera integration tests completed!")


if __name__ == "__main__":
    asyncio.run(run_async_tests())
