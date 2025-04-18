#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Roman Senate AI Game
CLI Runner

This script provides a convenient entry point to run the Roman Senate simulation
without having to worry about Python's module/import system.
Simply run: python run_senate.py [commands...]
"""

import os
import sys
import typer

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Import the CLI app after setting the correct path
from src.roman_senate.cli import app

# Run the typer CLI app
if __name__ == "__main__":
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    app()