#!/usr/bin/env python3
"""
Fixed Resume Parser Development Tool

A standalone tool for testing and developing the resume parser functionality
with fixed parsing logic based on debugging results.
"""

import os
import sys
import json
import re
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "app"))

try:
    import spacy
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️  spaCy not available, using basic parsing")

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not available, PDF parsing disabled")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not available, DOCX parsing disabled")


@dataclass
class PersonalInfo:
    """Personal information extracted from resume."""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin_url: str = ""
    github_url: str = ""
    website: str = ""


@dataclass
class Experience:
    """Work experience entry."""
    title: str = ""
    company: str = ""
    location: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    current: bool = False
    description: str = ""
    skills_used: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)


@dataclass
class Education:
    """Education entry."""
    degree: str = ""
    field_of_study: str = ""
    school: str = ""
    location: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[float] = None
    honors: List[str] = field(default_factory=list)


@dataclass
class Certification:
    """Certification entry."""
    name: str = ""
    issuer: str = ""
    date_earned: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: str = ""


@dataclass
class ResumeData:
    """Complete resume data structure."""
    personal_info: PersonalInfo
    summary: str = ""
    experience: List[Experience] = field(default_factory=list)
    education: List[Education] = field(default_factory=list)
    certifications: List[Certification] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    raw_text: str = ""
    confidence_score: float = 0.0
    parsed_at: datetime = field(default_factory=datetime.now)


class FixedResumeParser:
    """Fixed resume parser with corrected parsing logic."""

    def __init__(self):
        """Initialize the resume parser."""
        # Load spaCy model if available
        self.nlp = None
        self.matcher = None
        
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.matcher = Matcher(self.nlp.vocab)
                self._setup_skill_patterns()
                print("✅ spaCy model loaded successfully")
            except OSError:
                print("⚠️  spaCy model not found, using basic parsing")
                self.nlp = None

        # Common skills database
        self.skills_db = self._load_skills_database()

    def _setup_skill_patterns(self):
        """Setup spaCy patterns for skill extraction."""
        if not self.nlp:
            return

        # Programming languages
        prog_langs = [
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "Swift",
            "Kotlin", "Scala", "Ruby", "PHP", "Perl", "R", "MATLAB", "SQL", "TypeScript"
        ]

        # Frameworks and libraries
        frameworks = [
            "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask",
            "Spring", "Laravel", "Symfony", "ASP.NET", "jQuery", "Bootstrap"
        ]

        # Tools and technologies
        tools = [
            "AWS", "Docker", "Kubernetes", "Git", "Jenkins", "Terraform", "Ansible",
            "MongoDB", "PostgreSQL", "Redis", "Elasticsearch"
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
            "Python", "JavaScript", "Java", "C++", "C#", "Go", "Rust", "Swift",
            "Kotlin", "Scala", "Ruby", "PHP", "Perl", "R", "MATLAB", "SQL", "TypeScript",
            "Dart", "Clojure", "Haskell", "Erlang", "Elixir",
            # Web Technologies
            "HTML", "CSS", "React", "Angular", "Vue", "Node.js", "Express", "Django",
            "Flask", "Spring", "Laravel", "Symfony", "ASP.NET", "jQuery", "Bootstrap",
            "Tailwind", "SASS", "LESS", "Webpack",
            # Cloud & DevOps
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible",
            "Jenkins", "GitLab CI", "GitHub Actions", "CircleCI", "Prometheus", "Grafana",
            # Databases
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
            "DynamoDB", "Neo4j", "InfluxDB", "CouchDB",
            # Data Science & ML
            "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Matplotlib",
            "Seaborn", "Plotly", "Jupyter", "Apache Spark", "Hadoop", "Hive", "Pig",
            "Kafka", "Airflow",
            # Mobile Development
            "React Native", "Flutter", "Xamarin", "Cordova", "Ionic", "Android Studio",
            "Xcode", "SwiftUI", "Jetpack Compose",
            # Other Technologies
            "Git", "Linux", "Bash", "PowerShell", "REST API", "GraphQL", "Microservices",
            "Serverless", "Blockchain", "IoT", "AR/VR"
        ]

    def parse_resume(self, file_path: str) -> ResumeData:
        """
        Parse resume from file path.

        Args:
            file_path: Path to resume file (PDF, DOCX, TXT)

        Returns:
            Parsed resume data
        """
        try:
            # Extract text from file
            raw_text = self._extract_text_from_file(file_path)
            
            if not raw_text:
                raise Exception("Failed to extract text from resume")

            # Parse resume data
            resume_data = self._parse_resume_data(raw_text)
            resume_data.raw_text = raw_text

            # Calculate confidence score
            resume_data.confidence_score = self._calculate_confidence_score(resume_data)

            print(f"✅ Successfully parsed resume with confidence: {resume_data.confidence_score:.2f}")
            return resume_data

        except Exception as e:
            print(f"❌ Failed to parse resume: {str(e)}")
            raise

    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in ['.docx', '.doc']:
            return self._extract_text_from_docx(file_path)
        else:
            # Assume text file
            return self._extract_text_from_txt(file_path)

    def _extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        if not PDF_AVAILABLE:
            raise Exception("PDF parsing not available - PyPDF2 not installed")
        
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    def _extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            raise Exception("DOCX parsing not available - python-docx not installed")
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")

    def _extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from text file."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to extract text from file: {str(e)}")

    def _parse_resume_data(self, raw_text: str) -> ResumeData:
        """Parse resume data from raw text."""
        try:
            # Initialize resume data
            resume_data = ResumeData(
                personal_info=PersonalInfo(),
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
            print(f"❌ Failed to parse resume data: {str(e)}")
            return ResumeData(personal_info=PersonalInfo())

    def _extract_personal_info(self, text: str) -> PersonalInfo:
        """Extract personal information from text."""
        personal_info = PersonalInfo()

        # Extract email
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        email_match = re.search(email_pattern, text)
        if email_match:
            personal_info.email = email_match.group()

        # Extract phone
        phone_pattern = r"(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})"
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

        # Extract name - improved logic
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            # Skip if it looks like an email, phone, or URL
            if '@' in line or re.match(r'^[\d\s\-\(\)\+]+$', line) or 'http' in line:
                continue
            # Skip if it's too short or too long
            if len(line) < 2 or len(line) > 50:
                continue
            # Skip if it's all uppercase (likely a section header)
            if line.isupper() and len(line) > 3:
                continue
            # This looks like a name
            personal_info.name = line
            break

        # Extract location - improved logic
        location_patterns = [
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})",  # City, State
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)",  # City, Country
            r"Based in:\s*([^\n]+)",  # "Based in: ..."
            r"Location:\s*([^\n]+)",  # "Location: ..."
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, text, re.IGNORECASE)
            if location_match:
                personal_info.location = location_match.group().strip()
                break

        return personal_info

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text."""
        skills = []
        text_lower = text.lower()

        # Use spaCy if available
        if self.nlp and self.matcher:
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
        skills_section_pattern = r"(?:skills|technical skills|technologies):\s*([^\n]+(?:\n[^\n]+)*)"
        skills_match = re.search(skills_section_pattern, text, re.IGNORECASE | re.MULTILINE)
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

        # Find experience section using line-by-line approach
        lines = text.split('\n')
        experience_start = -1
        experience_end = -1
        
        # Find the start of experience section
        for i, line in enumerate(lines):
            if line.strip().upper() in ["EXPERIENCE", "WORK HISTORY", "EMPLOYMENT", "CAREER"]:
                experience_start = i
                break
        
        if experience_start == -1:
            return experiences
        
        # Find the end of experience section
        for i in range(experience_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line.isupper() and len(line) > 3 and i > experience_start + 2:
                experience_end = i
                break
        
        if experience_end == -1:
            experience_end = len(lines)
        
        # Extract the experience section
        experience_lines = lines[experience_start:experience_end]
        experience_text = '\n'.join(experience_lines)
        
        # Split into individual job entries
        job_entries = self._split_experience_entries(experience_text)
        
        for entry in job_entries:
            if self._is_valid_job_entry(entry):
                experience = self._parse_job_entry(entry)
                if experience:
                    experiences.append(experience)

        return experiences

    def _split_experience_entries(self, experience_text: str) -> List[str]:
        """Split experience text into individual job entries."""
        # Split by double newlines first
        entries = re.split(r'\n\s*\n', experience_text)
        
        # Filter out the section header
        entries = [entry for entry in entries if not entry.strip().upper() in ["EXPERIENCE", "WORK HISTORY", "EMPLOYMENT", "CAREER"]]
        
        # If we still have entries that are too long, try splitting by job title patterns
        final_entries = []
        for entry in entries:
            if len(entry.strip()) > 200:  # If entry is very long, try to split it
                # Look for job title patterns
                job_pattern = r'(?=\n[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*[-–]\s*[A-Z])'
                sub_entries = re.split(job_pattern, entry)
                final_entries.extend(sub_entries)
            else:
                final_entries.append(entry)
        
        return [entry.strip() for entry in final_entries if entry.strip()]

    def _is_valid_job_entry(self, entry: str) -> bool:
        """Check if an entry looks like a valid job entry."""
        # Skip if it's too short
        if len(entry.strip()) < 20:
            return False
        
        # Skip if it's all uppercase (likely a section header)
        if entry.strip().isupper() and len(entry.strip()) > 3:
            return False
        
        # Skip if it doesn't contain common job-related keywords
        job_keywords = ['engineer', 'developer', 'analyst', 'manager', 'director', 'specialist', 'coordinator', 'consultant']
        entry_lower = entry.lower()
        return any(keyword in entry_lower for keyword in job_keywords)

    def _parse_job_entry(self, entry: str) -> Optional[Experience]:
        """Parse individual job entry."""
        try:
            experience = Experience()
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            if not lines:
                return None

            # First line is usually title and company
            first_line = lines[0]
            
            # Try to split title and company
            if " - " in first_line:
                parts = first_line.split(" - ", 1)
                experience.title = parts[0].strip()
                experience.company = parts[1].strip()
            elif " at " in first_line:
                parts = first_line.split(" at ", 1)
                experience.title = parts[0].strip()
                experience.company = parts[1].strip()
            else:
                experience.title = first_line

            # Look for location in the next few lines
            for line in lines[1:4]:
                if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}$', line):
                    experience.location = line
                    break

            # Look for dates
            date_pattern = r'(\w{3,9}\s+\d{4})\s*[-–]\s*(\w{3,9}\s+\d{4}|present|current|now)'
            for line in lines:
                date_match = re.search(date_pattern, line, re.IGNORECASE)
                if date_match:
                    start_date_str = date_match.group(1)
                    end_date_str = date_match.group(2).lower()

                    if end_date_str in ["present", "current", "now"]:
                        experience.current = True
                    else:
                        experience.end_date = self._parse_date(end_date_str)

                    experience.start_date = self._parse_date(start_date_str)
                    break

            # Collect description from remaining lines
            description_lines = []
            for line in lines[1:]:
                if not self._is_date_line(line) and not re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}$', line):
                    description_lines.append(line)

            experience.description = '\n'.join(description_lines)

            # Extract skills from description
            experience.skills_used = self._extract_skills(experience.description)

            return experience

        except Exception as e:
            print(f"❌ Failed to parse job entry: {str(e)}")
            return None

    def _is_date_line(self, line: str) -> bool:
        """Check if line contains only dates."""
        date_pattern = r"^\s*(\w{3,9}\s+\d{4})\s*[-–]\s*(\w{3,9}\s+\d{4}|present|current|now)\s*$"
        return bool(re.match(date_pattern, line, re.IGNORECASE))

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object."""
        try:
            # Common date formats
            formats = [
                "%B %Y", "%b %Y", "%m/%Y", "%Y-%m", "%Y",
                "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue

            return None
        except Exception:
            return None

    def _extract_education(self, text: str) -> List[Education]:
        """Extract education information."""
        education = []

        # Find education section using line-by-line approach
        lines = text.split('\n')
        education_start = -1
        education_end = -1
        
        # Find the start of education section
        for i, line in enumerate(lines):
            if line.strip().upper() in ["EDUCATION", "ACADEMIC", "UNIVERSITY", "COLLEGE"]:
                education_start = i
                break
        
        if education_start == -1:
            return education
        
        # Find the end of education section
        for i in range(education_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line.isupper() and len(line) > 3 and i > education_start + 2:
                education_end = i
                break
        
        if education_end == -1:
            education_end = len(lines)
        
        # Extract the education section
        education_lines = lines[education_start:education_end]
        education_text = '\n'.join(education_lines)
        
        # Split into individual education entries
        edu_entries = re.split(r'\n\s*\n', education_text)
        edu_entries = [entry for entry in edu_entries if not entry.strip().upper() in ["EDUCATION", "ACADEMIC", "UNIVERSITY", "COLLEGE"]]
        
        for entry in edu_entries:
            if self._is_valid_education_entry(entry):
                edu = self._parse_education_entry(entry)
                if edu:
                    education.append(edu)

        return education

    def _is_valid_education_entry(self, entry: str) -> bool:
        """Check if an entry looks like a valid education entry."""
        # Skip if it's too short
        if len(entry.strip()) < 10:
            return False
        
        # Skip if it's all uppercase (likely a section header)
        if entry.strip().isupper() and len(entry.strip()) > 3:
            return False
        
        # Look for degree keywords
        degree_keywords = ['bachelor', 'master', 'phd', 'associate', 'certificate', 'diploma', 'degree']
        entry_lower = entry.lower()
        return any(keyword in entry_lower for keyword in degree_keywords)

    def _parse_education_entry(self, entry: str) -> Optional[Education]:
        """Parse individual education entry."""
        try:
            education = Education()
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            if not lines:
                return None

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
                education.school = school_match.group(1)

            # Extract location
            location_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})"
            location_match = re.search(location_pattern, entry)
            if location_match:
                education.location = location_match.group()

            # Extract dates
            date_pattern = r"(\d{4})\s*[-–]\s*(\d{4}|present)"
            date_match = re.search(date_pattern, entry)
            if date_match:
                education.start_date = date(int(date_match.group(1)), 1, 1)
                end_year = date_match.group(2)
                if end_year != "present":
                    education.end_date = date(int(end_year), 12, 31)

            # Extract GPA
            gpa_pattern = r"GPA:\s*(\d+\.?\d*)"
            gpa_match = re.search(gpa_pattern, entry, re.IGNORECASE)
            if gpa_match:
                education.gpa = float(gpa_match.group(1))

            return education

        except Exception as e:
            print(f"❌ Failed to parse education entry: {str(e)}")
            return None

    def _extract_certifications(self, text: str) -> List[Certification]:
        """Extract certifications from text."""
        certifications = []

        # Find certifications section using line-by-line approach
        lines = text.split('\n')
        cert_start = -1
        cert_end = -1
        
        # Find the start of certifications section
        for i, line in enumerate(lines):
            if line.strip().upper() in ["CERTIFICATIONS", "CERTIFICATES", "CREDENTIALS"]:
                cert_start = i
                break
        
        if cert_start == -1:
            return certifications
        
        # Find the end of certifications section
        for i in range(cert_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line.isupper() and len(line) > 3 and i > cert_start + 2:
                cert_end = i
                break
        
        if cert_end == -1:
            cert_end = len(lines)
        
        # Extract the certifications section
        cert_lines = lines[cert_start:cert_end]
        cert_text = '\n'.join(cert_lines)
        
        # Split into individual certification entries
        cert_entries = cert_text.split('\n')
        cert_entries = [entry.strip() for entry in cert_entries if entry.strip() and not entry.strip().upper() in ["CERTIFICATIONS", "CERTIFICATES", "CREDENTIALS"]]
        
        for entry in cert_entries:
            if len(entry) > 3:
                cert = self._parse_certification_entry(entry)
                if cert:
                    certifications.append(cert)

        return certifications

    def _parse_certification_entry(self, entry: str) -> Optional[Certification]:
        """Parse individual certification entry."""
        try:
            certification = Certification()

            # Extract certification name and issuer
            if " - " in entry:
                parts = entry.split(" - ", 1)
                certification.name = parts[0].strip()
                certification.issuer = parts[1].strip()
            else:
                certification.name = entry.strip()

            return certification

        except Exception as e:
            print(f"❌ Failed to parse certification entry: {str(e)}")
            return None

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary."""
        # Find summary section using line-by-line approach
        lines = text.split('\n')
        summary_start = -1
        summary_end = -1
        
        # Find the start of summary section
        for i, line in enumerate(lines):
            if line.strip().upper() in ["SUMMARY", "PROFILE", "ABOUT", "OBJECTIVE"]:
                summary_start = i
                break
        
        if summary_start == -1:
            # Fallback: use first paragraph
            paragraphs = text.split("\n\n")
            if paragraphs:
                first_para = paragraphs[0].strip()
                if len(first_para) > 50 and len(first_para) < 500:
                    return first_para
            return ""
        
        # Find the end of summary section
        for i in range(summary_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line.isupper() and len(line) > 3 and i > summary_start + 2:
                summary_end = i
                break
        
        if summary_end == -1:
            summary_end = len(lines)
        
        # Extract the summary section
        summary_lines = lines[summary_start:summary_end]
        summary_text = '\n'.join(summary_lines)
        
        # Remove the section header
        summary_text = re.sub(r'^(SUMMARY|PROFILE|ABOUT|OBJECTIVE):?\s*', '', summary_text, flags=re.IGNORECASE)
        
        return summary_text.strip()

    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from text."""
        languages = []

        # Find languages section using line-by-line approach
        lines = text.split('\n')
        lang_start = -1
        lang_end = -1
        
        # Find the start of languages section
        for i, line in enumerate(lines):
            if line.strip().upper() in ["LANGUAGES", "LANGUAGE SKILLS"]:
                lang_start = i
                break
        
        if lang_start == -1:
            return languages
        
        # Find the end of languages section
        for i in range(lang_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line.isupper() and len(line) > 3 and i > lang_start + 2:
                lang_end = i
                break
        
        if lang_end == -1:
            lang_end = len(lines)
        
        # Extract the languages section
        lang_lines = lines[lang_start:lang_end]
        lang_text = '\n'.join(lang_lines)
        
        # Remove the section header
        lang_text = re.sub(r'^(LANGUAGES|LANGUAGE SKILLS):?\s*', '', lang_text, flags=re.IGNORECASE)
        
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

        # Find projects section using line-by-line approach
        lines = text.split('\n')
        project_start = -1
        project_end = -1
        
        # Find the start of projects section
        for i, line in enumerate(lines):
            if line.strip().upper() in ["PROJECTS", "PORTFOLIO"]:
                project_start = i
                break
        
        if project_start == -1:
            return projects
        
        # Find the end of projects section
        for i in range(project_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line.isupper() and len(line) > 3 and i > project_start + 2:
                project_end = i
                break
        
        if project_end == -1:
            project_end = len(lines)
        
        # Extract the projects section
        project_lines = lines[project_start:project_end]
        project_text = '\n'.join(project_lines)
        
        # Split into individual project entries
        project_entries = re.split(r'\n\s*\n', project_text)
        project_entries = [entry for entry in project_entries if not entry.strip().upper() in ["PROJECTS", "PORTFOLIO"]]
        
        for entry in project_entries:
            if self._is_valid_project_entry(entry):
                project = self._parse_project_entry(entry)
                if project:
                    projects.append(project)

        return projects

    def _is_valid_project_entry(self, entry: str) -> bool:
        """Check if an entry looks like a valid project entry."""
        # Skip if it's too short
        if len(entry.strip()) < 10:
            return False
        
        # Skip if it's all uppercase (likely a section header)
        if entry.strip().isupper() and len(entry.strip()) > 3:
            return False
        
        return True

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
            print(f"❌ Failed to parse project entry: {str(e)}")
            return None

    def _calculate_confidence_score(self, resume_data: ResumeData) -> float:
        """Calculate confidence score for parsed resume."""
        try:
            score = 0.0
            max_score = 10.0

            # Personal info completeness (2 points)
            if resume_data.personal_info.name:
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
            print(f"❌ Failed to calculate confidence score: {str(e)}")
            return 0.0

    def to_dict(self, resume_data: ResumeData) -> Dict[str, Any]:
        """Convert ResumeData to dictionary for JSON serialization."""
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                result = {}
                for field_name, field_value in asdict(obj).items():
                    if isinstance(field_value, date):
                        result[field_name] = field_value.isoformat()
                    elif isinstance(field_value, datetime):
                        result[field_name] = field_value.isoformat()
                    elif isinstance(field_value, list):
                        result[field_name] = [convert_dataclass(item) if hasattr(item, '__dataclass_fields__') else item for item in field_value]
                    else:
                        result[field_name] = field_value
                return result
            return obj

        return convert_dataclass(resume_data)


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Fixed Resume Parser Development Tool")
    parser.add_argument("file_path", help="Path to resume file (PDF, DOCX, TXT)")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        # Initialize parser
        parser_instance = FixedResumeParser()

        # Parse resume
        print(f"🔍 Parsing resume: {args.file_path}")
        resume_data = parser_instance.parse_resume(args.file_path)

        # Convert to dictionary
        result = parser_instance.to_dict(resume_data)

        # Output results
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✅ Results saved to: {args.output}")
        else:
            print("\n📄 Parsed Resume Data:")
            print("=" * 50)
            print(f"Name: {resume_data.personal_info.name}")
            print(f"Email: {resume_data.personal_info.email}")
            print(f"Phone: {resume_data.personal_info.phone}")
            print(f"Location: {resume_data.personal_info.location}")
            print(f"LinkedIn: {resume_data.personal_info.linkedin_url}")
            print(f"GitHub: {resume_data.personal_info.github_url}")
            print(f"\nSummary: {resume_data.summary}")
            print(f"\nSkills ({len(resume_data.skills)}): {', '.join(resume_data.skills[:10])}")
            print(f"\nExperience ({len(resume_data.experience)} entries)")
            for i, exp in enumerate(resume_data.experience[:3], 1):
                print(f"  {i}. {exp.title} at {exp.company}")
                if exp.location:
                    print(f"     Location: {exp.location}")
                if exp.start_date:
                    end_date = "Present" if exp.current else exp.end_date
                    print(f"     Duration: {exp.start_date} - {end_date}")
            print(f"\nEducation ({len(resume_data.education)} entries)")
            for i, edu in enumerate(resume_data.education[:3], 1):
                print(f"  {i}. {edu.degree} in {edu.field_of_study} from {edu.school}")
                if edu.location:
                    print(f"     Location: {edu.location}")
                if edu.gpa:
                    print(f"     GPA: {edu.gpa}")
            print(f"\nConfidence Score: {resume_data.confidence_score:.2f}")

        if args.verbose:
            print(f"\n📊 Full JSON Output:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
