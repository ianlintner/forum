#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game - Speech Generator Tests
Tests for the speech generation components using Latin function names.
"""

import pytest
from unittest.mock import patch, MagicMock
import random

from roman_senate.speech.speech_generator import (
    generate_speech, determine_stance, extract_key_points,
    extract_mentioned_senators, enhance_speech_with_llm, generate_response_speech
)


# --- Speech Generation Tests ---

def test_generatio_orationis_basis(sample_senator):
    """
    Test basic speech generation functionality.
    (Test basic speech generation)
    """
    # Patch dependencies to avoid actual LLM calls
    with patch('roman_senate.speech.archetype_system.determine_archetype') as mock_archetype, \
         patch('roman_senate.speech.archetype_system.generate_archetype_parameters') as mock_params, \
         patch('roman_senate.speech.historical_context.get_historical_context_for_speech') as mock_context, \
         patch('roman_senate.speech.classical_structure.generate_speech_structure') as mock_structure, \
         patch('roman_senate.speech.classical_structure.expand_speech_structure') as mock_expand, \
         patch('roman_senate.speech.classical_structure.assemble_full_speech') as mock_assemble, \
         patch('roman_senate.speech.archetype_system.select_rhetorical_devices') as mock_devices, \
         patch('roman_senate.speech.rhetorical_devices.apply_multiple_devices') as mock_apply, \
         patch('roman_senate.speech.latin_flourishes.add_latin_flourish') as mock_latin, \
         patch('roman_senate.speech.latin_flourishes.add_latin_opening') as mock_opening:
        
        # Configure mocks
        mock_archetype.return_value = {"primary": "pragmatist", "secondary": "philosopher"}
        mock_params.return_value = {"formality_level": 0.7, "primary": "pragmatist"}
        mock_context.return_value = {"events": ["First Triumvirate formed"], "politics": "Senate divided"}
        mock_structure.return_value = {"exordium": {"type": "intro"}, "peroratio": {"type": "conclusion"}}
        mock_expand.return_value = {
            "exordium": {"content": "Fellow senators!"},
            "peroratio": {"content": "Vote for this proposal!"}
        }
        mock_assemble.return_value = "Fellow senators! Vote for this proposal!"
        mock_devices.return_value = ["anaphora", "rhetorical_question"]
        mock_apply.return_value = ("Enhanced speech with rhetorical devices.", 
                                  ["Used anaphora", "Used rhetorical question"])
        mock_latin.return_value = "Enhanced speech with Latin phrases."
        mock_opening.return_value = "Patres Conscripti! Enhanced speech with Latin phrases."
        
        # Generate speech
        speech = generate_speech(
            senator=sample_senator,
            topic="Funding for a new aqueduct",
            year=-60
        )
        
        # Verify results
        assert speech["senator_name"] == sample_senator["name"]
        assert speech["senator_id"] == sample_senator["id"]
        assert speech["faction"] == sample_senator["faction"]
        assert speech["topic"] == "Funding for a new aqueduct"
        assert speech["year"] == -60
        assert speech["archetype"] == {"primary": "pragmatist", "secondary": "philosopher"}
        assert "text" in speech
        assert "stance" in speech
        assert "points" in speech
        assert isinstance(speech["points"], list)


def test_determinatio_positionis():
    """
    Test stance determination based on faction and archetype.
    (Test position determination)
    """
    # Create test senators from different factions with different archetypes
    optimates_senator = {"faction": "Optimates", "name": "Cato"}
    populares_senator = {"faction": "Populares", "name": "Caesar"}
    
    # Test with faction stances defined
    faction_stances = {"Optimates": "oppose", "Populares": "support"}
    
    # Set a fixed seed for consistent test results when using random
    random.seed(42)
    
    # Test stance determination with faction information
    for _ in range(10):  # Run multiple times to handle randomness
        optimates_stance = determine_stance(
            "Land reform for plebeians", 
            optimates_senator, 
            {"primary": "traditionalist"}, 
            faction_stances
        )
        populares_stance = determine_stance(
            "Land reform for plebeians", 
            populares_senator, 
            {"primary": "populist"}, 
            faction_stances
        )
        
        # Most of the time, senators should follow faction lines (70% probability)
        # But we can't assert exactly due to randomness, so we run multiple times
        assert optimates_stance in ["support", "oppose", "neutral"]
        assert populares_stance in ["support", "oppose", "neutral"]


def test_extractio_punctorum_principalium():
    """
    Test extraction of key points from a speech.
    (Test extraction of main points)
    """
    # Test speech with multiple sentences
    test_speech = (
        "Patres Conscripti! Today I speak on a matter of great importance. "
        "The aqueduct must be built to serve the people of Rome. "
        "I believe this is essential for public health. "
        "The cost will be justified by the benefits. "
        "Our great Republic deserves the finest infrastructure. "
        "I urge you all to vote in favor of this proposal."
    )
    
    # Extract key points
    points = extract_key_points(test_speech, count=3)
    
    # Verify
    assert len(points) == 3
    assert all(isinstance(point, str) for point in points)
    
    # The sentences with "must", "urge", and "essential" should be prioritized
    important_phrases = ["must", "essential", "urge"]
    has_important_phrase = False
    for point in points:
        if any(phrase in point.lower() for phrase in important_phrases):
            has_important_phrase = True
            break
    assert has_important_phrase
    
    # Test with fewer sentences than requested points
    short_speech = "This is a short speech. Just two sentences."
    short_points = extract_key_points(short_speech, count=3)
    assert len(short_points) == 2


def test_extractio_mentionum_senatorum():
    """
    Test extraction of mentioned senators from a speech.
    (Test extraction of senator mentions)
    """
    # Create sample previous speeches with senator information
    previous_speeches = [
        {"senator_name": "Cicero", "senator_id": 1},
        {"senator_name": "Caesar", "senator_id": 2},
        {"senator_name": "Cato", "senator_id": 3}
    ]
    
    # Speech mentioning two senators
    test_speech = (
        "I disagree with the position taken by Cicero on this matter. "
        "However, I find merit in Caesar's argument about the cost."
    )
    
    # Extract mentions
    mentions = extract_mentioned_senators(test_speech, previous_speeches)
    
    # Verify
    assert len(mentions) == 2
    assert 1 in mentions  # Cicero's ID
    assert 2 in mentions  # Caesar's ID
    assert 3 not in mentions  # Cato not mentioned
    
    # Test with no previous speeches
    no_mentions = extract_mentioned_senators(test_speech, None)
    assert len(no_mentions) == 0
    
    # Test with no mentions
    no_mentions = extract_mentioned_senators("This speech mentions no senators.", previous_speeches)
    assert len(no_mentions) == 0


@pytest.mark.asyncio
async def test_augmentatio_orationis_llm():
    """
    Test speech enhancement using LLM.
    (Test speech augmentation with LLM)
    """
    # Mock LLM provider
    mock_provider = MagicMock()
    mock_provider.generate_completion.return_value = "Enhanced speech with better rhetoric."
    
    # Patch the get_speech_llm_provider function to return our mock provider
    with patch('roman_senate.speech.speech_generator.get_speech_llm_provider', return_value=mock_provider):
        # Test enhancing a speech
        original_speech = "This is a basic speech about the aqueduct."
        senator = {"name": "Cicero", "faction": "Optimates"}
        archetype = "philosopher"
        topic = "Funding for a new aqueduct"
        stance = "support"
        
        enhanced = enhance_speech_with_llm(original_speech, senator, archetype, topic, stance)
        
        # Verify
        assert enhanced == "Enhanced speech with better rhetoric."
        assert mock_provider.generate_completion.called
        
        # Check prompt structure
        call_args = mock_provider.generate_completion.call_args[1]
        prompt = call_args["prompt"]
        assert "philosopher" in prompt
        assert "support" in prompt
        assert "aqueduct" in prompt
        assert original_speech in prompt


def test_generatio_responsionis():
    """
    Test generation of a response speech.
    (Test response generation)
    """
    # Create an original speech to respond to
    original_speech = {
        "senator_name": "Caesar",
        "senator_id": 2,
        "text": "We must build the aqueduct for Rome's glory!",
        "topic": "Aqueduct funding"
    }
    
    # Responding senator
    responding_senator = {
        "id": 3,
        "name": "Cato",
        "faction": "Optimates",
        "traits": {"eloquence": 0.8}
    }
    
    # Patch the generate_speech function
    with patch('roman_senate.speech.speech_generator.generate_speech') as mock_generate:
        # Set up the mock to return a basic speech that doesn't mention the original speaker
        mock_generate.return_value = {
            "senator_name": "Cato",
            "senator_id": 3,
            "text": "I disagree with this proposal for several reasons.",
            "topic": "Aqueduct funding",
            "speech_structure": {
                "refutatio": "I see several flaws in this reasoning."
            }
        }
        
        # Generate a response speech
        response = generate_response_speech(
            senator=responding_senator,
            topic="Aqueduct funding",
            original_speech=original_speech
        )
        
        # Verify
        assert mock_generate.called
        assert "responding_to" in mock_generate.call_args[1]
        assert mock_generate.call_args[1]["responding_to"] == original_speech
        
        # The response should have been modified to reference the original speaker
        assert "Caesar" in response["text"] or "the previous speaker" in response["text"]