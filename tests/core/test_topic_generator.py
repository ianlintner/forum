#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game - Topic Generator Tests
Tests for the topic generation components using Latin function names.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

from roman_senate.core.topic_generator import (
    ensure_cache_dir_exists, load_cached_topics, save_cached_topics,
    get_historical_period_context, generate_topics_for_year,
    get_fallback_topics, get_topics_for_year, flatten_topics_by_category
)


# --- Topic Generator Tests ---

def test_creatio_directorii_cache():
    """
    Test that the cache directory is created if it doesn't exist.
    (Test creation of cache directory)
    """
    # Mock os.path.exists and os.makedirs
    with patch('os.path.exists', return_value=False), \
         patch('os.makedirs') as mock_makedirs:
        
        # Call the function
        ensure_cache_dir_exists()
        
        # Verify makedirs was called
        mock_makedirs.assert_called_once()


def test_oneratio_topicorum_ex_cache():
    """
    Test loading topics from cache.
    (Test loading topics from cache)
    """
    # Mock cache directory exists and file exists
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()), \
         patch('json.load', return_value={"year_key": "cached_topics"}) as mock_json_load:
        
        # Load cached topics
        result = load_cached_topics()
        
        # Verify result
        assert result == {"year_key": "cached_topics"}
        assert mock_json_load.called


def test_salvatio_topicorum_in_cache():
    """
    Test saving topics to cache.
    (Test saving topics to cache)
    """
    # Mock file operations
    mock_file = MagicMock()
    mock_open = MagicMock(return_value=mock_file)
    
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open), \
         patch('json.dump') as mock_json_dump:
        
        # Save topics to cache
        topics_cache = {"year_key": "topics_data"}
        save_cached_topics(topics_cache)
        
        # Verify json.dump was called with the correct arguments
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        assert args[0] == topics_cache  # First arg should be the topics cache


def test_acquisitio_contextus_historici():
    """
    Test historical context retrieval for different years.
    (Test historical context acquisition)
    """
    # Test context for different years
    early_republic = get_historical_period_context(-500)  # Early Republic
    mid_republic = get_historical_period_context(-220)    # Middle Republic
    late_republic = get_historical_period_context(-50)    # Late Republic
    
    # Verify context contains appropriate information for each period
    assert "Early Roman Republic" in early_republic or "expulsion of King Tarquinius" in early_republic
    assert "Punic War" in mid_republic or "expansion" in mid_republic
    assert "Caesar" in late_republic or "civil war" in late_republic
    
    # Test a specific year with known events
    specific_year = get_historical_period_context(-44)  # Year of Caesar's assassination
    assert "Caesar" in specific_year or "Ides of March" in specific_year or "dictator" in specific_year


@pytest.mark.asyncio
async def test_generatio_topicorum_cum_llm():
    """
    Test topic generation with LLM integration.
    (Test topic generation with LLM)
    """
    # Sample LLM response with valid JSON
    sample_llm_response = """
    {
      "Military funding": ["Funding for Pompey's campaign against pirates in the Mediterranean", "Increased stipends for Caesar's legions in Gaul"],
      "Public projects": ["Construction of a new forum in Rome", "Repairs to the Via Appia"]
    }
    """
    
    # Create mock LLM provider
    mock_llm = AsyncMock()
    mock_llm.generate_text = AsyncMock(return_value=sample_llm_response)
    
    # Mock dependencies
    with patch('roman_senate.core.topic_generator.load_cached_topics', return_value={}), \
         patch('roman_senate.core.topic_generator.save_cached_topics'), \
         patch('roman_senate.utils.llm.factory.get_provider', return_value=mock_llm):
        
        # Generate topics for year -60
        year = -60
        topics = await generate_topics_for_year(year, count=4)
        
        # Verify
        assert isinstance(topics, dict)
        assert "Military funding" in topics
        assert "Public projects" in topics
        assert len(topics["Military funding"]) == 2
        assert "Pompey" in topics["Military funding"][0]  # Specific historical reference
        assert mock_llm.generate_text.called


@pytest.mark.asyncio
async def test_tractatio_responsi_llm_invalidi():
    """
    Test handling of invalid LLM responses.
    (Test handling of invalid LLM response)
    """
    # Invalid JSON response
    invalid_response = """
    Military funding:
    - Funding for new legions
    - Naval budget increase
    
    Public projects:
    - New aqueduct construction
    """
    
    # Create mock LLM provider
    mock_llm = AsyncMock()
    mock_llm.generate_text = AsyncMock(return_value=invalid_response)
    
    # Mock dependencies
    with patch('roman_senate.core.topic_generator.load_cached_topics', return_value={}), \
         patch('roman_senate.core.topic_generator.save_cached_topics'), \
         patch('roman_senate.utils.llm.factory.get_provider', return_value=mock_llm):
        
        # Generate topics, should handle invalid JSON gracefully
        year = -60
        topics = await generate_topics_for_year(year, count=4)
        
        # Verify that it either:
        # 1. Successfully parsed the response manually
        # 2. Fell back to default topics
        assert isinstance(topics, dict)
        assert topics  # Not empty


@pytest.mark.asyncio
async def test_gestio_erroris_generationis():
    """
    Test error handling during topic generation.
    (Test error handling in generation)
    """
    # Mock LLM to raise an error
    mock_llm = AsyncMock()
    mock_llm.generate_text = AsyncMock(side_effect=Exception("API Error"))
    
    # Mock dependencies
    with patch('roman_senate.core.topic_generator.load_cached_topics', return_value={}), \
         patch('roman_senate.utils.llm.factory.get_provider', return_value=mock_llm), \
         patch('roman_senate.core.topic_generator.get_fallback_topics') as mock_fallback:
        
        # Setup fallback topics
        fallback_topics = {
            "Military funding": ["Fallback military topic"]
        }
        mock_fallback.return_value = fallback_topics
        
        # Generate topics, should catch the error and return fallbacks
        topics = await get_topics_for_year(-50, count=4)
        
        # Verify fallback was used
        assert topics == fallback_topics
        assert mock_fallback.called


def test_complanatio_topicorum_per_categorias():
    """
    Test flattening topics by category.
    (Test flattening topics by category)
    """
    # Sample categorized topics
    topics_by_category = {
        "Military funding": ["Legion funding", "Naval expansion"],
        "Public projects": ["Aqueduct construction", "Road repairs"]
    }
    
    # Flatten the topics
    flat_topics = flatten_topics_by_category(topics_by_category)
    
    # Verify
    assert isinstance(flat_topics, list)
    assert len(flat_topics) == 4  # Total number of topics
    
    # Check structure of flattened topics
    for topic in flat_topics:
        assert "text" in topic
        assert "category" in topic
        assert topic["text"] in ["Legion funding", "Naval expansion", 
                                "Aqueduct construction", "Road repairs"]
        assert topic["category"] in ["Military funding", "Public projects"]


def test_topis_categoriae_correctae():
    """
    Test that topic categories are correct in fallback topics.
    (Test correct topic categories)
    """
    # Get fallback topics
    fallback_topics = get_fallback_topics()
    
    # Verify structure
    assert isinstance(fallback_topics, dict)
    
    # Check expected categories are present
    expected_categories = [
        "Military funding", "Public projects", "Military campaigns",
        "Class rights", "General laws", "Trade relations", 
        "Foreign relations", "Religious matters", "Economic policy"
    ]
    
    for category in expected_categories:
        assert category in fallback_topics
        assert isinstance(fallback_topics[category], list)
        assert len(fallback_topics[category]) > 0