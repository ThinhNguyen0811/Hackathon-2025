"""Project domain models."""
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import List


class ExperienceLevel(str, Enum):
    """Experience level enum."""
    FRESHER = "fresher"
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    PRINCIPAL = "principal"


class WorkloadType(str, Enum):
    """Workload type enum."""
    FULLTIME = "fulltime"
    PARTTIME = "parttime"
    SUPPORT = "support"


@dataclass
class Skills:
    """Skills model for project requirements."""
    tech_stack: List[str]
    domains: List[str]


@dataclass
class ProjectRequirement:
    """Project requirement domain model."""
    title: str
    required_skills: Skills
    required_level: ExperienceLevel
    start_date: datetime 