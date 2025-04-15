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

def get_llm_provider(provider_type: str = "ollama", **kwargs) -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider.
    
    Args:
        provider_type: Type of provider ("openai", "ollama", or "mock")
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        An LLM provider instance
    
    Raises:
        ValueError: If an unknown provider type is specified
    """
    # Check for test mode - if enabled, use the mock provider regardless of requested type
    test_mode = os.environ.get("ROMAN_SENATE_TEST_MODE", "").lower() == "true"
    
    if test_mode:
        logger.info("Test mode enabled, using MockProvider regardless of requested type")
        return MockProvider(**kwargs)
    
    logger.info(f"Creating LLM provider of type: {provider_type}")
    
    if provider_type.lower() == "openai":
        return OpenAIProvider(**kwargs)
    elif provider_type.lower() == "ollama":
        return OllamaProvider(**kwargs)
    elif provider_type.lower() == "mock":
        return MockProvider(**kwargs)
    else:
        error_msg = f"Unknown provider type: {provider_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)

def get_provider(**kwargs) -> LLMProvider:
    """
    Alias for get_llm_provider to maintain compatibility with code using get_provider.
    
    Args:
        **kwargs: Arguments to pass to get_llm_provider
        
    Returns:
        An LLM provider instance
    """
    # Import here to avoid circular imports
    from ..config import LLM_PROVIDER, LLM_MODEL
    
    logger.debug("Using get_provider() alias for get_llm_provider()")
    
    # If provider_type and model_name not explicitly provided, use config values
    if 'provider_type' not in kwargs:
        kwargs['provider_type'] = LLM_PROVIDER
    if 'model_name' not in kwargs:
        kwargs['model_name'] = LLM_MODEL
        
    return get_llm_provider(**kwargs)