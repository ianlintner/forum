# Roman Senate Game Component Diagram

```mermaid
graph TB
    subgraph "Core Session Flow"
        SenateSession["SenateSession\n(senate_session.py)"]
    end

    subgraph "Component Modules"
        PO["PresidingOfficials\n(officials.py)"]
        INT["Interjections\n(interjections.py)"]
        PM["PoliticalManeuvering\n(political_maneuvering.py)"]
    end

    subgraph "Session Phases"
        Opening["Opening Ceremonies"]
        Attendance["Attendance & Seating"]
        Agenda["Agenda Introduction"]
        Backroom["Backroom Dealings"]
        Debate["Debate Process"]
        Voting["Voting Process"]
        Adjournment["Session Adjournment"]
    end

    SenateSession --> Opening
    SenateSession --> Attendance
    SenateSession --> Agenda
    SenateSession --> Debate
    SenateSession --> Voting
    SenateSession --> Adjournment
    
    SenateSession --> PO
    SenateSession --> INT
    SenateSession --> PM
    
    PO --> Agenda
    PO --> Debate
    
    INT --> Debate
    
    PM --> Backroom
    Backroom --> Debate
    PM --> Voting
    
    classDef core fill:#f96,stroke:#333,stroke-width:2px;
    classDef component fill:#99ccff,stroke:#333,stroke-width:1px;
    classDef phase fill:#d5f5e3,stroke:#333,stroke-width:1px;
    
    class SenateSession core;
    class PO,INT,PM component;
    class Opening,Attendance,Agenda,Backroom,Debate,Voting,Adjournment phase;
```

This diagram illustrates the relationships between the core SenateSession orchestrator and the specialized component modules, as well as how they interact with the various phases of a Roman Senate session.