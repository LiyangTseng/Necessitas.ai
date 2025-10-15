"""
Job Recommender Service

Handles job matching, recommendations, and skill gap analysis.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.models.user_profile import (
    UserProfile,
    JobPosting,
    JobRecommendation,
    SkillGapAnalysis,
)
from app.core.config import settings


class JobRecommender:
    """Job recommendation service using ML and similarity matching."""

    def __init__(self):
        """Initialize the job recommender."""
        self.embedding_model = None
        self.tfidf_vectorizer = None
        self._load_models()

    def _load_models(self):
        """Load ML models for job matching."""
        try:
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000, stop_words="english"
            )
            logger.info("ML models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {str(e)}")
            # Use fallback models
            self.embedding_model = None
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=100, stop_words="english"
            )

    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        location: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> List[JobRecommendation]:
        """
        Get personalized job recommendations for a user.

        Args:
            user_id: User ID
            limit: Number of recommendations
            location: Optional location filter
            industry: Optional industry filter

        Returns:
            List of job recommendations
        """
        try:
            # Get user profile (mock for now)
            user_profile = await self._get_user_profile(user_id)

            # Get available jobs (mock for now)
            available_jobs = await self._get_available_jobs(location, industry)

            # Calculate match scores
            recommendations = []
            for job in available_jobs:
                match_score = await self._calculate_match_score(user_profile, job)

                if match_score >= 0.5:  # Only include jobs with 50%+ match
                    recommendation = JobRecommendation(
                        job_posting=job,
                        match_score=match_score * 100,
                        match_reasons=self._get_match_reasons(user_profile, job),
                        skill_matches=self._get_skill_matches(user_profile, job),
                        skill_gaps=self._get_skill_gaps(user_profile, job),
                        salary_fit=self._check_salary_fit(user_profile, job),
                        location_fit=self._check_location_fit(user_profile, job),
                        experience_fit=self._check_experience_fit(user_profile, job),
                    )
                    recommendations.append(recommendation)

            # Sort by match score and return top results
            recommendations.sort(key=lambda x: x.match_score, reverse=True)
            return recommendations[:limit]

        except Exception as e:
            logger.error(f"Failed to get recommendations: {str(e)}")
            return []

    async def analyze_skill_gap(
        self, user_id: str, target_role: Optional[str] = None
    ) -> SkillGapAnalysis:
        """
        Analyze skill gaps for a user.

        Args:
            user_id: User ID
            target_role: Optional target role

        Returns:
            Skill gap analysis
        """
        try:
            # Get user profile
            user_profile = await self._get_user_profile(user_id)

            # Get target role requirements
            if not target_role:
                target_role = (
                    user_profile.preferences.target_roles[0]
                    if user_profile.preferences.target_roles
                    else "Software Engineer"
                )

            role_requirements = await self._get_role_requirements(target_role)

            # Analyze skills
            current_skills = [skill.name for skill in user_profile.skills]
            required_skills = role_requirements.get("required_skills", [])
            preferred_skills = role_requirements.get("preferred_skills", [])

            # Calculate gaps
            missing_skills = list(set(required_skills) - set(current_skills))
            developing_skills = list(set(preferred_skills) - set(current_skills))
            strong_skills = list(
                set(current_skills) & set(required_skills + preferred_skills)
            )

            # Generate recommendations
            recommendations = self._generate_skill_recommendations(
                missing_skills, developing_skills
            )

            return SkillGapAnalysis(
                user_id=user_id,
                target_role=target_role,
                current_skills=current_skills,
                required_skills=required_skills,
                missing_skills=missing_skills,
                developing_skills=developing_skills,
                strong_skills=strong_skills,
                recommendations=recommendations,
                priority_skills=missing_skills[:5],  # Top 5 priority skills
                learning_path=self._create_learning_path(missing_skills),
            )

        except Exception as e:
            logger.error(f"Failed to analyze skill gap: {str(e)}")
            return SkillGapAnalysis(
                user_id=user_id,
                target_role=target_role or "Software Engineer",
                current_skills=[],
                required_skills=[],
                missing_skills=[],
                developing_skills=[],
                strong_skills=[],
                recommendations=[],
                priority_skills=[],
                learning_path=[],
            )

    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile from database."""
        # Mock implementation - in real app, fetch from database
        from app.models.user_profile import UserProfile, Skill, CareerPreference

        return UserProfile(
            user_id=user_id,
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

    async def _get_available_jobs(
        self, location: Optional[str] = None, industry: Optional[str] = None
    ) -> List[JobPosting]:
        """Get available jobs from job APIs."""
        # Mock implementation - in real app, fetch from job APIs
        from app.models.user_profile import JobPosting, WorkType, ExperienceLevel

        jobs = [
            JobPosting(
                job_id="job_1",
                title="Senior Software Engineer",
                company="TechCorp",
                location="San Francisco, CA",
                remote=True,
                salary_min=130000,
                salary_max=160000,
                description="We're looking for a senior software engineer to join our team...",
                requirements=["Python", "React", "AWS", "Machine Learning"],
                preferred_skills=["Docker", "Kubernetes", "Leadership"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.SENIOR,
                posted_date=datetime.now(),
            ),
            JobPosting(
                job_id="job_2",
                title="Full Stack Developer",
                company="StartupXYZ",
                location="Remote",
                remote=True,
                salary_min=110000,
                salary_max=140000,
                description="Join our fast-growing startup as a full stack developer...",
                requirements=["Python", "React", "Node.js", "PostgreSQL"],
                preferred_skills=["Docker", "GraphQL", "Microservices"],
                work_type=WorkType.FULL_TIME,
                experience_level=ExperienceLevel.MID,
                posted_date=datetime.now(),
            ),
        ]

        # Filter by location and industry if specified
        if location:
            jobs = [
                job
                for job in jobs
                if location.lower() in job.location.lower() or job.remote
            ]

        return jobs

    async def _calculate_match_score(
        self, user_profile: UserProfile, job: JobPosting
    ) -> float:
        """Calculate match score between user and job."""
        try:
            # Skill matching (40% weight)
            user_skills = [skill.name.lower() for skill in user_profile.skills]
            job_skills = [
                skill.lower() for skill in job.requirements + job.preferred_skills
            ]

            skill_matches = len(set(user_skills) & set(job_skills))
            total_skills = len(job_skills)
            skill_score = skill_matches / total_skills if total_skills > 0 else 0

            # Location matching (20% weight)
            location_score = 1.0 if job.remote else 0.8  # Prefer remote jobs

            # Salary matching (20% weight)
            salary_score = 1.0
            if user_profile.preferences.salary_range_min and job.salary_min:
                if job.salary_min >= user_profile.preferences.salary_range_min:
                    salary_score = 1.0
                else:
                    salary_score = 0.5

            # Experience matching (20% weight)
            experience_score = 0.8  # Default good match

            # Calculate weighted score
            total_score = (
                skill_score * 0.4
                + location_score * 0.2
                + salary_score * 0.2
                + experience_score * 0.2
            )

            return min(total_score, 1.0)

        except Exception as e:
            logger.error(f"Failed to calculate match score: {str(e)}")
            return 0.5  # Default moderate match

    def _get_match_reasons(
        self, user_profile: UserProfile, job: JobPosting
    ) -> List[str]:
        """Get reasons why the job matches the user."""
        reasons = []

        # Skill matches
        user_skills = [skill.name.lower() for skill in user_profile.skills]
        job_skills = [skill.lower() for skill in job.requirements]
        matching_skills = set(user_skills) & set(job_skills)

        if matching_skills:
            reasons.append(f"Strong match in skills: {', '.join(matching_skills)}")

        # Location preference
        if job.remote:
            reasons.append("Remote work opportunity")

        # Salary range
        if user_profile.preferences.salary_range_min and job.salary_min:
            if job.salary_min >= user_profile.preferences.salary_range_min:
                reasons.append("Salary meets expectations")

        return reasons

    def _get_skill_matches(
        self, user_profile: UserProfile, job: JobPosting
    ) -> List[str]:
        """Get skills that match between user and job."""
        user_skills = [skill.name.lower() for skill in user_profile.skills]
        job_skills = [
            skill.lower() for skill in job.requirements + job.preferred_skills
        ]
        return list(set(user_skills) & set(job_skills))

    def _get_skill_gaps(self, user_profile: UserProfile, job: JobPosting) -> List[str]:
        """Get skills that the user is missing for the job."""
        user_skills = [skill.name.lower() for skill in user_profile.skills]
        job_skills = [skill.lower() for skill in job.requirements]
        return list(set(job_skills) - set(user_skills))

    def _check_salary_fit(self, user_profile: UserProfile, job: JobPosting) -> bool:
        """Check if salary fits user expectations."""
        if not user_profile.preferences.salary_range_min or not job.salary_min:
            return True
        return job.salary_min >= user_profile.preferences.salary_range_min

    def _check_location_fit(self, user_profile: UserProfile, job: JobPosting) -> bool:
        """Check if location fits user preferences."""
        return (
            job.remote or user_profile.preferences.location_preference.value == "onsite"
        )

    def _check_experience_fit(self, user_profile: UserProfile, job: JobPosting) -> bool:
        """Check if experience level fits user profile."""
        # Simple check - in real app, would be more sophisticated
        return True

    async def _get_role_requirements(self, target_role: str) -> Dict[str, List[str]]:
        """Get requirements for a target role."""
        # Mock implementation - in real app, would use ML or database
        role_requirements = {
            "Senior Software Engineer": {
                "required_skills": ["Python", "React", "AWS", "Leadership"],
                "preferred_skills": [
                    "Docker",
                    "Kubernetes",
                    "System Design",
                    "Mentoring",
                ],
            },
            "Tech Lead": {
                "required_skills": [
                    "Python",
                    "Leadership",
                    "System Design",
                    "Architecture",
                ],
                "preferred_skills": [
                    "Kubernetes",
                    "Microservices",
                    "Team Management",
                    "Strategic Planning",
                ],
            },
        }

        return role_requirements.get(
            target_role,
            {
                "required_skills": ["Python", "JavaScript", "SQL"],
                "preferred_skills": ["AWS", "Docker", "Git"],
            },
        )

    def _generate_skill_recommendations(
        self, missing_skills: List[str], developing_skills: List[str]
    ) -> List[str]:
        """Generate recommendations for skill development."""
        recommendations = []

        if missing_skills:
            recommendations.append(
                f"Focus on learning: {', '.join(missing_skills[:3])}"
            )

        if developing_skills:
            recommendations.append(
                f"Consider developing: {', '.join(developing_skills[:3])}"
            )

        recommendations.extend(
            [
                "Take online courses or certifications",
                "Build projects to practice new skills",
                "Join professional communities and forums",
            ]
        )

        return recommendations

    def _create_learning_path(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
        """Create a learning path for missing skills."""
        learning_path = []

        for skill in missing_skills[:5]:  # Top 5 skills
            learning_path.append(
                {
                    "skill": skill,
                    "priority": "high" if skill in missing_skills[:3] else "medium",
                    "resources": [
                        f"Online course for {skill}",
                        f"Practice projects with {skill}",
                        f"Community forums for {skill}",
                    ],
                    "timeline": "2-3 months",
                }
            )

        return learning_path
