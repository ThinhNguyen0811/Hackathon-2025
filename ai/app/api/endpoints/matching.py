"""Endpoints for employee matching."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any

from app.core.logging import get_logger
from app.schemas.project import TextProjectRequest, MatchingResponse
from app.services.matching import MatchingService
from app.services.parser import RequirementsParserService
from app.models.project import ProjectRequirement, Skills, ExperienceLevel

router = APIRouter()
logger = get_logger(__name__)

@router.post("/match", response_model=MatchingResponse)
async def match_employees(req: TextProjectRequest) -> Dict[str, Any]:
    """Match employees to project requirements described in free text."""
    try:
        logger.info(f"Received project requirement: {req.description[:100]}...")
        
        # Parse the free text into structured data
        parser_service = RequirementsParserService()
        parsed_req = parser_service.parse_requirements(req.description)
        
        # Create project requirement from parsed data
        project_requirement = await _create_project_requirement(
            title=parsed_req["title"],
            tech_stack=parsed_req["tech_stack"],
            domains=parsed_req["domains"],
            required_level=parsed_req["required_level"],
            start_date=parsed_req["start_date"]
        )
        
        # Run the matching workflow
        matching_service = MatchingService()
        result = matching_service.run_workflow(project_requirement)
        
        if result.get("error"):
            logger.warning(f"Matching workflow returned error: {result['error']}")
            return MatchingResponse(
                recommended_employees=[],
                selection_criteria=[],
                recommendation_summary=result.get("recommendation_summary", ""),
                error=result["error"]
            )
        
        return result
        
    except ValueError as e:
        logger.error(f"Error parsing requirements: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error parsing requirements: {str(e)}")
    except Exception as e:
        logger.error(f"Error in matching endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

async def _create_project_requirement(
    title: str, 
    tech_stack: list, 
    domains: list, 
    required_level: str, 
    start_date: str
) -> ProjectRequirement:
    """Helper function to create project requirement from parameters."""
    # Parse the start date
    try:
        parsed_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Map input level to enum
    try:
        level_map = {
            "senior": ExperienceLevel.SENIOR,
            "intermediate": ExperienceLevel.INTERMEDIATE, 
            "junior": ExperienceLevel.JUNIOR,
            "fresher": ExperienceLevel.FRESHER,
            "principal": ExperienceLevel.PRINCIPAL
        }
        required_level_enum = level_map.get(required_level.lower())
        if not required_level_enum:
            raise ValueError(f"Invalid level: {required_level}")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create project requirement
    return ProjectRequirement(
        title=title,
        required_skills=Skills(
            tech_stack=tech_stack,
            domains=domains
        ),
        required_level=required_level_enum,
        start_date=parsed_date
    ) 