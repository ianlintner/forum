# Roman Senate Game: Player System

This directory contains the implementation of the player-related functionality for the Roman Senate game.

## Overview

The player system handles all aspects of the human player's character in the game, including:

- Character creation and progression
- Speech generation and debate participation
- Political actions and maneuvering
- Relationship management with NPC senators
- Stats and resource management
- User interface for player interactions

## Components

### Player (`player.py`)

The core `Player` class represents the player's character and manages:

- Basic attributes (name, faction, wealth, influence, reputation)
- Skills system (oratory, intrigue, administration, military, commerce)
- Special abilities that unlock based on skill levels
- Political capital resource management
- Relationship tracking with other senators
- Character progression through experience

### PlayerManager (`player_manager.py`)

Handles the administration of player data:

- Creating new player characters
- Saving player data to JSON files
- Loading player data from saves
- Managing save files

### PlayerUI (`player_ui.py`)

Provides rich terminal user interface for player interactions:

- Character status displays with color-coded stats
- Relationship status visualization
- Speech and interjection option presentation
- Voting interfaces
- Political action menus
- Character creation screens

### PlayerActions (`player_actions.py`)

Implements gameplay mechanics for player actions:

- Speech generation and delivery using LLM integration
- Interjection system during other senators' speeches
- Voting on Senate proposals
- Political maneuvering actions
- Content generation for speeches and responses

### PlayerGameLoop (`game_loop.py`)

Orchestrates the overall player game experience:

- Character creation flow
- Senate session initiation with player participation
- Integration with senate simulation systems
- Managing the interactive gameplay loop

### PlayerSenateSession (`game_loop.py`)

Extended version of the standard SenateSession that incorporates player actions:

- Custom debate flow with player speech opportunities
- Interjection opportunities during NPC senator speeches
- Player voting system
- Seamless integration with the core senate simulation

## Gameplay Mechanics

### Character Progression

Players develop their character through gameplay:

- Skills improve through actions (making speeches improves oratory, etc.)
- Special abilities unlock at certain skill thresholds
- Reputation, influence, and wealth change based on actions

### Political Capital

A resource that represents the player's ability to influence events:

- Spent on special actions and interjections
- Gained through successful speeches and political maneuvering
- Limited resource that must be managed strategically

### Speech System

Players can deliver speeches in Senate debates:

1. Choose from generated speech approaches
2. AI generates a full speech based on the chosen approach
3. Impact depends on player's oratory skill and approach
4. Affects relationships with other senators based on content

### Interjection System

Players can interject during other senators' speeches:

1. Choose from generated interjection options
2. Spend political capital to make the interjection
3. Impact depends on player skills and chosen approach
4. Can change relationships and debate outcomes

### Voting

Players vote on Senate proposals:

- Choose to support, oppose, or abstain
- Vote affects relationships with senators on either side
- Contributes to overall debate outcome

### Political Actions

Special actions outside of debates:

- Host private dinners with senators
- Fund public games or buildings
- Form political alliances
- Bribe officials
- Gather information on opponents

## Running the Player Mode

To play the game as a Roman Senator, use the CLI command:

```bash
# Run with default settings
senate play-as-senator

# Customize your experience
senate play-as-senator --senators 12 --topics 4 --year -50
```

This will start the interactive mode where you can:
1. Create your senator character
2. Participate in senate sessions
3. Make speeches and interject during debates
4. Vote on proposals
5. Track your relationships and influence

## Interactive Gameplay Flow

The player gameplay loop follows this sequence:

1. **Character Creation**
   - Choose your name, faction, and background
   - Receive starting attributes based on choices

2. **Senate Session**
   - Attendance and seating based on rank
   - Introduction of topics for debate

3. **Debate Participation**
   - Choose when to speak on topics
   - Select from AI-generated speech approaches
   - Interject during other senators' speeches
   - Build or damage relationships

4. **Voting**
   - Cast your vote on each topic
   - See the outcome and impact on the Republic

5. **Character Progression**
   - Gain experience in various skills
   - Improve relationships with other senators
   - Unlock new abilities as you advance

## Integration

The player system integrates with:

- LLM providers for dynamic content generation
- Debate system for Senate sessions
- NPC senators for relationships and interactions
- Session management for game progression
- Core Senate session mechanics