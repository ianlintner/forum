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
- `political_maneuvering.py` - Backroom political dealings and faction relationships
- `officials.py` - Presiding officials and their behaviors
- `interjections.py` - Procedural interruptions and responses
- `senate_session.py` - Complete Senate session orchestration and flow

[2025-04-13 23:23:25] - Updated architecture includes components for a complete historical Roman Senate session flow, including opening ceremonies, political maneuvering, and formal procedures.

### Key Design Patterns

#### Command Pattern
The application uses Typer to implement a command-based interface, following the Command pattern for user interactions.

#### Factory Method
Senator creation follows a factory method approach, generating senators with random traits and faction alignments.

#### Strategy Pattern
Different debate and voting strategies can be employed based on senator traits and faction alignments.

#### Observer Pattern
The game state observes changes in debate and voting, updating the history accordingly.

#### Chain of Responsibility
[2025-04-13 23:23:25] - The Roman Senate session flow follows a Chain of Responsibility pattern, where each phase (opening, political maneuvering, debate, voting, adjournment) passes control to the next in sequence.

#### State Pattern
[2025-04-13 23:23:25] - The senate_session.py module implements a State pattern to manage the different phases of a Senate session, ensuring the proper progression through each stage.

## Data Flow

1. User initiates game via CLI commands
2. Senate is initialized with AI senators
3. Debate topics are selected
4. Senators participate in rounds of debate
   - AI generates speeches based on senator profiles
   - Speeches are scored and displayed
5. Voting is conducted based on debate positions and senator traits
6. Results are displayed and stored in game history

[2025-04-13 23:23:25] - Updated data flow with complete Roman Senate session:

1. User initiates game via CLI commands
2. Senate is initialized with AI senators and presiding officials
3. Opening ceremonies are conducted with religious observances
4. Attendance is taken and senators are seated according to rank
5. Agenda items are formally introduced (Relatio)
6. Backroom political dealings occur between senators
7. Formal debate proceeds in rounds with speeches and interjections
8. Political maneuvering may result in amendments or alliances
9. Voting is conducted based on debate positions, senator traits, and political deals
10. Results are announced and recorded
11. Process repeats for additional agenda items
12. Session concludes with formal adjournment

## API Integration

The system uses OpenAI's API for generating senator speeches. A robust fallback mechanism ensures the game can function even when API is unavailable by using pre-defined templates and randomization.

## Exception Handling

[2025-04-13 21:27:27] - The application implements robust error handling that allows the game to continue functioning even when errors occur in non-critical components.

[2025-04-13 23:23:25] - Implemented defensive programming techniques to handle missing or null senator attributes:

### Defensive Programming Strategies
- Safe attribute access using dictionary `.get()` method with default values
- Null coalescing with the `or` operator to provide fallbacks
- Type checking before critical operations
- Graceful degradation when optimal data is unavailable

### Known Issues
- In `logging_utils.py`, the `log_response` method assumes `self.start_time` is set by a prior call to `start_api_call`. However, during voting, `log_response` is sometimes called without this initialization, causing a TypeError when calculating elapsed time:
  ```python
  # Bug in logging_utils.py line 141:
  elapsed = time.time() - self.start_time  # TypeError when self.start_time is None
  ```

### Recommended Fixes
- Add a null check similar to the one in `end_api_call` method:
  ```python
  # Example fix for log_response method:
  elapsed = time.time() - (self.start_time or time.time())
  ```
- Ensure `start_api_call` is called before `log_response` in all code paths
- Consider adding a decorator or context manager to ensure proper call sequence

### Recently Implemented Bug Fixes
[2025-04-13 23:23:25] - Fixed critical bugs affecting the complete game flow:

1. **Safe Senator Trait Access in debate.py**:
   ```python
   # Before: Direct access that could fail
   eloquence = senator["traits"]["eloquence"]
   
   # After: Safe access with defaults
   traits = senator.get("traits", {}) or {}
   eloquence = traits.get("eloquence", 0.5)
   ```

2. **Safe Influence Access in senate_session.py**:
   ```python
   # Before: Direct access that could fail
   influence = senator["influence"]
   
   # After: Safe access with default
   influence = senator.get("influence", 0.5)
   ```

[2025-04-14 20:19:00] - **Updated Package Structure**

### New Module Architecture
The codebase has been reorganized from a flat structure into a proper Python package with logical subpackages:

```
src/
└── roman_senate/
   ├── __init__.py        # Package initialization
   ├── cli.py             # Command-line interface entry points
   ├── core/              # Core game mechanics
   │   ├── __init__.py
   │   ├── debate.py      # Debate system core
   │   ├── game_state.py  # Game state management
   │   ├── senate_session.py # Full session orchestration
   │   ├── senators.py    # Senator data models
   │   ├── topic_generator.py # Topic generation
   │   └── vote.py        # Voting system
   ├── debate/            # Debate mechanics
   │   ├── __init__.py
   │   └── speech_generator.py # Speech generation integration
   ├── player/            # Player interaction
   │   ├── __init__.py
   │   ├── game_loop.py   # Main player game loop
   │   ├── player.py      # Player data model
   │   ├── player_actions.py # Available player actions
   │   ├── player_manager.py # Player state management
   │   ├── player_ui.py   # User interface for player
   │   └── test_player.py # Tests for player functionality
   ├── speech/            # Speech generation system
   │   ├── __init__.py
   │   ├── archetype_system.py
   │   ├── classical_structure.py
   │   ├── historical_context.py
   │   ├── latin_flourishes.py
   │   ├── rhetorical_devices.py
   │   └── speech_generator.py
   └── utils/             # Shared utilities
       ├── __init__.py
       ├── config.py      # Configuration management
       └── llm/           # LLM integration
           ├── __init__.py
           ├── base.py    # Base LLM interface
           ├── factory.py # LLM provider factory
           ├── ollama_provider.py # Ollama integration
           └── openai_provider.py # OpenAI integration
```

The original `roman_senate_game/` module is maintained for backward compatibility while new development proceeds in the proper package structure.

### Enhanced Design Patterns

#### Dependency Injection
The new package structure implements dependency injection throughout the system, allowing for better testability and component replacement.

#### Interface Segregation
LLM providers now follow the Interface Segregation Principle with a common base interface defined in `utils/llm/base.py`.

#### Factory Method (Enhanced)
The LLM provider system uses an enhanced factory method pattern in `utils/llm/factory.py` to create the appropriate LLM provider instance based on configuration.