"""
Resume Parser Service

Service for parsing resumes using AWS Textract and AI-powered analysis.
Extracts skills, experience, education, and other key information.
"""

import boto3
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
# import spacy
# from spacy.matcher import Matcher
import requests
from urllib.parse import urlparse

from core.env import get_textract_credentials
import logging

# Import centralized models
from models import PersonalInfo, Experience, Education, Certification, ResumeData

logger = logging.getLogger(__name__)

class ResumeParser:
    """Main resume parsing service using AWS Textract and NLP."""

    def __init__(self):
        """Initialize the resume parser."""
        # AWS Textract client
        textract_credentials = get_textract_credentials()
        self.textract = boto3.client(
            "textract",
            aws_access_key_id=textract_credentials["aws_access_key_id"],
            aws_secret_access_key=textract_credentials["aws_secret_access_key"],
            region_name=textract_credentials["region_name"]
        )

        self.nlp = None
        # Load spaCy model
        # try:
        #     self.nlp = spacy.load("en_core_web_sm")
        # except OSError:
        #     logger.warning("spaCy model not found, using basic parsing")
        #     self.nlp = None

        # Initialize matcher for skill extraction
        # if self.nlp:
        #     self.matcher = Matcher(self.nlp.vocab)
        #     self._setup_skill_patterns()

        # Common skills database
        self.skills_db = self._load_skills_database()

        # Experience patterns
        self.experience_patterns = [
            r"(?i)(experience|work history|employment|career)",
            r"(?i)(software engineer|developer|programmer|analyst)",
            r"(?i)(senior|junior|lead|principal|staff)",
            r"(?i)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
            r"(?i)(present|current|now)",
        ]

    def _setup_skill_patterns(self):
        """Setup spaCy patterns for skill extraction."""
        if not self.nlp:
            return

        # Programming languages
        prog_langs = [
            "Python",
            "JavaScript",
            "Java",
            "C++",
            "C#",
            "Go",
            "Rust",
            "Swift",
            "Kotlin",
            "Scala",
            "Ruby",
            "PHP",
            "Perl",
            "R",
            "MATLAB",
            "SQL",
        ]

        # Frameworks and libraries
        frameworks = [
            "React",
            "Angular",
            "Vue",
            "Node.js",
            "Express",
            "Django",
            "Flask",
            "Spring",
            "Laravel",
            "Symfony",
            "ASP.NET",
            "jQuery",
            "Bootstrap",
        ]

        # Tools and technologies
        tools = [
            "AWS",
            "Docker",
            "Kubernetes",
            "Git",
            "Jenkins",
            "Terraform",
            "Ansible",
            "MongoDB",
            "PostgreSQL",
            "Redis",
            "Elasticsearch",
        ]

        # Create patterns
        patterns = []
        for skill in prog_langs + frameworks + tools:
            patterns.append([{"LOWER": skill.lower()}])

        self.matcher.add("SKILLS", patterns)

    def _load_skills_database(self) -> List[str]:
        """Load comprehensive skills database."""
        return [
            # Programming Languages
            "Python",
            "JavaScript",
            "Java",
            "C++",
            "C#",
            "Go",
            "Rust",
            "Swift",
            "Kotlin",
            "Scala",
            "Ruby",
            "PHP",
            "Perl",
            "R",
            "MATLAB",
            "SQL",
            "TypeScript",
            "Dart",
            "Clojure",
            "Haskell",
            "Erlang",
            "Elixir",
            # Web Technologies
            "HTML",
            "CSS",
            "React",
            "Angular",
            "Vue",
            "Node.js",
            "Express",
            "Django",
            "Flask",
            "Spring",
            "Laravel",
            "Symfony",
            "ASP.NET",
            "jQuery",
            "Bootstrap",
            "Tailwind",
            "SASS",
            "LESS",
            "Webpack",
            # Cloud & DevOps
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Terraform",
            "Ansible",
            "Jenkins",
            "GitLab CI",
            "GitHub Actions",
            "CircleCI",
            "Prometheus",
            "Grafana",
            "ELK Stack",
            "Splunk",
            # Databases
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Redis",
            "Elasticsearch",
            "Cassandra",
            "DynamoDB",
            "Neo4j",
            "InfluxDB",
            "CouchDB",
            # Data Science & ML
            "TensorFlow",
            "PyTorch",
            "Scikit-learn",
            "Pandas",
            "NumPy",
            "Matplotlib",
            "Seaborn",
            "Plotly",
            "Jupyter",
            "Apache Spark",
            "Hadoop",
            "Hive",
            "Pig",
            "Kafka",
            "Airflow",
            # Mobile Development
            "React Native",
            "Flutter",
            "Xamarin",
            "Cordova",
            "Ionic",
            "Android Studio",
            "Xcode",
            "SwiftUI",
            "Jetpack Compose",
            # Other Technologies
            "Git",
            "Linux",
            "Bash",
            "PowerShell",
            "REST API",
            "GraphQL",
            "Microservices",
            "Serverless",
            "Blockchain",
            "IoT",
            "AR/VR",
        ]

    async def parse_resume(self, file_path: str) -> ResumeData:
        """
        Parse resume from file path.

        Args:
            file_path: Path to resume file (PDF, DOCX, etc.)

        Returns:
            Parsed resume data
        """
        try:
            logger.info(f"Starting resume parsing for file: {file_path}")

            # Extract text using AWS Textract
            raw_text = await self._extract_text_with_textract(file_path)

            if not raw_text:
                raise Exception("Failed to extract text from resume")

            logger.info(f"Text extraction completed. Extracted {len(raw_text)} characters.")

            # Parse resume data
            logger.info("Parsing extracted text for resume data...")
            resume_data = self._parse_resume_data(raw_text)
            resume_data.raw_text = raw_text

            # Calculate confidence score
            resume_data.confidence_score = self._calculate_confidence_score(resume_data)

            logger.info(
                f"Successfully parsed resume with confidence: {resume_data.confidence_score:.2f}"
            )
            return resume_data

        except Exception as e:
            logger.error(f"Failed to parse resume: {str(e)}")
            raise

    async def parse_resume_from_url(self, url: str) -> ResumeData:
        """
        Parse resume from URL (e.g., LinkedIn profile).

        Args:
            url: URL to resume or LinkedIn profile

        Returns:
            Parsed resume data
        """
        try:
            # Download content from URL
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Determine content type
            content_type = response.headers.get("content-type", "").lower()

            if "pdf" in content_type:
                # Save temporarily and parse
                temp_path = f"/tmp/resume_{datetime.now().timestamp()}.pdf"
                with open(temp_path, "wb") as f:
                    f.write(response.content)

                try:
                    resume_data = await self.parse_resume(temp_path)
                finally:
                    import os

                    os.remove(temp_path)

                return resume_data
            else:
                # Parse as HTML/text
                raw_text = response.text
                resume_data = self._parse_resume_data(raw_text)
                resume_data.raw_text = raw_text
                resume_data.confidence_score = self._calculate_confidence_score(
                    resume_data
                )

                return resume_data

        except Exception as e:
            logger.error(f"Failed to parse resume from URL: {str(e)}")
            raise

    async def _extract_text_with_textract(self, file_path: str) -> str:
        """Extract text from document using AWS Textract."""
        try:
            with open(file_path, "rb") as document:
                response = self.textract.analyze_document(
                    Document={"Bytes": document.read()},
                    FeatureTypes=["TABLES", "FORMS"],
                )

            # Extract text from blocks
            text_blocks = []
            for block in response["Blocks"]:
                if block["BlockType"] == "LINE":
                    text_blocks.append(block["Text"])

            extracted_text = "\n".join(text_blocks)
            return extracted_text

        except Exception as e:
            logger.error(f"Textract extraction failed: {str(e)}")
            # Fallback to basic text extraction
            return ""

    def _parse_resume_data(self, raw_text: str) -> ResumeData:
        """Parse resume data from raw text."""
        try:
            # Initialize resume data
            resume_data = ResumeData(
                personal_info=PersonalInfo(full_name=""),
                experience=[],
                education=[],
                certifications=[],
                skills=[],
                languages=[],
                projects=[],
            )

            # Extract personal information
            resume_data.personal_info = self._extract_personal_info(raw_text)

            # Extract skills
            resume_data.skills = self._extract_skills(raw_text)

            # Extract experience
            resume_data.experience = self._extract_experience(raw_text)

            # Extract education
            resume_data.education = self._extract_education(raw_text)

            # Extract certifications
            resume_data.certifications = self._extract_certifications(raw_text)

            # Extract summary
            resume_data.summary = self._extract_summary(raw_text)

            # Extract languages
            resume_data.languages = self._extract_languages(raw_text)

            # Extract projects
            resume_data.projects = self._extract_projects(raw_text)

            return resume_data

        except Exception as e:
            logger.error(f"Failed to parse resume data: {str(e)}")
            return ResumeData(personal_info=PersonalInfo(full_name=""))

    def _extract_personal_info(self, text: str) -> PersonalInfo:
        """Extract personal information from text."""
        personal_info = PersonalInfo(full_name="")

        # Extract email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info.email = email_match.group()

        # Extract phone
        phone_pattern = (
            r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})"
        )
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            personal_info.phone = phone_match.group()

        # Extract LinkedIn URL
        linkedin_pattern = r"https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9-]+/?"
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            personal_info.linkedin_url = linkedin_match.group()

        # Extract GitHub URL
        github_pattern = r"https?://(?:www\.)?github\.com/[A-Za-z0-9-]+/?"
        github_match = re.search(github_pattern, text)
        if github_match:
            personal_info.github_url = github_match.group()

        # Extract name (first line or after "Name:")
        name_pattern = r"(?:name|full name):\s*([^\n]+)"
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            personal_info.full_name = name_match.group(1).strip()
        else:
            # Try first line as name
            first_line = text.split("\n")[0].strip()
            if len(first_line) < 50 and not "@" in first_line:  # Not email
                personal_info.full_name = first_line

        # Extract location
        location_pattern = r"(?:location|address|based in):\s*([^\n]+)"
        location_match = re.search(location_pattern, text, re.IGNORECASE)
        if location_match:
            personal_info.location = location_match.group(1).strip()

        return personal_info

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        skills = []
        text_lower = text.lower()

        # Use spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            matches = self.matcher(doc)

            for match_id, start, end in matches:
                skill = doc[start:end].text
                if skill not in skills:
                    skills.append(skill)

        # Fallback to regex-based extraction
        for skill in self.skills_db:
            if skill.lower() in text_lower:
                if skill not in skills:
                    skills.append(skill)

        # Extract skills from "Skills:" section
        skills_section_pattern = (
            r"(?:skills|technical skills|technologies):\s*([^\n]+(?:\n[^\n]+)*)"
        )
        skills_match = re.search(
            skills_section_pattern, text, re.IGNORECASE | re.MULTILINE
        )
        if skills_match:
            skills_text = skills_match.group(1)
            # Split by common delimiters
            skill_list = re.split(r"[,;|•\n]", skills_text)
            for skill in skill_list:
                skill = skill.strip()
                if skill and len(skill) > 1:
                    if skill not in skills:
                        skills.append(skill)

        return skills[:20]  # Limit to top 20 skills

    def _extract_experience(self, text: str) -> List[Experience]:
        """Extract work experience from text."""
        experiences = []

        # Split text into sections
        sections = re.split(r"\n\s*\n", text)

        for section in sections:
            if self._is_experience_section(section):
                experience = self._parse_experience_section(section)
                if experience:
                    experiences.append(experience)

        return experiences

    def _is_experience_section(self, section: str) -> bool:
        """Check if section contains work experience."""
        section_lower = section.lower()

        # Check for experience keywords
        experience_keywords = [
            "experience",
            "work history",
            "employment",
            "career",
            "software engineer",
            "developer",
            "programmer",
            "analyst",
            "senior",
            "junior",
            "lead",
            "principal",
            "staff",
        ]

        return any(keyword in section_lower for keyword in experience_keywords)

    def _parse_experience_section(self, section: str) -> Optional[Experience]:
        """Parse individual experience section."""
        try:
            experience = Experience(title="", company="", location="", start_date="")

            # Extract title and company (usually first line)
            lines = section.split("\n")
            if lines:
                first_line = lines[0].strip()
                # Try to split title and company
                if " at " in first_line:
                    parts = first_line.split(" at ", 1)
                    experience.title = parts[0].strip()
                    experience.company = parts[1].strip()
                elif " - " in first_line:
                    parts = first_line.split(" - ", 1)
                    experience.title = parts[0].strip()
                    experience.company = parts[1].strip()
                else:
                    experience.title = first_line

            # Extract dates
            date_pattern = (
                r"(\w{3,9}\s+\d{4})\s*[-–]\s*(\w{3,9}\s+\d{4}|present|current|now)"
            )
            date_match = re.search(date_pattern, section, re.IGNORECASE)
            if date_match:
                start_date_str = date_match.group(1)
                end_date_str = date_match.group(2).lower()

                if end_date_str in ["present", "current", "now"]:
                    experience.current = True
                else:
                    experience.end_date = self._parse_date(end_date_str)

                experience.start_date = self._parse_date(start_date_str)

            # Extract description
            description_lines = []
            for line in lines[1:]:
                if line.strip() and not self._is_date_line(line):
                    description_lines.append(line.strip())

            experience.description = "\n".join(description_lines)

            # Extract skills from description
            experience.skills_used = self._extract_skills(experience.description)

            return experience

        except Exception as e:
            logger.error(f"Failed to parse experience section: {str(e)}")
            return None

    def _is_date_line(self, line: str) -> bool:
        """Check if line contains only dates."""
        date_pattern = (
            r"^\s*(\w{3,9}\s+\d{4})\s*[-–]\s*(\w{3,9}\s+\d{4}|present|current|now)\s*$"
        )
        return bool(re.match(date_pattern, line, re.IGNORECASE))

    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to standardized string format."""
        try:
            # Common date formats
            formats = [
                "%B %Y",
                "%b %Y",
                "%m/%Y",
                "%Y-%m",
                "%Y",
                "%B %d, %Y",
                "%b %d, %Y",
                "%m/%d/%Y",
            ]

            for fmt in formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            return None
        except Exception:
            return None

    def _extract_education(self, text: str) -> List[Education]:
        """Extract education information."""
        education = []

        # Look for education section
        education_pattern = (
            r"(?:education|academic|university|college):\s*([^\n]+(?:\n[^\n]+)*)"
        )
        education_match = re.search(
            education_pattern, text, re.IGNORECASE | re.MULTILINE
        )

        if education_match:
            education_text = education_match.group(1)
            # Parse education entries
            entries = re.split(r"\n\s*\n", education_text)

            for entry in entries:
                if entry.strip():
                    edu = self._parse_education_entry(entry)
                    if edu:
                        education.append(edu)

        return education

    def _parse_education_entry(self, entry: str) -> Optional[Education]:
        """Parse individual education entry."""
        try:
            education = Education(degree="", institution="")

            # Extract degree and field
            degree_pattern = r"(Bachelor|Master|PhD|Associate|Certificate|Diploma)\s+(?:of|in)?\s*([^,\n]+)"
            degree_match = re.search(degree_pattern, entry, re.IGNORECASE)
            if degree_match:
                education.degree = degree_match.group(1)
                education.field_of_study = degree_match.group(2).strip()

            # Extract school
            school_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|College|Institute|School))"
            school_match = re.search(school_pattern, entry)
            if school_match:
                education.institution = school_match.group(1)

            # Extract dates
            date_pattern = r"(\d{4})\s*[-–]\s*(\d{4}|present)"
            date_match = re.search(date_pattern, entry)
            if date_match:
                education.start_date = f"{date_match.group(1)}-01-01"
                end_year = date_match.group(2)
                if end_year != "present":
                    education.end_date = f"{end_year}-12-31"

            # Extract GPA
            gpa_pattern = r"GPA:\s*(\d+\.?\d*)"
            gpa_match = re.search(gpa_pattern, entry, re.IGNORECASE)
            if gpa_match:
                education.gpa = float(gpa_match.group(1))

            return education

        except Exception as e:
            logger.error(f"Failed to parse education entry: {str(e)}")
            return None

    def _extract_certifications(self, text: str) -> List[Certification]:
        """Extract certifications from text."""
        certifications = []

        # Look for certifications section
        cert_pattern = (
            r"(?:certifications|certificates|credentials):\s*([^\n]+(?:\n[^\n]+)*)"
        )
        cert_match = re.search(cert_pattern, text, re.IGNORECASE | re.MULTILINE)

        if cert_match:
            cert_text = cert_match.group(1)
            entries = re.split(r"\n", cert_text)

            for entry in entries:
                if entry.strip():
                    cert = self._parse_certification_entry(entry)
                    if cert:
                        certifications.append(cert)

        return certifications

    def _parse_certification_entry(self, entry: str) -> Optional[Certification]:
        """Parse individual certification entry."""
        try:
            certification = Certification(name="", issuer="")

            # Extract certification name and issuer
            # Common pattern: "Certification Name - Issuer"
            if " - " in entry:
                parts = entry.split(" - ", 1)
                certification.name = parts[0].strip()
                certification.issuer = parts[1].strip()
            else:
                certification.name = entry.strip()

            return certification

        except Exception as e:
            logger.error(f"Failed to parse certification entry: {str(e)}")
            return None

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary."""
        # Look for summary section
        summary_pattern = (
            r"(?:summary|profile|about|objective):\s*([^\n]+(?:\n[^\n]+)*)"
        )
        summary_match = re.search(summary_pattern, text, re.IGNORECASE | re.MULTILINE)

        if summary_match:
            return summary_match.group(1).strip()

        # Fallback: use first paragraph
        paragraphs = text.split("\n\n")
        if paragraphs:
            first_para = paragraphs[0].strip()
            if len(first_para) > 50 and len(first_para) < 500:
                return first_para

        return ""

    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from text."""
        languages = []

        # Look for languages section
        lang_pattern = r"(?:languages|language skills):\s*([^\n]+)"
        lang_match = re.search(lang_pattern, text, re.IGNORECASE)

        if lang_match:
            lang_text = lang_match.group(1)
            # Split by common delimiters
            lang_list = re.split(r"[,;|•]", lang_text)
            for lang in lang_list:
                lang = lang.strip()
                if lang:
                    languages.append(lang)

        return languages

    def _extract_projects(self, text: str) -> List[Dict[str, Any]]:
        """Extract projects from text."""
        projects = []

        # Look for projects section
        project_pattern = r"(?:projects|portfolio):\s*([^\n]+(?:\n[^\n]+)*)"
        project_match = re.search(project_pattern, text, re.IGNORECASE | re.MULTILINE)

        if project_match:
            project_text = project_match.group(1)
            # Split by project entries
            entries = re.split(r"\n\s*\n", project_text)

            for entry in entries:
                if entry.strip():
                    project = self._parse_project_entry(entry)
                    if project:
                        projects.append(project)

        return projects

    def _parse_project_entry(self, entry: str) -> Optional[Dict[str, Any]]:
        """Parse individual project entry."""
        try:
            project = {"name": "", "description": "", "technologies": [], "url": ""}

            # Extract project name (usually first line)
            lines = entry.split("\n")
            if lines:
                project["name"] = lines[0].strip()

            # Extract description
            description_lines = []
            for line in lines[1:]:
                if line.strip():
                    description_lines.append(line.strip())

            project["description"] = "\n".join(description_lines)

            # Extract technologies
            project["technologies"] = self._extract_skills(entry)

            # Extract URL
            url_pattern = r"https?://[^\s]+"
            url_match = re.search(url_pattern, entry)
            if url_match:
                project["url"] = url_match.group()

            return project

        except Exception as e:
            logger.error(f"Failed to parse project entry: {str(e)}")
            return None

    def _calculate_confidence_score(self, resume_data: ResumeData) -> float:
        """Calculate confidence score for parsed resume."""
        try:
            score = 0.0
            max_score = 10.0

            # Personal info completeness (2 points)
            if resume_data.personal_info.full_name:
                score += 0.5
            if resume_data.personal_info.email:
                score += 0.5
            if resume_data.personal_info.phone:
                score += 0.5
            if resume_data.personal_info.location:
                score += 0.5

            # Skills extraction (2 points)
            if len(resume_data.skills) > 0:
                score += min(2.0, len(resume_data.skills) * 0.1)

            # Experience extraction (3 points)
            if len(resume_data.experience) > 0:
                score += min(3.0, len(resume_data.experience) * 0.5)

            # Education extraction (1 point)
            if len(resume_data.education) > 0:
                score += 1.0

            # Summary extraction (1 point)
            if resume_data.summary:
                score += 1.0

            # Text quality (1 point)
            if len(resume_data.raw_text) > 100:
                score += 1.0

            return min(score / max_score, 1.0)

        except Exception as e:
            logger.error(f"Failed to calculate confidence score: {str(e)}")
            return 0.0
