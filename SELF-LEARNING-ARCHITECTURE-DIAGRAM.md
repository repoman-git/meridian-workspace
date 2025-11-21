# 2025-11-20 - Self-Learning Architecture Diagram

**Date:** 2025-11-20  
**Purpose:** Visual representation of the self-learning architecture across Meridian repos

---

## 1. High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MERIDIAN SELF-LEARNING SYSTEM                        │
│                          (Multi-Domain Learning)                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           meridian-core                                      │
│                    (Foundation Layer - Generic)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    LearningEngine (Abstract)                        │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │  Abstract Methods:                                           │  │    │
│  │  │    • analyze_performance(period_days) → Dict[str, Any]       │  │    │
│  │  │    • detect_patterns(decisions) → List[Dict[str, Any]]       │  │    │
│  │  │    • generate_hypothesis(pattern) → str                       │  │    │
│  │  │  Generic Workflow:                                            │  │    │
│  │  │    • run_learning_cycle(period_days)                          │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                              ↑ extends                                       │
│                              │                                               │
│  ┌──────────────────────────┴───────────────────────────────────────────┐  │
│  │            Concrete Implementations in Core                           │  │
│  │  ┌───────────────────────────────────────────────────────────────┐   │  │
│  │  │ OrchestrationLearningEngine                                    │   │  │
│  │  │  • Analyzes orchestrator decisions                             │   │  │
│  │  │  • Detects agent/task failure patterns                         │   │  │
│  │  │  • Proposes allocation improvements                            │   │  │
│  │  │  Data Source: orchestration_decisions.db                       │   │  │
│  │  └───────────────────────────────────────────────────────────────┘   │  │
│  │  ┌───────────────────────────────────────────────────────────────┐   │  │
│  │  │ MetaReviewLearningEngine                                       │   │  │
│  │  │  • Analyzes meta-review results                                │   │  │
│  │  │  • Detects review quality patterns                             │   │  │
│  │  └───────────────────────────────────────────────────────────────┘   │  │
│  │  ┌───────────────────────────────────────────────────────────────┐   │  │
│  │  │ ModelConfigLearningEngine                                      │   │  │
│  │  │  • Analyzes model configuration performance                    │   │  │
│  │  │  • Detects optimal model settings                              │   │  │
│  │  └───────────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    ProposalManager                                  │    │
│  │  • Generic proposal storage (SQLite + SQLAlchemy)                  │    │
│  │  • Status tracking: pending → approved → implemented               │    │
│  │  • Thread-safe with connection pooling                             │    │
│  │  • Database: logs/proposals.db                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              OrchestrationDataAccess                                │    │
│  │  • Extracts orchestration decision data                            │    │
│  │  • Queries: decisions, agent performance, task performance         │    │
│  │  • Database: logs/orchestration_decisions.db                       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                              ↑ imports from
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐   ┌───────────────────┐
        │ meridian-research │   │ meridian-trading  │
        │  (Domain Adapter) │   │  (Domain Adapter) │
        └───────────────────┘   └───────────────────┘
```

---

## 2. Domain Adapter Learning Architecture

### meridian-research Implementation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        meridian-research                                     │
│                    (Research Domain Adapter)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    ResearchEngine                                   │    │
│  │  • Executes research queries                                        │    │
│  │  • Coordinates multi-AI research                                    │    │
│  │  • Generates research reports                                       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              │ records result                                 │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                   LearningBridge                                    │    │
│  │  • Bridge to meridian-core's LearningEngine                        │    │
│  │  • Imports: from meridian_core.learning.learning_engine            │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │  ResearchLearningEngine(LearningEngine)                       │  │    │
│  │  │    • analyze_performance() → Research metrics                 │  │    │
│  │  │    • detect_patterns() → Agent/skill effectiveness            │  │    │
│  │  │    • generate_hypothesis() → Improvement suggestions          │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              │ stores data                                   │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                   SessionStore                                      │    │
│  │  • Stores research sessions (JSON files)                           │    │
│  │  • Location: data/learning/sessions/*.json.enc                     │    │
│  │  • Includes: query, skill, confidence, agents, findings            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              │ creates proposals                             │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              ProposalManager (from meridian-core)                   │    │
│  │  • Uses shared proposal database                                   │    │
│  │  • Stores proposals in: logs/proposals.db                          │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              MLPatternDetector                                      │    │
│  │  • ML-based pattern detection (optional)                            │    │
│  │  • Agent performance patterns                                       │    │
│  │  • Skill effectiveness patterns                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              ResearchFeedbackBridge                                 │    │
│  │  • Bridge to meridian-core's feedback system                       │    │
│  │  • Records user feedback on research quality                        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### meridian-trading Implementation (PLANNED)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        meridian-trading                                      │
│                     (Trading Domain Adapter)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    Trading System                                   │    │
│  │  • Executes trades                                                  │    │
│  │  • Manages positions                                                │    │
│  │  • Calculates performance metrics                                   │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              │ records trades                                │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                   LearningBridge (PLACEHOLDER)                      │    │
│  │  ⚠️  Currently only bridge.py exists                                │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │  TradingLearningEngine(LearningEngine)  ❌ NOT IMPLEMENTED    │  │    │
│  │  │    • analyze_performance() → Trading metrics (Sharpe, etc.)  │  │    │
│  │  │    • detect_patterns() → TDOM, losing streaks, etc.          │  │    │
│  │  │    • generate_hypothesis() → Strategy improvements            │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              │ should store data                             │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              TradingData (TO BE CREATED)                           │    │
│  │  ❌ NOT IMPLEMENTED                                                │    │
│  │  • Should access: data/positions.db                                │    │
│  │  • Should query: trades, positions, market data                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              │ should create proposals                       │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              ProposalManager (from meridian-core)                   │    │
│  │  • Would use shared proposal database                               │    │
│  │  • Would store proposals in: logs/proposals.db                      │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              TradingPatternDetector (TO BE CREATED)                 │    │
│  │  ❌ NOT IMPLEMENTED                                                │    │
│  │  • TDOM pattern detection                                           │    │
│  │  • Losing streak detection                                          │    │
│  │  • Strategy-specific patterns                                       │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           LEARNING CYCLE DATA FLOW                            │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: DATA COLLECTION                                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │ Orchestrator │    │   Research   │    │   Trading    │                  │
│  │   Decisions  │    │   Reports    │    │    Trades    │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│         │                    │                    │                           │
│         ▼                    ▼                    ▼                           │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │                   Database Storage                                 │      │
│  │  • orchestration_decisions.db (core)                              │      │
│  │  • data/learning/sessions/*.json.enc (research)                   │      │
│  │  • data/positions.db (trading - when implemented)                 │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Learning Cycle Triggered
                                    │ (Every 10 tasks or scheduled)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 2: ANALYSIS                                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              LearningEngine.run_learning_cycle()                   │      │
│  │                                                                   │      │
│  │  1. analyze_performance(period_days)                              │      │
│  │     └─> Reads data from database                                  │      │
│  │     └─> Calculates metrics (success rates, confidence, etc.)      │      │
│  │                                                                   │      │
│  │  2. detect_patterns(decisions/trades/reports)                     │      │
│  │     └─> Analyzes data for patterns                                │      │
│  │     └─> Examples:                                                  │      │
│  │         • "Agent X fails 60% on task type Y"                      │      │
│  │         • "Claude performs best for security queries"             │      │
│  │         • "Losing trades cluster at 2-4 PM"                       │      │
│  │                                                                   │      │
│  │  3. generate_hypothesis(pattern)                                  │      │
│  │     └─> Creates improvement hypothesis                            │      │
│  │     └─> Examples:                                                  │      │
│  │         • "Exclude agent X from task type Y"                      │      │
│  │         • "Route security queries to Claude"                      │      │
│  │         • "Avoid trading 2-4 PM"                                  │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Hypothesis generated
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 3: PROPOSAL CREATION                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ProposalManager.add_proposal()                        │      │
│  │                                                                   │      │
│  │  Creates Proposal object:                                         │      │
│  │  {                                                                │      │
│  │    id: "uuid",                                                    │      │
│  │    hypothesis: "Exclude agent X from task type Y",                │      │
│  │    rationale: "Agent X fails 60% of the time...",                 │      │
│  │    pattern_id: "agent-task-failure-123",                          │      │
│  │    status: "pending",                                             │      │
│  │    performance_data: {...}                                        │      │
│  │  }                                                                │      │
│  │                                                                   │      │
│  │  Stores in: logs/proposals.db                                     │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Proposal stored
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 4: PROPOSAL REVIEW (Human-in-the-Loop)                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              Human Reviews Proposals                               │      │
│  │                                                                   │      │
│  │  CLI Commands:                                                     │      │
│  │  • meridian-core learning dashboard --show-proposals              │      │
│  │  • meridian-research learn proposals                              │      │
│  │                                                                   │      │
│  │  Actions:                                                          │      │
│  │  • Approve → status = "approved"                                  │      │
│  │  • Reject → status = "rejected"                                   │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Proposal approved
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 5: PROPOSAL APPLICATION                                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              ProposalApplicator.apply_proposals()                  │      │
│  │                                                                   │      │
│  │  • Auto-applies at session start (meridian-core)                  │      │
│  │  • Updates allocation weights                                     │      │
│  │  • Updates agent exclusion lists                                   │      │
│  │  • Updates routing rules                                           │      │
│  │                                                                   │      │
│  │  Status updated: "implemented"                                    │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Proposal implemented
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: EFFECTIVENESS TRACKING                                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────┐      │
│  │              EffectivenessTracker.track()                          │      │
│  │                                                                   │      │
│  │  • Measures improvement after proposal implementation             │      │
│  │  • Tracks success rates before/after                              │      │
│  │  • Updates proposal metadata with results                          │      │
│  └───────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Feedback loop
                                    ▼
                            ┌───────────────┐
                            │   New Data    │
                            │   Collected   │
                            └───────┬───────┘
                                    │
                            (Cycle repeats)
```

---

## 4. Database Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE ARCHITECTURE                                │
└──────────────────────────────────────────────────────────────────────────────┘

meridian-core/
├── meridian.db (Main Database - SQLAlchemy)
│   ├── Task                    # Task tracking
│   ├── TaskExecution           # Task execution results
│   ├── OrchestrationDecision   # Orchestration decisions
│   ├── Proposal                # Learning proposals (schema 1)
│   ├── LearningProposal        # Learning proposals (schema 2) ⚠️ Duplicate?
│   └── TaskCompletion          # Task completion tracking
│
├── logs/proposals.db (Proposal Database)
│   └── proposals               # Managed by ProposalManager
│       • id (PK)
│       • hypothesis
│       • rationale
│       • pattern_id
│       • status (pending/approved/rejected/implemented/failed)
│       • performance_data (JSON)
│       • created_at, reviewed_at, implemented_at
│
├── logs/orchestration_decisions.db (Decision Tracking)
│   └── orchestration_decisions
│       • id (PK)
│       • task_id
│       • agent_id
│       • task_type
│       • success (boolean)
│       • tokens_used
│       • duration_seconds
│       • timestamp
│
└── logs/decisions.db (Decision Memory Graph)
    └── voting_sessions         # Used by DecisionMemoryGraph
        • Voting sessions
        • Decision relationships

meridian-research/
├── meridian.db (Main Database)
│   ├── KnowledgeEntry          # Research knowledge base
│   └── ProjectTask             # Task tracking
│
├── meridian_research_tasks.db (Tasks Database)
│   └── (Unclear purpose - needs documentation)
│
└── data/learning/sessions/     # Session Storage (JSON Files)
    └── *.json.enc              # Encrypted research sessions
        • session_id
        • query
        • skill_used
        • confidence
        • agents_used
        • findings

meridian-trading/
├── meridian.db (Main Database)
│   └── (Basic structure)
│
└── data/positions.db (Trading Positions)
    └── positions               # Trading positions data
        • (Schema needs verification)

⚠️  ISSUE: Duplicate Proposal Schemas
    • Proposal table (in meridian.db and proposals.db)
    • LearningProposal table (different schema)
    → Needs consolidation or documentation
```

---

## 5. Component Relationships

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT RELATIONSHIP DIAGRAM                           │
└──────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────┐
                    │   meridian-core         │
                    │   (Foundation)          │
                    └─────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
        ┌───────────▼───────────┐  ┌───▼────────────────┐
        │                       │  │                    │
        │  LearningEngine       │  │  ProposalManager   │
        │  (Abstract Base)      │  │  (Generic)         │
        │                       │  │                    │
        │  • run_learning_cycle │  │  • add_proposal()  │
        │  • analyze_performance│  │  • get_proposals() │
        │  • detect_patterns    │  │  • update_status() │
        │  • generate_hypothesis│  │                    │
        └───────────┬───────────┘  └────────────────────┘
                    │                   │
        ┌───────────┴───────────┐       │
        │                       │       │ uses
        │  Orchestration        │       │
        │  LearningEngine       │       │
        │  (extends)            │       │
        └───────────┬───────────┘       │
                    │                   │
                    │ implements        │
                    │                   │
        ┌───────────┴───────────────────┴───────────┐
        │                                           │
        ▼                                           ▼
┌───────────────────┐                    ┌───────────────────┐
│ meridian-research │                    │ meridian-trading  │
└───────────────────┘                    └───────────────────┘
         │                                         │
         │ extends                                 │ extends (PLANNED)
         ▼                                         ▼
┌───────────────────┐                    ┌───────────────────┐
│ ResearchLearning  │                    │ TradingLearning   │
│ Engine            │                    │ Engine            │
│                   │                    │ ❌ NOT IMPLEMENTED │
│ ✅ Implemented    │                    │                   │
│                   │                    │ Only bridge.py    │
│ • Uses core's     │                    │ exists            │
│   ProposalManager │                    └───────────────────┘
│                   │
│ • Stores sessions │
│   in JSON         │
│                   │
│ • Uses core's     │
│   LearningEngine  │
└───────────────────┘
```

---

## 6. Learning Cycle Flow (Detailed)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      DETAILED LEARNING CYCLE FLOW                             │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  TRIGGER: Learning Cycle Starts                                              │
│  • Every 10 tasks (configurable)                                             │
│  • After 24 hours                                                            │
│  • Manual trigger via CLI                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │  LearningEngine           │
                    │  .run_learning_cycle()    │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
    ┌───────────────────────────────┐  ┌───────────────────────────────┐
    │  Domain Implementation:       │  │  Domain Implementation:       │
    │                               │  │                               │
    │  OrchestrationLearningEngine  │  │  ResearchLearningEngine       │
    │  .analyze_performance()       │  │  .analyze_performance()       │
    └───────────────┬───────────────┘  └───────────────┬───────────────┘
                    │                                   │
                    │ Reads from                        │ Reads from
                    ▼                                   ▼
    ┌───────────────────────────────┐  ┌───────────────────────────────┐
    │  orchestration_decisions.db   │  │  data/learning/sessions/      │
    │                               │  │  *.json.enc                   │
    │  • Agent performance          │  │                               │
    │  • Task type performance      │  │  • Research reports           │
    │  • Success/failure rates      │  │  • Confidence scores          │
    │  • Token usage                │  │  • Agent usage                │
    └───────────────┬───────────────┘  └───────────────┬───────────────┘
                    │                                   │
                    │ Calculates metrics                │ Calculates metrics
                    ▼                                   ▼
    ┌───────────────────────────────┐  ┌───────────────────────────────┐
    │  Returns:                     │  │  Returns:                     │
    │  {                            │  │  {                            │
    │    "agent_success_rates": {}, │  │    "avg_confidence": 0.85,    │
    │    "task_type_metrics": {},   │  │    "agent_performance": {},   │
    │    "overall_stats": {}        │  │    "skill_effectiveness": {}  │
    │  }                            │  │  }                            │
    └───────────────┬───────────────┘  └───────────────┬───────────────┘
                    │                                   │
                    │ Calls                             │ Calls
                    ▼                                   ▼
    ┌───────────────────────────────┐  ┌───────────────────────────────┐
    │  .detect_patterns()           │  │  .detect_patterns()           │
    │                               │  │                               │
    │  Detects:                     │  │  Detects:                     │
    │  • Agent-task failures        │  │  • Agent specialization       │
    │  • Task type failures         │  │  • Skill effectiveness        │
    │  • Agent overall failures     │  │  • Query categorization       │
    └───────────────┬───────────────┘  └───────────────┬───────────────┘
                    │                                   │
                    │ For each pattern                  │ For each pattern
                    ▼                                   ▼
    ┌───────────────────────────────┐  ┌───────────────────────────────┐
    │  .generate_hypothesis()       │  │  .generate_hypothesis()       │
    │                               │  │                               │
    │  Generates:                   │  │  Generates:                   │
    │  • "Exclude agent X..."       │  │  • "Route security to..."     │
    │  • "Increase tokens for..."   │  │  • "Review skill X..."        │
    └───────────────┬───────────────┘  └───────────────┬───────────────┘
                    │                                   │
                    │ Creates proposals                 │ Creates proposals
                    ▼                                   ▼
                    ┌───────────────────┐
                    │  ProposalManager  │
                    │  .add_proposal()  │
                    └─────────┬─────────┘
                              │
                              │ Stores in
                              ▼
                    ┌───────────────────┐
                    │  logs/proposals.db │
                    │  (Shared database) │
                    └───────────────────┘
                              │
                              │ Status: "pending"
                              ▼
                    ┌───────────────────┐
                    │  Human Review     │
                    │  (approve/reject) │
                    └─────────┬─────────┘
                              │
                              │ Status: "approved"
                              ▼
                    ┌───────────────────┐
                    │  ProposalApplicator│
                    │  .apply_proposals()│
                    └─────────┬─────────┘
                              │
                              │ Applies changes
                              │ Status: "implemented"
                              ▼
                    ┌───────────────────┐
                    │  Effectiveness    │
                    │  Tracking         │
                    └───────────────────┘
```

---

## 7. Current Implementation Status

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      IMPLEMENTATION STATUS MATRIX                             │
└──────────────────────────────────────────────────────────────────────────────┘

Component                          Core    Research  Trading  Status
───────────────────────────────────────────────────────────────────────────────
LearningEngine (Abstract)          ✅      ✅        ✅       Complete
ProposalManager                    ✅      ✅        ❌       Core+Research
OrchestrationLearningEngine        ✅      N/A       N/A      Complete
ResearchLearningEngine             N/A     ✅        N/A      Complete
TradingLearningEngine              N/A     N/A       ❌       Not Started
Data Access Layer                  ✅      ✅        ❌       Core+Research
Pattern Detection                  ✅      ✅        ❌       Core+Research
Proposal Application               ✅      ⚠️        ❌       Core (partial)
Effectiveness Tracking             ✅      ⚠️        ❌       Core (partial)
Learning Cycles                    ✅      ✅        ❌       Core+Research
CLI Commands                       ✅      ✅        ❌       Core+Research
Database Integration               ✅      ⚠️        ❌       Core (partial)

Legend:
✅ = Fully Implemented
⚠️  = Partially Implemented
❌ = Not Implemented
N/A = Not Applicable
```

---

## 8. Key Architecture Patterns

### Pattern 1: Bridge Pattern
```
Domain Adapter → Bridge → Core Framework

Example:
meridian-research/src/meridian_research/learning/bridge.py
  → imports from meridian_core.learning.learning_engine
  → Extends LearningEngine
  → Implements domain-specific methods
```

### Pattern 2: Template Method Pattern
```
LearningEngine.run_learning_cycle() (template)
  ├─> analyze_performance() (abstract - domain implements)
  ├─> detect_patterns() (abstract - domain implements)
  └─> generate_hypothesis() (abstract - domain implements)
```

### Pattern 3: Strategy Pattern
```
Different learning engines for different domains:
  • OrchestrationLearningEngine (framework learning)
  • ResearchLearningEngine (research learning)
  • TradingLearningEngine (trading learning - planned)
```

---

## 9. Summary

### ✅ Strengths
1. **Clean Architecture** - Foundation layer (core) + domain adapters
2. **Reusable Framework** - Abstract base classes work for any domain
3. **Data-Driven Learning** - All learning based on actual performance data
4. **Human-in-the-Loop** - Proposals require approval before implementation
5. **Effectiveness Tracking** - Measures if proposals actually improve performance

### ⚠️ Gaps
1. **meridian-trading** - Self-learning not implemented
2. **Database Consolidation** - Multiple proposal schemas need clarification
3. **Integration Verification** - Need to verify research learning fully integrates with core

### 🎯 Next Steps
1. Implement meridian-trading self-learning
2. Consolidate database schemas
3. Verify end-to-end learning cycles work
4. Improve documentation

---

**Last Updated:** 2025-11-20  
**Status:** Visual Architecture Complete

