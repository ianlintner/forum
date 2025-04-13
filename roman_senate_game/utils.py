#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
Utilities Module

This module provides utility functions used throughout the application,
including API interactions, text formatting, and argument scoring.
"""
import os
import random

# Import required dependencies
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


import tiktoken


from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize Rich console
console = Console()


def call_openai_api(prompt, model="gpt-4", temperature=0.7, max_tokens=1000):
    """
    Makes a call to the OpenAI API if available, otherwise returns a mock response.

    Args:
        prompt (str): The input prompt for the model
        model (str): The model to use, default is "gpt-4"
        temperature (float): Controls randomness (0-1)
        max_tokens (int): Maximum tokens in the response

    Returns:
        str: The model's response text or a mock response if API is unavailable
    """
    if not openai_available:
        # Return mock response when OpenAI is unavailable
        mock_responses = [
            "I propose we increase funding for the aqueduct project.",
            "The Senate should consider the needs of the plebeians before making a decision.",
            "My fellow senators, I must oppose this measure on principle.",
            "Let us consider the historical precedent before we vote.",
        ]
        import random

        return random.choice(mock_responses)

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        if rich_available:
            console.print(f"[bold red]Error calling OpenAI API: {e}[/]")
        else:
            print(f"Error calling OpenAI API: {e}")
        return "The senator makes a compelling argument."


def format_text(text, style="bold green", as_panel=False, title=None):
    """
    Formats text using Rich styling if available, otherwise prints plaintext.

    Args:
        text (str): Text to format
        style (str): Rich style string
        as_panel (bool): Whether to display as a panel
        title (str): Optional title for panel

    Returns:
        None: Prints directly to console
    """
    if as_panel:
        styled_text = Text(text)
        console.print(Panel(styled_text, title=title))
    else:
        console.print(text, style=style)


def score_argument(argument, context, criteria=None):
    """
    Scores an argument based on provided criteria.

    Args:
        argument (str): The argument text to evaluate
        context (str): The context/topic of the debate
        criteria (dict): Scoring criteria, defaults to basic criteria if None

    Returns:
        dict: Scores for each criterion and total score
    """
    # Default criteria if none provided
    if criteria is None:
        criteria = {
            "persuasiveness": 0.3,
            "historical_accuracy": 0.3,
            "logical_coherence": 0.2,
            "eloquence": 0.2,
        }

    # This is a simplified scoring mechanism
    # In a real implementation, this would use NLP or LLM evaluation
    # For MVP, we use a randomized placeholder scoring function

    import random

    scores = {}

    # Generate a score for each criterion, with some basic heuristics
    for criterion, weight in criteria.items():
        # Simple heuristics to make scores slightly more realistic
        if "the" in argument.lower() and "senate" in argument.lower():
            # Slightly higher score for formal arguments mentioning the senate
            base_score = 0.7
        else:
            base_score = 0.5

        # Add randomness
        variance = 0.3 * random.random()
        raw_score = min(1.0, base_score + variance)
        scores[criterion] = raw_score

    # Calculate weighted total
    total_score = sum(
        scores[criterion] * weight for criterion, weight in criteria.items()
    )
    scores["total"] = total_score

    return scores


def count_tokens(text, model="gpt-4"):
    """
    Count tokens in a string using tiktoken if available,
    otherwise estimate based on character count.

    Args:
        text (str): The text to count tokens for
        model (str): Model to use for encoding (default: gpt-4)

    Returns:
        int: Estimated token count
    """
    if not text:
        return 0

    try:
        # Use tiktoken for accurate token counting
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        console.print(f"[bold red]Error using tiktoken: {e}[/]")
        return 0
