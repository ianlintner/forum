#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Debate Package

This package handles the debate mechanics including speech generation
and interjections.
"""

from .speech_generator import generate_speech_text, generate_chat_completion

__all__ = [
    'generate_speech_text',
    'generate_chat_completion',
]