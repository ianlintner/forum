"""
Logging utilities for the Roman Senate application.

This module provides a configurable logging system with both file and console handlers.
Log files are timestamped and stored in a logs directory.
"""

import os
import sys
import logging
import datetime
from pathlib import Path


def setup_logging(
    log_level=None, 
    log_file=None, 
    verbose=False, 
    console=True
):
    """
    Configure the logging system with both file and console handlers.
    
    Args:
        log_level (str, optional): The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str, optional): Path to log file. If None, generates a timestamped file.
        verbose (bool, optional): If True, sets log level to DEBUG regardless of log_level param
        console (bool, optional): Whether to log to console as well as file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Determine log level
    if verbose:
        level = logging.DEBUG
    elif log_level:
        level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        # Handle both string and OptionInfo object cases
        if hasattr(log_level, 'upper'):
            log_level_str = log_level.upper()
        else:
            # Convert to string if it's another type (like OptionInfo object)
            log_level_str = str(log_level).upper()
        level = level_mapping.get(log_level_str, logging.INFO)
    else:
        level = logging.INFO
    
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).resolve().parent.parent.parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Generate timestamped log filename if not provided
    if not log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = logs_dir / f"run.{timestamp}.log"
    else:
        # Convert to string if it's not a string (like OptionInfo object)
        if not isinstance(log_file, (str, bytes, os.PathLike)):
            log_file = str(log_file)
            
        # If the log_file is just a filename (no path), put it in the logs directory
        if not os.path.dirname(log_file):
            log_file = logs_dir / log_file
        else:
            # If the log_file includes a path, make sure it exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create a formatter with timestamp, level, and source info
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)s | %(message)s', 
                                 '%Y-%m-%d %H:%M:%S')
    
    # Add file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Add console handler if requested
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    
    # Log initialization info
    logger.info(f"Logging initialized - Level: {logging.getLevelName(level)}, File: {log_file}")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Working directory: {os.getcwd()}")
    
    return logger


def get_logger(name=None):
    """
    Get a logger for the specified module.
    
    Args:
        name (str, optional): Logger name. If None, returns the root logger.
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)