"""
Job Matching Engine

Advanced job-candidate matching service using ML algorithms and multi-dimensional scoring.
Provides sophisticated matching between user profiles and job postings with detailed
compatibility analysis and skill gap identification.
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from models import (
    UserProfile,
    JobPosting,
    WorkType,
    ExperienceLevel,
    LocationPreference,
    MatchAnalysis,
    DetailedScores,
)

import logging
logger = logging.getLogger(__name__)

# No environment variables needed for this service

class JobMatchingEngine:
    """Advanced job-candidate matching engine using ML and multi-dimensional scoring."""
    def __init__(self):
        self.weights = {
            "skills": 0.4,
            "experience": 0.3,
            "location": 0.1,
            "salary": 0.1,
            "company_fit": 0.05,
            "work_type": 0.05,
        }

    # def _load_models(self):
    #     """Load ML models for job matching."""
    #     try:
    #         self.embedding_model = SentenceTransformer(settings.embedding_model)
    #         self.tfidf_vectorizer = TfidfVectorizer(
    #             max_features=1000, stop_words="english"
    #         )
    #         logger.info("ML models loaded successfully")
    #     except Exception as e:
    #         logger.error(f"Failed to load models: {str(e)}")
    #         # Use fallback models
    #         self.embedding_model = None
    #         self.tfidf_vectorizer = TfidfVectorizer(
    #             max_features=100, stop_words="english"
    #         )

    # def analyze_skill_gap(
    #     self, user_id: str, target_role: Optional[str] = None
    # ) -> SkillGapAnalysis:
    #     """
    #     Analyze skill gaps for a user's career development.

    #     Args:
    #         user_id: User ID
    #         target_role: Optional target role for analysis

    #     Returns:
    #         Detailed skill gap analysis
    #     """
    #     try:
    #         user_profile = self._get_user_profile(user_id)

    #         if target_role:
    #             role_requirements = self._get_role_requirements(target_role)
    #             required_skills = role_requirements.get('skills', [])
    #         else:
    #             # Analyze based on user's career preferences
    #             required_skills = self._get_career_skills(user_profile.preferences)

    #         current_skills = [skill.name.lower() for skill in user_profile.skills]
    #         missing_skills = list(set(required_skills) - set(current_skills))
    #         strong_skills = list(set(current_skills) & set(required_skills))

    #         return SkillGapAnalysis(
    #             user_id=user_id,
    #             target_role=target_role or "Career Development",
    #             current_skills=current_skills,
    #             required_skills=required_skills,
    #             missing_skills=missing_skills,
    #             strong_skills=strong_skills,
    #             recommendations=self._generate_skill_recommendations(missing_skills),
    #             learning_path=self._create_learning_path(missing_skills),
    #         )
    #     except Exception as e:
    #         logger.error(f"Failed to analyze skill gap: {str(e)}")
    #         return SkillGapAnalysis(user_id=user_id, target_role=target_role or "")

    # def generate_career_roadmap(
    #     self, user_id: str, target_role: str, timeline_months: int = 12
    # ) -> CareerRoadmap:
    #     """
    #     Generate a career roadmap for reaching a target role.

    #     Args:
    #         user_id: User ID
    #         target_role: Target role to achieve
    #         timeline_months: Timeline in months

    #     Returns:
    #         Career roadmap with milestones and learning path
    #     """
    #     try:
    #         user_profile = self._get_user_profile(user_id)
    #         skill_gap = self.analyze_skill_gap(user_id, target_role)

    #         # Generate roadmap based on skill gaps
    #         milestones = self._create_roadmap_milestones(
    #             skill_gap.missing_skills, timeline_months
    #         )

    #         return CareerRoadmap(
    #             user_id=user_id,
    #             target_role=target_role,
    #             current_position=user_profile.experience[-1].title if user_profile.experience else "Entry Level",
    #             timeline_months=timeline_months,
    #             milestones=milestones,
    #             skill_development_plan=self._create_skill_development_plan(skill_gap.missing_skills),
    #             networking_goals=self._generate_networking_goals(target_role),
    #             certification_goals=self._generate_certification_goals(target_role),
    #             experience_goals=self._generate_experience_goals(target_role),
    #         )
    #     except Exception as e:
    #         logger.error(f"Failed to generate career roadmap: {str(e)}")
    #         return CareerRoadmap(user_id=user_id, target_role=target_role)

    def find_matches(
        self, user_profile: UserProfile, job_postings: List[JobPosting],
        limit: int = 10, min_score: float = 0.5,
    ) -> Tuple[JobPosting, MatchAnalysis]:
        """
        Find the best job matches for a user.

        Args:
            user_profile: User profile
            job_postings: List of available job postings
            limit: Maximum number of recommendations
            min_score: Minimum match score threshold

        Returns:
            List of (job_posting, match_analysis) pairs sorted by match score
        """
        try:
            # Calculate matches for all jobs
            recommendations: List[Tuple[JobPosting, MatchAnalysis]] = []
            for job in job_postings:
                match_analysis = self.analyze_match(user_profile, job)

                if match_analysis.overall_score >= min_score:
                    recommendations.append((job, match_analysis))

            # Sort by match score and return top results
            recommendations.sort(key=lambda x: x[1].overall_score, reverse=True)
            return recommendations[:limit]

        except Exception as e:
            logger.error(f"Failed to find matches: {str(e)}")
            return []

    def analyze_match(self, user_profile: UserProfile, job: JobPosting) -> MatchAnalysis:
        """Analyze detailed match between user and job."""

        # Calculate individual scores
        detailed_scores = DetailedScores(
            skills=self._calculate_skill_score(user_profile, job),
            experience=self._calculate_experience_score(user_profile, job),
            location=self._calculate_location_score(user_profile, job),
            salary=self._calculate_salary_score(user_profile, job),
            company_fit=self._calculate_company_score(user_profile, job),
            work_type=self._calculate_work_type_score(user_profile, job),
        )

        return MatchAnalysis(
            overall_score=detailed_scores.calculate_overall_score(self.weights),
            detailed_scores=detailed_scores,
            skill_matches=self._get_skill_matches(user_profile, job),
            skill_gaps=self._get_skill_gaps(user_profile, job),
            reasons=self._generate_match_reasons(user_profile, job, detailed_scores),
            salary_fit=detailed_scores.salary > 0.5,
            location_fit=False,
            experience_fit=False,
            strengths=[],
            weaknesses=[],
            recommendations=[]
        )

    def _calculate_skill_score(self, user_profile: UserProfile, job: JobPosting) -> float:
        """Calculate skill compatibility score."""
        if not job.requirements:
            return 0.5  # Neutral if no requirements specified

        user_skills = [skill.name.lower() for skill in user_profile.skills]
        job_skills = [req.lower() for req in job.requirements]

        if not user_skills:
            return 0.0

        # Calculate skill overlap
        matches = len(set(user_skills) & set(job_skills))
        total_required = len(job_skills)

        if total_required == 0:
            return 1.0

        base_score = matches / total_required

        # Boost score based on skill levels
        level_boost = 0
        for user_skill in user_profile.skills:
            if user_skill.name.lower() in job_skills:
                level_boost += user_skill.level * 0.1  # 0.1 per level

        return min(1.0, base_score + level_boost)

    def _calculate_experience_score(self, user_profile: UserProfile, job: JobPosting) -> float:
        """Calculate experience level compatibility."""
        if not user_profile.experience:
            return 0.3 if job.experience_level == ExperienceLevel.ENTRY else 0.0

        # Calculate years of experience
        total_years = 0
        for exp in user_profile.experience:
            if exp.end_date:
                years = (exp.end_date - exp.start_date).days / 365.25
            else:
                years = (datetime.now() - exp.start_date).days / 365.25
            total_years += years

        # Map experience to levels
        if total_years < 1:
            user_level = ExperienceLevel.ENTRY
        elif total_years < 3:
            user_level = ExperienceLevel.JUNIOR
        elif total_years < 5:
            user_level = ExperienceLevel.MID
        elif total_years < 8:
            user_level = ExperienceLevel.SENIOR
        else:
            user_level = ExperienceLevel.LEAD

        # Calculate compatibility
        level_hierarchy = {
            ExperienceLevel.ENTRY: 1,
            ExperienceLevel.JUNIOR: 2,
            ExperienceLevel.MID: 3,
            ExperienceLevel.SENIOR: 4,
            ExperienceLevel.LEAD: 5,
            ExperienceLevel.PRINCIPAL: 6,
            ExperienceLevel.EXECUTIVE: 7,
        }

        user_level_num = level_hierarchy.get(user_level, 3)
        job_level_num = level_hierarchy.get(job.experience_level, 3)

        # Perfect match
        if user_level_num == job_level_num:
            return 1.0
        # User is overqualified (still good)
        elif user_level_num > job_level_num:
            return 0.8
        # User is underqualified
        else:
            gap = job_level_num - user_level_num
            return max(0.0, 1.0 - (gap * 0.3))

    def _calculate_location_score(self, user_profile: UserProfile, job: JobPosting) -> float:
        """Calculate location compatibility score."""
        user_pref = user_profile.preferences.location_preference

        # Remote work compatibility
        if job.remote:
            if user_pref in [LocationPreference.REMOTE, LocationPreference.FLEXIBLE]:
                return 1.0
            elif user_pref == LocationPreference.HYBRID:
                return 0.8
            else:  # ONSITE preference
                return 0.3
        else:
            if user_pref == LocationPreference.REMOTE:
                return 0.2
            elif user_pref == LocationPreference.FLEXIBLE:
                return 0.7
            else:
                return 0.8  # Assume location match for onsite/hybrid

    def _calculate_salary_score(self, user_profile: UserProfile, job: JobPosting) -> float:
        """Calculate salary compatibility score."""
        if not user_profile.preferences.salary_range_min or not job.salary_min:
            return 0.5  # Neutral if no salary info

        user_min = user_profile.preferences.salary_range_min
        job_min = job.salary_min

        if job_min >= user_min:
            return 1.0
        else:
            # Calculate how much below expectation
            gap = (user_min - job_min) / user_min
            return max(0.0, 1.0 - gap)

    def _calculate_company_score(self, user_profile: UserProfile, job: JobPosting) -> float:
        """Calculate company fit score."""
        # This would be enhanced with company culture data
        # For now, return neutral score
        return 0.5

    def _calculate_work_type_score(self, user_profile: UserProfile, job: JobPosting) -> float:
        """Calculate work type compatibility."""
        user_pref = user_profile.preferences.work_type_preference

        if user_pref == job.work_type:
            return 1.0
        elif user_pref == WorkType.FULL_TIME and job.work_type in [WorkType.PART_TIME, WorkType.CONTRACT]:
            return 0.6
        else:
            return 0.7  # Generally compatible

    def _get_skill_matches(self, user_profile: UserProfile, job: JobPosting) -> List[str]:
        """Get skills that match between user and job."""
        if not job.requirements:
            return []

        user_skills = [skill.name.lower() for skill in user_profile.skills]
        job_skills = [req.lower() for req in job.requirements]

        return list(set(user_skills) & set(job_skills))

    def _get_skill_gaps(self, user_profile: UserProfile, job: JobPosting) -> List[str]:
        """Get skills that user is missing for the job."""
        if not job.requirements:
            return []

        user_skills = [skill.name.lower() for skill in user_profile.skills]
        job_skills = [req.lower() for req in job.requirements]

        return list(set(job_skills) - set(user_skills))

    def _generate_match_reasons(
        self, user_profile: UserProfile, job: JobPosting, scores: DetailedScores
    ) -> List[str]:
        """Generate human-readable reasons for the match."""
        reasons = []

        if scores.skills > 0.7:
            reasons.append("Strong skill alignment")
        if scores.experience > 0.8:
            reasons.append("Experience level matches perfectly")
        if scores.location > 0.8:
            reasons.append("Location preferences align")
        if scores.salary > 0.8:
            reasons.append("Salary expectations met")

        return reasons

    # def _identify_strengths(self, user_profile: UserProfile, job: JobPosting) -> List[str]:
    #     """Identify user's strengths for this job."""
    #     strengths = []

    #     # Strong skills
    #     skill_matches = self._get_skill_matches(user_profile, job)
    #     if skill_matches:
    #         strengths.append(f"Strong in: {', '.join(skill_matches[:3])}")

    #     # Experience alignment
    #     if user_profile.experience:
    #         recent_exp = user_profile.experience[0]
    #         if recent_exp.title.lower() in job.title.lower():
    #             strengths.append("Relevant recent experience")

    #     return strengths

    # def _identify_weaknesses(self, user_profile: UserProfile, job: JobPosting) -> List[str]:
    #     """Identify areas for improvement."""
    #     weaknesses = []

    #     # Missing skills
    #     skill_gaps = self._get_skill_gaps(user_profile, job)
    #     if skill_gaps:
    #         weaknesses.append(f"Missing skills: {', '.join(skill_gaps[:3])}")

    #     # Experience gaps
    #     if not user_profile.experience and job.experience_level != ExperienceLevel.ENTRY:
    #         weaknesses.append("Limited professional experience")

    #     return weaknesses

    # def _generate_recommendations(
    #     self, user_profile: UserProfile, job: JobPosting
    # ) -> List[str]:
    #     """Generate actionable recommendations."""
    #     recommendations = []

    #     skill_gaps = self._get_skill_gaps(user_profile, job)
    #     if skill_gaps:
    #         recommendations.append(f"Consider learning: {', '.join(skill_gaps[:2])}")

    #     if not user_profile.experience and job.experience_level != ExperienceLevel.ENTRY:
    #         recommendations.append("Gain relevant experience through projects or internships")

    #     return recommendations

    # # Helper methods for skill gap analysis and career roadmaps
    # def _get_user_profile(self, user_id: str) -> UserProfile:
    #     """Get user profile from database."""
    #     # Mock implementation - in real app, fetch from database
    #     return UserProfile(
    #         user_id=user_id,
    #         skills=[
    #             Skill(name="Python", level=4, category="Programming"),
    #             Skill(name="JavaScript", level=3, category="Programming"),
    #             Skill(name="Machine Learning", level=2, category="AI/ML"),
    #         ],
    #         experience=[
    #             WorkExperience(
    #                 title="Software Engineer",
    #                 company="Tech Corp",
    #                 location="San Francisco, CA",
    #                 start_date=datetime(2022, 1, 1),
    #                 current=True,
    #                 description="Full-stack development",
    #                 skills_used=["Python", "JavaScript", "React"],
    #             )
    #         ],
    #         preferences=CareerPreference(
    #             salary_range_min=80000,
    #             salary_range_max=120000,
    #             location_preference=LocationPreference.REMOTE,
    #             work_type_preference=WorkType.FULL_TIME,
    #         ),
    #     )

    # def _get_role_requirements(self, target_role: str) -> Dict[str, List[str]]:
    #     """Get requirements for a target role."""
    #     # Mock implementation - in real app, would use ML or database
    #     role_requirements = {
    #         "Senior Software Engineer": {
    #             "skills": ["python", "javascript", "react", "aws", "docker"],
    #             "experience_years": 5,
    #             "education": ["Computer Science", "Software Engineering"],
    #         },
    #         "Data Scientist": {
    #             "skills": ["python", "machine learning", "sql", "statistics", "pandas"],
    #             "experience_years": 3,
    #             "education": ["Data Science", "Statistics", "Computer Science"],
    #         },
    #         "Product Manager": {
    #             "skills": ["product management", "agile", "user research", "analytics"],
    #             "experience_years": 4,
    #             "education": ["Business", "Product Management"],
    #         },
    #     }

    #     return role_requirements.get(target_role, {"skills": [], "experience_years": 0})

    # def _get_career_skills(self, preferences: CareerPreference) -> List[str]:
    #     """Get skills needed for user's career preferences."""
    #     # Mock implementation - would analyze target roles and industries
    #     return ["python", "javascript", "leadership", "communication"]

    # def _generate_skill_recommendations(self, missing_skills: List[str]) -> List[str]:
    #     """Generate recommendations for skill development."""
    #     recommendations = []

    #     skill_learning_map = {
    #         "python": "Take Python programming course",
    #         "javascript": "Learn JavaScript fundamentals",
    #         "machine learning": "Study ML algorithms and frameworks",
    #         "aws": "Get AWS certification",
    #         "docker": "Learn containerization with Docker",
    #     }

    #     for skill in missing_skills[:3]:  # Top 3 missing skills
    #         if skill in skill_learning_map:
    #             recommendations.append(skill_learning_map[skill])

    #     return recommendations

    # def _create_learning_path(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
    #     """Create a learning path for missing skills."""
    #     learning_path = []

    #     for i, skill in enumerate(missing_skills[:5]):  # Top 5 skills
    #         learning_path.append({
    #             "skill": skill,
    #             "priority": i + 1,
    #             "estimated_time": f"{2 + i} weeks",
    #             "resources": [f"Online course for {skill}", f"Practice projects in {skill}"],
    #         })

    #     return learning_path

    # def _create_roadmap_milestones(
    #     self, missing_skills: List[str], timeline_months: int
    # ) -> List[Dict[str, Any]]:
    #     """Create roadmap milestones."""
    #     milestones = []
    #     months_per_skill = timeline_months / max(len(missing_skills), 1)

    #     for i, skill in enumerate(missing_skills[:6]):  # Top 6 skills
    #         month = int((i + 1) * months_per_skill)
    #         milestones.append({
    #             "milestone": f"Master {skill}",
    #             "target_month": month,
    #             "description": f"Complete learning and practice in {skill}",
    #             "success_criteria": f"Build project using {skill}",
    #         })

    #     return milestones

    # def _create_skill_development_plan(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
    #     """Create detailed skill development plan."""
    #     return [
    #         {
    #             "skill": skill,
    #             "learning_approach": "Online courses + hands-on projects",
    #             "timeline": "4-6 weeks",
    #             "resources": [f"Course for {skill}", f"Practice with {skill}"],
    #         }
    #         for skill in missing_skills[:5]
    #     ]

    # def _generate_networking_goals(self, target_role: str) -> List[str]:
    #     """Generate networking goals for target role."""
    #     return [
    #         f"Connect with {target_role}s on LinkedIn",
    #         f"Join {target_role} professional groups",
    #         f"Attend {target_role} meetups and conferences",
    #     ]

    # def _generate_certification_goals(self, target_role: str) -> List[str]:
    #     """Generate certification goals."""
    #     cert_map = {
    #         "Senior Software Engineer": ["AWS Certified Developer", "Google Cloud Professional"],
    #         "Data Scientist": ["AWS Machine Learning", "Google Data Analytics"],
    #         "Product Manager": ["Certified Scrum Master", "Google Analytics"],
    #     }

    #     return cert_map.get(target_role, ["Industry-relevant certification"])

    # def _generate_experience_goals(self, target_role: str) -> List[str]:
    #     """Generate experience goals."""
    #     return [
    #         f"Gain hands-on experience in {target_role} projects",
    #         f"Lead a {target_role} initiative",
    #         f"Build portfolio showcasing {target_role} skills",
    #     ]
