#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
LLM Provider Factory

This module provides a factory function to get the appropriate LLM provider.
"""

import logging
import os
from typing import Optional, Dict, Any
from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider
from .mock_provider import MockProvider

logger = logging.getLogger(__name__)

def get_llm_provider(provider_type: str = "openai", task_type: str = None, **kwargs) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Args:
        provider_type: Type of provider ("openai", "ollama", or "mock")
        task_type: Type of task ("speech", "reasoning", "simple", or None for default)
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        An LLM provider instance
    
    Raises:
        ValueError: If an unknown provider type is specified
    """
    # Check for explicit provider choices from environment variables
    mock_provider = os.environ.get("ROMAN_SENATE_MOCK_PROVIDER", "").lower() == "true"
    test_mode = os.environ.get("ROMAN_SENATE_TEST_MODE", "").lower() == "true"
    
    # If ROMAN_SENATE_MOCK_PROVIDER is explicitly set, it takes precedence
    if mock_provider:
        logger.info("Mock provider explicitly requested via environment variable")
        return MockProvider(**kwargs)
    
    # If we're in test mode and no explicit provider choice was made, use mock by default
    if test_mode and os.environ.get("ROMAN_SENATE_MOCK_PROVIDER", "").lower() != "false":
        logger.info("Test mode enabled, using MockProvider as default for tests")
        return MockProvider(**kwargs)
    
    logger.info(f"Creating LLM provider of type: {provider_type}" + (f" for task: {task_type}" if task_type else ""))
    
    if provider_type.lower() == "openai":
        # Import here to avoid circular imports
        from ..config import (
            OPENAI_API_KEY, GPT_MODEL_TIER_SPEECH,
            GPT_MODEL_TIER_REASONING, GPT_MODEL_TIER_SIMPLE
        )
        
        # Select model based on task type if not explicitly specified
        if 'model_name' not in kwargs and task_type:
            if task_type.lower() == 'speech':
                kwargs['model_name'] = GPT_MODEL_TIER_SPEECH
                logger.info(f"Using speech-tier model: {GPT_MODEL_TIER_SPEECH}")
            elif task_type.lower() == 'reasoning':
                kwargs['model_name'] = GPT_MODEL_TIER_REASONING
                logger.info(f"Using reasoning-tier model: {GPT_MODEL_TIER_REASONING}")
            elif task_type.lower() == 'simple':
                kwargs['model_name'] = GPT_MODEL_TIER_SIMPLE
                logger.info(f"Using simple-tier model: {GPT_MODEL_TIER_SIMPLE}")
        
        # Pass the API key if it's not already in kwargs
        if 'api_key' not in kwargs and OPENAI_API_KEY:
            kwargs['api_key'] = OPENAI_API_KEY
        
        return OpenAIProvider(**kwargs)
    elif provider_type.lower() == "ollama":
        return OllamaProvider(**kwargs)
    elif provider_type.lower() == "mock":
        return MockProvider(**kwargs)
    else:
        error_msg = f"Unknown provider type: {provider_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def get_provider(task_type: str = None, **kwargs) -> LLMProvider:
    """
    Alias for get_llm_provider to maintain compatibility with code using get_provider.
    
    Args:
        task_type: Type of task ("speech", "reasoning", "simple", or None for default)
        **kwargs: Arguments to pass to get_llm_provider
        
    Returns:
        An LLM provider instance
    """
    # Import here to avoid circular imports
    from ..config import LLM_PROVIDER, LLM_MODEL
    
    logger.debug(f"Using get_provider() alias for get_llm_provider()" + (f" with task_type: {task_type}" if task_type else ""))
    
    # If provider_type and model_name not explicitly provided, use config values
    if 'provider_type' not in kwargs:
        kwargs['provider_type'] = LLM_PROVIDER
    if 'model_name' not in kwargs and task_type is None:
        kwargs['model_name'] = LLM_MODEL
    
    # Pass the task_type to get_llm_provider
    return get_llm_provider(task_type=task_type, **kwargs)