#!/usr/bin/env python3
"""
Debug script to understand section extraction issues
"""

import re
from pathlib import Path

def debug_section_extraction():
    """Debug the section extraction logic."""
    
    # Read the sample resume
    with open("test_resumes/sample_resume_1.txt", "r") as f:
        content = f.read()
    
    print("=== Original Content ===")
    print(content)
    print("\n" + "="*60 + "\n")
    
    # Test the section finding logic
    section_names = ["experience", "work history", "employment", "career"]
    
    for section_name in section_names:
        print(f"=== Testing section: {section_name} ===")
        
        # Original pattern from the code
        pattern = rf"(?:{section_name}):\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*(?:[A-Z][A-Z\s]+):|\n\s*$|$)"
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        if match:
            print(f"✅ Found section: {section_name}")
            print(f"Content: {match.group(1)[:200]}...")
        else:
            print(f"❌ No match for: {section_name}")
        
        # Try a simpler pattern
        simple_pattern = rf"(?:{section_name}):\s*(.*?)(?=\n[A-Z]+\n|\n[A-Z][A-Z\s]+:|\n\s*$|$)"
        simple_match = re.search(simple_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        
        if simple_match:
            print(f"✅ Simple pattern found: {section_name}")
            print(f"Content: {simple_match.group(1)[:200]}...")
        else:
            print(f"❌ Simple pattern no match for: {section_name}")
        
        print("-" * 40)

def debug_experience_parsing():
    """Debug the experience parsing logic."""
    
    with open("test_resumes/sample_resume_1.txt", "r") as f:
        content = f.read()
    
    print("=== Experience Section Debug ===")
    
    # Find the experience section manually
    lines = content.split('\n')
    experience_start = -1
    experience_end = -1
    
    for i, line in enumerate(lines):
        if line.strip().upper() == "EXPERIENCE":
            experience_start = i
            print(f"Found EXPERIENCE header at line {i}: '{line}'")
            break
    
    if experience_start >= 0:
        # Find the end of the experience section
        for i in range(experience_start + 1, len(lines)):
            line = lines[i].strip()
            if line and line.isupper() and len(line) > 3:
                experience_end = i
                print(f"Found next section at line {i}: '{line}'")
                break
        
        if experience_end == -1:
            experience_end = len(lines)
        
        # Extract the experience section
        experience_lines = lines[experience_start:experience_end]
        experience_text = '\n'.join(experience_lines)
        
        print(f"\nExperience section content:")
        print(experience_text)
        
        # Try to split into entries
        print(f"\n=== Splitting into entries ===")
        
        # Method 1: Split by double newlines
        entries1 = re.split(r'\n\s*\n', experience_text)
        print(f"Method 1 (double newlines): {len(entries1)} entries")
        for i, entry in enumerate(entries1):
            print(f"  Entry {i+1}: {entry[:100]}...")
        
        # Method 2: Split by job title patterns
        job_pattern = r'(?=\n[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*[-–]\s*[A-Z])'
        entries2 = re.split(job_pattern, experience_text)
        print(f"\nMethod 2 (job patterns): {len(entries2)} entries")
        for i, entry in enumerate(entries2):
            print(f"  Entry {i+1}: {entry[:100]}...")

if __name__ == "__main__":
    debug_section_extraction()
    print("\n" + "="*80 + "\n")
    debug_experience_parsing()
