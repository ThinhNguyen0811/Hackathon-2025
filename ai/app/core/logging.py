"""Logging configuration for the application."""
import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    """Set up logging configurations."""
    log_level = getattr(logging, settings.LOG_LEVEL)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # Set specific loggers to different levels if needed
    # For example, suppress noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logging.info("Logging setup complete")

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name) 