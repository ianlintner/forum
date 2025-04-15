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

[2025-04-14 21:37:00] - **Testing Architecture**

### Testing Framework
The project now implements a comprehensive testing framework using pytest:

```
tests/
├── __init__.py
├── conftest.py             # Shared fixtures and test configuration
├── core/                   # Core component tests
│   ├── __init__.py
│   ├── test_senate_session.py
│   └── test_topic_generator.py
├── speech/                 # Speech generation tests
│   ├── __init__.py
│   └── test_speech_generator.py
└── utils/                  # Utility tests
    ├── __init__.py
    └── llm/                # LLM provider tests
        ├── __init__.py
        ├── test_factory.py
        └── test_providers.py
```

### Roman-Themed Testing
The test functions use Latin names to maintain the Roman theme of the project while providing clear English docstrings to explain their purpose. Examples include:

```python
def test_responsio_completionis_openai():
    """Test that OpenAI provider correctly generates completion responses."""
    # Test implementation
    
def test_generatio_thematis_cum_contextu():
    """Test topic generation with historical context."""
    # Test implementation
```

### Testing Patterns

#### Fixture Usage
The testing system uses pytest fixtures to provide common test dependencies such as mock senators, LLM providers, and topic generators:

```python
@pytest.fixture
def senatus_fictus():
    """Provides a list of mock senators for testing."""
    return [
        {"name": "Marcus Tullius", "faction": "Optimates", "traits": {}},
        {"name": "Gaius Gracchus", "faction": "Populares", "traits": {}}
    ]
```

#### Mocking
Tests use the `unittest.mock` library to mock external dependencies, particularly LLM API calls:

```python
@patch("openai.chat.completions.create")
def test_responsio_completionis_openai(mock_completions_create):
    """Test OpenAI completion functionality with mocked API."""
    mock_completions_create.return_value = mock_response
    # Test implementation
```

#### Parameterization
Tests use pytest's parameterize functionality to test multiple scenarios with a single test function:

```python
@pytest.mark.parametrize("factio,expectatum", [
    ("Optimates", "traditional"), 
    ("Populares", "reform")
])
def test_oratio_cum_factione(factio, expectatum):
    """Test speech generation with different factions."""
    # Test implementation that varies by faction
```

#### Async Testing
The system incorporates pytest-asyncio for testing asynchronous functions in the LLM providers:

```python
@pytest.mark.asyncio
async def test_generatio_textus_async():
    """Test async text generation method."""
    # Async test implementation
```

### Documentation Integration
The project includes comprehensive documentation tightly integrated with the testing framework:

1. **Documentation Links**: Test files reference corresponding documentation to explain concepts
2. **Historical Context**: Documentation provides Roman historical background for the tested functionality
3. **Multilingual Support**: Both Latin (for test names) and English (for descriptions) are used
4. **Command-Line Examples**: Documentation includes examples of running the test suite

[2025-04-14 21:45:00] - **CI/CD and Automated Testing Architecture**

### Continuous Integration Workflows
The project now implements GitHub Actions workflows for automated testing and verification:

```
.github/
└── workflows/
    ├── pytest.yml          # Test suite workflow
    └── game-simulation.yml # Non-interactive gameplay test
```

#### Test Suite Workflow (pytest.yml)
This workflow runs the test suite on multiple Python versions (3.9, 3.10, 3.11) to ensure compatibility:

```yaml
name: Python Tests
on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master, develop ]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-asyncio
        pip install -e .
    - name: Test with pytest
      run: |
        pytest
```

#### Game Simulation Workflow (game-simulation.yml)
This workflow tests the full game functionality in non-interactive mode to verify core gameplay:

```yaml
name: Game Simulation Test
on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master, develop ]
  schedule:
    - cron: '0 0 * * 0'  # Run weekly on Sundays at midnight
jobs:
  simulate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.10
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        cache: 'pip'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
    - name: Run non-interactive game simulation
      run: |
        export ROMAN_SENATE_TEST_MODE=true
        python -m roman_senate.cli simulate --senators 5 --debate-rounds 2 --topics 1 --non-interactive
    - name: Archive simulation logs
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: simulation-logs
        path: |
          logs/
          data/saves/
```

### Non-Interactive Testing Pattern
The system now supports non-interactive testing through a dedicated CLI command and test mode:

#### Environment-Based Configuration

```python
# Detection of test environment
is_test_mode = os.environ.get('ROMAN_SENATE_TEST_MODE') == 'true' or 'pytest' in sys.modules
```

#### Deterministic Behavior in Test Mode

```python
# Use fixed seed for reproducible tests
if non_interactive:
    import random
    random.seed(42)
```

#### CLI Extensions
The CLI interface now includes a simulate command specifically for testing:

```python
@app.command(name="simulate")
def simulate(
    senators: int = typer.Option(10, help="Number of senators to simulate"),
    debate_rounds: int = typer.Option(3, help="Number of debate rounds per topic"),
    topics: int = typer.Option(3, help="Number of topics to debate"),
    year: int = typer.Option(-100, help="Year in Roman history (negative for BCE)"),
    non_interactive: bool = typer.Option(False, help="Run in non-interactive mode (for CI/CD testing)")
):
    """Run a non-interactive simulation of the Roman Senate for testing purposes."""
```

#### Test Mode Propagation
Test mode is propagated through the object hierarchy to modify behavior appropriately:

```python
# Create and run session with test mode
session = SenateSession(senate_members, year, game_state, test_mode)
results = await session.run_full_session(selected_topics, debate_rounds)
```

### Testing Benefits
The CI/CD integration provides several key benefits:

1. **Automatic Regression Detection**: Changes that break existing functionality are detected immediately
2. **Cross-Version Compatibility**: Tests ensure code works across multiple Python versions
3. **Scheduled Testing**: Weekly tests catch issues with external dependencies
4. **Non-Interactive Verification**: Core gameplay loops can be verified without manual testing
5. **Artifact Collection**: Logs and game data are preserved for post-test analysis