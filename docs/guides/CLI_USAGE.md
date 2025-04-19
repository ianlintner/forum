# Roman Senate CLI Usage Guide

This document explains how to use the Roman Senate CLI effectively.

## Overview

The Roman Senate simulation provides several commands for interacting with the simulation:

- `simulate`: Run a full senate simulation
- `play`: Start an interactive game session
- `play-as-senator`: Play as a senator in the simulation
- `info`: Display information about the game
- `save`: Save the current game state
- `load`: Load a saved game
- `list-saves`: List available save files

## Running the CLI

There are several ways to run the CLI:

### 1. Use the run_senate.py Script (Recommended)

The easiest way to run the CLI is to use the `run_senate.py` script in the project root:

```bash
python run_senate.py simulate
python run_senate.py info
python run_senate.py play
```

### 2. Install the CLI Command (Optional)

For even more convenience, you can install the `senate` command:

```bash
# Install the senate command
python setup_cli.py

# Use the command from anywhere
senate info
senate simulate
senate play
```

### 3. Direct Module Execution

You can also run the module directly (this handles imports correctly):

```bash
# From the project root
python -m src.roman_senate.cli simulate
python -m src.roman_senate.cli info
```

## Common Options

Most commands accept additional options:

```
--senators INTEGER        Number of senators to simulate
--debate-rounds INTEGER   Number of debate rounds per topic
--topics INTEGER          Number of topics to debate
--year INTEGER            Year in Roman history (negative for BCE)
```

Example:

```bash
python run_senate.py simulate --senators 15 --topics 5 --year -50
```

## Import System Fix

If you encounter import errors when running scripts directly, use the provided `run_senate.py` script or the module execution method, which properly handle Python's import system. The CLI has been updated to handle imports correctly regardless of how it's invoked.