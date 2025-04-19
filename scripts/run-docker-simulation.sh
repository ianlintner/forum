#!/bin/bash
set -e

# Default parameters
SENATORS=5
DEBATE_ROUNDS=2
TOPICS=1
YEAR=-100

# Function to display help message
show_help() {
  echo "Roman Senate Simulation Docker Runner"
  echo ""
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  -h, --help                 Show this help message"
  echo "  -s, --senators NUM         Number of senators (default: 5)"
  echo "  -d, --debate-rounds NUM    Debate rounds per topic (default: 2)"
  echo "  -t, --topics NUM           Number of topics (default: 1)"
  echo "  -y, --year NUM             Year in Roman history, negative for BCE (default: -100)"
  echo "  -k, --api-key KEY          OpenAI API key (alternatively, set OPENAI_API_KEY env var)"
  echo "  -m, --use-mock             Force use of mock provider regardless of API key presence"
  echo "  -r, --use-real-api         Force use of real OpenAI API even in test mode"
  echo ""
  echo "Example:"
  echo "  $0 --senators 10 --debate-rounds 3 --topics 2 --year -50"
}

# Initialize flags for API choices
USE_MOCK=false
USE_REAL_API=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -h|--help)
      show_help
      exit 0
      ;;
    -s|--senators)
      SENATORS="$2"
      shift 2
      ;;
    -d|--debate-rounds)
      DEBATE_ROUNDS="$2"
      shift 2
      ;;
    -t|--topics)
      TOPICS="$2"
      shift 2
      ;;
    -y|--year)
      YEAR="$2"
      shift 2
      ;;
    -k|--api-key)
      OPENAI_API_KEY="$2"
      shift 2
      ;;
    -m|--use-mock)
      USE_MOCK=true
      shift
      ;;
    -r|--use-real-api)
      USE_REAL_API=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

# Handle API options
if [ "$USE_MOCK" = true ] && [ "$USE_REAL_API" = true ]; then
  echo "❌ Error: Cannot use both --use-mock and --use-real-api at the same time."
  exit 1
fi

# Set the default provider mode based on flags
if [ "$USE_MOCK" = true ]; then
  echo "🤖 Using mock provider for simulation regardless of API key presence."
  FORCE_MOCK_PROVIDER=true
elif [ "$USE_REAL_API" = true ]; then
  echo "🌐 Using real OpenAI API even in test mode."
  FORCE_REAL_API=true
  
  # Check for API key if using real API
  if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: --use-real-api flag requires an OpenAI API key."
    echo "Please provide it using the --api-key option or by setting the OPENAI_API_KEY environment variable."
    exit 1
  fi
else
  # Default behavior
  FORCE_MOCK_PROVIDER=false
  FORCE_REAL_API=false
  
  # Check for API key
  if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ WARNING: No OpenAI API key provided."
    echo "The simulation will use the mock provider."
    echo "You can provide an API key using the --api-key option or by setting the OPENAI_API_KEY environment variable."
    echo "To explicitly use the mock provider, use the --use-mock flag."
    FORCE_MOCK_PROVIDER=true
  fi
fi

# Build the Docker image
echo "🔧 Building Docker image..."
docker build -t roman-senate-simulation .

# Run the simulation
echo "🏛️ Starting Roman Senate Simulation in Docker..."
echo "Parameters:"
echo "  - Senators: $SENATORS"
echo "  - Debate rounds: $DEBATE_ROUNDS"
echo "  - Topics: $TOPICS"
echo "  - Year: $YEAR"

docker run --rm \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e FORCE_MOCK_PROVIDER="$FORCE_MOCK_PROVIDER" \
  -e FORCE_REAL_API="$FORCE_REAL_API" \
  roman-senate-simulation \
  "$SENATORS" "$DEBATE_ROUNDS" "$TOPICS" "$YEAR"

echo "Docker simulation completed."