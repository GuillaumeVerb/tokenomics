"""Logging configuration for the application."""
import logging
import sys
from typing import Any, Dict, Optional

from app.core.config import settings

# Create logger
logger = logging.getLogger("tokenomics")

# Set log level from settings
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(log_level)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)

# Create formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an error with optional context.
    
    Args:
        error: The exception to log
        context: Optional dictionary with additional context
    """
    if context:
        logger.error(f"{str(error)} - Context: {context}")
    else:
        logger.error(str(error))

def log_info(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an info message with optional context.
    
    Args:
        message: The message to log
        context: Optional dictionary with additional context
    """
    if context:
        logger.info(f"{message} - Context: {context}")
    else:
        logger.info(message)

def log_warning(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a warning message with optional context.
    
    Args:
        message: The message to log
        context: Optional dictionary with additional context
    """
    if context:
        logger.warning(f"{message} - Context: {context}")
    else:
        logger.warning(message)

def log_debug(message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log a debug message with optional context.
    
    Args:
        message: The message to log
        context: Optional dictionary with additional context
    """
    if context:
        logger.debug(f"{message} - Context: {context}")
    else:
        logger.debug(message) 