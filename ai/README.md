# Employee Matching API

This API matches employees to project requirements based on skills, domains, and experience. The system uses AI to parse natural language project descriptions and find suitable employees.

## Project Structure

```
app/
├── api/               # API routes and endpoints
│   ├── endpoints/     # Individual endpoint modules
│   └── router.py      # Main API router
├── core/              # Core functionality
│   ├── config.py      # Application configuration
│   └── logging.py     # Logging setup
├── models/            # Domain models
│   └── project.py     # Project-related models
├── schemas/           # Pydantic schemas for API validation
│   └── project.py     # Project-related schemas
├── services/          # Business logic services
│   ├── matching.py    # Matching service
│   └── parser.py      # Text parsing service
└── main.py            # Application entry point
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the API

Option 1: Use the provided batch script:
```bash
run_api.bat
```

Option 2: Run with uvicorn directly:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Health Check
```
GET /api/health
```

### Match Employees to Project
```
POST /api/match
```

Example request:
```json
{
  "description": "We need to build an e-commerce platform for a retail client using React on the frontend and Node.js with MongoDB for the backend. The project involves payment systems integration. We're looking for a senior developer to start on April 1, 2025."
}
```

Example response:
```json
{
  "recommended_employees": [
    {
      "employee": "employee123",
      "overall_match_score": 0.85,
      "detailed_scoring_breakdown": {
        "skill_fit": 0.9,
        "domain_expertise_alignment": 0.8,
        "experience_level_appropriateness": 0.85
      },
      "key_strengths_and_relevant_experience": [
        "Advanced React skills",
        "Payment systems experience"
      ],
      "potential_concerns_or_limitations": [],
      "workload_compatibility_assessment": "Available at project start date"
    }
  ],
  "selection_criteria": [
    "Skill fit",
    "Domain expertise alignment",
    "Experience level appropriateness",
    "Workload compatibility"
  ],
  "recommendation_summary": "Selected 1 candidates based on skill match, domain expertise, and experience level."
}
```