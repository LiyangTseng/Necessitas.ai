# Coursera API Integration Guide

## Overview
The Coursera API integration allows your backend to search for courses and certifications, and provide personalized learning recommendations to users based on their skill gaps and career goals.

## 🚀 Quick Start

### 1. Basic Course Search
```python
from app.services.coursera_service import CourseraService
from app.models.coursera import CourseSearchRequest

# Initialize service
coursera_service = CourseraService()

# Search for Python courses
request = CourseSearchRequest(
    query="python",
    skills=["programming"],
    limit=3
)

response = await coursera_service.search_courses(request)
print(f"Found {len(response.courses)} courses")
```

### 2. Certification Search
```python
from app.models.coursera import CertificationSearchRequest

# Search for data science certifications
request = CertificationSearchRequest(
    query="data science",
    skills=["python", "machine learning"],
    limit=2
)

response = await coursera_service.search_certifications(request)
print(f"Found {len(response.certifications)} certifications")
```

### 3. Learning Recommendations
```python
# Get personalized learning recommendations
recommendations = await coursera_service.get_learning_recommendations(
    user_id="user_123",
    skill_gaps=["python", "machine learning", "data analysis"],
    target_role="Data Scientist"
)

print(f"Recommended courses: {len(recommendations.recommended_courses)}")
print(f"Estimated completion: {recommendations.estimated_completion_time} weeks")
```

## 📡 API Endpoints

### Course Search
- **GET** `/api/coursera/courses/search`
- **POST** `/api/coursera/courses/search`

**Parameters:**
- `query` - Search term (e.g., "python")
- `skills` - Comma-separated skills (e.g., "python,programming")
- `level` - Course level (beginner, intermediate, advanced)
- `is_free` - Filter free courses (true/false)
- `limit` - Number of results (1-50)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/coursera/courses/search?query=python&skills=programming&limit=3"
```

### Certification Search
- **GET** `/api/coursera/certifications/search`
- **POST** `/api/coursera/certifications/search`

**Parameters:**
- `query` - Search term (e.g., "data science")
- `skills` - Comma-separated skills
- `course_type` - Type (professional_certificate, specialization)
- `industry_recognition` - Industry recognized (true/false)
- `limit` - Number of results (1-50)

### Learning Recommendations
- **GET** `/api/coursera/recommendations/{user_id}`
- **POST** `/api/coursera/recommendations/{user_id}`

**Parameters:**
- `skill_gaps` - Comma-separated skill gaps
- `target_role` - Target job role

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/coursera/recommendations/user123?skill_gaps=python,machine%20learning&target_role=Data%20Scientist"
```

### Job-Specific Learning
- **GET** `/api/jobs/{job_id}/learning-recommendations`
- **POST** `/api/jobs/career-development/{user_id}`

## 📊 Response Formats

### Course Search Response
```json
{
  "courses": [
    {
      "id": "course_123",
      "title": "Python for Data Science",
      "description": "Learn Python programming for data analysis",
      "url": "https://coursera.org/learn/python-data-science",
      "institution": "University of Michigan",
      "level": "beginner",
      "skills": ["Python", "Data Analysis", "Pandas"],
      "duration_weeks": 6,
      "is_free": true,
      "price": 0.0,
      "certificate_available": true
    }
  ],
  "total_count": 1,
  "page": 1,
  "limit": 3,
  "has_more": false
}
```

### Learning Recommendations Response
```json
{
  "success": true,
  "recommendations": {
    "user_id": "user_123",
    "target_role": "Data Scientist",
    "skill_gaps": ["python", "machine learning", "data analysis"],
    "recommended_courses": [...],
    "recommended_certifications": [...],
    "learning_path": [
      {
        "step": 1,
        "title": "Foundation Skills",
        "duration_weeks": 6,
        "skills_covered": ["python", "data analysis"]
      }
    ],
    "estimated_completion_time": 12
  }
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Set your RapidAPI key for real Coursera data
export RAPIDAPI_KEY="your_rapidapi_key_here"
```

### Without API Key
- Uses mock data for testing
- All functionality works
- Sample courses and certifications provided

### With API Key
- Uses real Coursera data
- Live course and certification information
- Up-to-date pricing and availability

## 🎯 Use Cases

### 1. Career Development
```python
# Help user prepare for a specific role
recommendations = await coursera_service.get_learning_recommendations(
    user_id="user_123",
    skill_gaps=["python", "machine learning"],
    target_role="Data Scientist"
)
```

### 2. Job Application Preparation
```python
# Get learning recommendations for a specific job
from app.services.job_matching_engine import JobMatchingEngine

job_matcher = JobMatchingEngine()
recommendations = await job_matcher.get_learning_recommendations_for_job(
    user_profile=user_profile,
    job=job_posting
)
```

### 3. Skill Gap Analysis
```python
# Find courses to fill skill gaps
request = CourseSearchRequest(
    skills=["python", "machine learning"],
    level="intermediate",
    is_free=True
)
courses = await coursera_service.search_courses(request)
```

## 🧪 Testing

### Run Tests
```bash
# Run Coursera integration tests
python -m app.tests.unit.services.test_coursera_integration

# Run all tests
python -m app.tests.run_tests
```

### Test Examples
```bash
# Run usage examples
python -m app.agents.coursera_examples.coursera_api_examples
python -m app.agents.coursera_examples.simple_coursera_usage
```

## 📝 Input/Output Examples

### Input: Course Search
```python
CourseSearchRequest(
    query="python programming",
    skills=["python", "programming"],
    level="intermediate",
    is_free=True,
    limit=5
)
```

### Output: Course Results
```python
CourseSearchResponse(
    courses=[
        Course(
            title="Python for Data Science",
            institution="University of Michigan",
            level="beginner",
            skills=["Python", "Data Analysis"],
            is_free=True,
            duration_weeks=6
        )
    ],
    total_count=1,
    has_more=False
)
```

### Input: Learning Recommendations
```python
# User wants to become a Data Scientist
skill_gaps = ["python", "machine learning", "data analysis"]
target_role = "Data Scientist"
```

### Output: Learning Plan
```python
LearningRecommendation(
    user_id="user_123",
    target_role="Data Scientist",
    skill_gaps=["python", "machine learning", "data analysis"],
    recommended_courses=[...],  # 2 courses
    recommended_certifications=[...],  # 2 certifications
    learning_path=[...],  # Structured learning steps
    estimated_completion_time=12  # weeks
)
```

## 🔄 Integration with Job Matching

The Coursera API integrates seamlessly with the job matching system:

1. **Job Analysis**: Analyzes job requirements vs user skills
2. **Skill Gap Identification**: Finds missing skills for specific jobs
3. **Learning Recommendations**: Suggests courses to bridge gaps
4. **Career Development**: Creates learning paths for career advancement

## 🚀 Getting Started

1. **Install Dependencies**: All required packages are already included
2. **Set API Key** (optional): `export RAPIDAPI_KEY="your_key"`
3. **Start Server**: `python -m app.main`
4. **Test Endpoints**: Use the provided examples
5. **Integrate**: Add to your frontend or other services

## 📚 Additional Resources

- **API Documentation**: Available at `/docs` when server is running
- **Test Files**: `app/tests/unit/services/test_coursera_integration.py`
- **Example Scripts**: `app/agents/coursera_examples/`
- **Models**: `app/models/coursera.py`
- **Service**: `app/services/coursera_service.py`
- **Router**: `app/routers/coursera.py`

The Coursera API integration is now ready to help users find relevant courses, get personalized learning recommendations, and bridge skill gaps for their career development!
