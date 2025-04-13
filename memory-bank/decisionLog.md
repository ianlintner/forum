# Decision Log

## Key Design Decisions

[2025-04-13 18:25:07] - **AI Speech Generation Implementation**

**Decision:** Implement AI-generated debate speeches using OpenAI API with a robust fallback mechanism.

**Rationale:**
- Enhances immersion by providing authentic Roman-style speeches
- Creates more engaging gameplay with varied and contextual debates
- Fallback mechanism ensures game playability even when API is unavailable

**Implementation:**
- Added `generate_speech` function in `debate.py` that uses API with senator context
- Created templated fallback speech generation for offline play
- Implemented stance-based speech coloring for visual clarity

---

[2025-04-13 18:25:07] - **Detailed Voting Results Display**

**Decision:** Enhance voting display with detailed breakdown showing debate stance vs. final vote.

**Rationale:**
- Increases strategic depth by showing which senators can be swayed
- Provides feedback on the impact of debates on voting outcomes
- Creates more engaging and informative endgame statistics

**Implementation:**
- Added detailed voting breakdown table in `main.py`
- Implemented visual indicators for swayed senators
- Modified vote tallying to consider debate stance when determining votes
- Added color coding for different voting positions

---

[2025-04-13 18:25:07] - **Plain English Summaries**

**Decision:** Add plain English summaries explaining each senator's position during debates.

**Rationale:**
- Improves user understanding of complex political stances
- Bridges gap between Latin/formal speech and gameplay mechanics
- Provides clear information on senator motivations and likely votes

**Implementation:**
- Added `generate_position_summary` function in `debate.py`
- Created detailed summaries that explain faction motivations
- Used color coding and clear position tags (FOR/AGAINST/UNDECIDED)