# Roman Senate AI Game

A simulation game where AI senators debate and vote on topics in the Roman Senate. Experience politics in Ancient Rome with AI-powered senators from different factions.

## Features

- 🏛️ AI senators with unique personalities and political alignments
- 🗣️ Dynamic debate system with procedural arguments 
- 🗳️ Voting mechanics based on faction alignments and debate performance
- 📜 Historical context and Roman political factions

## Installation

This game has been designed with flexible installation options to accommodate environments with or without Rust (required for building tiktoken).

### Quick Start (Interactive Install)

For an interactive installation that guides you through options:

```bash
cd roman_senate_game
python install.py
```

### Installation Options

1. **Standard Installation** (requires Rust compiler)
   ```bash
   pip install -r requirements.txt
   ```

2. **Binary-Only Installation** (pre-built wheels, no compilation)
   ```bash
   pip install --only-binary=:all: -r requirements.txt
   ```

3. **With tiktoken-lite** (no Rust required)
   ```bash
   pip install -r requirements.txt --no-deps
   pip install tiktoken-lite
   pip install -r requirements.txt
   ```

4. **Minimal Installation** (core functionality only)
   ```bash
   pip install openai typer rich python-dotenv
   pip install crewai>=0.11.0,<0.12.0 --no-deps
   ```

For detailed installation instructions and troubleshooting, see [INSTALLATION.md](INSTALLATION.md).

## Usage

To run the game:

```bash
cd roman_senate_game
python main.py
```

### Game Modes

- **Play:** Start a new senate session
- **Info:** Display game rules and senator information

### OpenAI API Key

To use AI-generated content, set your OpenAI API key in a `.env` file:

```
OPENAI_API_KEY=your_key_here
```

Without a key, the game will use mock data.

## Game Flow

1. Initialize the Senate with AI senators from different factions
2. Select debate topics for the Senate to consider
3. Watch as senators present arguments based on their factions and traits
4. See the voting results and their implications
5. Continue with new topics or end the session

## Dependencies

The game uses several Python libraries including:
- CrewAI 0.11.x (for AI agent coordination)
- OpenAI 1.x (for generating senator responses)
- Typer (for CLI interface)
- Rich (for text formatting)

The code includes graceful fallbacks if any of these dependencies are unavailable. See [INSTALLATION.md](INSTALLATION.md) for version compatibility details and troubleshooting.

## License

[MIT License](LICENSE)

## Acknowledgments

- Inspired by the political dynamics of the Roman Republic
- Uses AI to simulate realistic political debates