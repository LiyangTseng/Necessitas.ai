#!/usr/bin/env python3
"""
Test script for debugging resume parser functionality
"""

import sys
from pathlib import Path
from resume_parser_dev import ResumeParserDev

def test_parsing_functions():
    """Test individual parsing functions with sample data."""
    parser = ResumeParserDev()
    
    # Test personal info extraction
    print("=== Testing Personal Info Extraction ===")
    sample_text = """
    John Doe
    Senior Software Engineer
    john.doe@email.com
    +1-555-123-4567
    San Francisco, CA
    https://linkedin.com/in/johndoe
    https://github.com/johndoe
    """
    
    personal_info = parser._extract_personal_info(sample_text)
    print(f"Name: {personal_info.name}")
    print(f"Email: {personal_info.email}")
    print(f"Phone: {personal_info.phone}")
    print(f"Location: {personal_info.location}")
    print(f"LinkedIn: {personal_info.linkedin_url}")
    print(f"GitHub: {personal_info.github_url}")
    print()
    
    # Test skills extraction
    print("=== Testing Skills Extraction ===")
    skills_text = """
    SKILLS
    Programming Languages: Python, JavaScript, TypeScript, Java, SQL
    Frameworks: React, Node.js, Express, Django, Flask
    Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, Terraform
    Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
    """
    
    skills = parser._extract_skills(skills_text)
    print(f"Skills found: {skills}")
    print()
    
    # Test experience extraction
    print("=== Testing Experience Extraction ===")
    experience_text = """
    EXPERIENCE
    Senior Software Engineer - TechCorp
    San Francisco, CA
    Jan 2021 - Present
    • Led development of microservices architecture serving 1M+ users
    • Mentored 3 junior developers and conducted code reviews
    • Technologies: Python, React, AWS, Docker, Kubernetes
    
    Software Engineer - StartupXYZ
    San Francisco, CA
    Jun 2019 - Dec 2020
    • Developed full-stack web applications using modern frameworks
    • Collaborated with product team to define technical requirements
    • Technologies: Python, JavaScript, PostgreSQL, Redis
    """
    
    experiences = parser._extract_experience(experience_text)
    print(f"Found {len(experiences)} experience entries:")
    for i, exp in enumerate(experiences, 1):
        print(f"  {i}. {exp.title} at {exp.company}")
        print(f"     Duration: {exp.start_date} - {exp.end_date}")
        print(f"     Current: {exp.current}")
        print(f"     Description: {exp.description[:100]}...")
        print()
    
    # Test education extraction
    print("=== Testing Education Extraction ===")
    education_text = """
    EDUCATION
    Bachelor of Computer Science
    University of Technology
    San Francisco, CA
    2014 - 2018
    GPA: 3.8
    Dean's List: 2016-2018
    """
    
    education = parser._extract_education(education_text)
    print(f"Found {len(education)} education entries:")
    for i, edu in enumerate(education, 1):
        print(f"  {i}. {edu.degree} in {edu.field_of_study}")
        print(f"     School: {edu.school}")
        print(f"     Location: {edu.location}")
        print(f"     Duration: {edu.start_date} - {edu.end_date}")
        print(f"     GPA: {edu.gpa}")
        print()

def test_full_resume():
    """Test parsing a full resume."""
    print("=== Testing Full Resume Parsing ===")
    parser = ResumeParserDev()
    
    # Read sample resume
    with open("test_resumes/sample_resume_1.txt", "r") as f:
        content = f.read()
    
    print("Raw text preview:")
    print(content[:500] + "...")
    print("\n" + "="*50 + "\n")
    
    # Parse the resume
    resume_data = parser._parse_resume_data(content)
    
    print("Parsed Results:")
    print(f"Name: {resume_data.personal_info.name}")
    print(f"Email: {resume_data.personal_info.email}")
    print(f"Phone: {resume_data.personal_info.phone}")
    print(f"Location: {resume_data.personal_info.location}")
    print(f"Skills: {resume_data.skills}")
    print(f"Experience entries: {len(resume_data.experience)}")
    print(f"Education entries: {len(resume_data.education)}")
    print(f"Confidence: {resume_data.confidence_score}")

if __name__ == "__main__":
    test_parsing_functions()
    print("\n" + "="*80 + "\n")
    test_full_resume()
