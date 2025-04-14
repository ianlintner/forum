#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Configuration Module

This module contains all configuration settings for the application.
"""

import os
import logging
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Configuration Module

This module handles configuration settings for the application,
including API keys and environment variables.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging Configuration
# --------------------
# Enable/disable debug logging
DEBUG_LOGGING_ENABLED = True

# Log file settings
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = "openai_debug.log"

# Console output for logs
LOG_CONSOLE_OUTPUT = True

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = logging.DEBUG if DEBUG_LOGGING_ENABLED else logging.INFO

# Log rotation settings
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Development mode flag (set to False for production)
# This controls which GPT model is used by default
DEV_MODE = os.getenv("DEV_MODE", "True").lower() in ("true", "1", "t")

# GPT Model configuration
# GPT-4 Turbo is faster but may have slightly different outputs than standard GPT-4
GPT_MODEL_DEV = "gpt-4-turbo-preview"  # Faster model for development
GPT_MODEL_PROD = "gpt-4"               # Standard model for production

# Default model based on environment
DEFAULT_GPT_MODEL = GPT_MODEL_DEV if DEV_MODE else GPT_MODEL_PROD

# Cache configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() in ("true", "1", "t")
CACHE_DURATION = int(os.getenv("CACHE_DURATION", "604800"))  # Default: 1 week in seconds