#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
OpenAI LLM Provider Implementation

This module implements the LLM provider interface for OpenAI.
"""

import logging
from typing import Dict, List, Any, Optional
import openai
from .base import LLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """OpenAI-based LLM provider."""
    
    def __init__(self, model_name: str = "gpt-4", api_key: Optional[str] = None):
        self.model_name = model_name
        if api_key:
            openai.api_key = api_key
        logger.info(f"Initialized OpenAI provider with model: {model_name}")
    
    def generate_completion(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> str:
        """Generate text completion using OpenAI."""
        try:
            logger.debug(f"Generating completion with OpenAI model {self.model_name}")
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            generated_text = response.choices[0].message.content
            logger.debug(f"Generated {len(generated_text)} characters of text")
            return generated_text
        except Exception as e:
            logger.error(f"Error with OpenAI completion: {e}")
            return f"[Error generating text: {str(e)}]"
    
    def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion using OpenAI."""
        try:
            logger.debug(f"Generating chat completion with OpenAI model {self.model_name}")
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            # Return the raw response object which can be indexed as needed
            logger.debug("Successfully generated chat completion with OpenAI")
            return response
        except Exception as e:
            logger.error(f"Error with OpenAI chat completion: {e}")
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
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generates text based on a prompt asynchronously.
        
        Args:
            prompt: The text prompt to generate from
            **kwargs: Additional arguments for the generation
            
        Returns:
            Generated text response
        """
        logger.debug("Using async generate_text() with OpenAI provider")
        try:
            logger.debug(f"Generating async completion with OpenAI model {self.model_name}")
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 500),
                **{k:v for k,v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )
            generated_text = response.choices[0].message.content
            logger.debug(f"Generated {len(generated_text)} characters of text")
            return generated_text
        except Exception as e:
            logger.error(f"Error with OpenAI async completion: {e}")
            return f"[Error generating text: {str(e)}]"
        return self.generate_completion(prompt, **kwargs)