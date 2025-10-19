#!/usr/bin/env python3
"""
Comprehensive test suite for resume parser development
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from resume_parser_fixed import FixedResumeParser, ResumeData, PersonalInfo, Experience, Education


class TestResumeParser(unittest.TestCase):
    """Test cases for the fixed resume parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = FixedResumeParser()
        self.sample_resume_path = "test_resumes/sample_resume_1.txt"
    
    def test_parse_resume_success(self):
        """Test successful resume parsing."""
        result = self.parser.parse_resume(self.sample_resume_path)
        
        self.assertIsInstance(result, ResumeData)
        self.assertIsInstance(result.personal_info, PersonalInfo)
        self.assertGreater(result.confidence_score, 0.0)
        self.assertLessEqual(result.confidence_score, 1.0)
    
    def test_personal_info_extraction(self):
        """Test personal information extraction."""
        with open(self.sample_resume_path, 'r') as f:
            content = f.read()
        
        personal_info = self.parser._extract_personal_info(content)
        
        self.assertEqual(personal_info.name, "John Doe")
        self.assertEqual(personal_info.email, "john.doe@email.com")
        self.assertEqual(personal_info.phone, "+1-555-123-4567")
        self.assertEqual(personal_info.location, "San Francisco, CA")
        self.assertIn("linkedin.com", personal_info.linkedin_url)
        self.assertIn("github.com", personal_info.github_url)
    
    def test_skills_extraction(self):
        """Test skills extraction."""
        with open(self.sample_resume_path, 'r') as f:
            content = f.read()
        
        skills = self.parser._extract_skills(content)
        
        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)
        self.assertIn("Python", skills)
        self.assertIn("React", skills)
        self.assertIn("AWS", skills)
        self.assertLessEqual(len(skills), 20)  # Should be limited to top 20
    
    def test_experience_extraction(self):
        """Test experience extraction."""
        with open(self.sample_resume_path, 'r') as f:
            content = f.read()
        
        experiences = self.parser._extract_experience(content)
        
        self.assertIsInstance(experiences, list)
        self.assertGreater(len(experiences), 0)
        
        # Check first experience
        first_exp = experiences[0]
        self.assertIsInstance(first_exp, Experience)
        self.assertIn("Senior Software Engineer", first_exp.title)
        self.assertIn("TechCorp", first_exp.company)
        self.assertEqual(first_exp.location, "San Francisco, CA")
        self.assertTrue(first_exp.current)
    
    def test_education_extraction(self):
        """Test education extraction."""
        with open(self.sample_resume_path, 'r') as f:
            content = f.read()
        
        education = self.parser._extract_education(content)
        
        self.assertIsInstance(education, list)
        self.assertGreater(len(education), 0)
        
        # Check first education entry
        first_edu = education[0]
        self.assertIsInstance(first_edu, Education)
        self.assertIn("Bachelor", first_edu.degree)
        self.assertIn("Computer Science", first_edu.field_of_study)
    
    def test_confidence_score_calculation(self):
        """Test confidence score calculation."""
        with open(self.sample_resume_path, 'r') as f:
            content = f.read()
        
        resume_data = self.parser._parse_resume_data(content)
        confidence = self.parser._calculate_confidence_score(resume_data)
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        self.assertGreater(confidence, 0.5)  # Should be a good confidence score
    
    def test_json_serialization(self):
        """Test JSON serialization."""
        result = self.parser.parse_resume(self.sample_resume_path)
        json_data = self.parser.to_dict(result)
        
        # Should be serializable to JSON
        json_str = json.dumps(json_data)
        self.assertIsInstance(json_str, str)
        
        # Should be deserializable back to dict
        parsed_data = json.loads(json_str)
        self.assertIsInstance(parsed_data, dict)
    
    def test_batch_processing(self):
        """Test batch processing of multiple files."""
        test_dir = Path("test_resumes")
        files = list(test_dir.glob("*.txt"))
        
        results = []
        for file_path in files:
            try:
                result = self.parser.parse_resume(str(file_path))
                results.append(result)
            except Exception as e:
                self.fail(f"Failed to parse {file_path}: {e}")
        
        self.assertGreater(len(results), 0)
        
        # All results should have reasonable confidence scores
        for result in results:
            self.assertGreater(result.confidence_score, 0.0)
            self.assertLessEqual(result.confidence_score, 1.0)


class TestResumeParserIntegration(unittest.TestCase):
    """Integration tests for resume parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = FixedResumeParser()
    
    def test_all_sample_resumes(self):
        """Test parsing all sample resumes."""
        test_dir = Path("test_resumes")
        sample_files = list(test_dir.glob("sample_resume_*.txt"))
        
        self.assertGreater(len(sample_files), 0, "No sample resume files found")
        
        results = {}
        for file_path in sample_files:
            with self.subTest(file=file_path.name):
                try:
                    result = self.parser.parse_resume(str(file_path))
                    results[file_path.name] = result
                    
                    # Basic validation
                    self.assertIsInstance(result, ResumeData)
                    self.assertGreater(result.confidence_score, 0.0)
                    
                except Exception as e:
                    self.fail(f"Failed to parse {file_path.name}: {e}")
        
        # Print summary
        print(f"\n📊 Batch Processing Results:")
        print("=" * 50)
        for filename, result in results.items():
            print(f"{filename}:")
            print(f"  Name: {result.personal_info.name}")
            print(f"  Skills: {len(result.skills)}")
            print(f"  Experience: {len(result.experience)}")
            print(f"  Education: {len(result.education)}")
            print(f"  Confidence: {result.confidence_score:.2f}")
            print()
    
    def test_error_handling(self):
        """Test error handling for invalid files."""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_resume("non_existent_file.txt")
        
        # Test with empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            result = self.parser.parse_resume(temp_path)
            # Should not crash, but confidence should be low
            self.assertIsInstance(result, ResumeData)
            self.assertEqual(result.confidence_score, 0.0)
        finally:
            os.unlink(temp_path)


def run_performance_test():
    """Run performance test on sample resumes."""
    import time
    
    parser = FixedResumeParser()
    test_dir = Path("test_resumes")
    sample_files = list(test_dir.glob("sample_resume_*.txt"))
    
    print("🚀 Performance Test")
    print("=" * 50)
    
    total_time = 0
    for file_path in sample_files:
        start_time = time.time()
        result = parser.parse_resume(str(file_path))
        end_time = time.time()
        
        parse_time = end_time - start_time
        total_time += parse_time
        
        print(f"{file_path.name}: {parse_time:.3f}s (confidence: {result.confidence_score:.2f})")
    
    avg_time = total_time / len(sample_files) if sample_files else 0
    print(f"\nAverage parse time: {avg_time:.3f}s")
    print(f"Total time: {total_time:.3f}s")


def create_test_report():
    """Create a comprehensive test report."""
    parser = FixedResumeParser()
    test_dir = Path("test_resumes")
    sample_files = list(test_dir.glob("sample_resume_*.txt"))
    
    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "total_files": len(sample_files),
        "results": []
    }
    
    for file_path in sample_files:
        try:
            result = parser.parse_resume(str(file_path))
            json_data = parser.to_dict(result)
            
            report["results"].append({
                "file": file_path.name,
                "success": True,
                "confidence": result.confidence_score,
                "personal_info": {
                    "name": result.personal_info.name,
                    "email": result.personal_info.email,
                    "phone": result.personal_info.phone,
                    "location": result.personal_info.location
                },
                "stats": {
                    "skills_count": len(result.skills),
                    "experience_count": len(result.experience),
                    "education_count": len(result.education),
                    "projects_count": len(result.projects)
                }
            })
        except Exception as e:
            report["results"].append({
                "file": file_path.name,
                "success": False,
                "error": str(e)
            })
    
    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("📊 Test Report Created: test_report.json")
    return report


if __name__ == "__main__":
    # Run unit tests
    print("🧪 Running Unit Tests")
    print("=" * 50)
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 80 + "\n")
    
    # Run performance test
    run_performance_test()
    
    print("\n" + "=" * 80 + "\n")
    
    # Create test report
    create_test_report()
