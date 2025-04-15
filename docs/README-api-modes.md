# API Mode Options for Roman Senate Simulation

This document explains how to configure API usage for the Roman Senate simulation in both local Docker testing and GitHub Actions environments.

## Overview

The Roman Senate simulation can use one of two providers for LLM responses:

1. **Real OpenAI API**: Uses actual OpenAI services for more realistic and varied responses
2. **Mock Provider**: Uses predetermined responses without network access (good for testing)

You can explicitly control which provider is used in both environments.

## GitHub Actions Configuration

The GitHub workflow now supports three API modes:

### 1. Via Workflow Dispatch UI

When manually triggering the workflow, you can select an API mode:

- `auto` (default): Use OpenAI API if key is available, otherwise use mock
- `mock`: Always use mock provider regardless of API key
- `real`: Always use OpenAI API (fails if key is not available)

![Workflow Dispatch UI](docs/assets/workflow-dispatch-ui.png)

### 2. Repository Setup

1. Add your OpenAI API key to GitHub repository secrets:
   - Go to repository Settings → Secrets and variables → Actions
   - Create a new secret named `OPENAI_API_KEY` with your API key

## Local Docker Simulation

You can control the API mode in local Docker simulation with these options:

### 1. Command-Line Flags

```bash
# Always use mock provider even if an API key is available
./run-docker-simulation.sh --use-mock

# Use real OpenAI API (requires an API key)
./run-docker-simulation.sh --use-real-api --api-key "your-api-key"

# Auto mode: use real API if key is available, otherwise mock
./run-docker-simulation.sh --api-key "your-api-key"
# OR
export OPENAI_API_KEY="your-api-key"
./run-docker-simulation.sh
```

### 2. Default Behavior

- If you provide an API key, the real OpenAI API is used
- If no API key is provided, the mock provider is automatically used
- Use explicit flags to override this behavior

## Technical Details

The provider selection works through these environment variables:

- `ROMAN_SENATE_TEST_MODE`: When "true", enables test/non-interactive mode
- `ROMAN_SENATE_MOCK_PROVIDER`: 
  - When "true", forces the mock provider
  - When "false", forces the real API provider
  - When unset, falls back to the default behavior based on test mode

## Troubleshooting

1. **"ERROR: Real API mode selected but no OPENAI_API_KEY is set"**:
   - You selected "real" API mode but no API key is available
   - Add the API key to repository secrets or provide via command line

2. **Slow or error-prone responses**:
   - If using the real API, check your OpenAI API quota and limits
   - Consider switching to mock mode during testing with `--use-mock`

3. **Inconsistent simulation behavior**:
   - Mock provider gives consistent but limited responses
   - Real API provides more varied but potentially inconsistent responses