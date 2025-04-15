# Roman Senate Game Simulation in Docker

This project includes Docker setup to simulate the GitHub Actions workflow locally. This allows you to test the code in an environment similar to GitHub Actions without having to push changes to GitHub repeatedly.

## Overview

The Docker setup consists of:

1. `Dockerfile` - Uses the official Python 3.11 slim image for faster builds
2. `docker-entrypoint.sh` - Script that runs the simulation inside the container
3. `run-docker-simulation.sh` - Convenience script to build and run the container

## Mock LLM Provider

A mock LLM provider has been added to the project that automatically activates in test mode. This allows the simulation to run without requiring actual API access to OpenAI or other external services.

The mock provider (`src/roman_senate/utils/llm/mock_provider.py`) returns predefined responses for different types of prompts (topics, speeches, interjections, etc.) making the simulation deterministic and repeatable.

## How to Use

### Prerequisites

- Docker installed on your system
- Bash shell environment

### Running the Simulation

1. Make the scripts executable:

```bash
chmod +x docker-entrypoint.sh run-docker-simulation.sh
```

2. Run the simulation using the convenience script:

```bash
./run-docker-simulation.sh
```

This will build the Docker image and run the simulation with default parameters (5 senators, 2 debate rounds, 1 topic, year -100 BCE).

### Customizing the Simulation

You can customize the simulation by passing arguments to the script:

```bash
./run-docker-simulation.sh --senators 10 --debate-rounds 3 --topics 2 --year -50
```

Run `./run-docker-simulation.sh --help` to see all available options.

### OpenAI API Key (Optional)

While the mock provider is used in test mode, you can still provide an OpenAI API key if you want to test with the actual API:

```bash
./run-docker-simulation.sh --api-key "your-api-key-here"
# or
export OPENAI_API_KEY="your-api-key-here"
./run-docker-simulation.sh
```

## Comparison to GitHub Actions

This Docker setup mimics the environment used in the GitHub Actions workflow defined in `.github/workflows/game-simulation.yml`. The key difference is that the Docker environment is local and you have full control over it.

### Benefits:

1. Full, immediate access to logs and output
2. Faster iteration cycle (no waiting for GitHub)
3. Ability to debug interactively
4. No GitHub minutes consumed
5. No need to commit and push changes to test them

## Troubleshooting

If you encounter issues:

1. Check that Docker is running
2. Verify that scripts are executable
3. Ensure the current working directory is the project root
4. Check for detailed logs in the Docker output