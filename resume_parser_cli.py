#!/usr/bin/env python3
"""
Resume Parser CLI Tool

A comprehensive command-line tool for testing and developing resume parser functionality.
Supports batch processing, detailed debugging, and iterative development.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import our parser
from resume_parser_improved import ImprovedResumeParser, ResumeData


class ResumeParserCLI:
    """CLI tool for resume parser development and testing."""
    
    def __init__(self):
        """Initialize the CLI tool."""
        self.parser = ImprovedResumeParser()
        self.results = []
    
    def parse_single_file(self, file_path: str, verbose: bool = False) -> ResumeData:
        """Parse a single resume file."""
        print(f"🔍 Parsing: {file_path}")
        
        try:
            resume_data = self.parser.parse_resume(file_path)
            
            if verbose:
                self._print_detailed_results(resume_data)
            else:
                self._print_summary(resume_data)
            
            return resume_data
            
        except Exception as e:
            print(f"❌ Error parsing {file_path}: {str(e)}")
            return None
    
    def parse_batch(self, directory: str, output_file: str = None, verbose: bool = False) -> List[ResumeData]:
        """Parse all resume files in a directory."""
        directory = Path(directory)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return []
        
        # Find all supported files
        supported_extensions = ['.txt', '.pdf', '.docx']
        files = []
        for ext in supported_extensions:
            files.extend(directory.glob(f"*{ext}"))
        
        if not files:
            print(f"❌ No supported files found in {directory}")
            return []
        
        print(f"📁 Found {len(files)} files to process")
        print("=" * 60)
        
        results = []
        for file_path in files:
            result = self.parse_single_file(str(file_path), verbose)
            if result:
                results.append(result)
                self.results.append({
                    'file': str(file_path),
                    'data': self.parser.to_dict(result)
                })
            print("-" * 40)
        
        # Save batch results
        if output_file:
            self._save_batch_results(output_file)
        
        return results
    
    def debug_parsing(self, file_path: str, section: str = None) -> None:
        """Debug specific parsing functions."""
        print(f"🐛 Debug mode for: {file_path}")
        print("=" * 60)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 File content preview (first 500 chars):")
            print(content[:500] + "..." if len(content) > 500 else content)
            print("\n" + "=" * 60)
            
            if section is None or section == "personal":
                print("👤 Personal Info Extraction:")
                personal_info = self.parser._extract_personal_info(content)
                print(f"  Name: '{personal_info.name}'")
                print(f"  Email: '{personal_info.email}'")
                print(f"  Phone: '{personal_info.phone}'")
                print(f"  Location: '{personal_info.location}'")
                print(f"  LinkedIn: '{personal_info.linkedin_url}'")
                print(f"  GitHub: '{personal_info.github_url}'")
                print()
            
            if section is None or section == "skills":
                print("🛠️  Skills Extraction:")
                skills = self.parser._extract_skills(content)
                print(f"  Found {len(skills)} skills: {skills}")
                print()
            
            if section is None or section == "experience":
                print("💼 Experience Extraction:")
                experiences = self.parser._extract_experience(content)
                print(f"  Found {len(experiences)} experience entries:")
                for i, exp in enumerate(experiences, 1):
                    print(f"    {i}. {exp.title} at {exp.company}")
                    print(f"       Location: {exp.location}")
                    print(f"       Duration: {exp.start_date} - {exp.end_date}")
                    print(f"       Current: {exp.current}")
                    print(f"       Description: {exp.description[:100]}...")
                print()
            
            if section is None or section == "education":
                print("🎓 Education Extraction:")
                education = self.parser._extract_education(content)
                print(f"  Found {len(education)} education entries:")
                for i, edu in enumerate(education, 1):
                    print(f"    {i}. {edu.degree} in {edu.field_of_study}")
                    print(f"       School: {edu.school}")
                    print(f"       Location: {edu.location}")
                    print(f"       Duration: {edu.start_date} - {edu.end_date}")
                    print(f"       GPA: {edu.gpa}")
                print()
            
            if section is None or section == "summary":
                print("📝 Summary Extraction:")
                summary = self.parser._extract_summary(content)
                print(f"  Summary: '{summary}'")
                print()
            
        except Exception as e:
            print(f"❌ Error in debug mode: {str(e)}")
    
    def compare_parsers(self, file_path: str) -> None:
        """Compare different parsing approaches."""
        print(f"🔄 Comparing parsers for: {file_path}")
        print("=" * 60)
        
        try:
            # Import both parsers
            from resume_parser_dev import ResumeParserDev as BasicParser
            from resume_parser_improved import ImprovedResumeParser as ImprovedParser
            
            basic_parser = BasicParser()
            improved_parser = ImprovedParser()
            
            # Parse with both
            print("📊 Basic Parser Results:")
            basic_result = basic_parser.parse_resume(file_path)
            self._print_summary(basic_result)
            
            print("\n📊 Improved Parser Results:")
            improved_result = improved_parser.parse_resume(file_path)
            self._print_summary(improved_result)
            
            # Compare key metrics
            print("\n📈 Comparison:")
            print(f"  Basic Parser Confidence: {basic_result.confidence_score:.2f}")
            print(f"  Improved Parser Confidence: {improved_result.confidence_score:.2f}")
            print(f"  Basic Parser Skills: {len(basic_result.skills)}")
            print(f"  Improved Parser Skills: {len(improved_result.skills)}")
            print(f"  Basic Parser Experience: {len(basic_result.experience)}")
            print(f"  Improved Parser Experience: {len(improved_result.experience)}")
            print(f"  Basic Parser Education: {len(basic_result.education)}")
            print(f"  Improved Parser Education: {len(improved_result.education)}")
            
        except Exception as e:
            print(f"❌ Error comparing parsers: {str(e)}")
    
    def create_test_report(self, directory: str, output_file: str = "test_report.json") -> None:
        """Create a comprehensive test report."""
        print(f"📊 Creating test report for: {directory}")
        print("=" * 60)
        
        results = self.parse_batch(directory, verbose=False)
        
        # Generate statistics
        stats = {
            'total_files': len(results),
            'successful_parses': len([r for r in results if r is not None]),
            'average_confidence': sum(r.confidence_score for r in results if r) / len(results) if results else 0,
            'skills_extracted': sum(len(r.skills) for r in results if r),
            'experience_entries': sum(len(r.experience) for r in results if r),
            'education_entries': sum(len(r.education) for r in results if r),
            'timestamp': datetime.now().isoformat()
        }
        
        # Create report
        report = {
            'statistics': stats,
            'results': self.results
        }
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Test report saved to: {output_file}")
        print(f"📈 Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Successful parses: {stats['successful_parses']}")
        print(f"  Average confidence: {stats['average_confidence']:.2f}")
        print(f"  Total skills extracted: {stats['skills_extracted']}")
        print(f"  Total experience entries: {stats['experience_entries']}")
        print(f"  Total education entries: {stats['education_entries']}")
    
    def _print_summary(self, resume_data: ResumeData) -> None:
        """Print a summary of parsed resume data."""
        print(f"  Name: {resume_data.personal_info.name}")
        print(f"  Email: {resume_data.personal_info.email}")
        print(f"  Phone: {resume_data.personal_info.phone}")
        print(f"  Location: {resume_data.personal_info.location}")
        print(f"  Skills: {len(resume_data.skills)} found")
        print(f"  Experience: {len(resume_data.experience)} entries")
        print(f"  Education: {len(resume_data.education)} entries")
        print(f"  Confidence: {resume_data.confidence_score:.2f}")
    
    def _print_detailed_results(self, resume_data: ResumeData) -> None:
        """Print detailed results of parsed resume data."""
        print(f"\n📄 Detailed Results:")
        print("=" * 50)
        print(f"Name: {resume_data.personal_info.name}")
        print(f"Email: {resume_data.personal_info.email}")
        print(f"Phone: {resume_data.personal_info.phone}")
        print(f"Location: {resume_data.personal_info.location}")
        print(f"LinkedIn: {resume_data.personal_info.linkedin_url}")
        print(f"GitHub: {resume_data.personal_info.github_url}")
        print(f"\nSummary: {resume_data.summary}")
        print(f"\nSkills ({len(resume_data.skills)}): {', '.join(resume_data.skills[:10])}")
        
        print(f"\nExperience ({len(resume_data.experience)} entries):")
        for i, exp in enumerate(resume_data.experience[:3], 1):
            print(f"  {i}. {exp.title} at {exp.company}")
            if exp.location:
                print(f"     Location: {exp.location}")
            if exp.start_date:
                end_date = "Present" if exp.current else exp.end_date
                print(f"     Duration: {exp.start_date} - {end_date}")
        
        print(f"\nEducation ({len(resume_data.education)} entries):")
        for i, edu in enumerate(resume_data.education[:3], 1):
            print(f"  {i}. {edu.degree} in {edu.field_of_study} from {edu.school}")
            if edu.location:
                print(f"     Location: {edu.location}")
            if edu.gpa:
                print(f"     GPA: {edu.gpa}")
        
        print(f"\nConfidence Score: {resume_data.confidence_score:.2f}")
    
    def _save_batch_results(self, output_file: str) -> None:
        """Save batch processing results to file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"💾 Batch results saved to: {output_file}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Resume Parser CLI Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse single file command
    parse_parser = subparsers.add_parser('parse', help='Parse a single resume file')
    parse_parser.add_argument('file_path', help='Path to resume file')
    parse_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parse_parser.add_argument('--output', '-o', help='Output JSON file')
    
    # Batch parse command
    batch_parser = subparsers.add_parser('batch', help='Parse all files in a directory')
    batch_parser.add_argument('directory', help='Directory containing resume files')
    batch_parser.add_argument('--output', '-o', help='Output JSON file for results')
    batch_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Debug command
    debug_parser = subparsers.add_parser('debug', help='Debug parsing for a specific file')
    debug_parser.add_argument('file_path', help='Path to resume file')
    debug_parser.add_argument('--section', choices=['personal', 'skills', 'experience', 'education', 'summary'], 
                             help='Specific section to debug')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare different parsers')
    compare_parser.add_argument('file_path', help='Path to resume file')
    
    # Test report command
    report_parser = subparsers.add_parser('report', help='Create comprehensive test report')
    report_parser.add_argument('directory', help='Directory containing resume files')
    report_parser.add_argument('--output', '-o', default='test_report.json', help='Output report file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ResumeParserCLI()
    
    try:
        if args.command == 'parse':
            result = cli.parse_single_file(args.file_path, args.verbose)
            if args.output and result:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(cli.parser.to_dict(result), f, indent=2, ensure_ascii=False)
                print(f"💾 Results saved to: {args.output}")
        
        elif args.command == 'batch':
            cli.parse_batch(args.directory, args.output, args.verbose)
        
        elif args.command == 'debug':
            cli.debug_parsing(args.file_path, args.section)
        
        elif args.command == 'compare':
            cli.compare_parsers(args.file_path)
        
        elif args.command == 'report':
            cli.create_test_report(args.directory, args.output)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
