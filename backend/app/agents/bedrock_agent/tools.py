from strands import tool
from services.job_matching_engine import JobMatchingEngine
from services.resume_parser import ResumeParser
from services.job_fetcher.service import JobFetcher
from services.company_info_fetcher.service import CompanyInfoFetcher
from models import UserProfile, JobPosting

# Initialize services
job_matcher = JobMatchingEngine()
resume_parser = ResumeParser()
job_fetcher = JobFetcher()
company_fetcher = CompanyInfoFetcher()

@tool
def find_job_matches(user_profile_data: dict, job_criteria: dict) -> dict:
    """Find matching jobs for a user profile."""
    # Convert dict to UserProfile object
    user_profile = UserProfile(**user_profile_data)
    # Call service
    matches = job_matcher.find_matches(user_profile, job_criteria)
    return matches

@tool
def parse_resume(resume_text: str) -> dict:
    """Parse resume text and extract structured information."""
    result = resume_parser.parse_resume(resume_text)
    return result

@tool
def search_jobs(query: str, location: str, limit: int = 10) -> dict:
    """Search for jobs based on query and location."""
    jobs = job_fetcher.search_jobs(query, location, limit)
    return jobs

@tool
def get_company_info(company_name: str) -> dict:
    """Get detailed company information."""
    info = company_fetcher.get_company_info(company_name)
    return info
