
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game - Test Fixtures
This module contains shared fixtures for all tests.
"""

import pytest
from unittest.mock import MagicMock, patch
import asyncio
from typing import Dict, List, Any

from roman_senate.utils.llm.base import LLMProvider
from roman_senate.utils.llm.openai_provider import OpenAIProvider
from roman_senate.utils.llm.ollama_provider import OllamaProvider


# --- General Fixtures ---

@pytest.fixture
def sample_senator():
    """Return a sample senator dictionary for testing."""
    return {
        "id": 1,
        "name": "Marcus Tullius Cicero",
        "faction": "Optimates",
        "traits": {
            "eloquence": 0.9,
            "intellect": 0.8,
            "ambition": 0.7,
            "honor": 0.8,
            "courage": 0.6,
            "pragmatism": 0.7
        }
    }


@pytest.fixture
def sample_topic():
    """Return a sample debate topic."""
    return {
        "text": "Funding for the new aqueduct in Rome",
        "category": "Public projects"
    }


# --- LLM Provider Fixtures ---

@pytest.fixture
def mock_openai_response():
    """Mock response from OpenAI API."""
    return MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="Mocked OpenAI response content"
                )
            )
        ]
    )


@pytest.fixture
def mock_ollama_response():
    """Mock response from Ollama API."""
    return {
        "model": "mistral:7b-instruct-v0.2-q4_K_M",
        "response": "Mocked Ollama response content",
        "done": True
    }


@pytest.fixture
def mock_openai_provider(mock_openai_response):
    """Create a mocked OpenAI provider that doesn't make actual API calls."""
    with patch('openai.chat.completions.create') as mock_create:
        mock_create.return_value = mock_openai_response
        
        # Setup for async generate_text
        async def mock_async_generate(*args, **kwargs):
            return mock_openai_response.choices[0].message.content
            
        provider = OpenAIProvider(model_name="gpt-4", api_key="mock-key")
        provider.generate_text = mock_async_generate
        
        yield provider


@pytest.fixture
def mock_ollama_provider(mock_ollama_response):
    """Create a mocked Ollama provider that doesn't make actual API calls."""
    with patch('requests.post') as mock_post:
        mock_post.return_value = MagicMock(
            raise_for_status=MagicMock(),
            json=MagicMock(return_value=mock_ollama_response)
        )
        
        # Setup for async generate_text
        async def mock_async_generate(*args, **kwargs):
            return mock_ollama_response["response"]
            
        # Create the provider
        provider = OllamaProvider(model_name="mistral:7b", api_base="http://localhost:11434")
        
        # Override the generate_chat_completion method to return proper format
        original_method = provider.generate_chat_completion
        def patched_chat_completion(*args, **kwargs):
            result = original_method(*args, **kwargs)
            # Ensure the response format has the correct structure with content
            result["choices"][0]["message"]["content"] = mock_ollama_response["response"]
            return result
            
        provider.generate_chat_completion = patched_chat_completion
        provider.generate_text = mock_async_generate
        
        yield provider


# --- Senate Fixtures ---

@pytest.fixture
def sample_speech():
    """Return a sample generated speech."""
    return {
        "text": "Patres Conscripti! (Conscript Fathers!) Today I stand before you to discuss a matter of great importance...",
        "senator_name": "Marcus Tullius Cicero",
        "senator_id": 1,
        "faction": "Optimates",
        "topic": "Funding for the new aqueduct in Rome",
        "stance": "support",
        "year": -65,
        "archetype": {"primary": "philosopher", "secondary": "traditionalist"},
        "points": [
            "The aqueduct will bring prosperity to all citizens of Rome.",
            "We must consider the investment in our future generations.",
            "This project stands as a testament to Roman engineering brilliance."
        ]
    }


@pytest.fixture
def sample_debate_round():
    """Return a sample debate round structure."""
    return {
        "topic": "Funding for the new aqueduct in Rome",
        "speeches": [
            {
                "senator_id": 1,
                "senator_name": "Marcus Tullius Cicero",
                "stance": "support",
                "text": "Speech 1 content"
            },
            {
                "senator_id": 2,
                "senator_name": "Gaius Julius Caesar",
                "stance": "oppose",
                "text": "Speech 2 content"
            }
        ],
        "votes": {
            "support": 3,
            "oppose": 2,
            "abstain": 0
        },
        "result": "passed"
    }


# --- Async Fixtures ---

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()