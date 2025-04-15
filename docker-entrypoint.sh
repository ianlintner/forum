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

# Ensure OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
  echo "⚠️ WARNING: OPENAI_API_KEY environment variable is not set."
  echo "The simulation may not function correctly without this key."
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