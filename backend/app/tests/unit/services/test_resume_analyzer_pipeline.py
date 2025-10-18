import asyncio
import json
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from app.services.resume_parser import ResumeParser
from app.agents.resume_analyzer.resume_analyzer import ResumeAnalyzer
from app.services.job_matching_engine import JobMatchingEngine
from app.models import JobPosting
from app.models.base import ExperienceLevel, WorkType, LocationPreference
from app.models.user import UserProfile, Skill, WorkExperience, Education, Certification, CareerPreference
from datetime import datetime
from loguru import logger
from dataclasses import dataclass, field
from pydantic.json import pydantic_encoder

def resume_to_user_profile(resume_data):
    """Convert ResumeData (dataclass) → UserProfile (Pydantic model)."""
    # 1. personal_info dict
    personal_info_dict = {
        "name": resume_data.personal_info.name,
        "email": resume_data.personal_info.email,
        "phone": resume_data.personal_info.phone,
        "location": resume_data.personal_info.location,
        "linkedin_url": resume_data.personal_info.linkedin_url,
        "github_url": resume_data.personal_info.github_url,
        "website": resume_data.personal_info.website,
    }

    # 2. skills (全部給 level=3)
    skill_models = [Skill(name=s, level=3, category="general") for s in resume_data.skills]

    # 3. experience
    exp_models = [
        WorkExperience(
            title=exp.title,
            company=exp.company,
            location=exp.location,
            start_date=exp.start_date or datetime.now(),
            end_date=exp.end_date,
            current=exp.current,
            description=exp.description,
            achievements=exp.achievements,
            skills_used=exp.skills_used,
        )
        for exp in resume_data.experience
    ]

    # 4. education
    edu_models = [
        Education(
            degree=edu.degree,
            institution=edu.school,
            field_of_study=edu.major,
            graduation_date=edu.end_date or datetime.now(),
            gpa=edu.gpa,
            honors=edu.honors,
        )
        for edu in resume_data.education
    ]

    # 5. certification
    cert_models = [
        Certification(
            name=cert.name,
            issuer=cert.issuer,
            issue_date=cert.date_earned or datetime.now(),
            expiry_date=cert.expiry_date,
            credential_id=cert.credential_id,
        )
        for cert in resume_data.certifications
    ]

    return UserProfile(
        user_id="test_user",
        personal_info=personal_info_dict,
        skills=skill_models,
        experience=exp_models,
        education=edu_models,
        certifications=cert_models,
        preferences=CareerPreference(),
    )

async def main():
    """
    End-to-end test for resume analyzer pipeline:
    1. Extract text using AWS Textract (fallback enabled)
    2. Send parsed output to JobMatchingEngine / ResumeAnalyzer
    3. Print JSON result
    """
    sample_resume = "app/tests/samples/resume.pdf"
    if not os.path.exists(sample_resume):
        logger.error(f"Test resume file not found: {sample_resume}")
        return

    # Step 1: Parsering
    parser = ResumeParser()
    logger.info("Starting Textract resume parsing...")
    resume_data = await parser.parse_resume(sample_resume)
    logger.info("Parsing complete — proceeding to analysis stage")

    # Step 2: Analysis
    logger.info("Stage 2: Convert to standardized UserProfile")
    analyzed_profile = resume_to_user_profile(resume_data)
    logger.success("UserProfile Ready")
    
    # Step 3: Job Matching
    
    # this is just for testing
    fake_job = JobPosting(
        job_id="fake-123",
        title="Software Engineer",
        company="OpenAI",
        location="Remote",
        requirements=["python", "machine learning", "aws"],
        experience_level=ExperienceLevel.MID,
        salary_min=80000,
        salary_max=150000,
        remote=True
    )

    matcher = JobMatchingEngine()
    logger.info("Stage 3: Job Matching")
    match_result = matcher.analyze_match(analyzed_profile, fake_job)
    logger.success("Matching Done")

    # Step 4: Output JSON
    print("\n===== FINAL PIPELINE JSON =====")
    print(json.dumps(match_result, indent=2, default=pydantic_encoder))


if __name__ == "__main__":
    asyncio.run(main())


# by chatgpt:
# Pipeline 已經完整打通，從 PDF 履歷 → 解析 → 轉成標準化 UserProfile → JobMatchingEngine 分析 → 回傳 JSON 結果，全流程目前是成功可執行的。
# 主要問題在於解析層太淺：skills 沒抓準（導致明明會 Python/ML 卻被當缺），experience 只讀標題沒讀內容，加上 matching 還是關鍵字規則式，沒有語意理解，結果評分被低估。
