# Roman Senate Game: User Guide

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 14, 2025

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Game Modes](#game-modes)
  - [Simulation Mode](#simulation-mode)
  - [Interactive Mode](#interactive-mode)
- [Command-Line Options](#command-line-options)
- [Game Flow](#game-flow)
- [Tips for Engaging Gameplay](#tips-for-engaging-gameplay)
- [Troubleshooting](#troubleshooting)

## Introduction

The Roman Senate Game is an immersive political simulation set in the late Roman Republic era. This guide will help you install, configure, and play the game in both its simulation and interactive modes.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- An LLM provider setup (OpenAI API key or Ollama running locally)

### Step-by-Step Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/roman-senate-game.git
   cd roman-senate-game
   ```

2. **Install the package**:
   ```bash
   pip install -e .
   ```

3. **Configure LLM Provider**:
   
   The game requires an LLM (Large Language Model) provider for generating speeches and processing player interactions.

   **For OpenAI**:
   - Ensure you have an OpenAI API key
   - Set your API key as an environment variable:
     ```bash
     export OPENAI_API_KEY="your-api-key"
     ```

   **For Ollama**:
   - Install Ollama from [https://ollama.ai/](https://ollama.ai/)
   - Start the Ollama service locally
   - Pull a compatible model:
     ```bash
     ollama pull llama2
     ```

4. **Verify Installation**:
   ```bash
   senate info
   ```
   
   This should display information about the game and confirm that your LLM provider is configured correctly.

## Game Modes

The Roman Senate Game offers two distinct ways to play:

### Simulation Mode

In Simulation Mode, you observe as AI-controlled senators debate and vote on important matters facing Rome.

**Starting Simulation Mode**:
```bash
senate play
```

**What Happens in Simulation Mode**:

1. **Senate Initialization**: The game creates a set of senators with diverse personalities, political alignments, and traits.

2. **Topic Generation**: Historically appropriate debate topics are generated based on the year setting.

3. **Debate Process**:
   - For each topic, multiple rounds of debate occur
   - AI senators give speeches supporting or opposing the motion
   - Speeches incorporate rhetorical devices, historical references, and Latin flourishes
   - Senators may respond directly to points made by previous speakers

4. **Voting Procedure**:
   - After debate concludes, senators cast their votes
   - The game tallies votes and announces the outcome
   - Results influence future senator behaviors and relationships

5. **Session Summary**: At the end, you'll see a summary of all topics debated and their outcomes.

### Interactive Mode

In Interactive Mode, you create and play as your own Roman senator, actively participating in Senate proceedings.

**Starting Interactive Mode**:
```bash
senate play-as-senator
```

**What Happens in Interactive Mode**:

1. **Character Creation**:
   - Choose your senator's name
   - Select a political faction (Optimates, Populares, or Independent)
   - Determine your background (Patrician or Plebeian)
   - Review your starting attributes (wealth, influence, reputation)

2. **Senate Session**:
   - Attendance and seating are determined (you're always present)
   - Topics are introduced for debate and voting

3. **Player Participation Options**:
   - **Make Speeches**: Craft your own speeches on debate topics
   - **Interject**: Interrupt other senators' speeches to support or oppose their points
   - **Cast Votes**: Vote "aye," "nay," or abstain on each topic
   - **Build Relationships**: Your actions affect your relationships with other senators

4. **Consequences**:
   - Successful arguments and winning votes increase your influence
   - Relationships with other senators affect their likelihood to support your position
   - Your faction alignment impacts your default stance on topics

## Command-Line Options

### Shared Options
- `--year`: The year in Roman history to simulate (negative for BCE)
  ```bash
  senate play --year -50   # Simulates the Senate in 50 BCE
  ```

### Simulation Mode Options
- `--senators`: Number of senators to simulate (default: 10)
  ```bash
  senate play --senators 15
  ```
- `--debate-rounds`: Number of debate rounds per topic (default: 3)
  ```bash
  senate play --debate-rounds 5
  ```
- `--topics`: Number of topics to debate (default: 3)
  ```bash
  senate play --topics 4
  ```

### Interactive Mode Options
- `--senators`: Number of NPC senators (default: 9, plus you)
  ```bash
  senate play-as-senator --senators 12
  ```
- `--topics`: Number of topics to debate (default: 3)
  ```bash
  senate play-as-senator --topics 5
  ```

### Combined Examples
```bash
# Simulate 15 senators in 50 BCE debating 4 topics with 2 rounds each
senate play --senators 15 --year -50 --topics 4 --debate-rounds 2

# Play as a senator with 15 NPC colleagues in 75 BCE debating 3 topics
senate play-as-senator --senators 15 --year -75
```

## Game Flow

### Simulation Mode Flow

```
┌───────────────────┐
│ Initialize Game   │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ Create Senators   │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ Generate Topics   │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ Start Senate      │
│ Session           │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ For Each Topic    │◄─────┐
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ Conduct Debate    │      │
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ Hold Vote         │      │
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ Record Results    │      │
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ More Topics?      │─Yes──┘
└─────────┬─────────┘
          │ No
┌─────────▼─────────┐
│ Display Session   │
│ Summary           │
└───────────────────┘
```

### Interactive Mode Flow

```
┌───────────────────┐
│ Initialize Game   │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ Character         │
│ Creation          │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ Create NPC        │
│ Senators          │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ Generate Topics   │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ Start Senate      │
│ Session           │
└─────────┬─────────┘
          │
┌─────────▼─────────┐
│ For Each Topic    │◄─────┐
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ Conduct Debate    │      │
│ with Player       │      │
│ Participation     │      │
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ Player Casts Vote │      │
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ NPCs Vote         │      │
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ Record Results    │      │
│ & Update Player   │      │
│ Status            │      │
└─────────┬─────────┘      │
          │                │
┌─────────▼─────────┐      │
│ More Topics?      │─Yes──┘
└─────────┬─────────┘
          │ No
┌─────────▼─────────┐
│ Display Final     │
│ Status & Relations│
└───────────────────┘
```

## Tips for Engaging Gameplay

### For Simulation Mode
- Try different historical years to see how debate topics change
- Experiment with different numbers of senators to observe dynamics
- Watch for faction patterns in voting behavior

### For Interactive Mode
- **Choose Your Faction Strategically**:
  - Optimates favor tradition and senatorial privilege
  - Populares advocate for reforms benefiting common citizens
  - Independents have more flexibility but less natural allies

- **Build Relationships**:
  - Agree with senators during debates to improve relations
  - Use interjections strategically to show support
  - Consider voting with powerful senators to gain favor

- **Make Compelling Speeches**:
  - Reference historical events for added credibility
  - Address previous speakers to show engagement
  - Balance emotion and logic in your arguments

## Troubleshooting

### Common Issues

**Issue**: Game crashes during speech generation
**Solution**: Check your LLM provider configuration and ensure you have API access or the local model is running

**Issue**: Slow performance during debates
**Solution**: Use fewer senators or debate rounds to reduce processing load

**Issue**: Topics seem anachronistic for the time period
**Solution**: Try a different year setting that might be more historically rich

### Getting Help

If you encounter persistent issues:
1. Check the project repository for known issues
2. Look for updates to the game
3. Contact the development team through the repository

---

This guide covers the basics of getting started with the Roman Senate Game. For more detailed information about specific systems, please see the additional documentation:

- [Speech Generation Framework](speech_generation.md)
- [Interactive Mode Guide](interactive_mode.md)
- [System Architecture](architecture.md)