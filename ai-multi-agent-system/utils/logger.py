"""
Logger Utility
Centralized logging configuration
"""
import sys
from loguru import logger
from config.settings import settings


def setup_logger():
    """Configure the application logger"""
    # Remove default logger
    logger.remove()
    
    # Add console handler with formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.app.log_level,
        colorize=True
    )
    
    # Add file handler
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        rotation="500 MB",
        retention="10 days",
        level=settings.app.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    return logger


def get_logger(name: str = None):
    """
    Get a logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    if name:
        return logger.bind(name=name)
    return logger


# Initialize logger on import
setup_logger()
