#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for Roman Senate logging functionality
"""

import os
import sys

# Add the project root to Python path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from src.roman_senate.utils import setup_logging

# Test the logging functionality with different options
def main():
    # Test default logging
    logger = setup_logging()
    logger.info("Default logging test")
    logger.debug("This debug message should be visible in the log file but may not show in console")
    
    # Test with verbose flag
    verbose_logger = setup_logging(verbose=True)
    verbose_logger.debug("This debug message should be visible with verbose flag")
    
    # Test with custom log level
    info_logger = setup_logging(log_level="INFO")
    info_logger.info("Custom log level (INFO) test")
    
    # Test with custom log file
    custom_file_logger = setup_logging(log_file="custom_test.log")
    custom_file_logger.info("Custom log file test")
    
    print("Logging tests complete. Check the logs directory for output files.")

if __name__ == "__main__":
    main()