import requests
from typing import Dict, List
import logging
from datetime import datetime, timedelta
from app.models.models import Employee, Project, Skill, AdditionalSkill, BusinessDomain
from app.core.config import settings

logger = logging.getLogger(__name__)

class APIService:
    def __init__(self):
        self.base_url_insider = settings.URL_INSIDER
        self.base_url_empinfo = settings.URL_EMPINFO
        self.token = settings.BEARER_TOKEN
    
    def _get_headers(self) -> Dict:
        return {
            "Authorization": self.token,
            "Content-Type": "application/json"
        }
    
    def parse_datetime(self, date_str: str) -> datetime:
        """Parse datetime string from API to datetime object."""
        try:
            # Remove 'Z' if present and replace with '+00:00'
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            
            # Split into main part and timezone
            main_part, timezone = date_str.rsplit('+', 1)
            if '.' in main_part:
                # Handle milliseconds
                base, ms = main_part.rsplit('.', 1)
                # Pad or truncate milliseconds to 6 digits
                ms = ms[:6].ljust(6, '0')
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
        if 'members' in proj_data:
            cleaned_members = []
            for member in proj_data['members']:
                if member is None:
                    continue
                cleaned_member = {
                    'id': member.get('id', 0),
                    'teamId': member.get('teamId', 0),
                    'empCode': member.get('empCode', ''),
                    'isTeamLeader': member.get('isTeamLeader', False),
                    'name': member.get('name', ''),
                    'skillNames': member.get('skillNames', []) or []  # Convert None to empty list
                }
                cleaned_members.append(cleaned_member)
            proj_data['members'] = cleaned_members
        
        # Clean coordinator data
        if 'projectCoordinator' in proj_data:
            coordinator = proj_data['projectCoordinator']
            if coordinator is None:
                coordinator = {
                    'id': 0,
                    'teamId': 0,
                    'empCode': '',
                    'isTeamLeader': False,
                    'name': '',
                    'skillNames': []
                }
            else:
                coordinator['skillNames'] = coordinator.get('skillNames', []) or []
            proj_data['projectCoordinator'] = coordinator
        
        # Ensure other required fields have default values
        proj_data['name'] = proj_data.get('name', '')
        proj_data['color'] = proj_data.get('color', '')
        proj_data['projectModelName'] = proj_data.get('projectModelName', '')
        proj_data['id'] = proj_data.get('id', 0)
        
        return proj_data
    
    def get_project_bookings(self) -> List[Project]:
        """Fetch project bookings from the API"""
        try:
            url = f"{self.base_url_insider}/project/get-all-for-booking"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            projects_data = response.json()
            logger.info(f"Retrieved {len(projects_data)} projects from API")
            
            projects = []
            for proj_data in projects_data:
                try:
                    # Convert string dates to datetime objects
                    if proj_data.get('startDate'):
                        proj_data['startDate'] = self.parse_datetime(proj_data['startDate'])
                    if proj_data.get('endDate'):
                        proj_data['endDate'] = self.parse_datetime(proj_data['endDate'])
                    
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
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            employees_data = response.json()
            logger.info(f"Retrieved {len(employees_data)} employees from API")
            
            employees = []
            for emp_data in employees_data:
                # Convert skills data to match our model
                skills = []
                for skill in emp_data.get('skills', []):
                    skills.append(Skill(
                        skillId=skill.get('skillId', 0),
                        skillName=skill.get('skillName', ''),
                        level=skill.get('level', 'Beginner'),
                        monthOfExperience=skill.get('monthOfExperience', 0),
                        isPrimary=skill.get('isPrimary', False)
                    ))
                
                # Convert additional skills
                additional_skills = []
                for add_skill in emp_data.get('additionalSkills', []):
                    additional_skills.append(AdditionalSkill(
                        id=add_skill.get('id', 0),
                        additionalSkillName=add_skill.get('additionalSkillName', ''),
                        proficiency=add_skill.get('proficiency', 'Beginner')
                    ))
                
                # Convert business domains
                business_domains = []
                for domain in emp_data.get('businessDomains', []):
                    business_domains.append(BusinessDomain(
                        id=domain.get('id', 0),
                        businessDomainName=domain.get('businessDomainName', '')
                    ))
                
                # Create employee object
                employee = Employee(
                    empCode=emp_data.get('empCode', ''),
                    skills=skills,
                    additionalSkills=additional_skills,
                    businessDomains=business_domains
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
            response = requests.get(url, headers=self._get_headers())
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

def parse_datetime(date_str: str) -> datetime:
    """Parse datetime string from API to datetime object."""
    try:
        # Remove 'Z' if present and replace with '+00:00'
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
            
        # Split into main part and timezone
        main_part, timezone = date_str.rsplit('+', 1)
        if '.' in main_part:
            # Handle milliseconds
            base, ms = main_part.rsplit('.', 1)
            # Pad or truncate milliseconds to 6 digits
            ms = ms[:6].ljust(6, '0')
            main_part = f"{base}.{ms}"
        
        # Reconstruct the string
        formatted_date = f"{main_part}+{timezone}"
        return datetime.fromisoformat(formatted_date)
        
    except Exception as e:
        logger.error(f"Error parsing datetime {date_str}: {str(e)}")
        return datetime.now()  # Fallback to current time

def get_employees() -> List[Employee]:
    """Get employee skills from API."""
    try:
        url = "https://uat-empinfoapi.saigontechnology.vn/integrate/skill"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IlNjeEUxUGJ0enFiRkFHdmUyMTZweXpza2R6TSIsInR5cCI6IkpXVCIsIng1dCI6IlNjeEUxUGJ0enFiRkFHdmUyMTZweXpza2R6TSJ9.eyJuYmYiOjE3NDE4NDExOTksImV4cCI6MTc0OTYxNzE5OSwiaXNzIjoiaHR0cHM6Ly91YXQtaWRlbnRpdHkuc2FpZ29udGVjaG5vbG9neS52biIsImF1ZCI6WyJodHRwczovL3VhdC1pZGVudGl0eS5zYWlnb250ZWNobm9sb2d5LnZuL3Jlc291cmNlcyIsInN0c19zeXN0ZW1fYXBpIiwic3RzX2ludGVybmFsX2FwaSIsInN0c19pbnNpZGVyX2FwaSIsInN0c19lbXBpbmZvcl9hcGkiLCJzdHNfY3JtX2FwaSIsInN0c19sZWF2ZV9hcGkiLCJzdHNfcG9wX2FwaSIsInN0c19maW5wbGFuX2FwaSJdLCJjbGllbnRfaWQiOiJzdHNfaW5zaWRlcl9qcyIsInN1YiI6InBodW9uZy50cmFuIiwiYXV0aF90aW1lIjoxNzQxODQxMTk5LCJpZHAiOiJsb2NhbCIsIm5hbWUiOiJwaHVvbmcudHJhbiIsInVzZXJDb2RlIjoicGh1b25nLnRyYW4iLCJlbWFpbCI6InBodW9uZy50cmFuMUBzYWlnb250ZWNobm9sb2d5LmNvbSIsImZ1bGxOYW1lIjoiUGh1b25nIFRyYW4iLCJmaXJzdE5hbWUiOiJQaHVvbmciLCJsYXN0TmFtZSI6IlRyYW4iLCJwcm9maWxlSW1hZ2UiOiIvYXZhdGFyL3BodW9uZy50cmFuLnBuZyIsInVzZXJBY3RpdmUiOiJUcnVlIiwicm9sZSI6WyJQcm9qZWN0TWFuYWdlciIsIkVtcGxveWVlIiwiUHJvamVjdENvb3JkaW5hdG9yIiwiRnVuY3Rpb25hbE1hbmFnZXIiXSwiYWNjZXNzaWJsZVN5c3RlbSI6WyJJZGVudGl0eSIsIkhlbHBkZXNrIiwiTGVhdmUiLCJBcHByYWlzYWwiLCJGaW5QbGFuIiwiQXNzZXRzIiwiRW1wSW5mb3IiLCJDUk0iLCJQb1AiXSwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsInN0c19zeXN0ZW1fYXBpIiwic3RzX2ludGVybmFsX2FwaSIsInN0c19pbnNpZGVyX2FwaSIsInN0c19lbXBpbmZvcl9hcGkiLCJzdHNfY3JtX2FwaSIsInN0c19sZWF2ZV9hcGkiLCJzdHNfcG9wX2FwaSIsInN0c19maW5wbGFuX2FwaSJdLCJhbXIiOlsicHdkIl19.VaU2UWGHgLrnXedvEryOIIaTR_HPUPI4hgKHDMUrig6nFzehaiA0rphaZKSP7e50uGqVW1RzAeUOfdWRXLDvg20UB6QCqm31IWHlBj2MfKfLsSwyX-ha91u0dbzZgphjF33A1Z4knjPfeCSdsPUtS0Ic40FYUiO4FMrSfQMEtMBsGXIiI6cE09olgOaAkmTJjUtK6YYgewgqTSQe-FYueLOIMAqiYa5O7TDZV5LyQUqQ0QQOgdjhwcmeKSGFSeiXWc_Qaf2bKDj1m5y1Bz0Ib4itkkAOBnmBTyMzI4rcLH7Lv8CYvpEywPoYWJMOXz9sC55IcdVZIlvxLswraHxPE4oWORSyRnH6EfTNaBDhbT8JOqB-DHR07jblxpGclJRnpBl3JqwAuscNWCdBZg3qzGYmZWUPy447ZG9lU2XQNHA2bNNWrd8D5vRxiTgLwxL8_kKctLPXYr7TNKsqNSAyDVD7GHThkt3zxhUGRJ6s4rPIaQ_yXUDtewoj5mUK0H-lk9mRiUm77Zvz2aFAoB_1xwK4634MD2bduQt0pnjqM7Bmrr9guvPlwTG5rQWWS7zgIp3eXzyWyvLVp_bwdrJJgeo8nhwZXz7dwZ4XfySKBbCC3C97-_B6VWyA0H4ZVlfctIXcriniliXwzCAMwiIuzSdP_-VQH5AXSt-xNzV670k"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        employees = []
        for emp_data in response.json():
            try:
                # Create skills list with all required fields
                skills = [
                    Skill(
                        skillId=skill.get("skillId", 0),
                        skillName=skill["skillName"],
                        level=skill["level"],
                        monthOfExperience=skill.get("monthOfExperience", 0),
                        isPrimary=skill.get("isPrimary", False)
                    )
                    for skill in emp_data.get("skills", [])
                ]
                
                # Create business domains list with required id field
                business_domains = [
                    BusinessDomain(
                        id=domain.get("id", 0),  # Default to 0 if not provided
                        businessDomainName=domain["businessDomainName"]
                    )
                    for domain in emp_data.get("businessDomains", [])
                ]
                
                # Create additional skills list with required fields
                additional_skills = [
                    AdditionalSkill(
                        id=skill.get("id", 0),  # Default to 0 if not provided
                        additionalSkillName=skill.get("additionalSkillName", skill.get("skillName", "")),  # Try both fields
                        proficiency=skill.get("proficiency", "Beginner")  # Default to Beginner if not provided
                    )
                    for skill in emp_data.get("additionalSkills", [])
                ]
                
                # Create employee object
                employee = Employee(
                    empCode=emp_data["empCode"],
                    skills=skills,
                    businessDomains=business_domains,
                    additionalSkills=additional_skills
                )
                employees.append(employee)
                
            except Exception as e:
                logger.error(f"Error processing employee data: {str(e)}")
                continue
        
        return employees
        
    except Exception as e:
        logger.error(f"Error fetching employee skills: {str(e)}")
        return []

def get_project_bookings() -> List[Dict]:
    """Get project bookings from API."""
    try:
        url = "https://uat-insiderapi.saigontechnology.vn/api/project/get-all-for-booking"
        headers = {
            "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IlNjeEUxUGJ0enFiRkFHdmUyMTZweXpza2R6TSIsInR5cCI6IkpXVCIsIng1dCI6IlNjeEUxUGJ0enFiRkFHdmUyMTZweXpza2R6TSJ9.eyJuYmYiOjE3NDE4NDExOTksImV4cCI6MTc0OTYxNzE5OSwiaXNzIjoiaHR0cHM6Ly91YXQtaWRlbnRpdHkuc2FpZ29udGVjaG5vbG9neS52biIsImF1ZCI6WyJodHRwczovL3VhdC1pZGVudGl0eS5zYWlnb250ZWNobm9sb2d5LnZuL3Jlc291cmNlcyIsInN0c19zeXN0ZW1fYXBpIiwic3RzX2ludGVybmFsX2FwaSIsInN0c19pbnNpZGVyX2FwaSIsInN0c19lbXBpbmZvcl9hcGkiLCJzdHNfY3JtX2FwaSIsInN0c19sZWF2ZV9hcGkiLCJzdHNfcG9wX2FwaSIsInN0c19maW5wbGFuX2FwaSJdLCJjbGllbnRfaWQiOiJzdHNfaW5zaWRlcl9qcyIsInN1YiI6InBodW9uZy50cmFuIiwiYXV0aF90aW1lIjoxNzQxODQxMTk5LCJpZHAiOiJsb2NhbCIsIm5hbWUiOiJwaHVvbmcudHJhbiIsInVzZXJDb2RlIjoicGh1b25nLnRyYW4iLCJlbWFpbCI6InBodW9uZy50cmFuMUBzYWlnb250ZWNobm9sb2d5LmNvbSIsImZ1bGxOYW1lIjoiUGh1b25nIFRyYW4iLCJmaXJzdE5hbWUiOiJQaHVvbmciLCJsYXN0TmFtZSI6IlRyYW4iLCJwcm9maWxlSW1hZ2UiOiIvYXZhdGFyL3BodW9uZy50cmFuLnBuZyIsInVzZXJBY3RpdmUiOiJUcnVlIiwicm9sZSI6WyJQcm9qZWN0TWFuYWdlciIsIkVtcGxveWVlIiwiUHJvamVjdENvb3JkaW5hdG9yIiwiRnVuY3Rpb25hbE1hbmFnZXIiXSwiYWNjZXNzaWJsZVN5c3RlbSI6WyJJZGVudGl0eSIsIkhlbHBkZXNrIiwiTGVhdmUiLCJBcHByYWlzYWwiLCJGaW5QbGFuIiwiQXNzZXRzIiwiRW1wSW5mb3IiLCJDUk0iLCJQb1AiXSwic2NvcGUiOlsib3BlbmlkIiwicHJvZmlsZSIsInN0c19zeXN0ZW1fYXBpIiwic3RzX2ludGVybmFsX2FwaSIsInN0c19pbnNpZGVyX2FwaSIsInN0c19lbXBpbmZvcl9hcGkiLCJzdHNfY3JtX2FwaSIsInN0c19sZWF2ZV9hcGkiLCJzdHNfcG9wX2FwaSIsInN0c19maW5wbGFuX2FwaSJdLCJhbXIiOlsicHdkIl19.VaU2UWGHgLrnXedvEryOIIaTR_HPUPI4hgKHDMUrig6nFzehaiA0rphaZKSP7e50uGqVW1RzAeUOfdWRXLDvg20UB6QCqm31IWHlBj2MfKfLsSwyX-ha91u0dbzZgphjF33A1Z4knjPfeCSdsPUtS0Ic40FYUiO4FMrSfQMEtMBsGXIiI6cE09olgOaAkmTJjUtK6YYgewgqTSQe-FYueLOIMAqiYa5O7TDZV5LyQUqQ0QQOgdjhwcmeKSGFSeiXWc_Qaf2bKDj1m5y1Bz0Ib4itkkAOBnmBTyMzI4rcLH7Lv8CYvpEywPoYWJMOXz9sC55IcdVZIlvxLswraHxPE4oWORSyRnH6EfTNaBDhbT8JOqB-DHR07jblxpGclJRnpBl3JqwAuscNWCdBZg3qzGYmZWUPy447ZG9lU2XQNHA2bNNWrd8D5vRxiTgLwxL8_kKctLPXYr7TNKsqNSAyDVD7GHThkt3zxhUGRJ6s4rPIaQ_yXUDtewoj5mUK0H-lk9mRiUm77Zvz2aFAoB_1xwK4634MD2bduQt0pnjqM7Bmrr9guvPlwTG5rQWWS7zgIp3eXzyWyvLVp_bwdrJJgeo8nhwZXz7dwZ4XfySKBbCC3C97-_B6VWyA0H4ZVlfctIXcriniliXwzCAMwiIuzSdP_-VQH5AXSt-xNzV670k"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        bookings = []
        for booking in response.json():
            try:
                # Process each booking
                processed_booking = {
                    "empCode": booking.get("empCode"),
                    "projectName": booking.get("projectName"),
                    "startDate": booking.get("startDate"),
                    "endDate": booking.get("endDate")
                }
                bookings.append(processed_booking)
                
            except Exception as e:
                logger.error(f"Error processing booking data: {str(e)}")
                continue
        
        return bookings
        
    except Exception as e:
        logger.error(f"Error fetching project bookings: {str(e)}")
        return [] 