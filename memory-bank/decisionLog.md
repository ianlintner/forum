# Decision Log

## Key Design Decisions

[2025-04-15 03:52:00] - **Two-Prompt Approach for Latin Generation**

**Decision:** Implement a sequential two-prompt approach for Latin generation, separating English content generation from Latin translation.

**Rationale:**
- Single-prompt approach with both languages wasn't producing reliable results
- Separate prompts allow focused generation for each language
- Ensures English content can be generated successfully even if Latin fails
- Enables specialized prompting optimized for classical Latin translation

**Implementation:**
- Modified `SenatorAgent.generate_speech()` to use separate prompts for English and Latin
- Updated `SenateEnvironment.run_debate()` to handle separate language texts
- Enhanced error handling to display full content when translation issues occur
- Updated extraction functions to support both approaches for backward compatibility

---

[2025-04-15 03:45:00] - **Stance Terminology Standardization**

**Decision:** Standardize stance terminology across the codebase to use "support"/"oppose"/"neutral" consistently.

**Rationale:**
- Inconsistent terminology ("for"/"against" vs "support"/"oppose") caused "UNKNOWN" position displays
- Standardized terms improve code readability and maintenance
- Ensures consistent user experience with clear position indicators
- Eliminates confusion in debate and voting phases

**Implementation:**
- Updated senator_agent.py to use "support"/"oppose"/"neutral" consistently
- Modified debate.py to handle both new terms and legacy terms for backward compatibility
- Updated environment.py to maintain consistent mapping between stances and votes
- Added clear documentation of stance terminology conventions

---

[2025-04-15 03:20:00] - **GPT-4 (Non-Turbo) Configuration for Classical Latin**

**Decision:** Configure OpenAI GPT-4 (non-turbo) as the default model for the Roman Senate simulation.

**Rationale:**
- Comprehensive evaluation showed GPT-4 (non-turbo) has superior Latin capabilities:
  - Better Latin grammar accuracy with complex syntactical structures
  - Richer classical vocabulary appropriate to historical periods
  - More authentic Roman rhetorical style implementation
  - Better historical contextualization of language usage
  - Superior translation accuracy between Latin and English
- Using a consistent default improves user experience

**Implementation:**
- Updated config.py to set OpenAI as the default provider
- Set DEV_MODE to default to False (which selects non-turbo GPT-4)
- Enhanced the LLM factory to ensure proper API key handling
- Updated the CLI interface with dedicated model parameter
- Created comprehensive documentation at docs/openai_gpt4_configuration.md

---

[2025-04-15 02:35:00] - **Topic Parsing and Display Fixes**

**Decision:** Implement robust string parsing and JSON validation for topic generation and display.

**Rationale:**
- LLM-generated topics occasionally contained malformed JSON responses
- Topic strings had artifacts like brackets, escaped quotes, and trailing commas
- Inconsistent topic display affected user experience and simulation quality
- Runtime errors occurred when parsing corrupted topic cache entries

**Implementation:**
- Added comprehensive `clean_topic_string` function in topic_generator.py:
  ```python
  # Clean a topic string by removing JSON artifacts
  def clean_topic_string(topic: str) -> str:
      # Multiple parsing strategies for different types of artifacts
      # Handles JSON arrays, escaped quotes, trailing commas, etc.
      # Returns clean, user-friendly strings for display
  ```
- Created `clean_topics_dict` function to recursively clean all topics:
  ```python
  # Clean entire dictionary of topics
  def clean_topics_dict(topics_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
      # Process each category and topic
      # Apply cleaning to every string
  ```
- Implemented multiple fallback parsing strategies when JSON parsing fails
- Added validation of JSON responses with proper error handling
- Created a dedicated `fix_topics_cache.py` utility for repairing corrupted cache entries
- Added cleaning during topic loading to ensure consistent display
- Improved error messages and logging for topic parsing issues

These changes significantly improved the reliability of topic generation and display, reducing runtime errors and enhancing user experience.

---

[2025-04-15 02:16:39] - **Agent-Driven Architecture Implementation**

**Decision:** Implement an agent-driven architecture for the Roman Senate simulation with autonomous senator agents.

**Rationale:**
- Creates more emergent and realistic political dynamics
- Enables senators to have memory, goals, and autonomous decision-making
- Provides a more engaging and unpredictable simulation
- Maintains rich presentation layer from the traditional approach

**Implementation:**
- Created `SenatorAgent` class with memory, goals, and decision-making capabilities
- Implemented `AgentMemory` system for storing experiences and forming opinions
- Built `SenateEnvironment` for agent interactions and event propagation
- Developed agent-driven debate with emergent speaking order
- Unified the traditional presentation layer with agent-driven logic
- Fixed topic parsing and display issues
- Simplified CLI by making agent-driven simulation the default approach

This architecture enables more dynamic, realistic senate proceedings while maintaining the rich presentation and historical accuracy of the traditional approach.

---

[2025-04-15 00:10:00] - **Mock Provider and Flexible API Mode Selection System**

**Decision:** Implement a MockProvider class and flexible API mode selection system for testing and CI environments.

**Rationale:**
- Resolves the GitHub Actions workflow failures due to missing API keys
- Enables deterministic testing without external API dependencies
- Provides flexible options for both local Docker testing and GitHub CI
- Makes the system more robust in non-interactive environments
- Allows users to choose between real API (for accuracy) and mock (for speed/reliability)

**Implementation:**
- Created `src/roman_senate/utils/llm/mock_provider.py` with pre-determined responses
- Updated LLM factory to support explicit provider selection via environment variables
- Modified GitHub workflow to support selectable API modes via workflow dispatch UI:
  ```yaml
  api-mode:
    description: 'API mode (auto, mock, real)'
    required: false
    default: 'auto'
    type: choice
    options:
      - auto
      - mock
      - real
  ```
- Created Docker-based simulation environment with Python 3.11 slim image
- Implemented flexible command-line options for Docker simulation:
  ```
  --use-mock           Force use of mock provider regardless of API key presence
  --use-real-api       Force use of real OpenAI API even in test mode
  ```
- Fixed interactive prompt handling in Docker container environment
- Added robust error handling for different vote result formats
- Created comprehensive documentation in README-api-modes.md and README-docker.md

---

[2025-04-14 21:45:00] - **Continuous Integration and Non-Interactive Testing**

**Decision:** Implement GitHub Actions CI workflow and non-interactive test mode.

**Rationale:**
- Ensures code quality is maintained through automated testing
- Provides early detection of regressions or breaking changes
- Enables automated verification of game functionality without manual interaction
- Simplifies testing in CI environments
- Makes the development process more robust

**Implementation:**
- Created `.github/workflows/pytest.yml` for running test suite on multiple Python versions
- Created `.github/workflows/game-simulation.yml` for non-interactive game testing
- Added a new `simulate` command to CLI that supports non-interactive mode
- Modified `SenateSession` to handle test mode with deterministic behavior
- Added environment variable support (`ROMAN_SENATE_TEST_MODE`) for CI testing
- Implemented proper exit codes for CI environment feedback

---

[2025-04-14 21:35:00] - **Documentation and Testing Enhancement**

**Decision:** Create comprehensive documentation and implement a testing framework with Latin naming convention.

**Rationale:**
- Enhances project usability with clear setup instructions for different LLM providers
- Provides rich historical context to improve the educational value of the game
- Ensures code quality through systematic testing
- Maintains Roman theming through Latin test names
- Verifies compatibility with both OpenAI and Ollama providers

**Implementation:**
- Created historical documentation:
  - Roman Senate history with timeline from founding to Imperial period
  - Famous Roman orators profiles and their rhetorical techniques
  - Political faction dynamics between Optimates and Populares
  - Senate traditions and procedures
- Implemented technical documentation:
  - Detailed LLM Provider Configuration Guide
  - Command-line usage examples
  - Updated README with ASCII art of the Roman Forum
- Developed pytest test suite with Latin function names:
  - Test files for all key components (LLM providers, speech, topics, session)
  - Latin test names (e.g., `test_responsio_completionis_openai`) with English docstrings
  - Fixed async implementation in LLM providers to ensure test compatibility
  - Added proper mocking to avoid actual API calls

---

[2025-04-14 20:18:00] - **Package Structure Reorganization**

**Decision:** Refactor the code from a flat module structure to a proper Python package organization.

**Rationale:**
- Improves maintainability by separating concerns into logical subpackages
- Enables proper package installation and distribution
- Makes the codebase more extensible and modular
- Follows Python best practices for package structure
- Simplifies imports and reduces circular dependencies

**Implementation:**
- Created src/roman_senate/ as the main package
- Organized functionality into subpackages: core, player, speech, debate, utils
- Updated import statements throughout the codebase
- Created proper package installation with pyproject.toml and setup.py
- Added command-line entry points in the cli.py module
- Maintained the original roman_senate_game/ module for backward compatibility
- Refactored file locations while preserving core functionality

---

[2025-04-13 23:22:30] - **Bug Fixes for Game Flow Completion**

**Decision:** Implement defensive programming techniques to handle missing senator attributes.

**Rationale:**
- Missing senator traits and influence values were causing game-breaking errors
- Errors occurred during debate speech analysis and voting phases
- Defensive programming ensures game can continue even with incomplete data
- Maintains gameplay flow without critical failures

**Implementation:**
- Modified debate.py to safely access senator traits:
  ```python
  # Handle potential missing traits safely
  traits = senator.get("traits", {}) or {}
  
  # Get trait values with defaults if missing
  eloquence = traits.get("eloquence", 0.5)
  loyalty = traits.get("loyalty", 0.5)
  corruption = traits.get("corruption", 0.1)
  ```
- Modified senate_session.py to safely access senator influence:
  ```python
  # Create voting record with safe access to influence
  voting_record.append({
      "senator": senator["name"],
      "faction": senator["faction"],
      "vote": vote,
      "influence": senator.get("influence", 0.5),  # Default influence value if missing
      "debate_stance": debate_stance
  })
  ```
- Added inline comments explaining the defensive programming approach

---

[2025-04-13 23:22:30] - **Implementation of Historically Accurate Roman Senate Flow**

**Decision:** Implement complete Roman Senate session flow following authentic historical procedures.

**Rationale:**
- Creates a more immersive and educational gameplay experience
- Follows the historically accurate sequence described in Roman sources
- Provides a complete game loop with all phases of Senate operations
- Addresses historical accuracy requirements in the game design

**Implementation:**
- Modified senate_session.py to handle the complete procedural flow
- Added opening ceremonies with religious observances and auspices
- Implemented attendance tracking and seating by rank
- Created formal introduction of agenda items (Relatio)
- Enhanced backroom political dealings between debates
- Added voting session with detailed results analysis
- Implemented formal session conclusion with adjournment speech

---

[2025-04-13 21:26:40] - **Bug Identified in Logging System**

**Decision:** Document bug in logging_utils.py related to time tracking during vote processing.

**Rationale:**
- Bug causes TypeError during voting phase: `unsupported operand type(s) for -: 'float' and 'NoneType'`
- Error occurs in log_response method when calculating elapsed time
- Despite errors, game continues functioning due to error handling

**Next Steps:**
- Investigate the self.start_time initialization in logging_utils.py
- Add proper null checking before time arithmetic operations
- Consider using a default value when start_time is None
- Create more comprehensive error handling in the logging module

---

[2025-04-13 18:25:07] - **Plain English Summaries**

**Decision:** Add plain English summaries explaining each senator's position during debates.

**Rationale:**
- Improves user understanding of complex political stances
- Bridges gap between Latin/formal speech and gameplay mechanics
- Provides clear information on senator motivations and likely votes

**Implementation:**
- Added `generate_position_summary` function in `debate.py`
- Created detailed summaries that explain faction motivations
- Used color coding and clear position tags (FOR/AGAINST/UNDECIDED)

---

[2025-04-13 18:25:07] - **Detailed Voting Results Display**

**Decision:** Enhance voting display with detailed breakdown showing debate stance vs. final vote.

**Rationale:**
- Increases strategic depth by showing which senators can be swayed
- Provides feedback on the impact of debates on voting outcomes
- Creates more engaging and informative endgame statistics

**Implementation:**
- Added detailed voting breakdown table in `main.py`
- Implemented visual indicators for swayed senators
- Modified vote tallying to consider debate stance when determining votes
- Added color coding for different voting positions

---

[2025-04-13 18:25:07] - **AI Speech Generation Implementation**

**Decision:** Implement AI-generated debate speeches using OpenAI API with a robust fallback mechanism.

**Rationale:**
- Enhances immersion by providing authentic Roman-style speeches
- Creates more engaging gameplay with varied and contextual debates
- Fallback mechanism ensures game playability even when API is unavailable

**Implementation:**
- Added `generate_speech` function in `debate.py` that uses API with senator context
- Created templated fallback speech generation for offline play
- Implemented stance-based speech coloring for visual clarity