from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from app.models.models import (
    Employee,
    ProjectRequirement,
    Skill,
    BusinessDomain,
    AdditionalSkill,
)
import logging
from collections import defaultdict

# Configure logging
logger = logging.getLogger(__name__)


class RequirementAnalysisSchema(BaseModel):
    """Schema for requirement analysis output."""

    technical_complexity: Dict = Field(
        description="Technical complexity details including frontend, backend, and other aspects"
    )
    domain_knowledge_requirements: List[Dict] = Field(
        description="List of required domain knowledge areas with details"
    )
    required_experience_level: str = Field(
        description="Required experience level for the project"
    )
    team_composition_needs: Dict = Field(
        description="Details about team composition including roles and their requirements"
    )
    recommended_team_size: Dict = Field(
        description="Recommended team size breakdown by role"
    )


class EmployeeAnalysisSchema(BaseModel):
    employee_name: str = Field(..., description="Name of the employee")
    technical_skills: Dict[str, List[str]] = Field(
        ..., description="Technical skills by level (advanced, intermediate, beginner)"
    )
    domain_expertise: Dict[str, List[str]] = Field(
        ..., description="Domain expertise (primary and secondary domains)"
    )
    experience_level: str = Field(
        ..., description="Current experience level (senior|intermediate|junior|fresher)"
    )
    key_strengths: List[str] = Field(..., description="Key strengths of the employee")
    development_areas: List[str] = Field(..., description="Areas for development")


class MatchEvaluationSchema(BaseModel):
    technical_fit: float = Field(..., description="Technical skills match score (0-1)")
    domain_match: float = Field(..., description="Domain expertise match score (0-1)")
    experience_match: float = Field(
        ..., description="Experience level match score (0-1)"
    )
    workload_compatibility: float = Field(
        ..., description="Workload compatibility score (0-1)"
    )
    overall_score: float = Field(..., description="Overall match score (0-1)")
    reasoning: str = Field(
        ..., description="Detailed reasoning for the match evaluation"
    )
    team_fit: Dict[str, float] = Field(
        ..., description="Assessment of how well the employee would fit in a team"
    )


class EmployeeRecommendation(BaseModel):
    employee_name: str = Field(..., description="Name of the recommended employee")
    match_score: float = Field(..., description="Overall match score")
    technical_fit: float = Field(..., description="Technical skills match score (0-1)")
    domain_match: float = Field(..., description="Domain expertise match score (0-1)")
    experience_match: float = Field(
        ..., description="Experience level match score (0-1)"
    )
    workload_compatibility: float = Field(
        ..., description="Workload compatibility score (0-1)"
    )
    current_workload: Dict[str, int] = Field(
        ..., description="Current workload details"
    )
    available_hours: int = Field(..., description="Available hours per week")
    key_strengths: List[str] = Field(..., description="Key strengths of the employee")
    potential_concerns: List[str] = Field(
        ..., description="Potential concerns or limitations"
    )
    detailed_reasoning: str = Field(
        ..., description="Detailed reasoning for the recommendation"
    )


class WorkloadOptimizationSchema(BaseModel):
    recommended_employees: List[EmployeeRecommendation] = Field(
        ..., description="List of recommended employees"
    )
    selection_criteria: Dict[str, str] = Field(
        ..., description="Criteria to consider when selecting an employee"
    )
    recommendation_summary: str = Field(
        ..., description="High-level summary of the recommendations"
    )


class RequirementAnalyzer:
    """Analyzes project requirements to determine key aspects and needs."""

    def analyze_requirement(self, requirement: ProjectRequirement) -> Dict:
        """Analyze a project requirement and return structured insights."""
        # Direct analysis without LLM
        return {
            "technical_complexity": {
                "frontend": {
                    "description": "Frontend technical requirements",
                    "requirements": [
                        skill
                        for skill in requirement.required_skills.tech_stack
                        if skill in ["React", "Angular", "JavaScript", "Vue"]
                    ],
                },
                "backend": {
                    "description": "Backend technical requirements",
                    "requirements": [
                        skill
                        for skill in requirement.required_skills.tech_stack
                        if skill in [".NET", "Java", "Python", "Node.js"]
                    ],
                },
            },
            "domain_knowledge_requirements": [
                {
                    "domain": domain,
                    "requirements": ["Domain expertise required"],
                    "importance": "high",
                }
                for domain in requirement.required_skills.domains
            ],
            "required_experience_level": requirement.required_level,
            "team_composition_needs": {
                "roles": ["Developer"],
                "skills": requirement.required_skills.tech_stack,
                "experience_distribution": {
                    "senior": "1-2",
                    "mid": "2-3",
                    "junior": "1-2",
                },
            },
            "recommended_team_size": {
                "total": "4-7",
                "breakdown": {
                    "frontend": "2-3",
                    "backend": "2-3",
                    "other_roles": "0-1",
                },
            },
        }


class EmployeeAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.parser = JsonOutputParser()

        self.analysis_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert at analyzing employee profiles.
            Analyze the provided employee profiles and extract key information about their skills,
            experience level, and domain expertise.
            
            For each employee, return a JSON object with this structure:
            {{
                "employee_name": "string",
                "technical_skills": {{
                    "advanced": ["skill1", "skill2"],
                    "intermediate": ["skill3", "skill4"],
                    "beginner": ["skill5", "skill6"]
                }},
                "domain_expertise": {{
                    "primary_domains": ["domain1", "domain2"],
                    "secondary_domains": ["domain3", "domain4"]
                }},
                "experience_level": "senior|intermediate|junior|fresher",
                "key_strengths": ["strength1", "strength2"],
                "development_areas": ["area1", "area2"]
            }}
            
            Return an array of these objects, one for each employee profile provided.
            """,
                ),
                ("human", "{employee_profile}"),
            ]
        )

        self.chain = self.analysis_prompt | self.llm | self.parser

    def analyze_employee(self, employee: Employee) -> Dict:
        """Analyze an employee's profile."""
        try:
            # Skip employees with invalid primary skills only
            if not employee.skills or any(
                not skill.skillName or skill.skillName.lower() == "none"
                for skill in employee.skills
            ):
                logger.info(
                    f"Skipping employee {employee.empCode} due to invalid primary skills"
                )
                return None

            # Format employee profile with validation
            profile = self._format_employee_profile(employee)
            if not profile:
                logger.info(
                    f"Skipping employee {employee.empCode} due to insufficient profile data"
                )
                return None

            # Get analysis from LLM
            result = self.chain.invoke({"employee_profile": profile})

            return result

        except Exception as e:
            logger.error(f"Error analyzing employee {employee.empCode}: {str(e)}")
            # Return a basic analysis based on available data
            return self._fallback_analysis(employee)

    def _format_employee_profile(self, employee: Employee) -> str:
        """Format employee profile with validation."""
        try:
            # Validate and format skills
            skills_str = self._format_skills(employee.skills)
            if skills_str == "No skills information available":
                return None

            # Validate and format domains
            domains_str = self._format_domains(employee.businessDomains)

            # Format additional skills (optional)
            additional_skills_str = self._format_additional_skills(
                employee.additionalSkills
            )

            # Construct profile
            profile = f"""
            Employee Code: {employee.empCode}
            
            Technical Skills:
            {skills_str}
            
            Business Domains:
            {domains_str}
            
            Additional Skills:
            {additional_skills_str}
            """

            return profile

        except Exception as e:
            logger.error(
                f"Error formatting employee profile for {employee.empCode}: {str(e)}"
            )
            return None

    def _format_skills(self, skills: List[Skill]) -> str:
        """Format skills for display with validation."""
        try:
            if not skills:
                return "No skills information available"

            # Filter out None or empty skills
            valid_skills = [
                skill
                for skill in skills
                if skill.skillName and skill.skillName.lower() != "none" and skill.level
            ]

            if not valid_skills:
                return "No skills information available"

            skill_levels = defaultdict(list)
            for skill in valid_skills:
                skill_levels[skill.level.lower()].append(skill.skillName)

            formatted_skills = []
            for level in ["advanced", "intermediate", "beginner"]:
                if skill_levels[level]:
                    formatted_skills.append(
                        f"- {level.capitalize()}: {', '.join(skill_levels[level])}"
                    )

            return (
                "\n".join(formatted_skills)
                if formatted_skills
                else "No skills information available"
            )

        except Exception as e:
            logger.error(f"Error formatting skills: {str(e)}")
            return "No skills information available"

    def _format_domains(self, domains: List[BusinessDomain]) -> str:
        """Format business domains for display (optional)."""
        try:
            if not domains:
                return "No domain information available"

            # Include all domains, even if they are "none"
            return "\n".join(
                f"- {domain.businessDomainName}"
                for domain in domains
                if domain.businessDomainName
            )

        except Exception as e:
            logger.error(f"Error formatting domains: {str(e)}")
            return "No domain information available"

    def _format_additional_skills(self, skills: List[AdditionalSkill]) -> str:
        """Format additional skills for display (optional)."""
        try:
            if not skills:
                return "No additional skills information available"

            # Include all additional skills, even if they are "none"
            return "\n".join(
                f"- {skill.additionalSkillName}"
                for skill in skills
                if skill.additionalSkillName
            )

        except Exception as e:
            logger.error(f"Error formatting additional skills: {str(e)}")
            return "No additional skills information available"

    def _fallback_analysis(self, employee: Employee) -> Dict:
        """Create a basic analysis when LLM fails."""
        try:
            # Group skills by level
            skill_levels = defaultdict(list)
            for skill in employee.skills:
                skill_levels[skill.level.lower()].append(skill.skillName)

            # Get domains
            domains = [domain.businessDomainName for domain in employee.businessDomains]

            # Determine experience level based on skill distribution
            if len(skill_levels.get("advanced", [])) > 2:
                exp_level = "senior"
            elif len(skill_levels.get("intermediate", [])) > 2:
                exp_level = "intermediate"
            else:
                exp_level = "junior"

            return {
                "employee_name": employee.empCode,
                "technical_skills": {
                    "advanced": skill_levels.get("advanced", []),
                    "intermediate": skill_levels.get("intermediate", []),
                    "beginner": skill_levels.get("beginner", []),
                },
                "domain_expertise": {
                    "primary_domains": domains[:2],
                    "secondary_domains": domains[2:],
                },
                "experience_level": exp_level,
                "key_strengths": [
                    f"Has {len(skill_levels.get('advanced', []))} advanced skills",
                    f"Experience in {len(domains)} business domains",
                ],
                "development_areas": [],
            }

        except Exception as e:
            logger.error(f"Error in fallback analysis for {employee.empCode}: {str(e)}")
            return {
                "employee_name": employee.empCode,
                "technical_skills": {
                    "advanced": [],
                    "intermediate": [],
                    "beginner": [],
                },
                "domain_expertise": {"primary_domains": [], "secondary_domains": []},
                "experience_level": "junior",
                "key_strengths": [],
                "development_areas": [],
            }

    def analyze_employees(self, employees: List[Employee]) -> List[Dict]:
        """Analyze all employees in a single batch."""
        try:
            # Skip employees with invalid primary skills
            valid_employees = []
            for employee in employees:
                if not employee.skills or any(
                    not skill.skillName or skill.skillName.lower() == "none"
                    for skill in employee.skills
                ):
                    logger.info(
                        f"Skipping employee {employee.empCode} due to invalid primary skills"
                    )
                    continue
                valid_employees.append(employee)

            if not valid_employees:
                logger.warning("No valid employees to analyze")
                return []

            # Format all employee profiles at once
            profiles = []
            employee_additional_skills = {}  # Store additional skills for each employee

            for employee in valid_employees:
                profile = self._format_employee_profile(employee)
                if profile:
                    # Extract additional skills
                    additional_skills = [
                        skill.additionalSkillName
                        for skill in employee.additionalSkills
                        if skill.additionalSkillName
                        and skill.additionalSkillName.lower() != "none"
                    ]
                    employee_additional_skills[employee.empCode] = additional_skills

                    profiles.append(
                        {"employee_code": employee.empCode, "profile": profile}
                    )

            if not profiles:
                logger.warning("No valid profiles to analyze")
                return []

            # Combine all profiles into a single prompt
            combined_profiles = (
                "\n\n=== EMPLOYEE PROFILES ===\n\n"
                + "\n\n---\n\n".join(
                    f"Employee: {p['employee_code']}\n{p['profile']}" for p in profiles
                )
            )

            # Get analysis from LLM for all employees at once
            result = self.chain.invoke({"employee_profile": combined_profiles})

            # Ensure result is a list
            analyses = result if isinstance(result, list) else [result]

            # Format analyses to match expected structure
            formatted_analyses = []
            for analysis in analyses:
                employee_code = analysis.get("employee_name", "")

                formatted_analysis = {
                    "employee_name": employee_code,
                    "technical_skills": {
                        "advanced": analysis.get("technical_skills", {}).get(
                            "advanced", []
                        ),
                        "intermediate": analysis.get("technical_skills", {}).get(
                            "intermediate", []
                        ),
                        "beginner": analysis.get("technical_skills", {}).get(
                            "beginner", []
                        ),
                    },
                    "domain_expertise": {
                        "primary_domains": analysis.get("domain_expertise", {}).get(
                            "primary_domains", []
                        ),
                        "secondary_domains": analysis.get("domain_expertise", {}).get(
                            "secondary_domains", []
                        ),
                    },
                    "experience_level": analysis.get("experience_level", "junior"),
                    "key_strengths": analysis.get("key_strengths", []),
                    "development_areas": analysis.get("development_areas", []),
                    # Include additional skills from our dictionary
                    "additional_skills": employee_additional_skills.get(
                        employee_code, []
                    ),
                }
                formatted_analyses.append(formatted_analysis)

            return formatted_analyses

        except Exception as e:
            logger.error(f"Error in batch employee analysis: {str(e)}")
            return []


class MatchingAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)
        self.parser = JsonOutputParser()

        self.matching_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an expert at evaluating employee matches for projects.
            Analyze the provided employee profiles and project requirements to determine the best matches.
            Consider all skills (both primary technical skills and additional skills), domain expertise, and experience level.
            
            For each employee, provide:
            1. Match score (0-1) - Overall suitability for the project
            2. Skill fit score (0-1) - How well their skills match project requirements
            3. Domain match score (0-1) - How well their domain expertise aligns with project domains
            4. Experience match score (0-1) - How appropriate their experience level is for the project
            5. Key strengths - Specific advantages this employee brings
            6. Potential concerns - Potential challenges or gaps
            7. Brief reasoning - Explanation for your ratings
            
            IMPORTANT GUIDELINES FOR SCORING:
            - For skill matching (45% of overall score): Consider skill relevance, related skills, and transferrable knowledge
            - For experience level (40% of overall score): Compare to the required level
            - For domain matching (15% of overall score): Use binary scoring only:
              * Score of 0 when there is NO EXACT MATCH with any of the required domains
              * Score between 0.7-1.0 ONLY when there is direct experience in at least one of the required domains
              * DO NOT give partial scores for related or adjacent domains
            
            Calculate the overall match score using these weights:
            match_score = (skill_fit * 0.45) + (experience_match * 0.4) + (domain_match * 0.15)
            
            Ensure your scores are consistent with your listed strengths and concerns. If you note a concern about
            lack of domain experience, the domain match score MUST be 0.
            
            Return a JSON object with this structure:
            {{
                "matches": [
                    {{
                        "employee": "employee_code",
                        "match_score": 0.85,
                        "skill_fit": 0.9,
                        "domain_match": 0.8,
                        "experience_match": 0.85,
                        "strengths": ["strength1", "strength2"],
                        "concerns": ["concern1", "concern2"],
                        "reasoning": "brief explanation"
                    }}
                ]
            }}""",
                ),
                (
                    "human",
                    """Project Requirements:
            {project_requirements}
            
            Available Employees (already filtered for availability):
            {employee_analyses}""",
                ),
            ]
        )

        self.chain = self.matching_prompt | self.llm | self.parser

    def evaluate_matches(
        self,
        employee_analyses: List[Dict],
        requirement_analysis: Dict,
        project_requirement: ProjectRequirement,
    ) -> List[Dict]:
        """Evaluate all available employees at once using LLM."""
        try:
            # Format project requirements
            project_info = f"""
            Title: {project_requirement.title}
            Required Level: {project_requirement.required_level}
            Required Skills: {', '.join(project_requirement.required_skills.tech_stack)}
            Required Domains: {', '.join(project_requirement.required_skills.domains)}
            Start Date: {project_requirement.start_date}
            """

            # Format employee analyses
            employee_info = []
            for analysis in employee_analyses:
                all_skills = []
                # Add all technical skills
                for level, skills in analysis["technical_skills"].items():
                    if skills:
                        all_skills.append(f"{level.capitalize()}: {', '.join(skills)}")

                # Add additional skills
                if analysis["additional_skills"]:
                    all_skills.append(
                        f"Additional: {', '.join(analysis['additional_skills'])}"
                    )

                emp_info = f"""
                Employee: {analysis['employee_name']}
                Skills: {' | '.join(all_skills)}
                Domain Expertise: {', '.join(analysis['domain_expertise']['primary_domains'])}
                Experience Level: {analysis['experience_level']}
                Key Strengths: {', '.join(analysis['key_strengths'])}
                """
                employee_info.append(emp_info)

            logger.info(
                f"Sending {len(employee_analyses)} employees to LLM for evaluation"
            )

            # Get matches from LLM
            result = self.chain.invoke(
                {
                    "project_requirements": project_info,
                    "employee_analyses": "\n".join(employee_info),
                }
            )

            logger.info(f"LLM returned {len(result.get('matches', []))} matches")

            # Process and format the results
            matches = []
            for match in result.get("matches", []):
                # Debug logging to check the calculated match_score value
                try:
                    employee_name = match.get("employee", "Unknown")
                    skill_fit = match.get("skill_fit", 0)
                    domain_match = match.get("domain_match", 0)
                    exp_match = match.get("experience_match", 0)
                    llm_match_score = match.get("match_score", 0)

                    # Recalculate based on our formula for comparison
                    calculated_score = (
                        skill_fit * 0.45 + exp_match * 0.4 + domain_match * 0.15
                    )

                    logger.debug(
                        f"LLM Match for {employee_name}: skill={skill_fit:.2f}, exp={exp_match:.2f}, domain={domain_match:.2f}"
                    )
                    logger.debug(
                        f"Scores: LLM={llm_match_score:.2f}, Calculated={calculated_score:.2f}"
                    )

                    # Use the calculated score instead of the LLM-provided score
                    match_score = calculated_score

                    formatted_match = {
                        "employee": employee_name,
                        "match_details": {
                            "match_score": match_score,
                            "skill_fit": skill_fit,
                            "domain_match": domain_match,
                            "experience_match": exp_match,
                            "strengths": match.get("strengths", []),
                            "concerns": match.get("concerns", []),
                            "reasoning": match.get("reasoning", ""),
                            "workload_assessment": "Available at project start date",
                        },
                    }
                    matches.append(formatted_match)
                except Exception as e:
                    logger.error(f"Error processing match: {str(e)}")
                    continue

            return matches

        except Exception as e:
            logger.error(f"Error in LLM-based matching: {str(e)}")
            logger.warning("Falling back to direct calculation for matching")
            return self._fallback_evaluate_matches(
                employee_analyses, project_requirement
            )

    def _fallback_evaluate_matches(
        self, employee_analyses: List[Dict], project_requirement: ProjectRequirement
    ) -> List[Dict]:
        """Fallback method using direct calculation if LLM fails."""
        logger.info("Using fallback calculation for matching")
        matches = []
        for analysis in employee_analyses:
            try:
                # Extract required skills and domains
                required_skills = set(project_requirement.required_skills.tech_stack)
                required_domains = set(project_requirement.required_skills.domains)

                # Extract all employee skills (primary + additional)
                employee_skills = set()
                # Add primary skills from all levels
                for level in ["advanced", "intermediate", "beginner"]:
                    employee_skills.update(analysis["technical_skills"][level])
                # Add additional skills
                employee_skills.update(analysis["additional_skills"])

                employee_domains = set(analysis["domain_expertise"]["primary_domains"])

                # Calculate skill match score
                skill_match = (
                    len(required_skills & employee_skills) / len(required_skills)
                    if required_skills
                    else 1.0
                )

                # Calculate domain match score - binary scoring
                matching_domains = required_domains & employee_domains
                # If there's at least one exact match, calculate proportion, otherwise 0
                if matching_domains:
                    domain_match = len(matching_domains) / len(required_domains)
                else:
                    domain_match = 0.0

                # Calculate experience match
                exp_levels = {
                    "senior": 1.0,
                    "intermediate": 0.7,
                    "junior": 0.4,
                    "fresher": 0.2,
                }
                exp_match = exp_levels.get(analysis["experience_level"].lower(), 0.5)

                # Calculate overall match score with updated weights
                # Skill: 45%, Experience: 40%, Domain: 15%
                match_score = skill_match * 0.45 + exp_match * 0.4 + domain_match * 0.15

                # Debug log for this specific issue
                logger.debug(
                    f"Match calculation for {analysis['employee_name']}: skill={skill_match:.2f}, exp={exp_match:.2f}, domain={domain_match:.2f}, total={match_score:.2f}"
                )

                # Prepare concerns list based on scores
                concerns = []
                if domain_match == 0:
                    concerns.append(
                        f"No domain expertise in {', '.join(required_domains)}"
                    )
                if exp_match == 0:
                    concerns.append(
                        "Experience level not aligned with project requirements"
                    )
                if skill_match < 0.5:
                    concerns.append(f"Limited skill match with required technologies")

                matches.append(
                    {
                        "employee": analysis["employee_name"],
                        "match_details": {
                            "match_score": match_score,
                            "skill_fit": skill_match,
                            "domain_match": domain_match,
                            "experience_match": exp_match,
                            "strengths": [
                                f"Skill match: {skill_match:.0%}",
                                f"Domain match: {domain_match:.0%}",
                                f"Experience match: {exp_match:.0%}",
                            ],
                            "concerns": concerns,
                            "reasoning": "Score based on direct skill and domain matching (fallback calculation)",
                            "workload_assessment": "Available at project start date",
                        },
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error in fallback matching for {analysis.get('employee_name', 'unknown')}: {str(e)}"
                )
                continue

        return sorted(
            matches, key=lambda x: x["match_details"]["match_score"], reverse=True
        )


class WorkloadOptimizer:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

    def optimize_workload(self, matches: List[Dict]) -> Dict:
        """Optimize workload distribution for project matches."""
        logger.info(f"Optimizing workload for {len(matches)} matches")

        # Sort matches by match score
        sorted_matches = sorted(
            matches,
            key=lambda x: (
                x["match_details"]["match_score"] if "match_details" in x else 0
            ),
            reverse=True,
        )

        # Filter matches based on minimum score threshold (40%)
        min_score_threshold = 0.4
        qualified_matches = [
            match
            for match in sorted_matches
            if match["match_details"]["match_score"] >= min_score_threshold
        ]

        logger.info(f"Found {len(qualified_matches)} matches with score >= 40%")

        # Format matches for output
        recommended_employees = []
        for match in qualified_matches:
            match_details = match["match_details"]

            # Transform to output format
            recommendation = {
                "employee": match["employee"],
                "overall_match_score": match_details["match_score"],
                "detailed_scoring_breakdown": {
                    "skill_fit": match_details["skill_fit"],
                    "domain_expertise_alignment": match_details["domain_match"],
                    "experience_level_appropriateness": match_details[
                        "experience_match"
                    ],
                },
                "key_strengths_and_relevant_experience": match_details["strengths"],
                "potential_concerns_or_limitations": match_details["concerns"],
                "workload_compatibility_assessment": match_details.get(
                    "workload_assessment", ""
                ),
            }
            recommended_employees.append(recommendation)

        # Create final recommendation
        result = {
            "recommended_employees": recommended_employees,
            "selection_criteria": [
                "Skill fit",
                "Domain expertise alignment",
                "Experience level appropriateness",
                "Workload compatibility",
            ],
            "recommendation_summary": f"Selected {len(recommended_employees)} candidates with match scores of 40% or higher based on skill match, domain expertise, and experience level.",
        }

        return result
