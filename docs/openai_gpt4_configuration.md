# Running Roman Senate with OpenAI GPT-4 (Non-Turbo)

## Default Configuration

**Important**: OpenAI GPT-4 (non-turbo) is now the default model for the Roman Senate simulation. No additional configuration is required to use it - just provide your OpenAI API key.

This guide explains the configuration details of the Roman Senate simulation with OpenAI's standard GPT-4 model (non-turbo).

## Prerequisites

1. An OpenAI API key with access to GPT-4 (not just GPT-4 Turbo)
2. The Roman Senate codebase

## Configuration Methods

There are three ways to configure the simulation to use OpenAI GPT-4 (non-turbo):

### Method 1: Environment Variables (Recommended)

Set these environment variables before running the simulation:

```bash
# Set provider to OpenAI
export LLM_PROVIDER=openai

# Set to "false" to use non-turbo GPT-4
export DEV_MODE=false

# Your OpenAI API key
export OPENAI_API_KEY=your_api_key_here
```

Then run the simulation normally:

```bash
python -m roman_senate.cli simulate
```

### Method 2: Command Line Arguments

You can specify the provider and model directly when running the simulation:

```bash
python -m roman_senate.cli simulate --provider openai --model gpt-4
```

Make sure your `OPENAI_API_KEY` is set in your environment or in a `.env` file in the project root.

### Method 3: Configuration in .env File

Create or edit a `.env` file in your project root:

```
LLM_PROVIDER=openai
DEV_MODE=false
OPENAI_API_KEY=your_api_key_here
```

Then run the simulation normally:

```bash
python -m roman_senate.cli simulate
```

## Verifying Configuration

When the simulation starts, it will display which provider and model it's using:

```
✓ LLM integration is working. Using provider: OpenAI with model: gpt-4
```

If you see `gpt-4-turbo-preview` instead of `gpt-4`, double-check your DEV_MODE setting or explicitly specify the model on the command line.

## Troubleshooting

### API Key Not Recognized

If you get an authentication error:
- Verify your API key is correct
- Ensure the environment variable is properly set
- Check that your account has access to GPT-4

### Wrong Model Being Used

If you see it's using GPT-4 Turbo instead of standard GPT-4:
- Make sure DEV_MODE is set to false
- Try explicitly specifying the model: `--model gpt-4`

### Cost Considerations

Note that standard GPT-4 (non-turbo) is typically more expensive than GPT-4 Turbo. Make sure your OpenAI account has sufficient credits for your simulation needs.