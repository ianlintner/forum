---
title: Agent-Driven Simulation User Guide
description: Guide to using the agent-driven simulation feature in the Roman Senate project
author: Roman Senate Project Team
date: April 15, 2025
version: 1.0.0
---

# Agent-Driven Simulation User Guide

## Table of Contents

- [Introduction](#introduction)
- [Key Differences](#key-differences)
- [Running the Simulation](#running-the-simulation)
- [Interpreting the Output](#interpreting-the-output)
  - [Senator Stances](#senator-stances)
  - [Speeches](#speeches)
  - [Voting](#voting)
  - [Relationships](#relationships)
- [Configuration Options](#configuration-options)
- [Examples](#examples)

## Introduction

The agent-driven simulation introduces a new approach to the Roman Senate simulation where senators function as autonomous agents with memory, goals, and decision-making capabilities. This creates a more dynamic and realistic simulation where senators' actions are influenced by their personality traits, factional allegiances, and ongoing relationships with other senators.

In this simulation, senators:
- Remember past debates and votes
- Form relationships with other senators
- Make decisions based on a combination of factors
- Provide reasoning for their decisions
- Change their behavior over time as relationships evolve

## Key Differences

| Traditional Simulation | Agent-Driven Simulation |
|------------------------|-------------------------|
| Senators make decisions based on predetermined factors | Senators autonomously decide positions based on multiple factors |
| No memory of past interactions | Persistent memory of past debates, votes, and interactions |
| Static relationships | Dynamic relationships that evolve based on voting patterns |
| Limited reasoning for decisions | Detailed reasoning for stances, speeches, and votes |
| Predictable patterns | Emergent behavior leading to more varied outcomes |

## Running the Simulation

To run the agent-driven simulation, use the `simulate` command from the command line interface (agent-driven is now the default):

```bash
senate simulate [OPTIONS]
```

### Basic Usage

```bash
# Run with default settings (10 senators, 3 topics, 3 debate rounds, year 100 BCE)
senate simulate
```
### With Custom Options

```bash
# Run with custom settings
senate simulate --senators 15 --topics 5 --debate-rounds 4 --year -50 --provider openai
```

### Running Traditional Simulation

To use the traditional (non-agent) simulation approach:

```bash
senate simulate --traditional
```
```

## Interpreting the Output

The agent simulation provides rich output that displays the internal workings of senators' decision-making processes and the evolving relationships between them.

### Senator Stances

When a new topic is introduced, each senator determines their stance:

```
DEBATE TOPIC: Should Rome expand its fleet to counter Carthaginian naval power?
CATEGORY: Military

Senators are considering their positions...
• Marcus Tullius (Optimates) takes a for position:
  As a member of the Optimates faction, I believe naval expansion is necessary to protect Rome's interests and maintain our dominance in the Mediterranean.
• Gaius Gracchus (Populares) takes an against position:
  The cost would fall heavily on common citizens while primarily benefiting wealthy merchants and patricians. Our focus should be on land reforms.
```

The stance includes the senator's reasoning, providing insight into their thought process based on faction, personality, and past experiences.

### Speeches

During debate rounds, senators deliver speeches that reflect their stance and rhetorical approach:

```
DEBATE ROUND 1

Marcus Tullius (Optimates) | FOR:
Esteemed colleagues, the shadow of Carthage looms ever larger on our horizon. Their ships multiply like locusts across the Mediterranean, threatening our trade and our allies. Rome must respond with equal strength on the seas, lest we find ourselves at the mercy of foreign navies. I urge you to support this expansion for the glory and security of Rome!
(Rhetorical approach: Used appeals to fear and patriotism to convince the Senate of the urgent threat)
```

Each speech is followed by a note on the rhetorical approach, showing how the senator strategically crafted their argument.

### Voting

When voting begins, senators cast their votes with accompanying reasoning:

```
VOTING BEGINS
• Marcus Tullius votes for:
  Consistent with my for stance on this issue.
• Gaius Gracchus votes against:
  The proposed naval expansion serves patrician interests while neglecting the needs of common citizens.

VOTE RESULT: PASSED (6 to 4)
```

Senators who were neutral during debate must make a final decision, and their reasoning reveals their thought process in making the final choice.

### Relationships

After all topics are debated, the simulation displays the evolving relationships between senators:

```
===== SENATOR RELATIONSHIPS =====
A simple visualization of senator relationships based on voting patterns:

Marcus Tullius (Optimates)
  Allies: Quintus Catulus (+0.6), Appius Claudius (+0.4), Lucius Crassus (+0.2)
  Rivals: Gaius Gracchus (-0.3), Tiberius Gracchus (-0.3)

Gaius Gracchus (Populares)
  Allies: Tiberius Gracchus (+0.8), Lucius Drusus (+0.4)
  Rivals: Marcus Tullius (-0.3), Quintus Catulus (-0.5)
```

These relationships are formed based on voting patterns - senators who frequently vote the same way develop positive relationships, while those who oppose each other develop rivalries.

## Configuration Options

The agent simulation can be configured with several command-line options:

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--senators` | Number of senators to simulate | 10 | `--senators 15` |
| `--debate-rounds` | Number of debate rounds per topic | 3 | `--debate-rounds 4` |
| `--topics` | Number of topics to debate | 3 | `--topics 5` |
| `--year` | Year in Roman history (negative for BCE) | -100 | `--year -50` |
| `--provider` | LLM provider to use | (from config) | `--provider openai` |

## Examples

### Example 1: Small Senate with Many Topics

For a more focused simulation with deeper relationship development:

```bash
senate agent --senators 6 --topics 8 --debate-rounds 3 --year -55
```

This creates a small senate where relationships will develop more quickly due to multiple voting interactions.

### Example 2: Large Senate in Early Republic

For a broader simulation set in the early Republic period:

```bash
senate agent --senators 20 --topics 4 --debate-rounds 2 --year -450
```

This simulates a larger senate with topics relevant to the early Republic, with fewer debate rounds for faster completion.

### Example 3: Late Republic Political Crisis

To simulate the contentious late Republic period:

```bash
senate agent --senators 15 --topics 3 --debate-rounds 4 --year -50
```

This focuses on deeper debates (4 rounds) during the politically volatile period of the late Republic.