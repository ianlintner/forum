# Roman Senate Speech Generation Framework

This module provides a comprehensive speech generation framework for the Roman Senate simulation game, implementing features for historically authentic, rhetorically sophisticated speeches with Latin flourishes.

## Overview

The speech generation framework transforms basic debate topics into fully-realized Roman oratory, incorporating:

- **Historical Authenticity**: References to appropriate figures, events, and contexts from Roman history
- **Classical Rhetoric**: Implementation of ancient rhetorical structures and devices
- **Latin Integration**: Appropriate Latin terminology, phrases, and expressions
- **Personality-Driven Variation**: Speech styles based on senator archetypes and traits
- **Evaluation System**: Scoring and feedback on speech effectiveness

## Components

### 1. `archetype_system.py`

Handles personality-based speech generation by implementing senator archetypes:

- Traditionalist: Conservative, formal, appealing to ancestral traditions
- Pragmatist: Practical, results-oriented, focused on concrete benefits
- Philosopher: Abstract, principle-focused, employing logical reasoning
- Populist: Emotional, direct, appealing to common people's interests
- Militarist: Security-focused, assertive, emphasizing strength and action

Functions:
- `determine_archetype()`: Analyzes senator traits to determine their archetype
- `generate_archetype_parameters()`: Creates speech parameters based on archetype
- `select_rhetorical_devices()`: Chooses appropriate rhetorical devices for an archetype

### 2. `historical_context.py`

Provides historically accurate references based on the simulation year:

- Historical figures and events appropriate to the time period
- Political terminology relevant to the era
- Roman values as understood during different periods
- Historically appropriate Latin phrases

Functions:
- `get_historical_context_for_speech()`: Provides contextualized historical information
- `get_historically_appropriate_address()`: Returns formal address forms for the era
- `generate_historical_reference()`: Creates specific historical references

### 3. `rhetorical_devices.py`

Implements classical Roman rhetorical techniques:

- Repetition-based devices (anaphora, tricolon, polysyndeton)
- Contrast-based devices (antithesis, chiasmus)
- Question-based devices (rhetorical questions, interrogatio)
- Reference-based devices (exemplum, sententia)
- Sophisticated devices (praeteritio, definitio, analogia)

Functions:
- `apply_rhetorical_device()`: Applies a specific device to text
- `apply_multiple_devices()`: Combines several devices in a single speech
- `suggest_devices()`: Recommends devices based on content analysis

### 4. `classical_structure.py`

Organizes speeches according to classical rhetorical structure:

- Exordium: Introduction to capture audience attention
- Narratio: Statement of facts and context
- Partitio: Outline of speech structure
- Confirmatio: Positive arguments supporting position
- Refutatio: Refutation of opposing arguments
- Peroratio: Conclusion with emotional appeal

Functions:
- `generate_speech_structure()`: Creates a structured speech outline
- `expand_speech_structure()`: Develops the outline into full content
- `assemble_full_speech()`: Compiles all sections into a complete oration

### 5. `latin_flourishes.py`

Integrates Latin language elements into speeches:

- Opening and closing Latin phrases
- Integration of Latin terminology with translations
- Latin political and institutional terms
- Roman virtues and values in Latin

Functions:
- `add_latin_flourish()`: Integrates Latin phrases into English text
- `generate_latin_speech_version()`: Creates a Latin version of a speech
- `add_latin_opening()`: Adds a formal Latin opening to a speech

### 6. `speech_evaluation.py`

Evaluates and scores speeches based on rhetorical effectiveness:

- Rhetorical device usage and variation
- Classical structure adherence
- Latin integration quality
- Historical authenticity
- Audience-appropriate appeals
- Topic relevance

Functions:
- `evaluate_speech()`: Provides comprehensive speech evaluation
- `calculate_audience_reaction()`: Determines how the audience would respond

## Usage

The framework is used primarily through the main `generate_speech()` function:

```python
from speech_generation import generate_speech

speech = generate_speech(
    senator=senator_data,
    topic="The expansion of citizenship to Italian allies",
    faction_stance={"Optimates": "oppose", "Populares": "support"},
    year=-91,  # 91 BCE (Social War period)
    responding_to=previous_speaker,
    previous_speeches=debate_speeches
)

# Access the generated speech
english_text = speech["text"]
latin_text = speech["latin_version"]
evaluation = speech["evaluation"]
```

Advanced users can also access the individual components:

```python
from speech_generation import archetype_system, rhetorical_devices, historical_context

# Determine senator archetype
archetype = archetype_system.determine_archetype(senator_data)

# Get historical context for a specific year
context = historical_context.get_historical_context_for_speech(-44)  # 44 BCE

# Apply rhetorical devices to text
enhanced_text, descriptions = rhetorical_devices.apply_multiple_devices(
    text, ["anaphora", "tricolon"]
)
```

## Integration with Existing System

The framework is designed to integrate with the existing debate system:

1. The main `debate.py` module now uses the enhanced speech generation
2. Backward compatibility is maintained with original function signatures
3. Enhanced speeches include additional metadata for rich display

## Extending the Framework

To add new speech generation features:
- New rhetorical devices: Add to the `RHETORICAL_DEVICES` dictionary in `rhetorical_devices.py`
- Additional historical references: Expand the period dictionaries in `historical_context.py`
- New senator archetypes: Add to `ARCHETYPES` list in `archetype_system.py`