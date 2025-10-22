#!/usr/bin/env python3
"""
Simple Coursera API Usage Examples

This script shows the most common ways to use the Coursera API
with clear input/output examples.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.services.coursera_service import CourseraService
from app.models.coursera import CourseSearchRequest, CertificationSearchRequest


async def simple_examples():
    """Simple examples of using the Coursera API."""
    
    # Initialize the service
    coursera_service = CourseraService()
    print("Coursera Service initialized!")
    print(f"API Available: {coursera_service.is_available}")
    print()
    
    # Example 1: Search for Python courses
    print("EXAMPLE 1: Search for Python courses")
    print("-" * 40)
    
    # Input: What we want to search for
    course_request = CourseSearchRequest(
        query="python",
        skills=["programming"],
        limit=2
    )
    
    print("INPUT:")
    print(f"  Query: {course_request.query}")
    print(f"  Skills: {course_request.skills}")
    print(f"  Limit: {course_request.limit}")
    print()
    
    # Output: What we get back
    course_response = await coursera_service.search_courses(course_request)
    
    print("OUTPUT:")
    print(f"  Found {len(course_response.courses)} courses")
    print()
    
    for i, course in enumerate(course_response.courses, 1):
        print(f"  Course {i}:")
        print(f"    Title: {course.title}")
        print(f"    Institution: {course.institution}")
        print(f"    Level: {course.level}")
        print(f"    Skills: {', '.join(course.skills)}")
        print(f"    Free: {course.is_free}")
        print(f"    URL: {course.url}")
        print()
    
    # Example 2: Search for certifications
    print("EXAMPLE 2: Search for Data Science certifications")
    print("-" * 40)
    
    # Input: What we want to search for
    cert_request = CertificationSearchRequest(
        query="data science",
        skills=["python", "machine learning"],
        limit=1
    )
    
    print("INPUT:")
    print(f"  Query: {cert_request.query}")
    print(f"  Skills: {cert_request.skills}")
    print(f"  Limit: {cert_request.limit}")
    print()
    
    # Output: What we get back
    cert_response = await coursera_service.search_certifications(cert_request)
    
    print("OUTPUT:")
    print(f"  Found {len(cert_response.certifications)} certifications")
    print()
    
    for i, cert in enumerate(cert_response.certifications, 1):
        print(f"  Certification {i}:")
        print(f"    Name: {cert.name}")
        print(f"    Institution: {cert.institution}")
        print(f"    Skills: {', '.join(cert.skills)}")
        print(f"    Free: {cert.is_free}")
        print(f"    Price: ${cert.price} {cert.currency}")
        print(f"    URL: {cert.url}")
        print()
    
    # Example 3: Get learning recommendations
    print("EXAMPLE 3: Get learning recommendations for a Data Scientist")
    print("-" * 40)
    
    # Input: User's skill gaps and target role
    user_id = "user_123"
    skill_gaps = ["python", "machine learning", "data analysis"]
    target_role = "Data Scientist"
    
    print("INPUT:")
    print(f"  User ID: {user_id}")
    print(f"  Skill Gaps: {skill_gaps}")
    print(f"  Target Role: {target_role}")
    print()
    
    # Output: Learning recommendations
    recommendations = await coursera_service.get_learning_recommendations(
        user_id=user_id,
        skill_gaps=skill_gaps,
        target_role=target_role
    )
    
    print("OUTPUT:")
    print(f"  Target Role: {recommendations.target_role}")
    print(f"  Skill Gaps: {recommendations.skill_gaps}")
    print(f"  Recommended Courses: {len(recommendations.recommended_courses)}")
    print(f"  Recommended Certifications: {len(recommendations.recommended_certifications)}")
    print(f"  Estimated Completion Time: {recommendations.estimated_completion_time} weeks")
    print(f"  Learning Path Steps: {len(recommendations.learning_path)}")
    print()
    
    # Show the learning path
    if recommendations.learning_path:
        print("  Learning Path:")
        for i, step in enumerate(recommendations.learning_path, 1):
            print(f"    Step {i}: {step.get('title', 'Learning Step')}")
            print(f"      Duration: {step.get('duration_weeks', 'N/A')} weeks")
            print(f"      Skills: {', '.join(step.get('skills_covered', []))}")
            print()


async def main():
    """Run all examples."""
    print("COURSERA API USAGE GUIDE")
    print("=" * 50)
    print()
    
    await simple_examples()
    
    print("SUMMARY")
    print("=" * 50)
    print("The Coursera API helps you:")
    print("• Find relevant courses and certifications")
    print("• Get personalized learning recommendations")
    print("• Create learning paths for career development")
    print("• Bridge skill gaps for specific jobs")
    print()
    print("All endpoints work with both GET and POST methods")
    print("Mock data is used when API key is not available")
    print("Real API data is used when RAPIDAPI_KEY is set")


if __name__ == "__main__":
    asyncio.run(main())
