"""
Unit tests for JobRecommender service using unittest.
"""

import unittest
from datetime import datetime, date
from models.user import UserProfile, Skill, WorkExperience, Education, CareerPreference
from models.job import JobPosting
from models.base import WorkType, ExperienceLevel, LocationPreference, CompanySize, Industry
from models.analysis import MatchAnalysis, DetailedScores
from services.job_matching_engine import JobMatchingEngine

class TestJobMatchingEngine(unittest.TestCase):
    """Test cases for JobMatchingEngine service."""

    def setUp(self):
        self.matching_engine = JobMatchingEngine()

    def test_find_matches(self):
        user_profile = UserProfile(
            user_id="user_001",
            personal_info={
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "location": "San Francisco, CA"
            },
            skills=[
                Skill(name="Python", level=5, category="Programming", years_experience=4),
                Skill(name="JavaScript", level=4, category="Programming", years_experience=3),
                Skill(name="React", level=4, category="Frontend", years_experience=3),
                Skill(name="AWS", level=3, category="Cloud", years_experience=2),
                Skill(name="Docker", level=3, category="DevOps", years_experience=2)
            ],
            work_experience=[
                WorkExperience(
                    title="Senior Software Engineer",
                    company="TechCorp",
                    location="San Francisco, CA",
                    start_date=datetime(2020, 1, 1),
                    end_date=None,
                    current=True,
                    description="Full-stack development with Python and React",
                    achievements=["Led team of 5 developers", "Improved system performance by 40%"]
                )
            ],
            education=[
                Education(
                    degree="Bachelor of Science",
                    institution="Stanford University",
                    field_of_study="Computer Science",
                    graduation_date="2019-06-01"
                )
            ],
            career_preferences=CareerPreference(
                preferred_locations=["San Francisco, CA", "Remote"],
                salary_expectations={"min": 120000, "max": 180000},
                work_type_preferences=[WorkType.FULL_TIME],
                experience_level_preferences=[ExperienceLevel.SENIOR],
                company_size_preferences=[CompanySize.MEDIUM, CompanySize.LARGE],
                industry_preferences=[Industry.TECHNOLOGY]
            )
        )
        job_postings = [
            JobPosting(
                job_id="job_001",
                title="Senior Python Developer",
                company="InnovateTech",
                location="San Francisco, CA",
                remote=True,
                salary_min=130000,
                salary_max=170000,
                description="We're looking for a senior Python developer with React experience...",
                requirements=["Python", "JavaScript", "React", "AWS", "Docker"],
                preferred_skills=["FastAPI", "PostgreSQL", "Kubernetes"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.SENIOR,
            ),
            JobPosting(
                job_id="job_002",
                title="Senior Java Developer",
                company="InnovateTech",
                location="San Francisco, CA",
                remote=True,
                salary_min=130000,
                salary_max=170000,
                description="We're looking for a senior Java developer with React experience...",
                requirements=["Java", "Spring", "React", "AWS", "Docker"],
                preferred_skills=["Spring Boot", "PostgreSQL", "Kubernetes"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.SENIOR,
            ),
            JobPosting(
                job_id="job_003",
                title="Senior Full Stack Developer",
                company="InnovateTech",
                location="San Francisco, CA",
                remote=True,
                salary_min=130000,
                salary_max=170000,
                description="We're looking for a senior full stack developer with React experience...",
                requirements=["Python", "JavaScript", "React", "AWS", "Docker"],
                preferred_skills=["FastAPI", "PostgreSQL", "Kubernetes"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.SENIOR,
            ),
            JobPosting(
                job_id="job_004",
                title="Senior Data Scientist",
                company="InnovateTech",
                location="San Francisco, CA",
                remote=True,
                salary_min=130000,
                salary_max=170000,
            ),
            JobPosting(
                job_id="job_005",
                title="Senior Data Engineer",
                company="InnovateTech",
                location="San Francisco, CA",
                remote=True,
                salary_min=130000,
                salary_max=170000,
                description="We're looking for a senior data engineer with React experience...",
                requirements=["Python", "JavaScript", "React", "AWS", "Docker"],
                preferred_skills=["FastAPI", "PostgreSQL", "Kubernetes"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.SENIOR,
            ),
            JobPosting(
                job_id="job_006",
                title="Senior DevOps Engineer",
                company="InnovateTech",
                location="San Francisco, CA",
                remote=True,
                salary_min=130000,
                salary_max=170000,
                description="We're looking for a senior devops engineer with React experience...",
                requirements=["Python", "JavaScript", "React", "AWS", "Docker"],
                preferred_skills=["FastAPI", "PostgreSQL", "Kubernetes"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.SENIOR,
            )
        ]
        num_matches = 3
        job_postings_with_analysis = self.matching_engine.find_matches(
            user_profile, job_postings, limit=num_matches
        )
        self.assertEqual(len(job_postings_with_analysis), num_matches)
        self.assertEqual(job_postings_with_analysis[0][0].job_id, "job_001")
        self.assertAlmostEqual(job_postings_with_analysis[0][1].overall_score, 0.625, places=2)

    def test_analysis_generation(self):
        user_profile = UserProfile(
            user_id="user_001",
            personal_info={
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "location": "San Francisco, CA"
            },
            skills=[
                Skill(name="Python", level=5, category="Programming", years_experience=4),
                Skill(name="JavaScript", level=4, category="Programming", years_experience=3),
                Skill(name="React", level=4, category="Frontend", years_experience=3),
                Skill(name="AWS", level=3, category="Cloud", years_experience=2),
                Skill(name="Docker", level=3, category="DevOps", years_experience=2)
            ],
            work_experience=[
                WorkExperience(
                    title="Senior Software Engineer",
                    company="TechCorp",
                    location="San Francisco, CA",
                    start_date=datetime(2020, 1, 1),
                    end_date=None,
                    current=True,
                    description="Full-stack development with Python and React",
                    achievements=["Led team of 5 developers", "Improved system performance by 40%"]
                )
            ],
            education=[
                Education(
                    degree="Bachelor of Science",
                    institution="Stanford University",
                    field_of_study="Computer Science",
                    graduation_date="2019-06-01"
                )
            ],
            career_preferences=CareerPreference(
                preferred_locations=["San Francisco, CA", "Remote"],
                salary_expectations={"min": 120000, "max": 180000},
                work_type_preferences=[WorkType.FULL_TIME],
                experience_level_preferences=[ExperienceLevel.SENIOR],
                company_size_preferences=[CompanySize.MEDIUM, CompanySize.LARGE],
                industry_preferences=[Industry.TECHNOLOGY]
            )
        )

        job_posting = JobPosting(
            job_id="job_001",
            title="Senior Python Developer",
            company="InnovateTech",
            location="San Francisco, CA",
            remote=True,
            salary_min=130000,
            salary_max=170000,
            description="We're looking for a senior Python developer with React experience...",
            requirements=["Python", "JavaScript", "React", "AWS", "Docker"],
            preferred_skills=["FastAPI", "PostgreSQL", "Kubernetes"],
            work_type=WorkType.FULL_TIME,
            experience_level=ExperienceLevel.SENIOR,
            benefits=["Health insurance", "401k", "Stock options", "Remote work"]
        )

        expected_analysis = MatchAnalysis(
            overall_score=0.625,
            detailed_scores=DetailedScores(
                skills=0.95,
                experience=0.95,
                location=0.95,
                salary=0.95,
                company_fit=0.95,
                work_type=0.95
            ),
            skill_matches=["Python", "JavaScript", "React", "AWS", "Docker"],
            skill_gaps=[],
            reasons=["Perfect skill alignment", "Relevant experience", "Location match"],
            salary_fit=True,
            location_fit=True,
            experience_fit=True,
            strengths=["Perfect skill alignment", "Relevant experience", "Location match"],
            weaknesses=[],
            recommendations=["This is an excellent match!"]
        )
        analysis = self.matching_engine.analyze_match(user_profile, job_posting)
        self.assertAlmostEqual(analysis.overall_score, expected_analysis.overall_score, places=2)

    # def test_partial_match(self):
    #     user_profile = UserProfile(
    #         user_id="user_001",
    #         personal_info={
    #             "name": "Alice Johnson",
    #             "email": "alice@example.com",
    #             "location": "San Francisco, CA"

if __name__ == "__main__":
    unittest.main()
