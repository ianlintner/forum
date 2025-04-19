"""
Pytest fixtures for LLM provider tests.

This module contains fixtures for testing the LLM providers.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from roman_senate.utils.llm.openai_provider import OpenAIProvider
from roman_senate.utils.llm.ollama_provider import OllamaProvider


@pytest.fixture
def mock_openai_response():
    """Fixture providing a mock OpenAI response."""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Mocked OpenAI response content"
                },
                "index": 0
            }
        ],
        "model": "gpt-4"
    }


@pytest.fixture
def mock_openai_provider(monkeypatch, mock_openai_response):
    """Fixture providing a mocked OpenAI provider."""
    # Create a mock provider
    provider = MagicMock(spec=OpenAIProvider)
    
    # Set up the mock methods
    provider.generate_completion.return_value = "Mocked OpenAI response content"
    provider.generate_chat_completion.return_value = mock_openai_response
    provider.generate_text = AsyncMock(return_value="Mocked OpenAI response content")
    
    return provider


@pytest.fixture
def mock_ollama_provider():
    """Fixture providing a mocked Ollama provider."""
    # Create a mock provider
    provider = MagicMock(spec=OllamaProvider)
    
    # Set up the mock methods
    provider.generate_completion.return_value = "Mocked Ollama response content"
    provider.generate_chat_completion.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Mocked Ollama response content"
                },
                "index": 0
            }
        ]
    }
    provider.generate_text = AsyncMock(return_value="Mocked Ollama response content")
    
    return provider