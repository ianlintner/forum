# Narrative System Event Flow

```mermaid
flowchart TD
    subgraph "Initialization"
        A[Game State] --> B[NarrativeEngine]
        C[LLM Provider] --> B
        B --> D[Initialize EventManager]
        B --> E[Initialize NarrativeContext]
        D --> F[Register Event Generators]
        D --> G[Register Event Processors]
    end

    subgraph "Event Generation"
        H[Generate Daily Narrative] --> I[EventManager.generate_events]
        I --> J[DailyEventGenerator]
        I --> K[RumorEventGenerator]
        I --> ML[MilitaryEventGenerator]
        I --> RL[ReligiousEventGenerator]
        I --> SL[SenatorEventGenerator]
        J --> N[Create Daily Events]
        K --> O[Create Rumors]
        ML --> MP[Create Military Events]
        RL --> RP[Create Religious Events]
        SL --> SP[Create Senator Events]
        N --> Q[Raw Events]
        O --> Q
        MP --> Q
        RP --> Q
        SP --> Q
    end

    subgraph "Event Processing"
        Q --> R[Process Each Event]
        R --> S[ConsistencyProcessor]
        S --> T[RelationshipProcessor]
        T --> U[Processed Events]
    end

    subgraph "Integration"
        U --> V[Add to NarrativeContext]
        V --> W[Update Recurring Entities]
        V --> X[Update Narrative Themes]
        V --> Y[Integrate with Game State]
        Y --> Z[Convert to Historical Events]
        Z --> AA[Add to Game State]
    end

    subgraph "Story Crier Integration"
        AB[StoryCrierAgent] --> AC[Request Narrative Content]
        AC --> AD[NarrativeEngine.generate_daily_narrative]
        AD --> AE[Format Announcements]
        AE --> AF[Display to Player]
    end

    AA --> AB