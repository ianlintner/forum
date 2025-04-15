#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Speech Generator Module

This module handles speech generation using the LLM provider abstraction.
"""

import logging
import time
from typing import Dict, List, Any, Optional

from ..utils.llm.factory import get_llm_provider
from ..utils.config import LLM_PROVIDER, LLM_MODEL

logger = logging.getLogger(__name__)

# Initialize the LLM provider based on configuration
llm_provider = get_llm_provider(
    provider_type=LLM_PROVIDER,
    model_name=LLM_MODEL
)

async def generate_speech_text(
    prompt: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
    **kwargs
) -> Optional[str]:
    """
    Generate speech text using the configured LLM provider.
    
    Args:
        prompt: The prompt to send to the LLM
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum number of tokens in response
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Generated text or None if generation failed
    """
    start_time = time.time()
    try:
        logger.info(f"Generating speech with {LLM_PROVIDER} provider")
        logger.debug(f"Using model: {LLM_MODEL}")
        
        # Use the provider's async generate_text method
        response_text = await llm_provider.generate_text(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Log generation time and text length
        generation_time = time.time() - start_time
        logger.info(f"Speech generated in {generation_time:.2f} seconds")
        logger.debug(f"Generated {len(response_text)} characters of text")
        
        return response_text
    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        generation_time = time.time() - start_time
        logger.info(f"Speech generation failed after {generation_time:.2f} seconds")
        return None

def generate_chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 500,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate a chat completion using the configured LLM provider.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        temperature: Controls randomness (0.0-1.0)
        max_tokens: Maximum number of tokens in response
        **kwargs: Additional provider-specific parameters
        
    Returns:
        Response object with choices containing messages
    """
    start_time = time.time()
    try:
        logger.info(f"Generating chat completion with {LLM_PROVIDER} provider")
        logger.debug(f"Using model: {LLM_MODEL}")
        
        # Use the provider abstraction
        response = llm_provider.generate_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Log generation time
        generation_time = time.time() - start_time
        logger.info(f"Chat completion generated in {generation_time:.2f} seconds")
        
        return response
    except Exception as e:
        logger.error(f"Error generating chat completion: {e}")
        generation_time = time.time() - start_time
        logger.info(f"Chat completion failed after {generation_time:.2f} seconds")
        
        # Return a minimal error response
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant", 
                        "content": f"[Error generating response: {str(e)}]"
                    },
                    "index": 0
                }
            ]
        }