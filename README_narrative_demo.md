# Roman Senate Narrative System Demo

This demo script showcases the AI-generated narrative system for the Roman Senate simulation. It demonstrates how the system generates dynamic narrative events, rumors, and interactions that provide context and atmosphere to the simulation.

## Features Demonstrated

- **Dynamic Event Generation**: See how the system generates daily events, rumors, military events, religious events, and senator-focused events based on the current game state and narrative context.
- **Narrative Consistency**: Observe how the ConsistencyProcessor ensures events maintain consistency with previous narrative elements.
- **Relationship Processing**: Watch how the RelationshipProcessor extracts and manages relationships between entities mentioned in events.
- **Game State Integration**: See how narrative events are integrated with the game state and influence senate topics.
- **Rich Text Output**: Experience the narrative content with rich text formatting for better readability.

## Requirements

- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`):
  - rich
  - All dependencies of the Roman Senate simulation

## Usage

Run the demo script with:

```bash
python demo_narrative.py [options]
```

### Command-line Options

- `--days DAYS`: Number of days to simulate (default: 5)
- `--event-types TYPES`: Types of events to generate (comma-separated: daily,rumor,military,religious,senator,all) (default: all)
- `--verbosity LEVEL`: Verbosity level (0=minimal, 1=normal, 2=detailed) (default: 1)
- `--year YEAR`: Starting year for the simulation (negative for BCE) (default: -50)
- `--month MONTH`: Starting month for the simulation (1-12) (default: 3)
- `--day DAY`: Starting day for the simulation (default: 15)
- `--seed SEED`: Random seed for reproducible results (default: random)

### Examples

1. Run a basic 5-day simulation with default settings:
   ```bash
   python demo_narrative.py
   ```

2. Run a 10-day simulation with only rumors:
   ```bash
   python demo_narrative.py --days 10 --event-types rumor
   ```

3. Run a detailed simulation with military and religious events only:
   ```bash
   python demo_narrative.py --event-types military,religious --verbosity 2
   ```

4. Run a simulation focusing on senator events starting in 44 BCE (the year of Caesar's assassination):
   ```bash
   python demo_narrative.py --year -44 --month 3 --day 15 --event-types senator
   ```

5. Run a reproducible simulation with a specific seed:
   ```bash
   python demo_narrative.py --seed 42
   ```

## Output Explanation

The demo generates and displays:

1. **Daily Events**: Regular occurrences in Rome and the empire, including:
   - Market activities and trade
   - Weather and natural phenomena
   - Religious ceremonies and omens
   - Public gatherings and entertainment
   - Minor crimes and disturbances

2. **Rumors**: Gossip and hearsay circulating in Rome, including:
   - Political alliances and rivalries
   - Personal scandals
   - Speculation about foreign affairs
   - Whispers about financial dealings
   - Rumors about religious omens

3. **Military Events**: Military affairs of the Roman Republic, including:
   - Battles and skirmishes
   - Troop movements and deployments
   - Military campaigns and strategies
   - Victories and defeats
   - Military appointments and promotions
   - Sieges and naval operations

4. **Religious Events**: Religious affairs in Rome, including:
   - Religious ceremonies and festivals
   - Omens and portents
   - Temple dedications and repairs
   - Priestly appointments
   - Divine interventions and interpretations
   - Sacrifices and religious observances

5. **Senator Events**: Personal events involving specific senators, including:
   - Personal achievements and milestones
   - Family events (marriages, births, deaths)
   - Property acquisitions or losses
   - Personal scandals or triumphs
   - Health issues or recoveries
   - Political maneuvers outside the Senate

6. **Summary Statistics**:
   - Event counts by type
   - Entity mentions
   - Narrative themes

## How It Works

The demo script:

1. Initializes the game state and narrative engine
2. Sets up the calendar to the specified date
3. For each day in the simulation:
   - Generates narrative events using the specified event types
   - Displays the events with appropriate formatting
   - Integrates events with the game state
   - Advances the calendar to the next day
4. Displays a summary of the simulation results

## Implementation Details

The narrative system consists of several interconnected components:

- **NarrativeEngine**: Central controller for narrative generation
- **EventManager**: Manages event generators and processors
- **NarrativeContext**: Maintains narrative memory and history
- **Event Generators**:
  - DailyEventGenerator: Creates events about daily life in Rome
  - RumorEventGenerator: Generates rumors and gossip
  - MilitaryEventGenerator: Creates events about military affairs
  - ReligiousEventGenerator: Generates events about religious matters
  - SenatorEventGenerator: Creates personal events for specific senators
- **Event Processors**:
  - ConsistencyProcessor: Ensures narrative consistency
  - RelationshipProcessor: Manages relationships between entities

The demo uses a MockProvider for the LLM to make it runnable without requiring an API key.

## Notes

- This demo is self-contained and doesn't modify any existing game state.
- The narrative content is generated using predefined templates and mock responses.
- In a real game session, the narrative system would interact with other components like the Senate debate system and senator agents.