#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Speech Generation Module

This module provides advanced speech generation capabilities for the Roman Senate simulation,
incorporating historical authenticity, classical rhetoric, and personality-driven speech patterns.
"""

# Main speech generation function
from .speech_generator import generate_speech

# Submodules for direct access to components
from . import archetype_system
from . import rhetorical_devices
from . import historical_context
from . import classical_structure
from . import latin_flourishes
from . import speech_evaluation

# Expose key functions for external use
__all__ = [
    'generate_speech',
    'archetype_system',
    'rhetorical_devices',
    'historical_context',
    'classical_structure',
    'latin_flourishes',
    'speech_evaluation'
]