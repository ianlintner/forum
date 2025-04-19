"""
Pytest fixtures for speech generation tests.

This module contains fixtures for testing the speech generation components.
"""

import pytest


@pytest.fixture
def sample_senator():
    """Fixture providing a sample senator for testing."""
    return {
        "id": "senator_cicero",
        "name": "Marcus Tullius Cicero",
        "faction": "Optimates",
        "traits": {
            "eloquence": 0.9,
            "charisma": 0.8,
            "intelligence": 0.9,
            "ambition": 0.7,
            "loyalty": 0.6
        },
        "background": "Renowned orator and philosopher",
        "political_positions": {
            "military_expansion": 0.3,
            "wealth_redistribution": -0.4,
            "senate_authority": 0.8,
            "provincial_governance": 0.5
        }
    }