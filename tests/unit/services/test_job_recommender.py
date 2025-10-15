"""
Unit tests for JobRecommender service using unittest.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, date

from backend.app.services.job_recommender import JobRecommender
from backend.app.models.user_profile import (
    UserProfile,
    Skill,
    CareerPreference,
    JobPosting,
    WorkType,
    ExperienceLevel,
)
from tests.test_utils import AsyncTestCase, MockDataFactory


class TestJobRecommender(AsyncTestCase):
    """Test cases for JobRecommender service."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.job_recommender = None
        self.mock_user_profile = None
        self.mock_job_posting = None

    def create_job_recommender(self):
        """Create JobRecommender instance for testing."""
        with (
            patch("backend.app.services.job_recommender.SentenceTransformer"),
            patch("backend.app.services.job_recommender.TfidfVectorizer"),
        ):
            return JobRecommender()

    def create_mock_user_profile(self):
        """Create mock user profile."""
        return UserProfile(
            user_id="test_user_123",
            skills=[
                Skill(name="Python", level=4, category="Programming"),
                Skill(name="React", level=3, category="Frontend"),
                Skill(name="AWS", level=3, category="Cloud"),
                Skill(name="Machine Learning", level=2, category="AI/ML"),
            ],
            preferences=CareerPreference(
                target_roles=["Senior Software Engineer", "Tech Lead"],
                target_industries=["Technology", "Fintech"],
                salary_range_min=120000,
                salary_range_max=150000,
            ),
        )

    def create_mock_job_posting(self):
        """Create mock job posting."""
        return JobPosting(
            job_id="job_123",
            title="Senior Software Engineer",
            company="TechCorp",
            location="San Francisco, CA",
            remote=True,
            salary_min=130000,
            salary_max=160000,
            description="We're looking for a senior software engineer...",
            requirements=["Python", "React", "AWS", "Machine Learning"],
            preferred_skills=["Docker", "Kubernetes", "Leadership"],
            work_type=WorkType.FULL_TIME,
            experience_level=ExperienceLevel.SENIOR,
            posted_date=datetime.now(),
        )

    def test_get_recommendations_success(self):
        """Test successful job recommendations."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Mock the internal methods
        self.job_recommender._get_user_profile = AsyncMock(
            return_value=self.mock_user_profile
        )
        self.job_recommender._get_available_jobs = AsyncMock(return_value=[Mock()])
        self.job_recommender._calculate_match_score = AsyncMock(return_value=0.8)
        self.job_recommender._get_match_reasons = Mock(
            return_value=["Strong skill match"]
        )
        self.job_recommender._get_skill_matches = Mock(return_value=["Python", "React"])
        self.job_recommender._get_skill_gaps = Mock(return_value=["Leadership"])
        self.job_recommender._check_salary_fit = Mock(return_value=True)
        self.job_recommender._check_location_fit = Mock(return_value=True)
        self.job_recommender._check_experience_fit = Mock(return_value=True)

        # Act
        recommendations = self.run_async(
            self.job_recommender.get_recommendations(
                user_id="test_user_123",
                limit=5,
                location="San Francisco, CA",
                industry="Technology",
            )
        )

        # Assert
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].match_score, 80.0)
        self.assertEqual(recommendations[0].skill_matches, ["Python", "React"])
        self.assertEqual(recommendations[0].skill_gaps, ["Leadership"])

    def test_get_recommendations_no_matches(self):
        """Test job recommendations with no matches."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()

        # Mock the internal methods
        self.job_recommender._get_user_profile = AsyncMock(
            return_value=self.mock_user_profile
        )
        self.job_recommender._get_available_jobs = AsyncMock(return_value=[Mock()])
        self.job_recommender._calculate_match_score = AsyncMock(
            return_value=0.3
        )  # Below threshold

        # Act
        recommendations = self.run_async(
            self.job_recommender.get_recommendations(user_id="test_user_123", limit=5)
        )

        # Assert
        self.assertEqual(len(recommendations), 0)

    def test_analyze_skill_gap_success(self):
        """Test successful skill gap analysis."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()

        # Mock the internal methods
        self.job_recommender._get_user_profile = AsyncMock(
            return_value=self.mock_user_profile
        )
        self.job_recommender._get_role_requirements = AsyncMock(
            return_value={
                "required_skills": ["Python", "React", "AWS", "Leadership"],
                "preferred_skills": ["Docker", "Kubernetes"],
            }
        )
        self.job_recommender._generate_skill_recommendations = Mock(
            return_value=[
                "Focus on learning: Leadership",
                "Take online courses or certifications",
            ]
        )
        self.job_recommender._create_learning_path = Mock(
            return_value=[
                {
                    "skill": "Leadership",
                    "priority": "high",
                    "resources": ["Online course for Leadership"],
                    "timeline": "2-3 months",
                }
            ]
        )

        # Act
        skill_gap = self.run_async(
            self.job_recommender.analyze_skill_gap(
                user_id="test_user_123", target_role="Senior Software Engineer"
            )
        )

        # Assert
        self.assertEqual(skill_gap.user_id, "test_user_123")
        self.assertEqual(skill_gap.target_role, "Senior Software Engineer")
        self.assertIn("Leadership", skill_gap.missing_skills)
        self.assertIn("Python", skill_gap.strong_skills)
        self.assertGreater(len(skill_gap.recommendations), 0)
        self.assertGreater(len(skill_gap.learning_path), 0)

    def test_analyze_skill_gap_default_role(self):
        """Test skill gap analysis with default target role."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()

        # Mock the internal methods
        self.job_recommender._get_user_profile = AsyncMock(
            return_value=self.mock_user_profile
        )
        self.job_recommender._get_role_requirements = AsyncMock(
            return_value={
                "required_skills": ["Python", "JavaScript", "SQL"],
                "preferred_skills": ["AWS", "Docker", "Git"],
            }
        )
        self.job_recommender._generate_skill_recommendations = Mock(return_value=[])
        self.job_recommender._create_learning_path = Mock(return_value=[])

        # Act
        skill_gap = self.run_async(
            self.job_recommender.analyze_skill_gap(user_id="test_user_123")
        )

        # Assert
        self.assertEqual(skill_gap.user_id, "test_user_123")
        self.assertEqual(skill_gap.target_role, "Software Engineer")  # Default role

    def test_calculate_match_score_high_match(self):
        """Test match score calculation with high match."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Act
        match_score = self.job_recommender._calculate_match_score(
            self.mock_user_profile, self.mock_job_posting
        )

        # Assert
        self.assertGreaterEqual(match_score, 0.0)
        self.assertLessEqual(match_score, 1.0)
        self.assertGreater(match_score, 0.5)  # Should be a good match

    def test_calculate_match_score_low_match(self):
        """Test match score calculation with low match."""
        # Arrange
        self.job_recommender = self.create_job_recommender()

        # Create user profile with different skills
        user_profile = UserProfile(
            user_id="test_user_123",
            skills=[
                Skill(name="Java", level=4, category="Programming"),
                Skill(name="Angular", level=3, category="Frontend"),
            ],
            preferences=CareerPreference(
                target_roles=["Java Developer"],
                target_industries=["Technology"],
                salary_range_min=80000,
                salary_range_max=100000,
            ),
        )

        # Create job posting with different requirements
        job_posting = JobPosting(
            job_id="job_123",
            title="Python Developer",
            company="TechCorp",
            location="San Francisco, CA",
            remote=False,
            salary_min=130000,
            salary_max=160000,
            description="Python developer position",
            requirements=["Python", "Django", "PostgreSQL"],
            preferred_skills=["Docker", "Kubernetes"],
            work_type=WorkType.FULL_TIME,
            experience_level=ExperienceLevel.SENIOR,
            posted_date=datetime.now(),
        )

        # Act
        match_score = self.job_recommender._calculate_match_score(
            user_profile, job_posting
        )

        # Assert
        self.assertGreaterEqual(match_score, 0.0)
        self.assertLessEqual(match_score, 1.0)
        self.assertLess(match_score, 0.5)  # Should be a low match

    def test_get_match_reasons(self):
        """Test match reasons generation."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Act
        reasons = self.job_recommender._get_match_reasons(
            self.mock_user_profile, self.mock_job_posting
        )

        # Assert
        self.assertIsInstance(reasons, list)
        self.assertGreater(len(reasons), 0)
        self.assertTrue(any("skill" in reason.lower() for reason in reasons))

    def test_get_skill_matches(self):
        """Test skill matches extraction."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Act
        skill_matches = self.job_recommender._get_skill_matches(
            self.mock_user_profile, self.mock_job_posting
        )

        # Assert
        self.assertIsInstance(skill_matches, list)
        self.assertIn("Python", skill_matches)
        self.assertIn("React", skill_matches)

    def test_get_skill_gaps(self):
        """Test skill gaps extraction."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Act
        skill_gaps = self.job_recommender._get_skill_gaps(
            self.mock_user_profile, self.mock_job_posting
        )

        # Assert
        self.assertIsInstance(skill_gaps, list)
        self.assertIn("Leadership", skill_gaps)

    def test_check_salary_fit(self):
        """Test salary fit checking."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Act
        salary_fit = self.job_recommender._check_salary_fit(
            self.mock_user_profile, self.mock_job_posting
        )

        # Assert
        self.assertIsInstance(salary_fit, bool)
        self.assertTrue(salary_fit)  # Job salary meets user expectations

    def test_check_location_fit(self):
        """Test location fit checking."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Act
        location_fit = self.job_recommender._check_location_fit(
            self.mock_user_profile, self.mock_job_posting
        )

        # Assert
        self.assertIsInstance(location_fit, bool)

    def test_check_experience_fit(self):
        """Test experience fit checking."""
        # Arrange
        self.job_recommender = self.create_job_recommender()
        self.mock_user_profile = self.create_mock_user_profile()
        self.mock_job_posting = self.create_mock_job_posting()

        # Act
        experience_fit = self.job_recommender._check_experience_fit(
            self.mock_user_profile, self.mock_job_posting
        )

        # Assert
        self.assertIsInstance(experience_fit, bool)

    def test_get_role_requirements(self):
        """Test role requirements retrieval."""
        # Arrange
        self.job_recommender = self.create_job_recommender()

        # Act
        requirements = self.run_async(
            self.job_recommender._get_role_requirements("Senior Software Engineer")
        )

        # Assert
        self.assertIsInstance(requirements, dict)
        self.assertIn("required_skills", requirements)
        self.assertIn("preferred_skills", requirements)
        self.assertIsInstance(requirements["required_skills"], list)
        self.assertIsInstance(requirements["preferred_skills"], list)

    def test_generate_skill_recommendations(self):
        """Test skill recommendations generation."""
        # Arrange
        self.job_recommender = self.create_job_recommender()

        # Act
        recommendations = self.job_recommender._generate_skill_recommendations(
            missing_skills=["Leadership", "System Design"],
            developing_skills=["Docker", "Kubernetes"],
        )

        # Assert
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        self.assertTrue(any("Leadership" in rec for rec in recommendations))

    def test_create_learning_path(self):
        """Test learning path creation."""
        # Arrange
        self.job_recommender = self.create_job_recommender()

        # Act
        learning_path = self.job_recommender._create_learning_path(
            ["Leadership", "System Design"]
        )

        # Assert
        self.assertIsInstance(learning_path, list)
        self.assertGreater(len(learning_path), 0)
        self.assertTrue(all("skill" in item for item in learning_path))
        self.assertTrue(all("priority" in item for item in learning_path))
        self.assertTrue(all("resources" in item for item in learning_path))
        self.assertTrue(all("timeline" in item for item in learning_path))

    def test_get_recommendations_exception_handling(self):
        """Test exception handling in get_recommendations."""
        # Arrange
        self.job_recommender = self.create_job_recommender()

        # Mock the internal methods to raise an exception
        self.job_recommender._get_user_profile = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Act
        recommendations = self.run_async(
            self.job_recommender.get_recommendations(user_id="test_user_123", limit=5)
        )

        # Assert
        self.assertEqual(recommendations, [])

    def test_analyze_skill_gap_exception_handling(self):
        """Test exception handling in analyze_skill_gap."""
        # Arrange
        self.job_recommender = self.create_job_recommender()

        # Mock the internal methods to raise an exception
        self.job_recommender._get_user_profile = AsyncMock(
            side_effect=Exception("Database error")
        )

        # Act
        skill_gap = self.run_async(
            self.job_recommender.analyze_skill_gap(
                user_id="test_user_123", target_role="Senior Software Engineer"
            )
        )

        # Assert
        self.assertEqual(skill_gap.user_id, "test_user_123")
        self.assertEqual(skill_gap.target_role, "Senior Software Engineer")
        self.assertEqual(skill_gap.current_skills, [])
        self.assertEqual(skill_gap.required_skills, [])
        self.assertEqual(skill_gap.missing_skills, [])
        self.assertEqual(skill_gap.developing_skills, [])
        self.assertEqual(skill_gap.strong_skills, [])
        self.assertEqual(skill_gap.recommendations, [])
        self.assertEqual(skill_gap.priority_skills, [])
        self.assertEqual(skill_gap.learning_path, [])

    def test_calculate_match_score_exception_handling(self):
        """Test exception handling in calculate_match_score."""
        # Arrange
        self.job_recommender = self.create_job_recommender()

        # Create invalid objects to trigger exception
        user_profile = None
        job_posting = None

        # Act
        match_score = self.job_recommender._calculate_match_score(
            user_profile, job_posting
        )

        # Assert
        self.assertEqual(match_score, 0.5)  # Default moderate match


if __name__ == "__main__":
    unittest.main()
