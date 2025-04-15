#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game - LLM Provider Tests
Tests for OpenAI and Ollama LLM providers using Latin function names.
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from roman_senate.utils.llm.openai_provider import OpenAIProvider
from roman_senate.utils.llm.ollama_provider import OllamaProvider


# --- OpenAI Provider Tests ---

def test_responsio_completionis_openai(mock_openai_provider):
    """
    Test that the OpenAI provider correctly generates completions.
    (Test response generation for completions)
    """
    # Generate a completion
    result = mock_openai_provider.generate_completion(
        prompt="Test prompt",
        temperature=0.7,
        max_tokens=100
    )
    
    # Assert we got the expected output
    assert result == "Mocked OpenAI response content"
    assert isinstance(result, str)


def test_responsio_colloquii_openai(mock_openai_provider, mock_openai_response):
    """
    Test that the OpenAI provider correctly handles chat completions.
    (Test response generation for conversations)
    """
    # Create chat messages
    messages = [
        {"role": "system", "content": "You are a Roman senator."},
        {"role": "user", "content": "Speak on the aqueduct proposal."}
    ]
    
    # Generate a chat completion
    result = mock_openai_provider.generate_chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )
    
    # Assert we got the expected output format
    assert result == mock_openai_response

@pytest.mark.asyncio
async def test_generatio_textus_async_openai(mock_openai_provider):
    """
    Test async text generation with OpenAI provider.
    (Test async text generation)
    """
    # Test the async generate_text method
    result = await mock_openai_provider.generate_text(
        prompt="Generate a speech for Cicero",
        temperature=0.8
    )
    
    # Assert we got the expected output
    assert result == "Mocked OpenAI response content"
    assert result == "Mocked OpenAI response content"


def test_tractatio_erroris_openai():
    """
    Test error handling in the OpenAI provider.
    (Test error handling)
    """
    # Create a provider that will raise an error
    with patch('openai.chat.completions.create') as mock_create:
        mock_create.side_effect = Exception("API error")
        provider = OpenAIProvider(model_name="gpt-4", api_key="invalid-key")
        
        # Test completion with error
        result = provider.generate_completion("Test prompt")
        assert "[Error generating text:" in result
        
        # Test chat completion with error
        chat_result = provider.generate_chat_completion([{"role": "user", "content": "Test"}])
        assert "Error generating response" in chat_result["choices"][0]["message"]["content"]


# --- Ollama Provider Tests ---

def test_responsio_completionis_ollama(mock_ollama_provider):
    """
    Test that the Ollama provider correctly generates completions.
    (Test response generation for completions)
    """
    # Generate a completion
    result = mock_ollama_provider.generate_completion(
        prompt="Test prompt",
        temperature=0.7,
        max_tokens=100
    )
    
    # Assert we got the expected output
    assert result == "Mocked Ollama response content"
    assert isinstance(result, str)


def test_responsio_colloquii_ollama(mock_ollama_provider):
    """
    Test that the Ollama provider correctly handles chat completions.
    (Test response generation for conversations)
    """
    # Create chat messages
    messages = [
        {"role": "system", "content": "You are a Roman senator."},
        {"role": "user", "content": "Speak on the aqueduct proposal."}
    ]
    
    # Generate a chat completion
    result = mock_ollama_provider.generate_chat_completion(
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )
    
    # Assert we got the expected output format
    assert "choices" in result
    assert result["choices"][0]["message"]["content"] == "Mocked Ollama response content"

@pytest.mark.asyncio
async def test_generatio_textus_async_ollama(mock_ollama_provider):
    """
    Test async text generation with Ollama provider.
    (Test async text generation)
    """
    # Test the async generate_text method
    result = await mock_ollama_provider.generate_text(
        prompt="Generate a speech for Cicero",
        temperature=0.8
    )
    
    # Assert we got the expected output
    assert result == "Mocked Ollama response content"
    assert result == "Mocked Ollama response content"


def test_tractatio_erroris_ollama():
    """
    Test error handling in the Ollama provider.
    (Test error handling)
    """
    # Create a provider that will raise an error
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("Connection error")
        provider = OllamaProvider(model_name="mistral:7b", api_base="http://invalid-url")
        
        # Test completion with error
        result = provider.generate_completion("Test prompt")
        assert "[Error generating text:" in result
        
        # Test chat completion with error
        chat_result = provider.generate_chat_completion([{"role": "user", "content": "Test"}])
        assert "Error generating response" in chat_result["choices"][0]["message"]["content"]


# --- Integration tests for both providers ---

def test_conformatio_interfacii(mock_openai_provider, mock_ollama_provider):
    """
    Test that both providers conform to the same interface.
    (Test interface conformity)
    """
    # Same input for both providers
    prompt = "Generate a speech for the Senate"
    messages = [{"role": "user", "content": prompt}]
    
    # Test the same methods on both providers
    openai_completion = mock_openai_provider.generate_completion(prompt)
    ollama_completion = mock_ollama_provider.generate_completion(prompt)
    
    openai_chat = mock_openai_provider.generate_chat_completion(messages)
    ollama_chat = mock_ollama_provider.generate_chat_completion(messages)
    
    # Assert that both return string completions
    assert isinstance(openai_completion, str)
    assert isinstance(ollama_completion, str)
    
    # Assert that both return dictionaries for chat completions
    assert isinstance(openai_chat, (dict, MagicMock))
    assert isinstance(ollama_chat, dict)