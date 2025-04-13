# System Patterns

## Architecture Patterns
[2025-04-13 18:24:53] - Current system uses a modular architecture with separate modules for different components of the Roman Senate simulation.

### Module Structure
- `main.py` - Entry point and orchestration
- `debate.py` - Debate mechanics and speech generation
- `senators.py` - Senator data models and generation
- `vote.py` - Voting logic and tallying
- `utils.py` - Shared utilities and API integration
- `config.py` - Configuration and environment variables

### Key Design Patterns

#### Command Pattern
The application uses Typer to implement a command-based interface, following the Command pattern for user interactions.

#### Factory Method
Senator creation follows a factory method approach, generating senators with random traits and faction alignments.

#### Strategy Pattern
Different debate and voting strategies can be employed based on senator traits and faction alignments.

#### Observer Pattern
The game state observes changes in debate and voting, updating the history accordingly.

## Data Flow

1. User initiates game via CLI commands
2. Senate is initialized with AI senators
3. Debate topics are selected
4. Senators participate in rounds of debate
   - AI generates speeches based on senator profiles
   - Speeches are scored and displayed
5. Voting is conducted based on debate positions and senator traits
6. Results are displayed and stored in game history

## API Integration

The system uses OpenAI's API for generating senator speeches. A robust fallback mechanism ensures the game can function even when API is unavailable by using pre-defined templates and randomization.