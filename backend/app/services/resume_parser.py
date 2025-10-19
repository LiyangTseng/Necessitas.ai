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
from dataclasses import dataclass, field
# import spacy
# from spacy.matcher import Matcher
import requests
from urllib.parse import urlparse

from core.config import settings
import logging

logger = logging.getLogger(__name__)


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
    major: str = ""
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


class ResumeParser:
    """Main resume parsing service using AWS Textract and NLP."""

    def __init__(self):
        """Initialize the resume parser."""
        # AWS Textract client
        self.textract = boto3.client(
            "textract",
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

        # Load spaCy model
        # try to load spaCy, but keep attributes defined even if unavailable
        try:
            import spacy

            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                logger.warning("spaCy model 'en_core_web_sm' not found, spaCy features disabled")
                self.nlp = None
        except Exception:
            logger.info("spaCy not installed, proceeding with fallback parsing")
            self.nlp = None

        # Initialize matcher for skill extraction

        # Common skills database (load before creating matchers)
        self.skills_db = self._load_skills_database()

        # Ensure matcher/phrase_matcher attribute exists even when spaCy not available
        try:
            if self.nlp:
                # Prefer PhraseMatcher for phrase-based skill matching
                from spacy.matcher import PhraseMatcher

                self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
                self._setup_skill_patterns()
            else:
                self.phrase_matcher = None
        except Exception:
            logger.warning("Failed to initialize spaCy PhraseMatcher; continuing without it")
            self.phrase_matcher = None

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

        # Build phrase patterns from skills_db for PhraseMatcher
        try:
            # Use a subset to avoid extremely large matcher lists if needed
            patterns = []
            for skill in self.skills_db:
                if not skill:
                    continue
                # create a Doc for the phrase matcher (case-insensitive via attr="LOWER")
                patterns.append(self.nlp.make_doc(skill))

            if patterns:
                # Add under the label 'SKILLS'
                self.phrase_matcher.add("SKILLS", patterns)
        except Exception:
            logger.warning("Error while setting up PhraseMatcher patterns")
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

        # Backwards-compatible: also add short token patterns to PhraseMatcher
        try:
            short_patterns = []
            for skill in prog_langs + frameworks + tools:
                if not skill:
                    continue
                short_patterns.append(self.nlp.make_doc(skill))

            if short_patterns:
                # add or extend existing SKILLS entry
                # PhraseMatcher will raise if label exists; safe-add by removing then re-adding
                try:
                    self.phrase_matcher.remove("SKILLS")
                except Exception:
                    pass
                self.phrase_matcher.add("SKILLS", short_patterns)
        except Exception:
            logger.debug("Failed to add short skill patterns to PhraseMatcher")

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
            # Extract text using AWS Textract
            raw_text = await self._extract_text_with_textract(file_path)

            if not raw_text:
                raise Exception("Failed to extract text from resume")

            # Parse resume data
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
                # Use Textract for document analysis
                response = self.textract.analyze_document(
                    Document={"Bytes": document.read()},
                    FeatureTypes=["TABLES", "FORMS"],
                )

            # Extract text from blocks
            text_blocks = []
            for block in response["Blocks"]:
                if block["BlockType"] == "LINE":
                    text_blocks.append(block["Text"])

            return "\n".join(text_blocks)

        except Exception as e:
            logger.error(f"Textract extraction failed: {str(e)}")
            # Fallback to basic text extraction
            return await self._extract_text_fallback(file_path)

    async def _extract_text_fallback(self, file_path: str) -> str:
        """Fallback text extraction method."""
        try:
            if file_path.lower().endswith(".pdf"):
                # Prefer pdfplumber for more accurate PDF text extraction/layout
                try:
                    import pdfplumber

                    text = ""
                    with pdfplumber.open(file_path) as pdf:
                        for page in pdf.pages:
                            # Prefer extracting words and rebuild lines using coordinates to preserve spacing
                            try:
                                words = page.extract_words()
                                if words:
                                    # Sort words by 'top' then 'x0'
                                    words_sorted = sorted(words, key=lambda w: (float(w.get("top", 0)), float(w.get("x0", 0))))
                                    lines: List[List[dict]] = []
                                    current_line: List[dict] = []
                                    last_top = None
                                    for w in words_sorted:
                                        top = float(w.get("top", 0))
                                        # start new line when vertical gap is significant (>3 px)
                                        if last_top is None or abs(top - last_top) > 3:
                                            if current_line:
                                                lines.append(current_line)
                                            current_line = [w]
                                            last_top = top
                                        else:
                                            current_line.append(w)
                                            last_top = (last_top + top) / 2.0

                                    if current_line:
                                        lines.append(current_line)

                                    page_lines: List[str] = []
                                    for ln in lines:
                                        # sort by x0 and join words with single space
                                        ln_sorted = sorted(ln, key=lambda w: float(w.get("x0", 0)))
                                        page_lines.append(" ".join(w.get("text", "") for w in ln_sorted))

                                    page_text = "\n".join(page_lines)
                                else:
                                    page_text = page.extract_text() or ""
                            except Exception:
                                page_text = page.extract_text() or ""
                            # preserve page break
                            text += page_text + "\n\n"
                    return text
                except Exception:
                    # Fallback to PyPDF2 if pdfplumber not available or fails
                    try:
                        import PyPDF2

                        with open(file_path, "rb") as file:
                            reader = PyPDF2.PdfReader(file)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text() or ""
                            return text
                    except Exception:
                        logger.warning("pdfplumber and PyPDF2 failed to extract PDF text; continuing to other fallbacks")
            elif file_path.lower().endswith(".docx"):
                from docx import Document

                doc = Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            else:
                with open(file_path, "r", encoding="utf-8") as file:
                    return file.read()
        except Exception as e:
            logger.error(f"Fallback text extraction failed: {str(e)}")
            return ""

    def _clean_text(self, text: str) -> str:
        """Lightweight cleaning of extracted text to remove OCR/artifact noise."""
        if not text:
            return ""

        # Ensure common section headers are on their own lines (helps when PDFs lose newlines)
        headers = [
            "PROFESSIONAL EXPERIENCE",
            "WORK EXPERIENCE",
            "EXPERIENCE",
            "EDUCATION",
            "TECHNICAL SKILLS",
            "SKILLS",
            "PROJECTS",
            "SELECTIVE PROJECTS",
            "PUBLICATIONS",
            "PUBLICATION",
            "CERTIFICATIONS",
            "LANGUAGES",
            "SUMMARY",
        ]
        def _ensure_header_newlines(s: str) -> str:
            for h in headers:
                # insert newline before and after the header if it's run together
                s = re.sub(rf"(?i)\b{re.escape(h)}\b", f"\n{h}\n", s)
            return s

        text = _ensure_header_newlines(text)

        # Remove common '(cid:123)' artifacts and weird unicode control characters
        text = re.sub(r"\(cid:\d+\)", " ", text)
        # Replace multiple non-word sequences (except newlines) with a single space
        text = re.sub(r"[\u2000-\u206F\u2E00-\u2E7F]+", " ", text)
        # Fix missing spaces between letters/digits (e.g., 'Jun2027' -> 'Jun 2027') for common month patterns
        text = re.sub(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?=\d{4})", r"\1 ", text)
        # Insert spaces between lowercase->Uppercase (e.g., 'SoftwareEngineering' -> 'Software Engineering')
        text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
        # Insert spaces between letters and digits (e.g., 'a5x' -> 'a 5x') and digits->letters
        text = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", text)
        text = re.sub(r"(?<=\d)(?=[A-Za-z])", " ", text)
        # Normalize multiple spaces and preserve paragraphs
        lines = [re.sub(r"[ \t]{2,}", " ", l).strip() for l in text.splitlines()]
        # Remove empty lines at the edges and collapse consecutive blank lines to one
        cleaned_lines = []
        blank = False
        for l in lines:
            if not l:
                if not blank:
                    cleaned_lines.append("")
                blank = True
            else:
                cleaned_lines.append(l)
                blank = False

        cleaned = "\n".join(cleaned_lines).strip() + "\n"
        return cleaned

    def _split_into_headed_sections(self, text: str) -> List[Tuple[str, str]]:
        """Split text into (heading, body) pairs using all-caps headings or common section keywords.

        Returns a list of tuples where heading may be empty for leading content.
        """
        if not text:
            return []

        # Heuristic: headings are lines in ALL CAPS or lines that match common section names
        section_headers = [
            "EXPERIENCE",
            "PROFESSIONAL EXPERIENCE",
            "WORK EXPERIENCE",
            "EDUCATION",
            "TECHNICAL SKILLS",
            "SKILLS",
            "PROJECTS",
            "PUBLICATIONS",
            "CERTIFICATIONS",
            "LANGUAGES",
            "SUMMARY",
        ]

        lines = text.splitlines()
        sections: List[Tuple[str, List[str]]] = []
        current_header = ""
        current_body: List[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                # preserve paragraph breaks
                current_body.append("")
                continue

            is_header = False
            # all-caps heuristic (and reasonably short)
            if stripped.isupper() and len(stripped) < 60:
                is_header = True

            # explicit known headers
            if any(h in stripped.upper() for h in section_headers):
                is_header = True

            if is_header:
                # push previous
                if current_header or current_body:
                    sections.append((current_header, current_body))
                # set new header and reset body
                current_header = stripped.upper()
                current_body = []
            else:
                current_body.append(line)

        # append last
        if current_header or current_body:
            sections.append((current_header, current_body))

        # Convert bodies back to strings
        return [(h, "\n".join(b).strip()) for h, b in sections]

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

            # Clean text first to reduce OCR artifacts
            cleaned = self._clean_text(raw_text)

            # Extract personal information (use cleaned text)
            resume_data.personal_info = self._extract_personal_info(cleaned)

            # Extract skills
            resume_data.skills = self._extract_skills(cleaned)

            # Extract experience using headed sections + fallback
            resume_data.experience = self._extract_experience(cleaned)

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

        # Use spaCy NER for name extraction if available
        if self.nlp:
            try:
                doc = self.nlp(text)
                # Look for PERSON entity
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        # Take first PERSON entity as name if it looks like a name line
                        candidate = ent.text.strip()
                        if candidate and len(candidate) < 100:
                            personal_info.name = candidate
                            break
            except Exception:
                logger.debug("spaCy NER failed for name extraction, falling back to regex")

        # If spaCy didn't yield a name, use previous heuristics
        if not personal_info.name:
            name_pattern = r"(?:name|full name):\s*([^\n]+)"
            name_match = re.search(name_pattern, text, re.IGNORECASE)
            if name_match:
                personal_info.name = name_match.group(1).strip()
            else:
                # Try first non-empty line as name
                for line in text.split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if len(line) < 100 and "@" not in line and not line.lower().startswith("summary"):
                        personal_info.name = line
                        break

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

        # Use spaCy PhraseMatcher if available
        if self.nlp and self.phrase_matcher:
            try:
                doc = self.nlp(text)
                matches = self.phrase_matcher(doc)
                for match_id, start, end in matches:
                    span = doc[start:end]
                    skill = span.text.strip()
                    if skill and skill not in skills:
                        skills.append(skill)
            except Exception:
                logger.debug("PhraseMatcher failed; falling back to DB matching")

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

        # First try stronger headed-section splitting
        sections = self._split_into_headed_sections(text)

        found = False
        for heading, body in sections:
            if heading and self._is_experience_section(heading + "\n" + body):
                # body may contain multiple entries separated by double newlines
                entries = re.split(r"\n\s*\n", body)
                # If there's no blank-line separation, try splitting by date markers
                if len(entries) <= 1:
                    entries = self._split_entries_by_dates(body)
                for entry in entries:
                    entry = entry.strip()
                    if not entry:
                        continue
                    exp = self._parse_experience_section(entry)
                    if exp:
                        experiences.append(exp)
                        found = True

        # Fallback: scan entire text for experience-like sections
        if not found:
            sections = re.split(r"\n\s*\n", text)
            for section in sections:
                if self._is_experience_section(section):
                    exp = self._parse_experience_section(section)
                    if exp:
                        experiences.append(exp)

        return experiences

    def _split_entries_by_dates(self, text: str) -> List[str]:
        """Attempt to split a block of text into multiple experience entries using date markers.

        This helps when the PDF lost paragraph breaks and multiple experiences are concatenated.
        """
        if not text:
            return []

        # Use line-based scanning: start a new entry when a line contains a month/year or year range
        month_regex = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}"
        year_regex = r"\d{4}"
        date_line_regex = re.compile(rf"({month_regex}|{year_regex}).*(?:[-–—].*({month_regex}|{year_regex}|present|current))?", re.IGNORECASE)

        lines = text.splitlines()
        entries: List[List[str]] = []
        current: List[str] = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                # preserve as potential separator
                if current and current[-1] != "":
                    current.append("")
                continue

            is_date_line = bool(date_line_regex.search(stripped))

            # Heuristic: if the line contains a date range or a month-year, consider it a start of a new entry
            if is_date_line and current:
                # Start new entry if current already has content
                entries.append(current)
                current = [line]
            else:
                current.append(line)

        if current:
            entries.append(current)

        # Join back into text blocks
        joined = ["\n".join(e).strip() for e in entries if "\n".join(e).strip()]

        # If we detected only one block, just return the original text as single entry
        if len(joined) <= 1:
            return [text.strip()]

        return joined

    def _parse_experience_section(self, section: str) -> Optional[Experience]:
        """Parse individual experience section or mini-entry into an Experience object.

        Improved heuristics: use spaCy ORG and DATE entities to detect company and dates,
        and look for common role keywords to identify title.
        """
        try:
            experience = Experience()

            # Normalize whitespace
            sec = section.strip()
            # Normalize common dash characters and remove odd spacing around en/em dashes
            sec = re.sub(r"[\u2012\u2013\u2014\u2015]", "-", sec)
            sec = re.sub(r"\s*[-–—]\s*", " - ", sec)
            lines = [l.strip() for l in sec.splitlines() if l.strip()]

            # If spaCy is available, use NER to find ORG and DATE entities
            org_candidate = None
            date_candidates: List[str] = []
            if self.nlp:
                try:
                    doc = self.nlp(sec)
                    for ent in doc.ents:
                        if ent.label_ == "ORG" and not org_candidate:
                            org_candidate = ent.text.strip()
                        if ent.label_ == "DATE":
                            date_candidates.append(ent.text.strip())
                except Exception:
                    logger.debug("spaCy NER failed during experience parsing")

            # If first line contains a company-like pattern (comma separated) try to split
            if lines:
                first = lines[0]
                # common: 'Company Aug2024–Dec2024' or 'Title, Company — Date'
                # Try to detect 'Title at Company' or 'Company Aug 2024'
                if " at " in first:
                    parts = first.split(" at ", 1)
                    experience.title = parts[0].strip()
                    experience.company = parts[1].strip()
                elif "," in first and any(kw in first.lower() for kw in ["inc", "llc", "company", "university", "center", "lab", "research", "corporation"]):
                    parts = first.split(",", 1)
                    experience.company = parts[0].strip()
                    experience.title = parts[1].strip()
                else:
                    # fallback: take a short first line as title candidate
                    if len(first) < 100 and len(lines) > 1:
                        # prefer to treat first as title if it contains role keywords
                        role_kw = r"\b(intern|engineer|research|developer|manager|scientist|analyst|consultant|designer|teacher)\b"
                        if re.search(role_kw, first, re.IGNORECASE):
                            experience.title = first
                        else:
                            # if spaCy found an ORG and it appears in first line, set company
                            if org_candidate and org_candidate in first:
                                experience.company = org_candidate
                            else:
                                # If first line contains a company name followed by dates (e.g., 'National Center Aug 2024–Dec 2024'),
                                # then shift: set company from first line and set title from second line if it looks like a role.
                                # If first line contains a date range glued to it, extract the date part then set company to remaining
                                date_range_inline = re.search(r"(?P<pre>.*?)(?P<dates>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\s*[-–—]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4})\b", first, re.IGNORECASE)
                                if date_range_inline:
                                    pre = date_range_inline.group("pre").strip()
                                    datestr = date_range_inline.group("dates").strip()
                                    # set company to text before the date
                                    if pre:
                                        experience.company = pre
                                    # parse dates
                                    try:
                                        # normalize datestr then parse
                                        dr = re.sub(r"\s+", " ", datestr)
                                        # if it's a range separated by '-', split
                                        if "-" in dr:
                                            parts = [p.strip() for p in dr.split("-") if p.strip()]
                                            if parts:
                                                experience.start_date = self._parse_date(parts[0])
                                            if len(parts) > 1:
                                                if parts[1].lower() not in ["present", "current"]:
                                                    experience.end_date = self._parse_date(parts[1])
                                                else:
                                                    experience.current = True
                                        else:
                                            experience.start_date = self._parse_date(dr)
                                    except Exception:
                                        pass
                                    # set title from next line if it looks like a role
                                    if len(lines) > 1:
                                        second = lines[1]
                                        if re.search(role_kw, second, re.IGNORECASE):
                                            experience.title = second
                                        else:
                                            # fallback: leave title blank (will be set later)
                                            pass
                                else:
                                    date_like = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}", first, re.IGNORECASE)
                                    if date_like and len(lines) > 1:
                                        # treat first as company and second as title when second matches role keywords
                                        experience.company = first
                                        second = lines[1]
                                        if re.search(role_kw, second, re.IGNORECASE):
                                            experience.title = second
                                        else:
                                            experience.title = first
                                else:
                                    experience.title = first

            # If company not found yet, try to find ORG in other lines
            if not experience.company and org_candidate:
                experience.company = org_candidate

            # Extract date ranges using flexible regex (handles 'Aug 2024', 'Aug2024', '2024', and ranges)
            date_range_regex = re.compile(r"(?P<start>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}|\d{4})\s*[-–—]\s*(?P<end>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}|\d{4}|present|current)", re.IGNORECASE)
            m = date_range_regex.search(sec)
            if m:
                start_s = m.group("start")
                end_s = m.group("end")
                experience.start_date = self._parse_date(start_s)
                if end_s and end_s.lower() not in ["present", "current"]:
                    experience.end_date = self._parse_date(end_s)
                else:
                    experience.current = True
            else:
                # Try to parse single year/month mentions as start date if present in top lines
                for line in lines[:2]:
                    ym = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}|\d{4}", line)
                    if ym:
                        experience.start_date = self._parse_date(ym.group())
                        break

            # Build description: include lines that are not title/company/date
            desc_lines = []
            skip_patterns = [r"\b(Aug|Sep|Oct|Nov|Dec|Jan|Feb|Mar|Apr|May|Jun)\b", r"\d{4}"]
            for line in lines:
                # skip lines that match company/title exact
                if line == experience.title or line == experience.company:
                    continue
                # skip if line is a short date-only line
                if re.match(r"^\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}\s*$", line, re.IGNORECASE):
                    continue
                desc_lines.append(line)

            experience.description = "\n".join(desc_lines).strip()

            # Extract skills from description
            experience.skills_used = self._extract_skills(experience.description)

            # Validate we have at least some content
            if not experience.title and not experience.company and not experience.description:
                return None

            return experience

        except Exception as e:
            logger.error(f"Failed to parse experience section: {str(e)}")
            return None

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
            experience = Experience()

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

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse date string to date object."""
        try:
            # Try strict formats first
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
                    return datetime.strptime(date_str.strip(), fmt).date()
                except Exception:
                    continue

            # Fallback: try dateutil if available which handles many informal formats
            try:
                from dateutil import parser as dateutil_parser

                # dateutil may return a datetime; prefer year/month if present
                dt = dateutil_parser.parse(date_str, default=datetime(1900, 1, 1))
                return date(dt.year, dt.month, 1)
            except Exception:
                # Last resort: extract a 4-digit year
                y = re.search(r"(19|20)\d{2}", date_str)
                if y:
                    return date(int(y.group()), 1, 1)

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
            education = Education()

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
            certification = Certification()

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
            logger.error(f"Failed to calculate confidence score: {str(e)}")
            return 0.0
