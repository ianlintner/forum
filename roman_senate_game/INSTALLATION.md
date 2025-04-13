# Roman Senate AI Game - Installation Guide

This guide provides instructions for installing the Roman Senate AI Game. The game requires Python 3.8 or higher.

## Installation

```bash
# Clone the repository (if applicable)
# git clone <repository-url>
# cd roman-senate-game

# Install dependencies
pip install -r requirements.txt
```

## Required Dependencies

The game requires the following packages:
- openai (1.0.0 or higher)
- typer (0.9.0 or higher)
- rich (13.0.0 or higher)
- python-dotenv (1.0.0 or higher)
- tiktoken (0.5.0 or higher)
- crewai (0.11.x)

### Version Constraints

The game has been tested and is compatible with:
- crewai 0.11.x (specifically 0.11.2)
- openai >= 1.0.0, < 2.0.0
- typer >= 0.9.0
- rich >= 13.0.0
- python-dotenv >= 1.0.0

If you're having issues with newer versions of any packages, try installing the specific versions:

```bash
pip install openai==1.3.0 typer==0.9.0 rich==13.6.0 python-dotenv==1.0.0 crewai==0.11.2
```

## Running the Game

Once installed, you can run the game using the CLI commands:

```bash
cd roman_senate_game
python main.py play  # Start a new game session
python main.py info  # Display game rules and senator information
```

The game supports the following commands:
- `play`: Start a new game session with optional parameters:
  - `--senators INTEGER`: Number of senators (default: 10)
  - `--debate-rounds INTEGER`: Number of debate rounds per topic (default: 3)
  - `--topics INTEGER`: Number of topics to debate (default: 3)
- `info`: Display game rules and current senator information

Example with custom parameters:
```bash
python main.py play --senators 15 --debate-rounds 4 --topics 5
```

## Troubleshooting

### Missing Module Errors

If you see errors about missing modules, you can install them individually:

```bash
pip install <module_name>
```

### OpenAI API Key

To use real AI-generated content, set your OpenAI API key in an `.env` file:

```
OPENAI_API_KEY=your_key_here
```

Without a key, the game will use mock data.

### Low Memory Systems

On systems with limited memory, you might need to use a smaller model:

```bash
# Edit config.py and change GPT-4 to a smaller model, or
# Set an environment variable:
export OPENAI_MODEL=gpt-3.5-turbo
```

## Operating System Specifics

### Windows
- If having issues with Rust, consider using Windows Subsystem for Linux (WSL)

### macOS
- You may need to install Xcode command line tools: `xcode-select --install`

### Linux
- Ensure you have development packages installed: `sudo apt install build-essential` (Ubuntu/Debian)