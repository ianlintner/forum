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
  echo ""
  echo "Example:"
  echo "  $0 --senators 10 --debate-rounds 3 --topics 2 --year -50"
}

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
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
  # Check if it's in the environment
  if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ WARNING: No OpenAI API key provided."
    echo "The simulation may not function correctly without an API key."
    echo "You can provide it using the --api-key option or by setting the OPENAI_API_KEY environment variable."
    read -p "Do you want to continue anyway? (y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
      echo "Exiting."
      exit 1
    fi
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
  roman-senate-simulation \
  "$SENATORS" "$DEBATE_ROUNDS" "$TOPICS" "$YEAR"

echo "Docker simulation completed."