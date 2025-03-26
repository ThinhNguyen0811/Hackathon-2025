"""Service for matching employees to projects."""
from typing import Dict, Any

from app.core.logging import get_logger
from app.models.project import ProjectRequirement
from app.core.workflow import run_workflow

logger = get_logger(__name__)

class MatchingService:
    """Service for matching employees to projects."""
    
    def __init__(self):
        """Initialize the matching service."""
        logger.info("Initializing matching service")
    
    def run_workflow(self, project_requirement: ProjectRequirement) -> Dict[str, Any]:
        """Run the matching workflow to find suitable employees for the project."""
        try:
            logger.info(f"Starting matching workflow for project: {project_requirement.title}")
            
            # Use the existing workflow function
            result = run_workflow(project_requirement)
            
            # Log results
            recommended_count = len(result.get("recommended_employees", []))
            logger.info(f"Matching workflow completed. Found {recommended_count} recommended employees")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in matching workflow: {str(e)}")
            return {
                "error": f"Failed to run matching workflow: {str(e)}",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "An error occurred during the matching process."
            } 