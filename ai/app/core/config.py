"""Configuration settings for the application."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """API settings."""
    
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Employee Matching API"
    VERSION: str = "1.0.0"
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    URL_INSIDER: Optional[str] = os.getenv("URL_INSIDER")
    URL_EMPINFO: Optional[str] = os.getenv("URL_EMPINFO")
    BEARER_TOKEN: Optional[str] = os.getenv("BEARER_TOKEN")
    
    # Logging
    LOG_LEVEL: str = "INFO"

settings = Settings() 