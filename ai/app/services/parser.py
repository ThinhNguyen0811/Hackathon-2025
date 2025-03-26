"""Service for parsing free-text project requirements."""

from typing import Dict, Any, List
import re
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ParsedProjectRequirement(BaseModel):
    """Parsed project requirements from free text."""

    title: str = Field(description="The title of the project")
    tech_stack: List[str] = Field(
        description="List of required technical skills/technologies"
    )
    domains: List[str] = Field(
        description="List of business domains relevant to the project"
    )
    required_level: str = Field(
        description="Required experience level (fresher, junior, intermediate, senior, principal)"
    )
    start_date: str = Field(description="Project start date in ISO format (YYYY-MM-DD)")


class RequirementsParserService:
    """Service for parsing project requirements from free text."""

    def __init__(self):
        """Initialize the parser service."""
        self.llm = ChatOpenAI(
            model="gpt-4o", temperature=0.1, api_key=settings.OPENAI_API_KEY
        )
        self.parser = PydanticOutputParser(pydantic_object=ParsedProjectRequirement)

    def parse_requirements(self, text: str) -> Dict[str, Any]:
        """Parse project requirements from free text."""
        try:
            logger.info("Parsing project requirements from free text")

            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are an expert project analyst who extracts structured information from 
                project requirement descriptions. 
                
                Extract the following information from the text:
                1. Project title - Come up with a concise, professional title if not explicitly stated
                2. Required technical skills/tech stack - List specific technologies, programming languages, frameworks
                3. Business domains - Extract business domains or sectors relevant to the project
                4. Required experience level - Determine the experience level (fresher, junior, intermediate, senior, principal)
                5. Project start date - Extract the start date or use the current date + 1 month if not specified
                
                Format the output as specified by the output parser.
                If certain information is missing, make reasonable assumptions based on the context.
                For missing start dates, use a date one month from today.""",
                    ),
                    ("human", "{text}"),
                    ("system", "Format the output as follows:\n{format_instructions}"),
                ]
            ).partial(format_instructions=self.parser.get_format_instructions())

            response = self.llm.invoke(prompt.format(text=text))

            # Parse the response
            parsed_req = self.parser.parse(response.content)

            # Convert to dictionary
            result = parsed_req.dict()

            # Format date if needed
            if result.get("start_date") and not re.match(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", result["start_date"]
            ):
                # If date doesn't have time component, add it
                if re.match(r"\d{4}-\d{2}-\d{2}", result["start_date"]):
                    result["start_date"] = f"{result['start_date']}T00:00:00"

            logger.info(f"Successfully parsed project requirements: {result}")
            return result

        except Exception as e:
            logger.error(f"Error parsing project requirements: {str(e)}")
            raise ValueError(f"Failed to parse project requirements: {str(e)}")
