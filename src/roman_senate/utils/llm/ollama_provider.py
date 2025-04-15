#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Ollama LLM Provider Implementation

This module implements the LLM provider interface for Ollama.
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from .base import LLMProvider

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """Ollama-based LLM provider for local model inference."""
    
    def __init__(self, model_name: str = "mistral:7b-instruct-v0.2-q4_K_M", api_base: str = "http://localhost:11434"):
        self.model_name = model_name
        self.api_base = api_base
        self.generate_endpoint = f"{self.api_base}/api/generate"
        self.chat_endpoint = f"{self.api_base}/api/chat"
        logger.info(f"Initialized Ollama provider with model: {model_name}")
    
    def generate_completion(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> str:
        """Generate text completion using Ollama."""
        try:
            logger.debug(f"Generating completion with Ollama model {self.model_name}")
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            response = requests.post(
                self.generate_endpoint,
                json=payload
            )
            response.raise_for_status()
            
            # Ollama returns the full response
            result = response.json()
            generated_text = result.get("response", "")
            logger.debug(f"Generated {len(generated_text)} characters of text")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error with Ollama completion: {e}")
            return f"[Error generating text: {str(e)}]"
    
    def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion using Ollama."""
        try:
            logger.debug(f"Generating chat completion with Ollama model {self.model_name}")
            # Ollama expects messages in [{"role": "user", "content": "..."}] format
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_length": max_tokens,  # Ollama uses max_length instead of max_tokens
                **kwargs
            }
            
            response = requests.post(
                self.chat_endpoint,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Format response to match OpenAI structure for easier integration
            formatted_response = {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": result.get("message", {}).get("content", "")
                        },
                        "index": 0
                    }
                ],
                "model": self.model_name,
                "raw_response": result  # Include the raw response for debugging
            }
            
            logger.debug("Successfully generated chat completion with Ollama")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error with Ollama chat completion: {e}")
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
        logger.debug("Using async generate_text() with Ollama provider")
        try:
            logger.debug(f"Generating async completion with Ollama model {self.model_name}")
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 500)
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **{k:v for k,v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            }
            
            # Import here to avoid adding asyncio as a global dependency for non-async code
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.generate_endpoint, json=payload) as response:
                    response.raise_for_status()
                    result = await response.json()
                    generated_text = result.get("response", "")
                    logger.debug(f"Generated {len(generated_text)} characters of text")
                    return generated_text
                    
        except Exception as e:
            logger.error(f"Error with Ollama async completion: {e}")
            return f"[Error generating text: {str(e)}]"
        return self.generate_completion(prompt, **kwargs)