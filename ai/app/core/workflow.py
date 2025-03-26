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
import asyncio
import concurrent.futures
import math
from app.services.services import APIService

# Configure logging
logger = logging.getLogger(__name__)

# Batch size for employee analysis to prevent token limit issues
EMPLOYEE_BATCH_SIZE = 50


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
            "api_service": api_service,  # Store API service in state for reuse
        }

        return state

    except Exception as e:
        logger.error(f"Error in initialize_workflow: {str(e)}")
        return None


def process_employee_batch(employees_batch, analyzer):
    """Process a single batch of employees."""
    try:
        batch_size = len(employees_batch)
        logger.info(f"Processing batch of {batch_size} pre-filtered employees")

        # The batch now contains only valid employees, so we can send directly to the analyzer
        batch_analyses = analyzer.analyze_employees(employees_batch)

        if not batch_analyses:
            logger.warning(f"No analyses returned for batch of {batch_size} employees")
            return []

        logger.info(
            f"Successfully analyzed batch of {batch_size} employees, got {len(batch_analyses)} results"
        )
        return batch_analyses
    except Exception as e:
        logger.error(f"Error processing employee batch: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return []


async def analyze_employees_async(
    employees: List[Employee], analyzer: EmployeeAnalyzer
) -> List[Dict]:
    """Analyze employees in batches asynchronously."""
    total_employees = len(employees)
    logger.info(
        f"Analyzing {total_employees} employees in batches of {EMPLOYEE_BATCH_SIZE}..."
    )

    # No employees to analyze
    if not employees:
        return []

    # Calculate number of batches
    num_batches = math.ceil(total_employees / EMPLOYEE_BATCH_SIZE)
    logger.info(f"Split into {num_batches} batches for processing")

    # Create batches
    batches = []
    for i in range(0, total_employees, EMPLOYEE_BATCH_SIZE):
        batch = employees[i : i + EMPLOYEE_BATCH_SIZE]
        batches.append(batch)

    # Process batches in thread pool to enable concurrent processing
    all_analyses = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, process_employee_batch, batch, analyzer)
            for batch in batches
        ]

        # Process results as they complete
        completed = 0
        for batch_result in await asyncio.gather(*futures):
            completed += 1
            logger.info(f"Completed batch {completed}/{num_batches}")
            all_analyses.extend(batch_result)

    logger.info(
        f"Successfully analyzed {len(all_analyses)} employees across {num_batches} batches"
    )
    return all_analyses


def analyze_employees(
    employees: List[Employee],
    analyzer: EmployeeAnalyzer,
    project_requirement: ProjectRequirement,
) -> List[Dict]:
    """Analyze all employees by processing in batches to handle large numbers."""
    logger.info(f"Starting employee analysis for {len(employees)} employees...")

    try:
        total_employees = len(employees)

        # No employees to analyze
        if not total_employees:
            return []

        # Pre-filter employees with null primary skills upfront
        logger.info("Pre-filtering employees with null primary skills...")
        valid_employees = []
        for employee in employees:
            if not employee.skills or any(
                not skill.skillName or skill.skillName.lower() == "none"
                for skill in employee.skills
            ):
                logger.debug(
                    f"Pre-filtering: Skipping employee {employee.empCode} due to null or invalid primary skills"
                )
                continue
            valid_employees.append(employee)

        filtered_count = total_employees - len(valid_employees)
        logger.info(
            f"Pre-filtered {filtered_count} employees with null primary skills. Proceeding with {len(valid_employees)} valid employees."
        )

        # Filter out employees whose primary skills don't exist in project requirements
        logger.info(
            "Filtering employees whose primary skills don't match project requirements..."
        )
        required_skills = set(
            [skill.lower() for skill in project_requirement.required_skills.tech_stack]
        )
        matching_skill_employees = []

        for employee in valid_employees:
            employee_skills = set(
                [
                    skill.skillName.lower()
                    for skill in employee.skills
                    if skill.skillName
                ]
            )
            # Check if any of the employee's skills match any of the required skills
            if employee_skills.intersection(required_skills):
                matching_skill_employees.append(employee)
            else:
                logger.debug(
                    f"Filtering out employee {employee.empCode} - no matching primary skills with project requirements"
                )

        skill_filtered_count = len(valid_employees) - len(matching_skill_employees)
        logger.info(
            f"Filtered out {skill_filtered_count} employees with no matching primary skills. Proceeding with {len(matching_skill_employees)} employees."
        )

        # If no valid employees after filtering
        if not matching_skill_employees:
            logger.warning(
                "No employees with matching primary skills to project requirements after filtering"
            )
            return []

        # Calculate number of batches based on valid employees
        num_batches = math.ceil(len(matching_skill_employees) / EMPLOYEE_BATCH_SIZE)
        logger.info(
            f"Processing {len(matching_skill_employees)} qualified employees in {num_batches} batches of {EMPLOYEE_BATCH_SIZE}..."
        )

        # Create batches from valid employees only
        batches = []
        for i in range(0, len(matching_skill_employees), EMPLOYEE_BATCH_SIZE):
            batch = matching_skill_employees[i : i + EMPLOYEE_BATCH_SIZE]
            batches.append(batch)

        # Process batches sequentially (non-async alternative)
        all_analyses = []
        for i, batch in enumerate(batches):
            logger.info(
                f"Processing batch {i+1}/{num_batches} with {len(batch)} employees"
            )
            batch_result = process_employee_batch(batch, analyzer)
            all_analyses.extend(batch_result)
            logger.info(f"Completed batch {i+1}/{num_batches}")

        if not all_analyses:
            logger.warning("No valid employee analyses found")
            return []

        logger.info(f"Successfully analyzed {len(all_analyses)} employees in total")
        return all_analyses

    except Exception as e:
        logger.error(f"Error in batch employee analysis: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
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
        # Use the API service instance stored in state
        api_service = state[
            "api_service"
        ]  # Reuse the instance created in initialize_workflow
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

        # Extract employee codes from bookings where dailyHour > 6
        booked_employees = set()
        high_workload_count = 0
        for booking in employee_bookings:
            emp_code = booking.get("empCode")
            daily_hour = booking.get("dailyHour", 0)

            # Check if dailyHour > 6.0
            if emp_code and daily_hour > 6.0:
                booked_employees.add(emp_code)
                high_workload_count += 1

        logger.info(f"Found {high_workload_count} bookings with dailyHour > 6")
        logger.info(
            f"Found {len(booked_employees)} unique employees with dailyHour > 6"
        )

        # Filter available employees
        all_employees = state["employees"]
        available_employees = [
            emp for emp in all_employees if emp.empCode not in booked_employees
        ]

        logger.info(
            f"Filtered from {len(all_employees)} to {len(available_employees)} available employees based on high workload criterion (dailyHour > 6)"
        )

        if not available_employees:
            return {
                "error": "No available employees found",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "No employees are available for the project start date due to existing bookings.",
            }

        # Create analyzer instance and analyze available employees using batch processing
        employee_analyzer = EmployeeAnalyzer()

        # Pass project_requirement to analyze_employees to enable skill filtering
        employee_analyses = analyze_employees(
            available_employees, employee_analyzer, project_requirement
        )

        if not employee_analyses:
            return {
                "error": "No valid employee analyses",
                "recommended_employees": [],
                "selection_criteria": [],
                "recommendation_summary": "No employees with matching skills were found for the project requirements.",
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
