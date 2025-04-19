# Senator Relationship System: User Guide

**Author:** Documentation Team  
**Version:** 1.0.0  
**Date:** April 19, 2025

## Table of Contents

- [Introduction](#introduction)
- [Understanding Relationships](#understanding-relationships)
  - [Relationship Types](#relationship-types)
  - [Relationship Values](#relationship-values)
  - [Relationship Decay](#relationship-decay)
- [Using Relationships in Simulations](#using-relationships-in-simulations)
  - [Setting Initial Relationships](#setting-initial-relationships)
  - [Observing Relationship Changes](#observing-relationship-changes)
  - [Relationship-Influenced Decisions](#relationship-influenced-decisions)
- [Command Line Options](#command-line-options)
- [Visualizing Relationships](#visualizing-relationships)
- [Common Scenarios](#common-scenarios)
  - [Political Alliances](#political-alliances)
  - [Personal Rivalries](#personal-rivalries)
  - [Mentor-Mentee Dynamics](#mentor-mentee-dynamics)
  - [Family Connections](#family-connections)
- [Troubleshooting](#troubleshooting)
- [Related Documentation](#related-documentation)

## Introduction

The Senator Relationship System adds a new layer of realism to the Roman Senate simulation by modeling the complex web of relationships between senators. This guide will help you understand how to use and observe these relationships in your simulations.

In the Roman Senate, political decisions were heavily influenced by personal and political relationships. Senators formed alliances, rivalries, mentorships, and family connections that shaped their behavior. The relationship system models these dynamics, allowing for more realistic and nuanced senator behavior.

## Understanding Relationships

### Relationship Types

The system models five types of relationships between senators:

1. **Political** - Represents political alliances and oppositions
   - Changes rapidly based on political actions
   - Heavily influenced by stance alignment and voting patterns
   - Example: Cicero and Caesar had a complex political relationship that shifted over time

2. **Personal** - Represents personal friendship or animosity
   - Changes more slowly than political relationships
   - Influenced by personal interactions and support
   - Example: Despite political differences, some senators maintained personal friendships

3. **Mentor/Mentee** - Represents teaching/learning relationships
   - Very stable, changes slowly
   - Typically forms between senior and junior senators
   - Example: Cicero mentored many younger senators in oratory

4. **Rival** - Represents direct competition or rivalry
   - Moderately stable
   - Can exist alongside positive relationships in other dimensions
   - Example: Cicero and Hortensius were rivals in the courts but respected each other

5. **Family** - Represents family connections
   - Extremely stable, rarely changes
   - Typically set at creation
   - Example: Family connections were crucial in Roman politics

### Relationship Values

Relationship values range from -1.0 (strongest negative) to 1.0 (strongest positive):

- **1.0 to 0.7**: Strong positive relationship (close ally, friend, family)
- **0.7 to 0.3**: Moderate positive relationship (ally, friendly)
- **0.3 to -0.3**: Neutral or weak relationship (acquaintance, colleague)
- **-0.3 to -0.7**: Moderate negative relationship (opponent, dislike)
- **-0.7 to -1.0**: Strong negative relationship (enemy, hatred)

These values influence how senators interact with each other and make decisions.

### Relationship Decay

Relationships naturally decay over time when there are no interactions:

- Each relationship type has a different monthly decay rate:
  - Political: 0.08 per month
  - Personal: 0.04 per month
  - Mentor: 0.02 per month
  - Rival: 0.05 per month
  - Family: 0.01 per month

- Relationships decay toward neutral (0.0)
- Stronger relationships decay faster in absolute terms
- Decay is applied daily based on the number of days elapsed

This decay simulates the natural erosion of relationships over time and encourages ongoing interactions to maintain strong relationships.

## Using Relationships in Simulations

### Setting Initial Relationships

When starting a new simulation, you can set initial relationships between senators:

1. **Using the Configuration File**:
   
   Edit the `senator_relationships.json` file in the `config` directory:

   ```json
   {
     "senator_cicero": {
       "senator_caesar": {
         "political": -0.4,
         "personal": 0.2,
         "mentor": 0.0,
         "rival": 0.5,
         "family": 0.0
       },
       "senator_cato": {
         "political": 0.7,
         "personal": 0.5
       }
     }
   }
   ```

2. **Using the API**:

   ```python
   # Get the senator agent
   cicero = senator_dict["senator_cicero"]
   
   # Set up relationships
   cicero.relationship_manager.update_relationship(
       "senator_caesar", "political", -0.4, "Political rivalry but respect for abilities"
   )
   cicero.relationship_manager.update_relationship(
       "senator_caesar", "personal", 0.2, "Personal respect despite political differences"
   )
   ```

3. **Using the CLI**:

   ```bash
   python -m src.roman_senate.cli set-relationship --senator "senator_cicero" --target "senator_caesar" --type "political" --value -0.4 --reason "Political rivalry"
   ```

### Observing Relationship Changes

During a simulation, relationships change based on interactions:

1. **Console Output**:
   
   With verbose logging enabled, relationship changes are logged to the console:

   ```
   INFO - Relationship changed: Cicero -> Caesar (political) from -0.40 to -0.35 (Supported my proposal on military funding)
   ```

2. **Relationship Network Display**:

   Use the `display-relationships` command to see the current relationship network:

   ```bash
   python -m src.roman_senate.cli display-relationships
   ```

   This will show a table of relationships between all senators.

3. **Relationship History**:

   To view the history of a specific relationship:

   ```bash
   python -m src.roman_senate.cli relationship-history --senator "senator_cicero" --target "senator_caesar" --type "political"
   ```

### Relationship-Influenced Decisions

Relationships influence senator decisions in several ways:

1. **Stance Decisions**:
   - Senators are more likely to align with allies on neutral topics
   - Senators may oppose the positions of rivals
   - Strong relationships can sway neutral positions

2. **Speech Reactions**:
   - Positive relationships increase the chance of positive reactions
   - Negative relationships increase the chance of negative reactions

3. **Interjections**:
   - Allies are more likely to support each other with positive interjections
   - Rivals are more likely to challenge each other

4. **Voting Patterns**:
   - Senators with strong positive relationships tend to vote similarly
   - Senators with strong negative relationships tend to vote oppositely

To observe these influences, watch for stance changes and voting patterns during debates.

## Command Line Options

The CLI provides several commands for working with relationships:

```bash
# Display all relationships
python -m src.roman_senate.cli display-relationships

# Set a relationship
python -m src.roman_senate.cli set-relationship --senator "senator_cicero" --target "senator_caesar" --type "political" --value -0.4 --reason "Political rivalry"

# View relationship history
python -m src.roman_senate.cli relationship-history --senator "senator_cicero" --target "senator_caesar" --type "political"

# Apply time decay
python -m src.roman_senate.cli apply-decay --days 30

# Run simulation with relationship logging
python -m src.roman_senate.cli simulate --log-level INFO --log-relationships
```

## Visualizing Relationships

The system provides several ways to visualize relationships:

1. **Relationship Network Graph**:

   ```bash
   python -m src.roman_senate.cli visualize-relationships --output "relationships.png"
   ```

   This generates a network graph showing relationships between senators.

2. **Relationship Matrix**:

   ```bash
   python -m src.roman_senate.cli relationship-matrix --type "political" --output "political_matrix.csv"
   ```

   This generates a CSV file with a matrix of relationships of the specified type.

3. **Relationship Timeline**:

   ```bash
   python -m src.roman_senate.cli relationship-timeline --senator "senator_cicero" --target "senator_caesar" --output "timeline.png"
   ```

   This generates a timeline showing how a relationship has changed over time.

## Common Scenarios

### Political Alliances

Political alliances are formed and strengthened through:
- Aligned votes on proposals
- Supporting each other's speeches
- Positive interjections during debates

Example scenario:
```
1. Cicero and Cato both vote against a land reform proposal
2. Their political relationship strengthens
3. In future debates, they're more likely to support each other
```

### Personal Rivalries

Personal rivalries develop through:
- Negative reactions to speeches
- Challenging interjections
- Opposing votes on important issues

Example scenario:
```
1. Caesar makes an emotional interjection during Cicero's speech
2. Their personal relationship deteriorates
3. Cicero is more likely to oppose Caesar's proposals in the future
```

### Mentor-Mentee Dynamics

Mentor-mentee relationships develop between senior and junior senators:
- Senior senators guide junior senators
- Junior senators learn from and support senior senators
- These relationships are very stable over time

Example scenario:
```
1. Cicero (senior senator) takes a junior senator under his wing
2. The junior senator supports Cicero's positions
3. Cicero provides guidance and political protection
```

### Family Connections

Family connections are typically set at the start of a simulation:
- Family members generally support each other
- Family connections are extremely stable
- Family ties can override political differences

Example scenario:
```
1. Two senators from the same family have different political views
2. Despite this, they maintain a strong overall relationship
3. They avoid directly opposing each other in public debates
```

## Troubleshooting

### Common Issues

1. **Relationships Not Changing**:
   - Check that the event system is properly configured
   - Ensure that senators are interacting (speeches, votes, etc.)
   - Verify that relationship event handlers are registered

2. **Unexpected Relationship Changes**:
   - Enable verbose logging to see all relationship changes
   - Check event handlers for the specific event types
   - Review the relationship update logic

3. **Relationships Not Persisting**:
   - Ensure the memory persistence system is properly configured
   - Check that relationship memory items are being saved
   - Verify that the memory is being loaded on restart

### Logging Relationships

To enable detailed relationship logging:

```bash
python -m src.roman_senate.cli simulate --log-level DEBUG --log-relationships
```

This will log all relationship changes to the console and log file.

## Related Documentation

- [Relationship System Overview](../relationship_system.md) - General overview of the relationship system
- [Relationship System Design](../senator_relationship_system_design.md) - Detailed design document
- [Developer Guide](developer_guide.md) - Guide for developers extending the relationship system
- [Integration Guide](integration_guide.md) - Guide for integrating with the relationship system
- [Event System Documentation](../event_system/index.md) - Documentation for the event system