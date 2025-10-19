"""
Resume Analyzer Agent

AI agent for analyzing resumes and extracting insights.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)

from models import (
    UserProfile,
    Skill,
    WorkExperience,
    Education,
    Certification,
)
from services.resume_parser import ResumeParser


class ResumeAnalyzer:
    """AI agent for resume analysis and insight generation."""

    def __init__(self):
        """Initialize the resume analyzer."""
        self.parser = ResumeParser()

    async def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze resume and generate insights.

        Args:
            resume_data: Parsed resume data

        Returns:
            Analysis results with insights
        """
        try:
            # Extract basic information
            personal_info = resume_data.get("personal_info", {})
            skills = resume_data.get("skills", [])
            experience = resume_data.get("experience", [])
            education = resume_data.get("education", [])
            certifications = resume_data.get("certifications", [])

            # Analyze skills
            skill_analysis = self._analyze_skills(skills)

            # Analyze experience
            experience_analysis = self._analyze_experience(experience)

            # Analyze education
            education_analysis = self._analyze_education(education)

            # Generate career insights
            career_insights = self._generate_career_insights(
                skills, experience, education, certifications
            )

            # Calculate career score
            career_score = self._calculate_career_score(
                skill_analysis, experience_analysis, education_analysis
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                skill_analysis, experience_analysis, career_insights
            )

            return {
                "personal_info": personal_info,
                "skills": skills,
                "skill_analysis": skill_analysis,
                "experience": experience,
                "experience_analysis": experience_analysis,
                "education": education,
                "education_analysis": education_analysis,
                "certifications": certifications,
                "career_insights": career_insights,
                "career_score": career_score,
                "recommendations": recommendations,
                "analyzed_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to analyze resume: {str(e)}")
            raise

    def _analyze_skills(self, skills: List[str]) -> Dict[str, Any]:
        """Analyze skills and categorize them."""
        try:
            # Categorize skills
            skill_categories = {
                "programming": [],
                "frameworks": [],
                "cloud": [],
                "databases": [],
                "tools": [],
                "soft_skills": [],
                "other": [],
            }

            for skill in skills:
                skill_lower = skill.lower()
                if any(
                    tech in skill_lower
                    for tech in [
                        "python",
                        "java",
                        "javascript",
                        "typescript",
                        "go",
                        "rust",
                        "c++",
                        "c#",
                    ]
                ):
                    skill_categories["programming"].append(skill)
                elif any(
                    tech in skill_lower
                    for tech in [
                        "react",
                        "vue",
                        "angular",
                        "node",
                        "express",
                        "django",
                        "flask",
                        "spring",
                    ]
                ):
                    skill_categories["frameworks"].append(skill)
                elif any(
                    tech in skill_lower
                    for tech in ["aws", "azure", "gcp", "cloud", "docker", "kubernetes"]
                ):
                    skill_categories["cloud"].append(skill)
                elif any(
                    tech in skill_lower
                    for tech in [
                        "mysql",
                        "postgresql",
                        "mongodb",
                        "redis",
                        "sql",
                        "database",
                    ]
                ):
                    skill_categories["databases"].append(skill)
                elif any(
                    tech in skill_lower
                    for tech in ["git", "jenkins", "ci/cd", "agile", "scrum", "jira"]
                ):
                    skill_categories["tools"].append(skill)
                elif any(
                    tech in skill_lower
                    for tech in [
                        "leadership",
                        "communication",
                        "teamwork",
                        "management",
                    ]
                ):
                    skill_categories["soft_skills"].append(skill)
                else:
                    skill_categories["other"].append(skill)

            # Calculate skill strength
            total_skills = len(skills)
            programming_ratio = (
                len(skill_categories["programming"]) / total_skills
                if total_skills > 0
                else 0
            )
            cloud_ratio = (
                len(skill_categories["cloud"]) / total_skills if total_skills > 0 else 0
            )
            framework_ratio = (
                len(skill_categories["frameworks"]) / total_skills
                if total_skills > 0
                else 0
            )

            return {
                "categories": skill_categories,
                "total_skills": total_skills,
                "programming_ratio": programming_ratio,
                "cloud_ratio": cloud_ratio,
                "framework_ratio": framework_ratio,
                "skill_diversity": len(
                    [cat for cat in skill_categories.values() if cat]
                )
                / len(skill_categories),
                "strengths": self._identify_skill_strengths(skill_categories),
                "gaps": self._identify_skill_gaps(skill_categories),
            }

        except Exception as e:
            logger.error(f"Failed to analyze skills: {str(e)}")
            return {}

    def _analyze_experience(self, experience: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze work experience."""
        try:
            if not experience:
                return {
                    "total_experience": 0,
                    "career_progression": "entry",
                    "insights": [],
                }

            # Calculate total experience
            total_experience = self._calculate_total_experience(experience)

            # Analyze career progression
            career_progression = self._analyze_career_progression(experience)

            # Identify key achievements
            achievements = self._extract_achievements(experience)

            # Analyze company diversity
            companies = [
                exp.get("company", "") for exp in experience if exp.get("company")
            ]
            company_diversity = len(set(companies)) / len(companies) if companies else 0

            return {
                "total_experience": total_experience,
                "career_progression": career_progression,
                "achievements": achievements,
                "company_diversity": company_diversity,
                "companies": list(set(companies)),
                "insights": self._generate_experience_insights(
                    experience, total_experience
                ),
            }

        except Exception as e:
            logger.error(f"Failed to analyze experience: {str(e)}")
            return {}

    def _analyze_education(self, education: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze education background."""
        try:
            if not education:
                return {
                    "highest_degree": "none",
                    "relevance": "unknown",
                    "insights": [],
                }

            # Find highest degree
            degree_levels = {"bachelor": 1, "master": 2, "phd": 3, "doctorate": 3}
            highest_degree = "none"
            highest_level = 0

            for edu in education:
                degree = edu.get("degree", "").lower()
                for level_name, level in degree_levels.items():
                    if level_name in degree and level > highest_level:
                        highest_degree = level_name
                        highest_level = level

            # Analyze relevance to tech roles
            relevance = self._assess_education_relevance(education)

            return {
                "highest_degree": highest_degree,
                "relevance": relevance,
                "institutions": [edu.get("institution", "") for edu in education],
                "fields_of_study": [edu.get("field_of_study", "") for edu in education],
                "insights": self._generate_education_insights(
                    education, highest_degree
                ),
            }

        except Exception as e:
            logger.error(f"Failed to analyze education: {str(e)}")
            return {}

    def _generate_career_insights(
        self,
        skills: List[str],
        experience: List[Dict[str, Any]],
        education: List[Dict[str, Any]],
        certifications: List[str],
    ) -> List[str]:
        """Generate career insights based on resume analysis."""
        insights = []

        # Skill-based insights
        if len(skills) > 10:
            insights.append("Strong technical skill set with good diversity")
        elif len(skills) < 5:
            insights.append("Consider developing more technical skills")

        # Experience-based insights
        if len(experience) > 3:
            insights.append("Solid work experience with multiple roles")
        elif len(experience) == 1:
            insights.append("Early career stage - focus on skill development")

        # Education-based insights
        if education:
            insights.append("Strong educational background")
        else:
            insights.append("Consider highlighting relevant coursework or projects")

        # Certification insights
        if certifications:
            insights.append("Good commitment to professional development")
        else:
            insights.append("Consider obtaining relevant certifications")

        return insights

    def _calculate_career_score(
        self,
        skill_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any],
        education_analysis: Dict[str, Any],
    ) -> float:
        """Calculate overall career score."""
        try:
            score = 0.0

            # Skills score (40%)
            skill_score = min(skill_analysis.get("total_skills", 0) / 15, 1.0) * 0.4
            score += skill_score

            # Experience score (40%)
            exp_score = (
                min(experience_analysis.get("total_experience", 0) / 5, 1.0) * 0.4
            )
            score += exp_score

            # Education score (20%)
            edu_score = 0.0
            if education_analysis.get("highest_degree") in [
                "bachelor",
                "master",
                "phd",
            ]:
                edu_score = 0.2
            score += edu_score

            return min(score, 1.0)

        except Exception as e:
            logger.error(f"Failed to calculate career score: {str(e)}")
            return 0.5

    def _generate_recommendations(
        self,
        skill_analysis: Dict[str, Any],
        experience_analysis: Dict[str, Any],
        career_insights: List[str],
    ) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []

        # Skill-based recommendations
        if skill_analysis.get("total_skills", 0) < 10:
            recommendations.append(
                "Develop more technical skills through online courses"
            )

        if skill_analysis.get("cloud_ratio", 0) < 0.2:
            recommendations.append("Learn cloud technologies (AWS, Azure, or GCP)")

        # Experience-based recommendations
        if experience_analysis.get("total_experience", 0) < 2:
            recommendations.append(
                "Focus on building practical experience through projects"
            )

        if experience_analysis.get("company_diversity", 0) < 0.5:
            recommendations.append(
                "Consider gaining experience at different types of companies"
            )

        # General recommendations
        recommendations.extend(
            [
                "Build a strong portfolio showcasing your projects",
                "Network with professionals in your field",
                "Stay updated with industry trends and technologies",
            ]
        )

        return recommendations

    def _calculate_total_experience(self, experience: List[Dict[str, Any]]) -> float:
        """Calculate total years of experience."""
        total_years = 0.0

        for exp in experience:
            duration = exp.get("duration", "")
            if duration:
                # Simple parsing - in real app, would be more sophisticated
                if "year" in duration.lower():
                    years = 1.0
                elif "month" in duration.lower():
                    years = 0.5
                else:
                    years = 1.0  # Default
                total_years += years

        return total_years

    def _analyze_career_progression(self, experience: List[Dict[str, Any]]) -> str:
        """Analyze career progression."""
        if len(experience) < 2:
            return "entry"

        # Simple analysis based on titles
        titles = [exp.get("title", "").lower() for exp in experience]

        if any("senior" in title or "lead" in title for title in titles):
            return "senior"
        elif any("manager" in title or "director" in title for title in titles):
            return "management"
        else:
            return "mid"

    def _extract_achievements(self, experience: List[Dict[str, Any]]) -> List[str]:
        """Extract key achievements from experience."""
        achievements = []

        for exp in experience:
            description = exp.get("description", "")
            if description:
                # Simple extraction - in real app, would use NLP
                if (
                    "improved" in description.lower()
                    or "increased" in description.lower()
                ):
                    achievements.append(description)

        return achievements

    def _generate_experience_insights(
        self, experience: List[Dict[str, Any]], total_experience: float
    ) -> List[str]:
        """Generate experience-based insights."""
        insights = []

        if total_experience > 5:
            insights.append("Experienced professional with solid track record")
        elif total_experience > 2:
            insights.append("Mid-level professional with growing expertise")
        else:
            insights.append("Early career professional with potential for growth")

        return insights

    def _assess_education_relevance(self, education: List[Dict[str, Any]]) -> str:
        """Assess relevance of education to tech roles."""
        relevant_fields = [
            "computer",
            "engineering",
            "science",
            "technology",
            "mathematics",
        ]

        for edu in education:
            field = edu.get("field_of_study", "").lower()
            if any(relevant in field for relevant in relevant_fields):
                return "high"

        return "medium"

    def _generate_education_insights(
        self, education: List[Dict[str, Any]], highest_degree: str
    ) -> List[str]:
        """Generate education-based insights."""
        insights = []

        if highest_degree in ["master", "phd"]:
            insights.append("Advanced degree demonstrates commitment to learning")
        elif highest_degree == "bachelor":
            insights.append("Solid educational foundation")
        else:
            insights.append(
                "Consider highlighting relevant coursework or certifications"
            )

        return insights

    def _identify_skill_strengths(
        self, skill_categories: Dict[str, List[str]]
    ) -> List[str]:
        """Identify skill strengths."""
        strengths = []

        for category, skills in skill_categories.items():
            if len(skills) >= 3:
                strengths.append(f"Strong in {category.replace('_', ' ')}")

        return strengths

    def _identify_skill_gaps(self, skill_categories: Dict[str, List[str]]) -> List[str]:
        """Identify skill gaps."""
        gaps = []

        if not skill_categories["programming"]:
            gaps.append("Programming languages")
        if not skill_categories["cloud"]:
            gaps.append("Cloud technologies")
        if not skill_categories["frameworks"]:
            gaps.append("Modern frameworks")

        return gaps
