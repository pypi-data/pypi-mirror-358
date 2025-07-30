"""
Robutler - API client and tools for the Robutler ecosystem
"""

import logging
import os

from .server import Server

__version__ = "0.1.0" 

__all__ = ["Server"]

# Configure logging for the robutler package
def setup_logging(level=None):
    """
    Set up logging for the robutler package.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses LOG_LEVEL environment variable or INFO
    """
    if level is None:
        level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level, logging.INFO)
    
    # Configure the robutler logger
    logger = logging.getLogger('robutler')
    logger.setLevel(numeric_level)
    
    # Only add handler if none exists to avoid duplicates
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Set up default logging
setup_logging() 