"""
Logging utilities for Monsoon Crop Predictor
"""

import logging
import logging.config
from pathlib import Path
from typing import Optional
from .config import Config


def setup_logging(
    log_level: str = "INFO", log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    config = Config.LOGGING_CONFIG.copy()

    # Update log level
    config["handlers"]["default"]["level"] = log_level
    config["loggers"][""]["level"] = log_level

    # Update log file if provided
    if log_file:
        config["handlers"]["file"]["filename"] = log_file

    logging.config.dictConfig(config)
    return logging.getLogger(__name__)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return logging.getLogger(self.__class__.__name__)
