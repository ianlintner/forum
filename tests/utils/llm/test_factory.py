#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game - LLM Factory Tests
Tests for the LLM factory using Latin function names.
"""

import pytest
from unittest.mock import patch

from roman_senate.utils.llm.factory import get_llm_provider, get_provider
from roman_senate.utils.llm.openai_provider import OpenAIProvider
from roman_senate.utils.llm.ollama_provider import OllamaProvider


def test_selectio_fabricae_openai():
    """
    Test that the factory correctly returns an OpenAI provider.
    (Test factory selection for OpenAI)
    """
    # Test with explicit OpenAI
    provider = get_llm_provider(provider_type="openai", model_name="gpt-4")
    
    # Assert we got the right type
    assert isinstance(provider, OpenAIProvider)
    assert provider.model_name == "gpt-4"


def test_selectio_fabricae_ollama():
    """
    Test that the factory correctly returns an Ollama provider.
    (Test factory selection for Ollama)
    """
    # Test with explicit Ollama
    provider = get_llm_provider(provider_type="ollama", model_name="mistral:7b")
    
    # Assert we got the right type
    assert isinstance(provider, OllamaProvider)
    assert provider.model_name == "mistral:7b"


def test_error_provider_invalidus():
    """
    Test that the factory raises an error for invalid provider types.
    (Test error for invalid provider)
    """
    # Test with invalid provider type
    with pytest.raises(ValueError) as excinfo:
        get_llm_provider(provider_type="invalid")
    
    # Check the error message
    assert "Unknown provider type" in str(excinfo.value)


def test_configuratio_provideris_ex_config():
    """
    Test that the get_provider function uses configuration values correctly.
    (Test provider configuration from config)
    """
    # Mock the config values
    with patch('roman_senate.utils.config.LLM_PROVIDER', 'openai'), \
         patch('roman_senate.utils.config.LLM_MODEL', 'gpt-3.5-turbo'):
        
        # Get provider without explicit args
        provider = get_provider()
        
        # Assert we got the right provider with config values
        assert isinstance(provider, OpenAIProvider)
        assert provider.model_name == 'gpt-3.5-turbo'


def test_prioritas_argumentorum_explicitorum():
    """
    Test that explicit arguments override configuration values.
    (Test priority of explicit arguments)
    """
    # Mock the config values
    with patch('roman_senate.utils.config.LLM_PROVIDER', 'openai'), \
         patch('roman_senate.utils.config.LLM_MODEL', 'gpt-3.5-turbo'):
        
        # Get provider with explicit args
        provider = get_provider(provider_type='ollama', model_name='mistral:7b')
        
        # Assert explicit args were used instead of config
        assert isinstance(provider, OllamaProvider)
        assert provider.model_name == 'mistral:7b'


def test_transmissio_argumentorum_additorum():
    """
    Test that additional arguments are passed to the provider constructor.
    (Test transmission of additional arguments)
    """
    # Extra arguments for OpenAI
    with patch('roman_senate.utils.llm.openai_provider.OpenAIProvider.__init__', return_value=None) as mock_init:
        get_llm_provider(provider_type='openai', model_name='gpt-4', api_key='test-key')
        
        # Assert the extra argument was passed
        mock_init.assert_called_once_with(model_name='gpt-4', api_key='test-key')
    
    # Extra arguments for Ollama
    with patch('roman_senate.utils.llm.ollama_provider.OllamaProvider.__init__', return_value=None) as mock_init:
        get_llm_provider(provider_type='ollama', model_name='mistral:7b', api_base='http://custom:11434')
        
        # Assert the extra argument was passed
        mock_init.assert_called_once_with(model_name='mistral:7b', api_base='http://custom:11434')