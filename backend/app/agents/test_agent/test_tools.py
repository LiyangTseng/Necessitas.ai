"""
Test script for Test Agent tools
Run this to verify that all tools work correctly before deploying the agent.
"""

import sys
import os

# Add backend/app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from tools import (
    search_jobs,
    parse_resume_text,
    analyze_skill_gap,
    match_jobs_to_profile,
    generate_learning_path,
    get_job_market_insights
)


def test_search_jobs():
    """Test job search functionality."""
    print("\n" + "="*60)
    print("Testing: search_jobs")
    print("="*60)

    result = search_jobs("Python Developer", "San Francisco", 5)
    print(f"Success: {result['success']}")
    print(f"Jobs found: {result['count']}")

    if result['success'] and result['jobs']:
        print("\nFirst job:")
        job = result['jobs'][0]
        print(f"  Title: {job['title']}")
        print(f"  Company: {job['company']}")
        print(f"  Location: {job['location']}")
        print(f"  Requirements: {job['requirements'][:3]}")

    return result['success']


def test_parse_resume():
    """Test resume parsing functionality."""
    print("\n" + "="*60)
    print("Testing: parse_resume_text")
    print("="*60)

    sample_resume = """
John Doe
Software Engineer
Email: john.doe@example.com
Phone: (555) 123-4567
Location: San Francisco, CA

Skills: Python, JavaScript, React, Django, SQL, AWS, Docker

Experience:
Senior Software Engineer at Tech Corp
San Francisco, CA
January 2020 - Present
- Built scalable web applications using Django and React
- Managed AWS infrastructure and Docker deployments
- Led a team of 5 developers

Software Engineer at StartupXYZ
New York, NY
June 2018 - December 2019
- Developed REST APIs using Flask
- Implemented CI/CD pipelines

Education:
Bachelor of Science in Computer Science
Stanford University
2014 - 2018
GPA: 3.8
"""

    result = parse_resume_text(sample_resume)
    print(f"Success: {result['success']}")

    if result['success']:
        data = result['data']
        print(f"\nName: {data['personal_info']['name']}")
        print(f"Email: {data['personal_info']['email']}")
        print(f"Skills: {len(data['skills'])} skills found")
        print(f"  Top skills: {data['skills'][:5]}")
        print(f"Experience: {len(data['experience'])} positions")
        print(f"Confidence: {data['confidence_score']:.2f}")

    return result['success']


def test_skill_gap_analysis():
    """Test skill gap analysis functionality."""
    print("\n" + "="*60)
    print("Testing: analyze_skill_gap")
    print("="*60)

    user_skills = ["Python", "Django", "SQL", "Git"]
    target_role = "Full Stack Developer"

    result = analyze_skill_gap(user_skills, target_role)
    print(f"Success: {result['success']}")

    if result['success']:
        print(f"\nTarget Role: {result['target_role']}")
        print(f"Match Percentage: {result['match_percentage']}%")
        print(f"Readiness Level: {result['readiness_level']}")
        print(f"\nMatched Skills ({len(result['matched_skills'])}):")
        print(f"  {result['matched_skills']}")
        print(f"\nMissing Skills ({len(result['missing_skills'])}):")
        print(f"  {result['missing_skills']}")
        print(f"\nTop Learning Recommendations:")
        for rec in result['learning_recommendations'][:3]:
            print(f"  - {rec['skill']} ({rec['priority']} priority)")

    return result['success']


def test_job_matching():
    """Test job matching functionality."""
    print("\n" + "="*60)
    print("Testing: match_jobs_to_profile")
    print("="*60)

    user_skills = ["Python", "Django", "React", "SQL", "AWS"]
    job_query = "Full Stack Developer"

    result = match_jobs_to_profile(user_skills, job_query, min_score=0.3)
    print(f"Success: {result['success']}")

    if result['success']:
        print(f"\nQuery: {result['query']}")
        print(f"Total jobs searched: {result['total_jobs_searched']}")
        print(f"Matched jobs: {result['match_count']}")
        print(f"Average match score: {result['average_match_score']}")

        if result['matched_jobs']:
            print("\nTop 3 matches:")
            for i, match in enumerate(result['matched_jobs'][:3], 1):
                print(f"\n  {i}. {match['job']['title']} at {match['job']['company']}")
                print(f"     Match Score: {match['match_score']}")
                print(f"     Skill Matches: {match['skill_matches'][:3]}")
                print(f"     Skill Gaps: {match['skill_gaps'][:3]}")

    return result['success']


def test_learning_path_generation():
    """Test learning path generation functionality."""
    print("\n" + "="*60)
    print("Testing: generate_learning_path")
    print("="*60)

    user_skills = ["Python", "SQL"]
    target_role = "Data Scientist"
    timeline = 6

    result = generate_learning_path(target_role, user_skills, timeline)
    print(f"Success: {result['success']}")

    if result['success']:
        print(f"\nTarget Role: {result['target_role']}")
        print(f"Timeline: {result['timeline_months']} months")
        print(f"Study Hours/Week: {result['estimated_study_hours_per_week']}")

        print(f"\nSkill Gap Summary:")
        summary = result['skill_gap_summary']
        print(f"  Total skills needed: {summary['total_skills_needed']}")
        print(f"  Skills you have: {summary['skills_you_have']}")
        print(f"  Skills to learn: {summary['skills_to_learn']}")
        print(f"  Readiness: {summary['readiness_level']}")

        print(f"\nLearning Milestones:")
        for milestone in result['learning_milestones'][:3]:
            print(f"\n  Month {milestone['month']}: {milestone['milestone_title']}")
            print(f"    Skills: {milestone['skills_to_learn']}")
            print(f"    Activities: {len(milestone['learning_activities'])} activities")

        print(f"\nNetworking Goals:")
        for goal in result['networking_goals']:
            print(f"  - {goal}")

    return result['success']


def test_market_insights():
    """Test market insights functionality."""
    print("\n" + "="*60)
    print("Testing: get_job_market_insights")
    print("="*60)

    role = "Software Engineer"
    location = "San Francisco"

    result = get_job_market_insights(role, location)
    print(f"Success: {result['success']}")

    if result['success']:
        print(f"\nRole: {result['role']}")
        print(f"Location: {result['location']}")
        print(f"Total job postings: {result['total_job_postings']}")
        print(f"Remote percentage: {result['remote_job_percentage']}%")
        print(f"Demand level: {result['demand_level']}")

        print(f"\nTop Required Skills:")
        for skill in result['top_required_skills'][:5]:
            print(f"  - {skill['skill']}: {skill['frequency']} jobs")

        print(f"\nTop Hiring Companies:")
        for company in result['top_hiring_companies'][:5]:
            print(f"  - {company}")

        print(f"\nMarket Insights:")
        insights = result['market_insights']
        print(f"  Trend: {insights['trend']}")
        print(f"  Competition: {insights['competition_level']}")
        print(f"  Recommendation: {insights['recommendation']}")

    return result['success']


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print(" TEST AGENT TOOLS - COMPREHENSIVE TESTING")
    print("="*80)

    tests = [
        ("Search Jobs", test_search_jobs),
        ("Parse Resume", test_parse_resume),
        ("Skill Gap Analysis", test_skill_gap_analysis),
        ("Job Matching", test_job_matching),
        ("Learning Path Generation", test_learning_path_generation),
        ("Market Insights", test_market_insights)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = "✓ PASS" if success else "✗ FAIL"
        except Exception as e:
            results[test_name] = f"✗ ERROR: {str(e)[:50]}"

    # Summary
    print("\n" + "="*80)
    print(" TEST SUMMARY")
    print("="*80)
    for test_name, result in results.items():
        print(f"{test_name:.<40} {result}")

    passed = sum(1 for r in results.values() if "PASS" in r)
    total = len(results)
    print("\n" + "="*80)
    print(f" TOTAL: {passed}/{total} tests passed")
    print("="*80)


if __name__ == "__main__":
    # Check if FastAPI backend is required
    print("NOTE: Make sure FastAPI backend is running at http://localhost:8000")
    print("Start it with: python backend/app/main.py")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)

    run_all_tests()
