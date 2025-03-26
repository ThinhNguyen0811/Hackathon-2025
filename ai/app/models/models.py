from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class WorkloadType(str, Enum):
    FULLTIME = "fulltime"
    PARTTIME = "parttime"
    SUPPORT = "support"

class ExperienceLevel(str, Enum):
    FRESHER = "fresher"
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    PRINCIPAL = "principal"

class Workload(BaseModel):
    start_date: datetime
    end_date: datetime
    workload_type: WorkloadType
    daily_hours: int
    days_per_week: int

class Skills(BaseModel):
    tech_stack: List[str]
    domains: List[str]

class SkillLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class Skill(BaseModel):
    skillId: int
    skillName: str
    level: str
    monthOfExperience: int
    isPrimary: bool

class AdditionalSkill(BaseModel):
    id: int
    additionalSkillName: str
    proficiency: str

class BusinessDomain(BaseModel):
    id: int
    businessDomainName: str

class Employee(BaseModel):
    empCode: str
    skills: List[Skill]
    additionalSkills: List[AdditionalSkill]
    businessDomains: List[BusinessDomain]

class ProjectMember(BaseModel):
    id: int
    teamId: int
    empCode: str
    isTeamLeader: bool
    name: str
    skillNames: Optional[List[str]]

class ProjectCoordinator(BaseModel):
    id: int
    teamId: int
    empCode: str
    isTeamLeader: bool
    name: str
    skillNames: Optional[List[str]]

class Project(BaseModel):
    name: str
    startDate: datetime
    endDate: Optional[datetime]
    id: int
    projectCoordinator: ProjectCoordinator
    color: str
    members: List[ProjectMember]
    projectModelName: str

class ProjectRequirement(BaseModel):
    title: str
    required_skills: Skills
    required_level: ExperienceLevel
    start_date: datetime

class MatchScore(BaseModel):
    technical_fit: float
    domain_match: float
    experience_match: float
    workload_compatibility: float
    match_score: float
    sdc_adjustment: float = 0.0
    base_match_score: float = 0.0
    workload_assessment: str = ""
    strengths: List[str] = []
    concerns: List[str] = []
    reasoning: str = ""

class MatchResult(BaseModel):
    employee: str
    match_details: MatchScore 