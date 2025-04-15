#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Configuration Module

This module contains all configuration settings for the application.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Logging Configuration
# --------------------
# Enable/disable debug logging
DEBUG_LOGGING_ENABLED = True

# Log file settings
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "logs")
LOG_FILE = "roman_senate.log"

# Console output for logs
LOG_CONSOLE_OUTPUT = True

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = logging.DEBUG if DEBUG_LOGGING_ENABLED else logging.INFO

# Log rotation settings
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# LLM Provider Configuration
# -------------------------
# Which LLM provider to use: "openai" or "ollama"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # Force OpenAI as the default provider

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Development mode flag (set to False for production)
# This controls which GPT model is used by default
DEV_MODE = os.getenv("DEV_MODE", "False").lower() in ("true", "1", "t")  # Default to production mode for non-turbo GPT-4

# GPT Model configuration
GPT_MODEL_DEV = "gpt-4-turbo-preview"  # Faster model for development
GPT_MODEL_PROD = "gpt-4"               # Standard model for production (non-turbo GPT-4)

# Default OpenAI model based on environment - use GPT_MODEL_PROD (non-turbo) by default
DEFAULT_GPT_MODEL = GPT_MODEL_DEV if DEV_MODE else GPT_MODEL_PROD

# Ollama Configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b-instruct-v0.2-q4_K_M")
OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

# Configure model based on provider
if LLM_PROVIDER == "openai":
    LLM_MODEL = DEFAULT_GPT_MODEL
else:  # ollama
    LLM_MODEL = OLLAMA_MODEL

# Cache configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() in ("true", "1", "t")
CACHE_DURATION = int(os.getenv("CACHE_DURATION", "604800"))  # Default: 1 week in seconds

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "cache")

# Create directories if they don't exist
for directory in [LOG_DIR, DATA_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)