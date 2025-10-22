# Coursera API Examples

This directory contains examples and documentation for the Coursera API integration.

## Files

- `coursera_api_examples.py` - Comprehensive examples showing all API features
- `simple_coursera_usage.py` - Simple usage examples with clear input/output
- `COURSERA_API_GUIDE.md` - Complete API documentation and usage guide

## Usage

These files demonstrate how to use the Coursera API integration:

1. **Basic Usage**: Run `simple_coursera_usage.py` for basic examples
2. **Advanced Usage**: Run `coursera_api_examples.py` for comprehensive examples
3. **Documentation**: Read `COURSERA_API_GUIDE.md` for complete API reference

## Running Examples

```bash
# From the backend directory
cd backend
python -m app.agents.coursera_examples.simple_coursera_usage
python -m app.agents.coursera_examples.coursera_api_examples
```

## API Endpoints

The Coursera API provides the following endpoints:

- `/api/coursera/courses/search` - Search for courses
- `/api/coursera/certifications/search` - Search for certifications
- `/api/coursera/recommendations/{user_id}` - Get learning recommendations
- `/api/jobs/{job_id}/learning-recommendations` - Job-specific learning
- `/api/jobs/career-development/{user_id}` - Career development plans

## Features

- Course search with filtering
- Certification search with industry recognition
- Personalized learning recommendations
- Learning path generation
- Job-specific skill gap analysis
- Integration with job matching system

## Configuration

Set the `RAPIDAPI_KEY` environment variable to use real Coursera data:
```bash
export RAPIDAPI_KEY="your_rapidapi_key_here"
```

Without the API key, the system uses mock data for testing.
