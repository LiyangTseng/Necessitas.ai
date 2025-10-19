# Resume Parser Development Guide

This guide explains how to start and iteratively test and build the resume parser function for the necessitas.ai project.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Navigate to project directory
cd /Users/zhanyisheng/Desktop/necessitas.ai

# Activate virtual environment
source venv/bin/activate

# Install dependencies (if not already done)
pip install boto3 spacy requests python-docx PyPDF2 loguru pydantic pydantic-settings

# Download spaCy English model
python -m spacy download en_core_web_sm
```

### 2. Test the Parser

```bash
# Parse a single resume
python resume_parser_fixed.py test_resumes/sample_resume_1.txt

# Parse with verbose output
python resume_parser_fixed.py test_resumes/sample_resume_1.txt --verbose

# Parse and save to JSON
python resume_parser_fixed.py test_resumes/sample_resume_1.txt --output result.json
```

### 3. Run Tests

```bash
# Run comprehensive test suite
python test_resume_parser.py

# Run specific tests
python -m unittest test_resume_parser.TestResumeParser.test_personal_info_extraction
```

## 📁 Project Structure

```
necessitas.ai/
├── resume_parser_fixed.py          # Main working parser (recommended)
├── resume_parser_dev.py            # Basic parser (for comparison)
├── resume_parser_improved.py       # Intermediate version
├── resume_parser_cli.py            # CLI tool for batch processing
├── test_resume_parser.py           # Comprehensive test suite
├── debug_sections.py               # Debugging utilities
├── test_resumes/                   # Sample resume files
│   ├── sample_resume_1.txt
│   ├── sample_resume_2.txt
│   └── sample_resume_3.txt
└── test_report.json               # Generated test report
```

## 🛠️ Development Workflow

### Iterative Testing Process

1. **Make Changes**: Edit `resume_parser_fixed.py`
2. **Test Single File**: `python resume_parser_fixed.py test_resumes/sample_resume_1.txt`
3. **Run Tests**: `python test_resume_parser.py`
4. **Debug Issues**: Use `debug_sections.py` for detailed debugging
5. **Compare Versions**: Use `resume_parser_cli.py compare` to compare different parsers

### Debugging Tools

```bash
# Debug specific parsing functions
python debug_sections.py

# Debug specific sections
python resume_parser_cli.py debug test_resumes/sample_resume_1.txt --section experience

# Compare different parser versions
python resume_parser_cli.py compare test_resumes/sample_resume_1.txt
```

### Batch Processing

```bash
# Process all resumes in test_resumes directory
python resume_parser_cli.py batch test_resumes

# Create comprehensive test report
python resume_parser_cli.py report test_resumes --output my_report.json
```

## 📊 Current Parser Performance

Based on test results with sample resumes:

| Metric | Performance |
|--------|-------------|
| **Personal Info** | ✅ Excellent (name, email, phone, location, URLs) |
| **Skills** | ✅ Excellent (20+ skills extracted) |
| **Education** | ✅ Good (degree, school, location, dates) |
| **Experience** | ⚠️ Partial (works for some formats, needs improvement) |
| **Summary** | ✅ Good (extracts professional summary) |
| **Confidence Score** | 0.70-0.85 (good to excellent) |
| **Parse Speed** | ~0.08s per resume |

## 🔧 Key Features

### ✅ Working Features

- **Personal Information Extraction**: Name, email, phone, location, LinkedIn, GitHub
- **Skills Detection**: 20+ technical skills using spaCy and regex patterns
- **Education Parsing**: Degree, field of study, school, location, dates, GPA
- **Summary Extraction**: Professional summary/objective
- **Multiple File Formats**: TXT, PDF (with PyPDF2), DOCX (with python-docx)
- **Confidence Scoring**: 0-1 scale based on extracted data quality
- **JSON Serialization**: Full data export to JSON format
- **Error Handling**: Graceful handling of parsing errors

### ⚠️ Areas for Improvement

- **Experience Parsing**: Some resume formats not fully supported
- **Date Parsing**: Could be more robust for various date formats
- **Section Detection**: Could be improved for non-standard resume formats
- **AWS Integration**: Not yet implemented (pending task)

## 🧪 Testing Strategy

### Unit Tests
- Individual function testing
- Edge case handling
- Error condition testing

### Integration Tests
- End-to-end parsing
- Multiple file format testing
- Performance benchmarking

### Sample Data
- 3 sample resumes with different formats
- Various skill sets and experience levels
- Different education backgrounds

## 🚀 Next Steps

### Immediate Improvements
1. **Fix Experience Parsing**: Improve regex patterns for different resume formats
2. **Enhance Date Parsing**: Support more date formats
3. **Add More File Formats**: Support additional document types
4. **Improve Section Detection**: Better handling of non-standard formats

### AWS Integration (Pending)
1. **AWS Textract**: For better PDF parsing
2. **S3 Integration**: For file storage and retrieval
3. **DynamoDB**: For storing parsed results
4. **Lambda Deployment**: For serverless processing

### Advanced Features
1. **Machine Learning**: Use ML models for better parsing
2. **Validation**: Add data validation and cleaning
3. **Export Formats**: Support multiple output formats
4. **API Integration**: REST API for resume parsing

## 📝 Usage Examples

### Basic Usage
```python
from resume_parser_fixed import FixedResumeParser

parser = FixedResumeParser()
result = parser.parse_resume("path/to/resume.pdf")

print(f"Name: {result.personal_info.name}")
print(f"Skills: {result.skills}")
print(f"Confidence: {result.confidence_score}")
```

### Batch Processing
```python
import json
from pathlib import Path

parser = FixedResumeParser()
results = []

for file_path in Path("resumes").glob("*.pdf"):
    result = parser.parse_resume(str(file_path))
    results.append(parser.to_dict(result))

with open("results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### CLI Usage
```bash
# Parse single file
python resume_parser_fixed.py resume.pdf --output result.json

# Debug specific section
python resume_parser_cli.py debug resume.pdf --section experience

# Batch process directory
python resume_parser_cli.py batch ./resumes --output batch_results.json
```

## 🐛 Troubleshooting

### Common Issues

1. **spaCy Model Not Found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **PDF Parsing Errors**
   - Ensure PyPDF2 is installed
   - Check if PDF is text-based (not scanned image)

3. **Low Confidence Scores**
   - Check if resume format is supported
   - Verify text extraction quality
   - Review parsing patterns

4. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Debug Mode
```bash
# Enable verbose output
python resume_parser_fixed.py resume.pdf --verbose

# Debug specific parsing function
python debug_sections.py
```

## 📈 Performance Monitoring

The parser includes built-in performance monitoring:

- **Parse Time**: Average ~0.08s per resume
- **Memory Usage**: Minimal (text-based processing)
- **Accuracy**: 70-85% confidence scores
- **Error Rate**: Low (graceful error handling)

## 🔄 Continuous Development

### Recommended Workflow
1. Make small, incremental changes
2. Test with sample resumes after each change
3. Run full test suite before committing
4. Monitor performance and accuracy metrics
5. Document changes and improvements

### Version Control
- Keep working versions in separate files
- Use descriptive commit messages
- Tag stable versions
- Maintain test coverage

This development setup provides a solid foundation for iterative resume parser development with comprehensive testing and debugging tools.
