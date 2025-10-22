"""
Coursera Service

Service for fetching courses and certifications from Coursera API via RapidAPI.
"""

import httpx
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from ..models.coursera import (
    Course, Certification, CourseSearchRequest, CourseSearchResponse,
    CertificationSearchRequest, CertificationSearchResponse,
    LearningRecommendation, LearningPath, LearningPathStep,
    CourseLevel, CourseType, Language
)
from ..core.config import settings

logger = logging.getLogger(__name__)


class CourseraService:
    """Service for interacting with Coursera API via RapidAPI."""

    def __init__(self):
        """Initialize the Coursera service."""
        self.base_url = "https://collection-for-coursera-courses.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": getattr(settings, 'rapidapi_key', None),
            "X-RapidAPI-Host": "collection-for-coursera-courses.p.rapidapi.com"
        }
        self.is_available = bool(getattr(settings, 'rapidapi_key', None))

    async def search_courses(
        self, 
        request: CourseSearchRequest
    ) -> CourseSearchResponse:
        """
        Search for courses based on criteria.

        Args:
            request: Course search parameters

        Returns:
            Course search results
        """
        try:
            if not self.is_available:
                logger.warning("Coursera API not available - using mock data")
                return await self._get_mock_courses(request)

            async with httpx.AsyncClient() as client:
                # Build query parameters
                params = {}
                if request.query:
                    params['q'] = request.query
                if request.skills:
                    params['skills'] = ','.join(request.skills)
                if request.level:
                    params['level'] = request.level.value
                if request.course_type:
                    params['type'] = request.course_type.value
                if request.language:
                    params['language'] = request.language.value
                if request.is_free is not None:
                    params['free'] = str(request.is_free).lower()
                if request.institution:
                    params['institution'] = request.institution

                params['limit'] = request.limit

                response = await client.get(
                    f"{self.base_url}/courses",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()

                data = response.json()
                courses = self._parse_courses(data.get('courses', []))
                
                return CourseSearchResponse(
                    courses=courses,
                    total_count=data.get('total', len(courses)),
                    page=1,
                    limit=request.limit,
                    has_more=len(courses) >= request.limit
                )

        except Exception as e:
            logger.error(f"Failed to search courses: {str(e)}")
            return await self._get_mock_courses(request)

    async def search_certifications(
        self, 
        request: CertificationSearchRequest
    ) -> CertificationSearchResponse:
        """
        Search for certifications based on criteria.

        Args:
            request: Certification search parameters

        Returns:
            Certification search results
        """
        try:
            if not self.is_available:
                logger.warning("Coursera API not available - using mock data")
                return await self._get_mock_certifications(request)

            async with httpx.AsyncClient() as client:
                # Build query parameters
                params = {}
                if request.query:
                    params['q'] = request.query
                if request.skills:
                    params['skills'] = ','.join(request.skills)
                if request.course_type:
                    params['type'] = request.course_type.value
                if request.language:
                    params['language'] = request.language.value
                if request.is_free is not None:
                    params['free'] = str(request.is_free).lower()
                if request.institution:
                    params['institution'] = request.institution
                if request.industry_recognition is not None:
                    params['industry_recognition'] = str(request.industry_recognition).lower()

                params['limit'] = request.limit

                response = await client.get(
                    f"{self.base_url}/certifications",
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()

                data = response.json()
                certifications = self._parse_certifications(data.get('certifications', []))
                
                return CertificationSearchResponse(
                    certifications=certifications,
                    total_count=data.get('total', len(certifications)),
                    page=1,
                    limit=request.limit,
                    has_more=len(certifications) >= request.limit
                )

        except Exception as e:
            logger.error(f"Failed to search certifications: {str(e)}")
            return await self._get_mock_certifications(request)

    async def get_learning_recommendations(
        self, 
        user_id: str, 
        skill_gaps: List[str],
        target_role: Optional[str] = None
    ) -> LearningRecommendation:
        """
        Get personalized learning recommendations based on skill gaps.

        Args:
            user_id: User identifier
            skill_gaps: List of skills the user needs to develop
            target_role: Optional target role

        Returns:
            Learning recommendations
        """
        try:
            # Search for courses that address skill gaps
            course_request = CourseSearchRequest(
                skills=skill_gaps,
                limit=5
            )
            course_response = await self.search_courses(course_request)

            # Search for relevant certifications
            cert_request = CertificationSearchRequest(
                skills=skill_gaps,
                limit=3
            )
            cert_response = await self.search_certifications(cert_request)

            # Create learning path
            learning_path = self._create_learning_path(
                skill_gaps, course_response.courses, cert_response.certifications
            )

            return LearningRecommendation(
                user_id=user_id,
                target_role=target_role,
                skill_gaps=skill_gaps,
                recommended_courses=course_response.courses,
                recommended_certifications=cert_response.certifications,
                learning_path=learning_path,
                estimated_completion_time=self._estimate_completion_time(
                    course_response.courses, cert_response.certifications
                ),
                priority_skills=skill_gaps[:3]  # Top 3 skills as priority
            )

        except Exception as e:
            logger.error(f"Failed to get learning recommendations: {str(e)}")
            return LearningRecommendation(
                user_id=user_id,
                skill_gaps=skill_gaps,
                target_role=target_role
            )

    def _parse_courses(self, raw_courses: List[Dict[str, Any]]) -> List[Course]:
        """Parse raw course data from API response."""
        courses = []
        
        for course_data in raw_courses:
            try:
                course = Course(
                    id=course_data.get('id', ''),
                    title=course_data.get('title', ''),
                    description=course_data.get('description', ''),
                    url=course_data.get('url', ''),
                    institution=course_data.get('institution', ''),
                    instructor=course_data.get('instructor'),
                    level=CourseLevel(course_data.get('level', 'beginner')),
                    course_type=CourseType(course_data.get('type', 'course')),
                    language=Language(course_data.get('language', 'en')),
                    duration_weeks=course_data.get('duration_weeks'),
                    hours_per_week=course_data.get('hours_per_week'),
                    rating=course_data.get('rating'),
                    enrollment_count=course_data.get('enrollment_count'),
                    skills=course_data.get('skills', []),
                    prerequisites=course_data.get('prerequisites', []),
                    learning_outcomes=course_data.get('learning_outcomes', []),
                    price=course_data.get('price'),
                    currency=course_data.get('currency', 'USD'),
                    is_free=course_data.get('is_free', False),
                    certificate_available=course_data.get('certificate_available', False)
                )
                courses.append(course)
            except Exception as e:
                logger.warning(f"Failed to parse course: {e}")
                continue

        return courses

    def _parse_certifications(self, raw_certs: List[Dict[str, Any]]) -> List[Certification]:
        """Parse raw certification data from API response."""
        certifications = []
        
        for cert_data in raw_certs:
            try:
                certification = Certification(
                    id=cert_data.get('id', ''),
                    name=cert_data.get('name', ''),
                    description=cert_data.get('description', ''),
                    url=cert_data.get('url', ''),
                    institution=cert_data.get('institution', ''),
                    course_type=CourseType(cert_data.get('type', 'professional_certificate')),
                    duration_weeks=cert_data.get('duration_weeks'),
                    skills=cert_data.get('skills', []),
                    prerequisites=cert_data.get('prerequisites', []),
                    price=cert_data.get('price'),
                    currency=cert_data.get('currency', 'USD'),
                    is_free=cert_data.get('is_free', False),
                    industry_recognition=cert_data.get('industry_recognition', False)
                )
                certifications.append(certification)
            except Exception as e:
                logger.warning(f"Failed to parse certification: {e}")
                continue

        return certifications

    def _create_learning_path(
        self, 
        skill_gaps: List[str], 
        courses: List[Course], 
        certifications: List[Certification]
    ) -> List[Dict[str, Any]]:
        """Create a structured learning path."""
        learning_path = []
        
        # Group skills by difficulty/priority
        priority_skills = skill_gaps[:3]  # Top 3 skills
        secondary_skills = skill_gaps[3:6]  # Next 3 skills
        
        # Step 1: Foundation courses for priority skills
        if priority_skills:
            foundation_courses = [c for c in courses if any(
                skill.lower() in c.title.lower() or 
                any(skill.lower() in skill_name.lower() for skill_name in c.skills)
                for skill in priority_skills
            )][:2]
            
            if foundation_courses:
                learning_path.append({
                    "step": 1,
                    "title": "Foundation Skills",
                    "description": "Build foundational knowledge in priority skills",
                    "courses": [{"title": c.title, "url": c.url} for c in foundation_courses],
                    "duration_weeks": max([c.duration_weeks or 4 for c in foundation_courses]),
                    "skills_covered": priority_skills[:2]
                })

        # Step 2: Advanced courses and certifications
        if secondary_skills:
            advanced_courses = [c for c in courses if any(
                skill.lower() in c.title.lower() or 
                any(skill.lower() in skill_name.lower() for skill_name in c.skills)
                for skill in secondary_skills
            )][:2]
            
            if advanced_courses:
                learning_path.append({
                    "step": 2,
                    "title": "Advanced Skills",
                    "description": "Develop advanced skills and get certified",
                    "courses": [{"title": c.title, "url": c.url} for c in advanced_courses],
                    "certifications": [{"name": c.name, "url": c.url} for c in certifications[:1]],
                    "duration_weeks": max([c.duration_weeks or 6 for c in advanced_courses]),
                    "skills_covered": secondary_skills[:2]
                })

        return learning_path

    def _estimate_completion_time(
        self, 
        courses: List[Course], 
        certifications: List[Certification]
    ) -> int:
        """Estimate total completion time in weeks."""
        total_weeks = 0
        
        for course in courses:
            total_weeks += course.duration_weeks or 4
        
        for cert in certifications:
            total_weeks += cert.duration_weeks or 6
            
        return min(total_weeks, 24)  # Cap at 24 weeks

    async def _get_mock_courses(self, request: CourseSearchRequest) -> CourseSearchResponse:
        """Return mock course data when API is unavailable."""
        mock_courses = [
            Course(
                id="mock-1",
                title="Python for Data Science",
                description="Learn Python programming for data analysis and visualization",
                url="https://coursera.org/learn/python-data-science",
                institution="University of Michigan",
                level=CourseLevel.BEGINNER,
                course_type=CourseType.COURSE,
                duration_weeks=6,
                hours_per_week=5,
                rating=4.5,
                skills=["Python", "Data Analysis", "Pandas", "Matplotlib"],
                is_free=True,
                certificate_available=True
            ),
            Course(
                id="mock-2",
                title="Machine Learning Fundamentals",
                description="Introduction to machine learning algorithms and applications",
                url="https://coursera.org/learn/machine-learning",
                institution="Stanford University",
                level=CourseLevel.INTERMEDIATE,
                course_type=CourseType.COURSE,
                duration_weeks=8,
                hours_per_week=6,
                rating=4.7,
                skills=["Machine Learning", "Python", "Scikit-learn", "Statistics"],
                is_free=False,
                price=49.0,
                certificate_available=True
            )
        ]
        
        # Filter based on request criteria
        filtered_courses = mock_courses
        if request.skills:
            filtered_courses = [
                c for c in filtered_courses 
                if any(skill.lower() in ' '.join(c.skills).lower() for skill in request.skills)
            ]
        
        return CourseSearchResponse(
            courses=filtered_courses[:request.limit],
            total_count=len(filtered_courses),
            page=1,
            limit=request.limit,
            has_more=False
        )

    async def _get_mock_certifications(self, request: CertificationSearchRequest) -> CertificationSearchResponse:
        """Return mock certification data when API is unavailable."""
        mock_certifications = [
            Certification(
                id="mock-cert-1",
                name="Google Data Analytics Professional Certificate",
                description="Professional certificate in data analytics using Google tools",
                url="https://coursera.org/professional-certificates/google-data-analytics",
                institution="Google",
                course_type=CourseType.PROFESSIONAL_CERTIFICATE,
                duration_weeks=12,
                skills=["Data Analysis", "SQL", "R", "Tableau"],
                is_free=False,
                price=39.0,
                industry_recognition=True
            ),
            Certification(
                id="mock-cert-2",
                name="AWS Machine Learning Specialty",
                description="AWS certification for machine learning on cloud platform",
                url="https://coursera.org/specializations/aws-machine-learning",
                institution="Amazon Web Services",
                course_type=CourseType.PROFESSIONAL_CERTIFICATE,
                duration_weeks=16,
                skills=["AWS", "Machine Learning", "Python", "Cloud Computing"],
                is_free=False,
                price=99.0,
                industry_recognition=True
            )
        ]
        
        # Filter based on request criteria
        filtered_certs = mock_certifications
        if request.skills:
            filtered_certs = [
                c for c in filtered_certs 
                if any(skill.lower() in ' '.join(c.skills).lower() for skill in request.skills)
            ]
        
        return CertificationSearchResponse(
            certifications=filtered_certs[:request.limit],
            total_count=len(filtered_certs),
            page=1,
            limit=request.limit,
            has_more=False
        )
