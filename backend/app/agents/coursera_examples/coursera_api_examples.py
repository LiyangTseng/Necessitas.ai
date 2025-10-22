#!/usr/bin/env python3
"""
Coursera API Usage Examples

This script demonstrates how to use the Coursera API endpoints
with various input parameters and shows the expected outputs.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.coursera_service import CourseraService
from app.models.coursera import (
    CourseSearchRequest, CertificationSearchRequest,
    CourseLevel, CourseType, Language
)


async def example_course_search():
    """Example: Search for courses with different parameters."""
    print("=" * 60)
    print("EXAMPLE 1: COURSE SEARCH")
    print("=" * 60)
    
    coursera_service = CourseraService()
    
    # Example 1: Basic course search
    print("\n1. Basic Course Search:")
    print("Input: Search for 'python' courses")
    
    request = CourseSearchRequest(
        query="python",
        limit=3
    )
    
    response = await coursera_service.search_courses(request)
    
    print(f"Output: Found {len(response.courses)} courses")
    for i, course in enumerate(response.courses, 1):
        print(f"  {i}. {course.title}")
        print(f"     Institution: {course.institution}")
        print(f"     Level: {course.level}")
        print(f"     Skills: {', '.join(course.skills)}")
        print(f"     Free: {course.is_free}")
        print(f"     URL: {course.url}")
        print()
    
    # Example 2: Advanced course search with filters
    print("\n2. Advanced Course Search with Filters:")
    print("Input: Search for 'machine learning' courses, intermediate level, free only")
    
    request = CourseSearchRequest(
        query="machine learning",
        skills=["python", "statistics"],
        level=CourseLevel.INTERMEDIATE,
        is_free=True,
        limit=2
    )
    
    response = await coursera_service.search_courses(request)
    
    print(f"Output: Found {len(response.courses)} courses")
    for i, course in enumerate(response.courses, 1):
        print(f"  {i}. {course.title}")
        print(f"     Institution: {course.institution}")
        print(f"     Level: {course.level}")
        print(f"     Free: {course.is_free}")
        print(f"     Duration: {course.duration_weeks} weeks")
        print()


async def example_certification_search():
    """Example: Search for certifications."""
    print("=" * 60)
    print("EXAMPLE 2: CERTIFICATION SEARCH")
    print("=" * 60)
    
    coursera_service = CourseraService()
    
    # Example 1: Professional certificate search
    print("\n1. Professional Certificate Search:")
    print("Input: Search for 'data science' certifications")
    
    request = CertificationSearchRequest(
        query="data science",
        skills=["python", "machine learning"],
        course_type=CourseType.PROFESSIONAL_CERTIFICATE,
        limit=2
    )
    
    response = await coursera_service.search_certifications(request)
    
    print(f"Output: Found {len(response.certifications)} certifications")
    for i, cert in enumerate(response.certifications, 1):
        print(f"  {i}. {cert.name}")
        print(f"     Institution: {cert.institution}")
        print(f"     Type: {cert.course_type}")
        print(f"     Skills: {', '.join(cert.skills)}")
        print(f"     Free: {cert.is_free}")
        print(f"     Price: ${cert.price} {cert.currency}")
        print(f"     Industry Recognition: {cert.industry_recognition}")
        print(f"     URL: {cert.url}")
        print()


async def example_learning_recommendations():
    """Example: Get personalized learning recommendations."""
    print("=" * 60)
    print("EXAMPLE 3: LEARNING RECOMMENDATIONS")
    print("=" * 60)
    
    coursera_service = CourseraService()
    
    # Example 1: Career development recommendations
    print("\n1. Career Development Recommendations:")
    print("Input: User wants to become a Data Scientist")
    print("       Skill gaps: ['python', 'machine learning', 'data analysis']")
    
    recommendations = await coursera_service.get_learning_recommendations(
        user_id="user_123",
        skill_gaps=["python", "machine learning", "data analysis"],
        target_role="Data Scientist"
    )
    
    print(f"Output: Learning recommendations for {recommendations.target_role}")
    print(f"        Estimated completion time: {recommendations.estimated_completion_time} weeks")
    print(f"        Recommended courses: {len(recommendations.recommended_courses)}")
    print(f"        Recommended certifications: {len(recommendations.recommended_certifications)}")
    print(f"        Learning path steps: {len(recommendations.learning_path)}")
    
    print("\nRecommended Courses:")
    for i, course in enumerate(recommendations.recommended_courses, 1):
        print(f"  {i}. {course.title}")
        print(f"     Institution: {course.institution}")
        print(f"     Skills: {', '.join(course.skills)}")
        print(f"     Duration: {course.duration_weeks} weeks")
        print()
    
    print("Recommended Certifications:")
    for i, cert in enumerate(recommendations.recommended_certifications, 1):
        print(f"  {i}. {cert.name}")
        print(f"     Institution: {cert.institution}")
        print(f"     Skills: {', '.join(cert.skills)}")
        print()
    
    print("Learning Path:")
    for i, step in enumerate(recommendations.learning_path, 1):
        print(f"  Step {i}: {step.get('title', 'Learning Step')}")
        print(f"    Duration: {step.get('duration_weeks', 'N/A')} weeks")
        print(f"    Skills: {', '.join(step.get('skills_covered', []))}")
        print()


async def main():
    """Run all examples."""
    print("COURSERA API USAGE EXAMPLES")
    print("=" * 60)
    print("This script demonstrates how to use the Coursera API")
    print("with various input parameters and shows expected outputs.")
    print()
    
    await example_course_search()
    await example_certification_search()
    await example_learning_recommendations()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("The Coursera API provides:")
    print("1. Course search with filtering by skills, level, price, etc.")
    print("2. Certification search with industry recognition filters")
    print("3. Personalized learning recommendations based on skill gaps")
    print("4. Learning path generation for career development")
    print("5. Integration with job matching for skill gap analysis")
    print()
    print("All endpoints work with both GET and POST methods")
    print("Mock data is used when RapidAPI key is not available")
    print("Real API data is used when RAPIDAPI_KEY environment variable is set")


if __name__ == "__main__":
    asyncio.run(main())
