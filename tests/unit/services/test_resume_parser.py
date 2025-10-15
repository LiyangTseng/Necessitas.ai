"""
Unit tests for ResumeParser service using unittest.
"""

import unittest
from unittest.mock import Mock, patch, AsyncMock, mock_open
from datetime import datetime, date
import tempfile
import os

from backend.app.services.resume_parser import (
    ResumeParser,
    ResumeData,
    PersonalInfo,
    Experience,
    Education,
    Certification,
    WorkType,
    ExperienceLevel,
)
from tests.test_utils import AsyncTestCase, MockDataFactory


class TestResumeParser(AsyncTestCase):
    """Test cases for ResumeParser service."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.resume_parser = None
        self.mock_resume_text = None

    def create_resume_parser(self):
        """Create ResumeParser instance for testing."""
        with (
            patch("backend.app.services.resume_parser.boto3.client"),
            patch("backend.app.services.resume_parser.spacy.load"),
            patch("backend.app.services.resume_parser.Matcher"),
        ):
            return ResumeParser()

    def create_mock_resume_text(self):
        """Create mock resume text for testing."""
        return """
        John Doe
        Senior Software Engineer
        john.doe@email.com
        +1-555-123-4567
        San Francisco, CA
        https://linkedin.com/in/johndoe
        https://github.com/johndoe

        SUMMARY
        Experienced software engineer with 5+ years in Python and React development.
        Passionate about building scalable web applications and leading technical teams.

        EXPERIENCE
        Senior Software Engineer - TechCorp
        San Francisco, CA
        Jan 2021 - Present
        • Led development of microservices architecture
        • Mentored junior developers
        • Technologies: Python, React, AWS, Docker

        Software Engineer - StartupXYZ
        San Francisco, CA
        Jun 2019 - Dec 2020
        • Developed full-stack web applications
        • Technologies: Python, JavaScript, PostgreSQL

        EDUCATION
        Bachelor of Computer Science
        University of Technology
        San Francisco, CA
        2018 - 2022
        GPA: 3.8

        SKILLS
        Python, React, AWS, Docker, Kubernetes, Machine Learning, SQL, Git

        CERTIFICATIONS
        AWS Solutions Architect - Amazon Web Services
        Certified Kubernetes Administrator - CNCF

        PROJECTS
        ML Recommendation System
        Built a machine learning recommendation system using Python and TensorFlow
        https://github.com/johndoe/ml-recommendation
        """

    def test_parse_resume_success(self):
        """Test successful resume parsing."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Mock the text extraction
        self.resume_parser._extract_text_with_textract = AsyncMock(
            return_value=self.mock_resume_text
        )
        self.resume_parser._extract_text_fallback = AsyncMock(
            return_value=self.mock_resume_text
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file.write(self.mock_resume_text)
            temp_path = temp_file.name

        try:
            # Act
            resume_data = self.run_async(self.resume_parser.parse_resume(temp_path))

            # Assert
            self.assertIsInstance(resume_data, ResumeData)
            self.assertEqual(resume_data.personal_info.name, "John Doe")
            self.assertEqual(resume_data.personal_info.email, "john.doe@email.com")
            self.assertEqual(resume_data.personal_info.phone, "+1-555-123-4567")
            self.assertEqual(resume_data.personal_info.location, "San Francisco, CA")
            self.assertIn("Python", resume_data.skills)
            self.assertIn("React", resume_data.skills)
            self.assertGreater(len(resume_data.experience), 0)
            self.assertGreater(len(resume_data.education), 0)
            self.assertGreater(resume_data.confidence_score, 0.0)
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_parse_resume_from_url_success(self):
        """Test successful resume parsing from URL."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Mock the requests and text extraction
        with patch("backend.app.services.resume_parser.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "text/html"}
            mock_response.text = self.mock_resume_text
            mock_get.return_value = mock_response

            # Act
            resume_data = self.run_async(
                self.resume_parser.parse_resume_from_url("https://example.com/resume")
            )

            # Assert
            self.assertIsInstance(resume_data, ResumeData)
            self.assertEqual(resume_data.personal_info.name, "John Doe")
            self.assertIn("Python", resume_data.skills)

    def test_parse_resume_from_url_pdf(self):
        """Test resume parsing from PDF URL."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Mock the requests and file operations
        with (
            patch("backend.app.services.resume_parser.requests.get") as mock_get,
            patch(
                "backend.app.services.resume_parser.tempfile.NamedTemporaryFile"
            ) as mock_temp,
            patch("os.remove") as mock_remove,
        ):

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "application/pdf"}
            mock_response.content = b"PDF content"
            mock_get.return_value = mock_response

            mock_temp_file = Mock()
            mock_temp_file.name = "/tmp/resume.pdf"
            mock_temp.return_value.__enter__.return_value = mock_temp_file

            # Mock the parse_resume method
            self.resume_parser.parse_resume = AsyncMock(
                return_value=ResumeData(
                    personal_info=PersonalInfo(name="John Doe"),
                    skills=["Python", "React"],
                    confidence_score=0.8,
                )
            )

            # Act
            resume_data = self.run_async(
                self.resume_parser.parse_resume_from_url(
                    "https://example.com/resume.pdf"
                )
            )

            # Assert
            self.assertIsInstance(resume_data, ResumeData)
            self.assertEqual(resume_data.personal_info.name, "John Doe")

    def test_extract_text_with_textract_success(self):
        """Test successful text extraction with Textract."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Mock the Textract response
        mock_textract_response = {
            "Blocks": [
                {"BlockType": "LINE", "Text": "John Doe"},
                {"BlockType": "LINE", "Text": "Senior Software Engineer"},
                {"BlockType": "LINE", "Text": "Python, React, AWS"},
            ]
        }
        self.resume_parser.textract.analyze_document.return_value = (
            mock_textract_response
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file.write("Test content")
            temp_path = temp_file.name

        try:
            # Act
            text = self.run_async(
                self.resume_parser._extract_text_with_textract(temp_path)
            )

            # Assert
            self.assertEqual(
                text, "John Doe\nSenior Software Engineer\nPython, React, AWS"
            )
        finally:
            os.unlink(temp_path)

    def test_extract_text_with_textract_fallback(self):
        """Test text extraction fallback when Textract fails."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Mock Textract to raise exception
        self.resume_parser.textract.analyze_document.side_effect = Exception(
            "Textract error"
        )
        self.resume_parser._extract_text_fallback = AsyncMock(
            return_value="Fallback text"
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file.write("Test content")
            temp_path = temp_file.name

        try:
            # Act
            text = self.run_async(
                self.resume_parser._extract_text_with_textract(temp_path)
            )

            # Assert
            self.assertEqual(text, "Fallback text")
        finally:
            os.unlink(temp_path)

    def test_extract_personal_info(self):
        """Test personal information extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Act
        personal_info = self.resume_parser._extract_personal_info(self.mock_resume_text)

        # Assert
        self.assertIsInstance(personal_info, PersonalInfo)
        self.assertEqual(personal_info.name, "John Doe")
        self.assertEqual(personal_info.email, "john.doe@email.com")
        self.assertEqual(personal_info.phone, "+1-555-123-4567")
        self.assertEqual(personal_info.location, "San Francisco, CA")
        self.assertIn("linkedin.com", personal_info.linkedin_url)
        self.assertIn("github.com", personal_info.github_url)

    def test_extract_skills(self):
        """Test skills extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Act
        skills = self.resume_parser._extract_skills(self.mock_resume_text)

        # Assert
        self.assertIsInstance(skills, list)
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
        self.assertIn("AWS", skills)
        self.assertIn("Docker", skills)
        self.assertLessEqual(len(skills), 20)  # Should be limited to top 20

    def test_extract_experience(self):
        """Test experience extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Act
        experiences = self.resume_parser._extract_experience(self.mock_resume_text)

        # Assert
        self.assertIsInstance(experiences, list)
        self.assertGreater(len(experiences), 0)

        # Check first experience
        first_exp = experiences[0]
        self.assertIsInstance(first_exp, Experience)
        self.assertIn("Senior Software Engineer", first_exp.title)
        self.assertIn("TechCorp", first_exp.company)
        self.assertIn("San Francisco", first_exp.location)
        self.assertTrue(first_exp.current)

    def test_extract_education(self):
        """Test education extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Act
        education = self.resume_parser._extract_education(self.mock_resume_text)

        # Assert
        self.assertIsInstance(education, list)
        self.assertGreater(len(education), 0)

        # Check first education entry
        first_edu = education[0]
        self.assertIsInstance(first_edu, Education)
        self.assertIn("Bachelor", first_edu.degree)
        self.assertIn("Computer Science", first_edu.field)
        self.assertIn("University of Technology", first_edu.school)

    def test_extract_certifications(self):
        """Test certifications extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Act
        certifications = self.resume_parser._extract_certifications(
            self.mock_resume_text
        )

        # Assert
        self.assertIsInstance(certifications, list)
        self.assertGreater(len(certifications), 0)

        # Check first certification
        first_cert = certifications[0]
        self.assertIsInstance(first_cert, Certification)
        self.assertIn("AWS Solutions Architect", first_cert.name)
        self.assertIn("Amazon Web Services", first_cert.issuer)

    def test_extract_summary(self):
        """Test summary extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Act
        summary = self.resume_parser._extract_summary(self.mock_resume_text)

        # Assert
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
        self.assertIn("software engineer", summary.lower())

    def test_extract_languages(self):
        """Test languages extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Test text with languages section
        text_with_languages = """
        John Doe
        Software Engineer

        LANGUAGES
        English, Spanish, French
        """

        # Act
        languages = self.resume_parser._extract_languages(text_with_languages)

        # Assert
        self.assertIsInstance(languages, list)
        self.assertIn("English", languages)
        self.assertIn("Spanish", languages)
        self.assertIn("French", languages)

    def test_extract_projects(self):
        """Test projects extraction."""
        # Arrange
        self.resume_parser = self.create_resume_parser()
        self.mock_resume_text = self.create_mock_resume_text()

        # Act
        projects = self.resume_parser._extract_projects(self.mock_resume_text)

        # Assert
        self.assertIsInstance(projects, list)
        self.assertGreater(len(projects), 0)

        # Check first project
        first_project = projects[0]
        self.assertIsInstance(first_project, dict)
        self.assertIn("ML Recommendation System", first_project["name"])
        self.assertIn("machine learning", first_project["description"].lower())
        self.assertIn("github.com", first_project["url"])

    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Create mock resume data
        resume_data = ResumeData(
            personal_info=PersonalInfo(
                name="John Doe",
                email="john@email.com",
                phone="+1-555-123-4567",
                location="San Francisco, CA",
            ),
            skills=["Python", "React", "AWS"],
            experience=[
                Experience(
                    title="Software Engineer",
                    company="TechCorp",
                    location="San Francisco, CA",
                )
            ],
            education=[
                Education(
                    degree="Bachelor of Computer Science",
                    school="University of Technology",
                )
            ],
            summary="Experienced software engineer",
            raw_text="John Doe\nSoftware Engineer\nPython, React, AWS",
        )

        # Act
        confidence = self.resume_parser._calculate_confidence_score(resume_data)

        # Assert
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        self.assertGreater(confidence, 0.5)  # Should be a good confidence score

    def test_parse_date(self):
        """Test date parsing."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Test various date formats
        test_dates = [
            "January 2021",
            "Jan 2021",
            "2021-01",
            "2021",
            "January 15, 2021",
            "01/15/2021",
        ]

        for date_str in test_dates:
            # Act
            parsed_date = self.resume_parser._parse_date(date_str)

            # Assert
            if parsed_date:
                self.assertIsInstance(parsed_date, date)

    def test_is_experience_section(self):
        """Test experience section detection."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Test positive cases
        positive_sections = [
            "EXPERIENCE\nSoftware Engineer at TechCorp",
            "WORK HISTORY\nSenior Developer",
            "EMPLOYMENT\nPython Developer",
            "CAREER\nData Scientist",
        ]

        for section in positive_sections:
            # Act & Assert
            self.assertTrue(self.resume_parser._is_experience_section(section))

        # Test negative cases
        negative_sections = [
            "EDUCATION\nBachelor of Computer Science",
            "SKILLS\nPython, React, AWS",
            "PROJECTS\nML Recommendation System",
        ]

        for section in negative_sections:
            # Act & Assert
            self.assertFalse(self.resume_parser._is_experience_section(section))

    def test_is_date_line(self):
        """Test date line detection."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Test positive cases
        positive_lines = ["Jan 2021 - Present", "June 2019 - Dec 2020", "2021 - 2023"]

        for line in positive_lines:
            # Act & Assert
            self.assertTrue(self.resume_parser._is_date_line(line))

        # Test negative cases
        negative_lines = [
            "Software Engineer at TechCorp",
            "Led development of microservices",
            "Technologies: Python, React, AWS",
        ]

        for line in negative_lines:
            # Act & Assert
            self.assertFalse(self.resume_parser._is_date_line(line))

    def test_parse_resume_exception_handling(self):
        """Test exception handling in parse_resume."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Mock text extraction to raise exception
        self.resume_parser._extract_text_with_textract = AsyncMock(
            side_effect=Exception("Textract error")
        )
        self.resume_parser._extract_text_fallback = AsyncMock(
            side_effect=Exception("Fallback error")
        )

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as temp_file:
            temp_file.write("Test content")
            temp_path = temp_file.name

        try:
            # Act & Assert
            with self.assertRaises(Exception):
                self.run_async(self.resume_parser.parse_resume(temp_path))
        finally:
            os.unlink(temp_path)

    def test_parse_resume_from_url_exception_handling(self):
        """Test exception handling in parse_resume_from_url."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Mock requests to raise exception
        with patch("backend.app.services.resume_parser.requests.get") as mock_get:
            mock_get.side_effect = Exception("Network error")

            # Act & Assert
            with self.assertRaises(Exception):
                self.run_async(
                    self.resume_parser.parse_resume_from_url(
                        "https://example.com/resume"
                    )
                )

    def test_extract_personal_info_no_data(self):
        """Test personal info extraction with no data."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Act
        personal_info = self.resume_parser._extract_personal_info("")

        # Assert
        self.assertIsInstance(personal_info, PersonalInfo)
        self.assertEqual(personal_info.name, "")
        self.assertEqual(personal_info.email, "")
        self.assertEqual(personal_info.phone, "")

    def test_extract_skills_no_data(self):
        """Test skills extraction with no data."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Act
        skills = self.resume_parser._extract_skills("")

        # Assert
        self.assertIsInstance(skills, list)
        self.assertEqual(len(skills), 0)

    def test_calculate_confidence_score_no_data(self):
        """Test confidence score calculation with no data."""
        # Arrange
        self.resume_parser = self.create_resume_parser()

        # Create empty resume data
        resume_data = ResumeData(
            personal_info=PersonalInfo(),
            skills=[],
            experience=[],
            education=[],
            summary="",
            raw_text="",
        )

        # Act
        confidence = self.resume_parser._calculate_confidence_score(resume_data)

        # Assert
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        self.assertEqual(confidence, 0.0)  # Should be 0 for no data


if __name__ == "__main__":
    unittest.main()
