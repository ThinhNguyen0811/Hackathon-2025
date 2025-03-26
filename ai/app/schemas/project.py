"""Pydantic schemas for project-related requests and responses."""
from typing import List, Optional
from pydantic import BaseModel, Field

class TextProjectRequest(BaseModel):
    """Request model for free-text project requirements."""
    description: str = Field(
        ..., 
        description="Free text description of the project requirements including title, required skills, domains, experience level, and start date."
    )

class MatchScoreResponse(BaseModel):
    """Response model for match scores."""
    skill_fit: float
    domain_expertise_alignment: float
    experience_level_appropriateness: float

class EmployeeMatchResponse(BaseModel):
    """Response model for employee matches."""
    employee: str
    overall_match_score: float
    detailed_scoring_breakdown: MatchScoreResponse
    key_strengths_and_relevant_experience: List[str]
    potential_concerns_or_limitations: List[str]
    workload_compatibility_assessment: Optional[str] = None

class MatchingResponse(BaseModel):
    """Response model for the matching operation."""
    recommended_employees: List[EmployeeMatchResponse]
    selection_criteria: List[str]
    recommendation_summary: str
    error: Optional[str] = None 