# Roman Senate AI Game

## Project Overview
A simulation game that recreates the debates and voting procedures of the Roman Senate. The game uses an agent-driven architecture to create autonomous senators with memory, goals, and decision-making capabilities. Senators generate realistic Roman-style speeches in both classical Latin and English, form relationships, and engage in complex political dynamics. Players can participate as senators, making speeches, forming alliances, and influencing votes on important legislation.

## Core Features
- AI Senators with distinct personalities, factions, and traits
- Agent-driven senators with memory, goals, and autonomous decision-making
- Procedural debate system with AI-generated speeches
- Dynamic relationship formation between senators based on interactions
- Player participation as a senator with speech options and interjections
- Historically accurate Roman Senate procedures and customs
- Political maneuvering and backroom dealings between debate rounds
- Voting simulation based on factions, personality traits, and debate performance
- Rich console interface with detailed speech and voting displays
- Authentic classical Latin generation with English translations
- Comprehensive documentation including historical context

## Technology Stack
- Python
- Rich (for terminal UI)
- OpenAI API with GPT-4 (for optimal classical Latin generation)
- Ollama (alternative local LLM provider)
- Typer (for CLI commands)
- pytest (for testing with Latin function names)

## Architecture
- Agent-driven design with autonomous senator agents
- Memory systems for tracking experiences and forming opinions
- Environment for agent interactions and event propagation
- Two-prompt approach for speech generation: English content → Latin translation
- Robust string parsing and JSON validation for LLM responses
- Standardized terminology conventions across the codebase
- Proper Python package structure (src/roman_senate/)
- Modular design with logical subpackages (core, agents, player, speech, debate, utils)
- Dependency injection for better testability
- Interface segregation for LLM providers
- Factory method for component creation

## Target Users
- History enthusiasts
- Strategy game players
- Educational institutions
- Roman history students and scholars
- Latin language learners

## Current Version
Beta with complete gameplay loop:
- Agent-driven simulation with autonomous senators
- Memory and relationship systems for dynamic interactions
- Unified simulation approach with rich presentation
- Player interaction system fully implemented
- Historically accurate Senate session flow
- Comprehensive speech generation framework with authentic classical Latin
- Two-prompt approach for superior language generation
- Optimized for GPT-4 (non-turbo) to ensure high-quality Latin
- Standardized stance terminology for consistent senator positions
- Robust topic parsing and display with clean formatting
- Support for both OpenAI and Ollama LLM providers
- Mock LLM provider for testing and CI environments
- Flexible API mode selection in both Docker and GitHub Actions environments
- Robust testing framework with pytest
- Extensive documentation including historical context and configuration guides

## CI/CD Integration
- GitHub Actions workflow for automated testing
- Configurable API modes (mock, real, auto) in GitHub workflow
- Docker-based simulation environment for local testing
- Feature flags for controlling LLM provider selection

## Language Features
- Authentic classical Latin generation optimized for GPT-4
- Proper rhetorical structures following Roman oratorical traditions
- Latin-to-English translation of all speeches
- Historical Latin phrases and expressions
- Period-appropriate vocabulary and grammar