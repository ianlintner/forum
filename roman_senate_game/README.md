# Roman Senate AI Game

A simulation of the Roman Senate during the Republican era (509 BCE to 27 BCE), featuring AI-powered senators who debate and vote on historically accurate topics relevant to the selected time period.

## New: Enhanced Historical Senate Session Flow

This enhanced version now features a historically accurate Senate session flow, complete with:

- Authentic opening ceremonies and religious observances
- Formal attendance taking and hierarchical seating arrangements
- Proper introduction of agenda (relatio) by presiding officials
- Behind-the-scenes political maneuvering and backroom dealings
- Dynamic debate with realistic interjections and interruptions
- Historically accurate voting procedures
- Formal session adjournment and record-keeping

For comprehensive documentation on these enhancements, see the [detailed documentation in the docs folder](../docs/README.md).

## Features

- 🏛️ Historical Year Selection (509 BCE to 27 BCE) with period-appropriate context
- 🧠 AI-powered senators with unique personalities and faction affiliations
- 📜 GPT-generated historically accurate debate topics based on the selected year
- 🗣️ Dynamic debate system with Latin and English speeches informed by historical context
- 🏆 Categorized topics including military funding, public projects, class rights, etc.
- 🗳️ Voting mechanism based on senators' factions, personalities, and debate performances
- 📊 Detailed session summaries and vote tracking

## Performance Optimizations

The following optimizations have been implemented to improve performance:

### Speech Generation Streaming

- Speeches now stream in real-time as they're being generated
- You can see the speech taking shape word by word
- Visual feedback shows the actual content being generated

### Asynchronous Processing

- Multiple senator speeches can be generated in parallel
- Debate rounds process speakers concurrently where possible
- Background tasks run without blocking the main game experience

### Caching System

- Previously generated speeches are cached to avoid redundant API calls
- Cache is automatically invalidated after the configured duration
- Significantly speeds up repeated game sessions with similar topics

## Historical Period

The Roman Republic existed from 509 BCE (the overthrow of the last Roman king) to 27 BCE (when Octavian became Augustus, the first Roman Emperor). This simulation allows you to explore senatorial politics throughout this critical 482-year period, with historically appropriate:

- Political structures and offices
- Military conflicts and threats
- Economic and social conditions
- Geographic extent of Roman control
- Key historical figures and events

## Topic Generation System

The game includes a sophisticated topic generation system that:

- Creates historically accurate debate topics based on the selected year
- Organizes topics into thematic categories:
  - Military funding
  - Public projects
  - Personal ego projects
  - Military campaigns
  - Class rights
  - General laws
  - Trade relations
  - Foreign diplomacy
  - Religious matters
  - Economic policy
- Caches generated topics to avoid redundant API calls
- Provides fallback topics in case of API failures
- Ensures topics are specific and relevant to the time period

## Historical Context Engine

Senators' speeches and positions are informed by a historical context engine that:

- Provides accurate references to events in the selected year
- References appropriate historical figures active during the chosen period
- Adapts speech patterns to the early, middle, or late Republic
- Includes Latin versions of speeches using period-appropriate terminology
- Adjusts faction positions based on the historical context of the selected year

## Game Flow

1. Select a year for your Senate session (509 BCE to 27 BCE)
2. Review the historical context summary for your chosen year
3. Initialize the Senate with AI senators from different factions
4. Select debate topics appropriate for your selected year
5. Watch as senators present historically informed arguments
6. See the voting results and their implications
7. Continue with new topics or end the session

## Requirements

- Python 3.8+
- OpenAI API key (set in .env file or environment variables)
- Required Python packages (see requirements.txt)

## Installation

This game has been designed with flexible installation options to accommodate different environments.

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

## Configuration Options

You can configure the performance options via environment variables:

- `CACHE_ENABLED`: Set to "True" or "False" to enable/disable caching
- `CACHE_DURATION`: Duration in seconds for how long to keep cached responses (default: 1 week)

## Usage

To run the game:

```bash
cd roman_senate_game
python main.py play
```

### Command Line Options

```
python main.py play [--senators=10] [--debate-rounds=3] [--topics=3]
```

- `--senators`: Number of AI senators to create (default: 10)
- `--debate-rounds`: Number of debate rounds per topic (default: 3)
- `--topics`: Number of topics to debate in a session (default: 3)

### Game Modes

- **Play:** Start a new senate session
- **Info:** Display game rules and senator information

### OpenAI API Key

To use AI-generated content, set your OpenAI API key in a `.env` file:

```
OPENAI_API_KEY=your_key_here
```

Without a key, the game will use mock data and fallback topics.

## Factions

The game models historical Roman political factions:

- **Optimates**: Conservative aristocrats who seek to preserve traditional power structures
- **Populares**: Reform-minded politicians who appeal to common citizens
- **Military**: Generals and veterans focused on military matters and expansion
- **Religious**: Priests and religious conservatives concerned with tradition and piety
- **Merchant**: Business interests focused on trade and economic policy

## License

[MIT License](LICENSE)

## Acknowledgments

- Inspired by the political dynamics of the Roman Republic
- Uses AI to simulate realistic political debates and historical contexts