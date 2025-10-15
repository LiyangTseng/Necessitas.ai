"""
AWS Lambda Function: Resume Parser

Processes resume files using AWS Textract and extracts structured information.
"""

import json
import boto3
import base64
from typing import Dict, Any
import re
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client("s3")
textract_client = boto3.client("textract")
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for resume parsing.

    Args:
        event: Lambda event containing file information
        context: Lambda context

    Returns:
        Parsed resume data
    """
    try:
        # Extract file information from event
        bucket_name = event.get("bucket")
        file_key = event.get("key")
        user_id = event.get("user_id")

        if not all([bucket_name, file_key, user_id]):
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {"error": "Missing required parameters: bucket, key, user_id"}
                ),
            }

        # Download file from S3
        file_content = download_file_from_s3(bucket_name, file_key)

        # Parse resume based on file type
        file_extension = file_key.split(".")[-1].lower()

        if file_extension == "pdf":
            parsed_data = parse_pdf_resume(file_content)
        elif file_extension in ["docx", "doc"]:
            parsed_data = parse_docx_resume(file_content)
        else:
            parsed_data = parse_text_resume(file_content)

        # Store results in DynamoDB
        store_resume_data(user_id, parsed_data)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "user_id": user_id,
                    "parsed_data": parsed_data,
                    "message": "Resume parsed successfully",
                }
            ),
        }

    except Exception as e:
        print(f"Error processing resume: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Failed to parse resume: {str(e)}"}),
        }


def download_file_from_s3(bucket_name: str, file_key: str) -> bytes:
    """Download file from S3."""
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return response["Body"].read()
    except Exception as e:
        raise Exception(f"Failed to download file from S3: {str(e)}")


def parse_pdf_resume(file_content: bytes) -> Dict[str, Any]:
    """Parse PDF resume using Textract."""
    try:
        # Use Textract to extract text
        response = textract_client.detect_document_text(
            Document={"Bytes": file_content}
        )

        # Extract text from Textract response
        text = extract_text_from_textract(response)

        # Parse the extracted text
        return parse_resume_text(text)

    except Exception as e:
        raise Exception(f"Failed to parse PDF: {str(e)}")


def parse_docx_resume(file_content: bytes) -> Dict[str, Any]:
    """Parse DOCX resume."""
    try:
        # For DOCX files, we would use python-docx library
        # This is a simplified version
        text = file_content.decode("utf-8", errors="ignore")
        return parse_resume_text(text)
    except Exception as e:
        raise Exception(f"Failed to parse DOCX: {str(e)}")


def parse_text_resume(file_content: bytes) -> Dict[str, Any]:
    """Parse plain text resume."""
    try:
        text = file_content.decode("utf-8", errors="ignore")
        return parse_resume_text(text)
    except Exception as e:
        raise Exception(f"Failed to parse text: {str(e)}")


def extract_text_from_textract(response: Dict[str, Any]) -> str:
    """Extract text from Textract response."""
    text = ""
    for block in response.get("Blocks", []):
        if block.get("BlockType") == "LINE":
            text += block.get("Text", "") + "\n"
    return text


def parse_resume_text(text: str) -> Dict[str, Any]:
    """Parse resume text and extract structured information."""
    # Clean text
    text = re.sub(r"\s+", " ", text).strip()

    # Extract personal information
    personal_info = extract_personal_info(text)

    # Extract skills
    skills = extract_skills(text)

    # Extract experience
    experience = extract_experience(text)

    # Extract education
    education = extract_education(text)

    # Extract certifications
    certifications = extract_certifications(text)

    return {
        "personal_info": personal_info,
        "skills": skills,
        "experience": experience,
        "education": education,
        "certifications": certifications,
        "raw_text": text,
        "parsed_at": datetime.now().isoformat(),
    }


def extract_personal_info(text: str) -> Dict[str, str]:
    """Extract personal information from resume text."""
    personal_info = {}

    # Email
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    email_match = re.search(email_pattern, text)
    if email_match:
        personal_info["email"] = email_match.group()

    # Phone
    phone_pattern = r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})"
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        personal_info["phone"] = phone_match.group()

    # LinkedIn
    linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?"
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        personal_info["linkedin"] = linkedin_match.group()

    return personal_info


def extract_skills(text: str) -> list:
    """Extract skills from resume text."""
    # Common technical skills
    technical_skills = [
        "Python",
        "Java",
        "JavaScript",
        "TypeScript",
        "React",
        "Vue",
        "Angular",
        "Node.js",
        "Express",
        "Django",
        "Flask",
        "FastAPI",
        "Spring",
        "Laravel",
        "AWS",
        "Azure",
        "GCP",
        "Docker",
        "Kubernetes",
        "Jenkins",
        "Git",
        "MySQL",
        "PostgreSQL",
        "MongoDB",
        "Redis",
        "Elasticsearch",
        "Machine Learning",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Data Science",
        "Pandas",
        "NumPy",
        "Matplotlib",
        "Seaborn",
        "Agile",
        "Scrum",
        "DevOps",
        "CI/CD",
        "Microservices",
    ]

    found_skills = []
    text_lower = text.lower()

    for skill in technical_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


def extract_experience(text: str) -> list:
    """Extract work experience from resume text."""
    experience = []

    # Look for experience section
    exp_section = re.search(
        r"(?i)(experience|work\s+history|employment|professional\s+experience)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
        text,
        re.DOTALL,
    )
    if exp_section:
        exp_text = exp_section.group(2)

        # Split by common patterns
        entries = re.split(r"\n(?=\w)", exp_text)

        for entry in entries:
            if entry.strip():
                # Extract job title, company, and duration
                title_match = re.search(r"^([^,\n]+)", entry)
                company_match = re.search(r"at\s+([^,\n]+)", entry, re.IGNORECASE)
                duration_match = re.search(
                    r"(\d{4}[-–]\d{4}|\d{4}\s*[-–]\s*present|\d{4}\s*[-–]\s*now)",
                    entry,
                    re.IGNORECASE,
                )

                if title_match:
                    exp_entry = {
                        "title": title_match.group(1).strip(),
                        "company": (
                            company_match.group(1).strip() if company_match else ""
                        ),
                        "duration": (
                            duration_match.group(1).strip() if duration_match else ""
                        ),
                        "description": entry.strip(),
                    }
                    experience.append(exp_entry)

    return experience


def extract_education(text: str) -> list:
    """Extract education information from resume text."""
    education = []

    # Look for education section
    edu_section = re.search(
        r"(?i)(education|academic\s+background|qualifications)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
        text,
        re.DOTALL,
    )
    if edu_section:
        edu_text = edu_section.group(2)

        # Split by common patterns
        entries = re.split(r"\n(?=\w)", edu_text)

        for entry in entries:
            if entry.strip():
                # Extract degree, institution, and year
                degree_match = re.search(r"^([^,\n]+)", entry)
                institution_match = re.search(r"at\s+([^,\n]+)", entry, re.IGNORECASE)
                year_match = re.search(r"(\d{4})", entry)

                if degree_match:
                    edu_entry = {
                        "degree": degree_match.group(1).strip(),
                        "institution": (
                            institution_match.group(1).strip()
                            if institution_match
                            else ""
                        ),
                        "year": year_match.group(1).strip() if year_match else "",
                        "description": entry.strip(),
                    }
                    education.append(edu_entry)

    return education


def extract_certifications(text: str) -> list:
    """Extract certifications from resume text."""
    certifications = []

    # Look for certifications section
    cert_section = re.search(
        r"(?i)(certifications|certificates|licenses)[:\s]*(.*?)(?=\n\n|\n[A-Z]|$)",
        text,
        re.DOTALL,
    )
    if cert_section:
        cert_text = cert_section.group(2)

        # Split by lines and extract individual certifications
        lines = cert_text.split("\n")
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:
                certifications.append(line)

    return certifications


def store_resume_data(user_id: str, parsed_data: Dict[str, Any]) -> None:
    """Store parsed resume data in DynamoDB."""
    try:
        table = dynamodb.Table("careercompass-ai-user-profiles")

        table.put_item(
            Item={
                "user_id": user_id,
                "resume_data": parsed_data,
                "updated_at": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        print(f"Failed to store resume data: {str(e)}")
        # Don't raise exception to avoid failing the entire process
