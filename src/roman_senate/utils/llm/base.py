#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
LLM Provider Base Class

This module defines the base abstract class for LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    @abstractmethod
    def generate_completion(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> str:
        """Generate text completion for the given prompt."""
        pass
    
    @abstractmethod
    def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 500,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion for the given messages."""
        pass
        
    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generates text based on a prompt.
        
        Args:
            prompt: The text prompt to generate from
            **kwargs: Additional arguments for the generation
            
        Returns:
            Generated text response
        """
        pass