from typing import Dict, List
from app.models.models import Employee, ProjectRequirement
from app.services.agents import (
    RequirementAnalyzer,
    EmployeeAnalyzer,
    MatchingAgent,
    WorkloadOptimizer,
)
import logging
import time
from app.services.services import APIService

# Configure logging
logger = logging.getLogger(__name__)


def initialize_workflow(project_requirement: ProjectRequirement) -> Dict:
    """Initialize workflow with required data."""
    try:
        start_time = time.time()

        # Initialize API service for better caching
        api_service = APIService()

        # Get employees from API
        logger.info("Retrieving employees...")
        employees = api_service.get_employee_skills()
        logger.info(f"Retrieved {len(employees)} employees")

        # Create initial state
        state = {
            "project_requirement": project_requirement,
            "employees": employees,
            "requirement_analysis": None,
            "employee_analyses": [],
            "matches": [],
            "start_time": start_time,
        }

        return state

    except Exception as e:
        logger.error(f"Error in initialize_workflow: {str(e)}")
        return None


def analyze_employees(
    employees: List[Employee], analyzer: EmployeeAnalyzer
) -> List[Dict]:
    """Analyze all employees in a single batch."""
    logger.info(f"Analyzing {len(employees)} employees...")

    try:
        # Process all employees in a single batch
        analyses = analyzer.analyze_employees(employees)

        if not analyses:
            logger.warning("No valid employee analyses found")
            return []

        logger.info(f"Successfully analyzed {len(analyses)} employees")
        return analyses

    except Exception as e:
        logger.error(f"Error in batch employee analysis: {str(e)}")
        return []


def match_employees(state: Dict) -> Dict:
    """Match analyzed employees with project requirements."""
    try:
        # Use the existing employee analyses
        if not state.get("employee_analyses"):
            logger.warning("No employee analyses found")
            state["matches"] = []
            return state

        logger.info(f"Matching {len(state['employee_analyses'])} analyzed employees")

        # Match analyzed employees
        matcher = MatchingAgent()
        matches = matcher.evaluate_matches(
            state["employee_analyses"],
            state["requirement_analysis"],
            state["project_requirement"],
        )

        if matches:
            logger.info(f"Found {len(matches)} potential matches")
        else:
            logger.warning("No matches found after evaluation")

        state["matches"] = matches
        return state

    except Exception as e:
        logger.error(f"Error in match_employees: {str(e)}")
        state["matches"] = []
        return state


def run_workflow(project_requirement: ProjectRequirement) -> Dict:
    """Run the complete workflow."""
    try:
        # Initialize state
        state = initialize_workflow(project_requirement)
        if not state:
            logger.error("Failed to initialize workflow")
            return {
                "error": "Failed to initialize workflow",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "Error occurred during workflow initialization.",
            }

        # Analyze requirements
        analyzer = RequirementAnalyzer()
        state["requirement_analysis"] = analyzer.analyze_requirement(
            state["project_requirement"]
        )
        if not state.get("requirement_analysis"):
            logger.error("Failed to analyze requirements")
            return {
                "error": "Failed to analyze requirements",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "Error occurred during requirement analysis.",
            }

        # Get employee bookings from the new API endpoint
        api_service = APIService()
        project_start_date = state["project_requirement"].start_date

        # Ensure project_start_date is naive for consistent comparison
        if (
            hasattr(project_start_date, "tzinfo")
            and project_start_date.tzinfo is not None
        ):
            # Convert to naive UTC
            project_start_date = project_start_date.replace(tzinfo=None)

        logger.info(
            f"Fetching employee bookings for project start date: {project_start_date}"
        )

        employee_bookings = api_service.get_employee_bookings(project_start_date)

        if not employee_bookings:
            logger.warning(
                "No employee bookings found, assuming all employees are available"
            )
        else:
            logger.info(f"Retrieved {len(employee_bookings)} employee bookings")

        # Extract all employee codes from bookings
        booked_employees = set()
        for booking in employee_bookings:
            emp_code = booking.get("empCode")
            if emp_code:
                booked_employees.add(emp_code)

        logger.info(f"Found {len(booked_employees)} unique employees with bookings")

        # Filter available employees
        all_employees = state["employees"]
        available_employees = [
            emp for emp in all_employees if emp.empCode not in booked_employees
        ]

        logger.info(
            f"Filtered from {len(all_employees)} to {len(available_employees)} available employees based on bookings"
        )

        if not available_employees:
            return {
                "error": "No available employees found",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "No employees are available for the project start date due to existing bookings.",
            }

        # Create analyzer instance and analyze available employees
        employee_analyzer = EmployeeAnalyzer()
        employee_analyses = employee_analyzer.analyze_employees(available_employees)

        if not employee_analyses:
            return {
                "error": "No valid employee analyses",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "No valid employee profiles were found for analysis.",
            }

        # Update state with analyses
        state["employee_analyses"] = employee_analyses
        logger.info(f"Successfully analyzed {len(employee_analyses)} employees")

        # Match employees
        matcher = MatchingAgent()
        matches = matcher.evaluate_matches(
            employee_analyses,
            state["requirement_analysis"],
            state["project_requirement"],
        )

        if not matches:
            logger.info("No matches found, ending workflow")
            return {
                "error": "No matches found",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "No suitable matches were found for the project requirements.",
            }

        state["matches"] = matches
        logger.info(f"Found {len(matches)} potential matches")

        # Optimize workload
        optimizer = WorkloadOptimizer()
        recommendations = optimizer.optimize_workload(matches)

        if not recommendations:
            return {
                "error": "Optimization failed",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "Failed to optimize workload distribution.",
            }

        return recommendations

    except Exception as e:
        logger.error(f"Error running workflow: {str(e)}")
        return {
            "error": str(e),
            "recommended_employees": [],
            "selection_criteria": [],
            "recommendation_summary": f"An error occurred: {str(e)}",
        }
