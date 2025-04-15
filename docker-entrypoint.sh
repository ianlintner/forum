#!/bin/bash
set -e

# Default values
SENATORS=${1:-5}
DEBATE_ROUNDS=${2:-2}
TOPICS=${3:-1}
YEAR=${4:--100}

echo "🏛️ Starting Roman Senate Simulation..."
echo "Number of senators: $SENATORS"
echo "Debate rounds per topic: $DEBATE_ROUNDS"
echo "Number of topics: $TOPICS"
echo "Year (negative for BCE): $YEAR"

# Handle API choice
if [ "$FORCE_MOCK_PROVIDER" = "true" ]; then
  echo "🤖 Using mock provider for LLM responses (forced via flag)"
  export ROMAN_SENATE_MOCK_PROVIDER=true
elif [ "$FORCE_REAL_API" = "true" ]; then
  echo "🌐 Using real OpenAI API for LLM responses (forced via flag)"
  export ROMAN_SENATE_MOCK_PROVIDER=false
  
  # Ensure OPENAI_API_KEY is set when using real API
  if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY environment variable is not set."
    echo "When using the real API (--use-real-api), an API key is required."
    exit 1
  fi
else
  # Default behavior - use mock if no API key
  if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ WARNING: OPENAI_API_KEY environment variable is not set."
    echo "Automatically using mock provider instead."
    export ROMAN_SENATE_MOCK_PROVIDER=true
  else
    echo "🔑 OPENAI_API_KEY detected - using real OpenAI API"
    export ROMAN_SENATE_MOCK_PROVIDER=false
  fi
fi

# Set test mode
export ROMAN_SENATE_TEST_MODE=true

# Run the simulation
echo "🚀 Executing simulation..."
python -m roman_senate.cli simulate \
  --senators $SENATORS \
  --debate-rounds $DEBATE_ROUNDS \
  --topics $TOPICS \
  --year $YEAR \
  --non-interactive

# Return the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Simulation completed successfully!"
else
  echo "❌ Simulation failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE