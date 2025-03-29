import requests
from typing import Dict, List
import logging
from datetime import datetime, timedelta
from app.models.models import Employee, Project, Skill, AdditionalSkill, BusinessDomain
from app.core.config import settings

logger = logging.getLogger(__name__)


class APIService:
    def __init__(self):
        self.base_url_insider = "https://uat-insiderapi.saigontechnology.vn/api"
        self.base_url_empinfo = "https://uat-empinfoapi.saigontechnology.vn"
        self._employee_skills_cache = None
        self._employee_bookings_cache = {}
        self._employee_active_status_cache = None

    def _get_headers(self, token) -> Dict:
        return {"Authorization": token, "Content-Type": "application/json"}

    def parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string from API to datetime object."""
        try:
            # Remove 'Z' if present and replace with '+00:00'
            if date_str.endswith("Z"):
                date_str = date_str[:-1] + "+00:00"

            # Split into main part and timezone
            main_part, timezone = date_str.rsplit("+", 1)
            if "." in main_part:
                # Handle milliseconds
                base, ms = main_part.rsplit(".", 1)
                # Pad or truncate milliseconds to 6 digits
                ms = ms[:6].ljust(6, "0")
                main_part = f"{base}.{ms}"

            # Reconstruct the string
            formatted_date = f"{main_part}+{timezone}"
            return datetime.fromisoformat(formatted_date)

        except Exception as e:
            logger.error(f"Error parsing datetime {date_str}: {str(e)}")
            return datetime.now()  # Fallback to current time

    def clean_project_data(self, proj_data: Dict) -> Dict:
        """Clean project data by removing null values and ensuring valid data types"""
        # Clean members data
        if "members" in proj_data:
            cleaned_members = []
            for member in proj_data["members"]:
                if member is None:
                    continue
                cleaned_member = {
                    "id": member.get("id", 0),
                    "teamId": member.get("teamId", 0),
                    "empCode": member.get("empCode", ""),
                    "isTeamLeader": member.get("isTeamLeader", False),
                    "name": member.get("name", ""),
                    "skillNames": member.get("skillNames", [])
                    or [],  # Convert None to empty list
                }
                cleaned_members.append(cleaned_member)
            proj_data["members"] = cleaned_members

        # Clean coordinator data
        if "projectCoordinator" in proj_data:
            coordinator = proj_data["projectCoordinator"]
            if coordinator is None:
                coordinator = {
                    "id": 0,
                    "teamId": 0,
                    "empCode": "",
                    "isTeamLeader": False,
                    "name": "",
                    "skillNames": [],
                }
            else:
                coordinator["skillNames"] = coordinator.get("skillNames", []) or []
            proj_data["projectCoordinator"] = coordinator

        # Ensure other required fields have default values
        proj_data["name"] = proj_data.get("name", "")
        proj_data["color"] = proj_data.get("color", "")
        proj_data["projectModelName"] = proj_data.get("projectModelName", "")
        proj_data["id"] = proj_data.get("id", 0)

        return proj_data

    def get_project_bookings(self) -> List[Project]:
        """Fetch project bookings from the API"""
        try:
            url = f"{self.base_url_insider}/project/get-all-for-booking"
            response = requests.get(
                url, headers=self._get_headers(settings.INSIDER_BEARER_TOKEN)
            )
            response.raise_for_status()

            projects_data = response.json()
            logger.info(f"Retrieved {len(projects_data)} projects from API")

            projects = []
            for proj_data in projects_data:
                try:
                    # Convert string dates to datetime objects
                    if proj_data.get("startDate"):
                        proj_data["startDate"] = self.parse_datetime(
                            proj_data["startDate"]
                        )
                    if proj_data.get("endDate"):
                        proj_data["endDate"] = self.parse_datetime(proj_data["endDate"])

                    # Clean and validate project data
                    cleaned_data = self.clean_project_data(proj_data)

                    # Create project object
                    project = Project(**cleaned_data)
                    projects.append(project)

                except Exception as e:
                    logger.error(f"Error processing project data: {str(e)}")
                    logger.error(f"Problematic project data: {proj_data}")
                    continue

            logger.info(f"Successfully processed {len(projects)} projects")
            return projects

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching project bookings: {str(e)}")
            return []

    def get_employee_skills(self) -> List[Employee]:
        """Fetch employee skills from the API"""
        try:
            url = f"{self.base_url_empinfo}/integrate/skill"
            response = requests.get(
                url, headers=self._get_headers(settings.EMP_INFO_TOKEN)
            )
            response.raise_for_status()

            employees_data = response.json()
            logger.info(f"Retrieved {len(employees_data)} employees from API")

            employees = []
            for emp_data in employees_data:
                # Convert skills data to match our model
                skills = []
                for skill in emp_data.get("skills", []):
                    skills.append(
                        Skill(
                            skillId=skill.get("skillId", 0),
                            skillName=skill.get("skillName", ""),
                            level=skill.get("level", "Beginner"),
                            monthOfExperience=skill.get("monthOfExperience", 0),
                            isPrimary=skill.get("isPrimary", False),
                        )
                    )

                # Convert additional skills
                additional_skills = []
                for add_skill in emp_data.get("additionalSkills", []):
                    additional_skills.append(
                        AdditionalSkill(
                            id=add_skill.get("id", 0),
                            additionalSkillName=add_skill.get(
                                "additionalSkillName", ""
                            ),
                            proficiency=add_skill.get("proficiency", "Beginner"),
                        )
                    )

                # Convert business domains
                business_domains = []
                for domain in emp_data.get("businessDomains", []):
                    business_domains.append(
                        BusinessDomain(
                            id=domain.get("id", 0),
                            businessDomainName=domain.get("businessDomainName", ""),
                        )
                    )

                # Create employee object
                employee = Employee(
                    empCode=emp_data.get("empCode", ""),
                    skills=skills,
                    additionalSkills=additional_skills,
                    businessDomains=business_domains,
                )
                employees.append(employee)

            return employees

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching employee skills: {str(e)}")
            return []

    def get_employee_bookings(self, start_date: datetime) -> List[Dict]:
        """Fetch employee bookings from the API using the new endpoint.

        Args:
            start_date: The project start date

        Returns:
            List of employee booking records
        """
        try:
            # Calculate date range: from 30 days before start_date to start_date
            from_date = start_date - timedelta(days=30)

            # Format dates for API URL
            from_date_str = from_date.strftime("%Y-%m-%d")
            to_date_str = start_date.strftime("%Y-%m-%d")

            # Call the new API endpoint
            url = f"{self.base_url_insider}/booking/byPlanner/97/{from_date_str}/{to_date_str}"
            response = requests.get(
                url, headers=self._get_headers(settings.INSIDER_BEARER_TOKEN)
            )
            response.raise_for_status()

            bookings_data = response.json()
            logger.info(f"Retrieved {len(bookings_data)} employee bookings from API")

            return bookings_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching employee bookings: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_employee_bookings: {str(e)}")
            return []

    def get_employee_active_status(self) -> List[Dict]:
        """Get employee active status information from the API."""
        try:
            # Return cached data if available
            if self._employee_active_status_cache is not None:
                logger.debug("Using cached employee active status")
                return self._employee_active_status_cache

            logger.info("Fetching employee active status from API...")
            # Use the proper authorization headers
            response = requests.get(
                f"{self.base_url_empinfo}/.well-known/employee",
                headers=self._get_headers(settings.EMP_INFO_TOKEN),
            )

            if response.status_code != 200:
                logger.error(
                    f"Failed to fetch employee active status: {response.status_code}"
                )
                return []

            employees_data = response.json()
            logger.info(f"Retrieved active status for {len(employees_data)} employees")

            # Cache the results
            self._employee_active_status_cache = employees_data

            return employees_data

        except Exception as e:
            logger.error(f"Error fetching employee active status: {str(e)}")
            return []


def parse_datetime(date_str: str) -> datetime:
    """Parse datetime string from API to datetime object."""
    try:
        # Remove 'Z' if present and replace with '+00:00'
        if date_str.endswith("Z"):
            date_str = date_str[:-1] + "+00:00"

        # Split into main part and timezone
        main_part, timezone = date_str.rsplit("+", 1)
        if "." in main_part:
            # Handle milliseconds
            base, ms = main_part.rsplit(".", 1)
            # Pad or truncate milliseconds to 6 digits
            ms = ms[:6].ljust(6, "0")
            main_part = f"{base}.{ms}"

        # Reconstruct the string
        formatted_date = f"{main_part}+{timezone}"
        return datetime.fromisoformat(formatted_date)

    except Exception as e:
        logger.error(f"Error parsing datetime {date_str}: {str(e)}")
        return datetime.now()  # Fallback to current time

