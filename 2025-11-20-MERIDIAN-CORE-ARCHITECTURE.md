# 2025-11-20 - Meridian Core Architecture (Current State)

**Date:** 2025-11-20  
**Status:** ✅ **PRODUCTION READY**  
**Purpose:** Comprehensive architectural overview of meridian-core framework

---

## Executive Summary

**Meridian Core** is a **domain-agnostic AI orchestration framework** that enables multiple AI models (Claude, GPT-4, Gemini, Grok, Local LLMs) to work together on complex tasks. It provides:

- **Smart Task Allocation**: Automatically matches tasks to the best AI based on capabilities, cost, and workload
- **Multi-AI Consensus**: Voting system for critical decisions
- **Decision Memory**: Learns from past assignments to improve future routing
- **Autonomous Operation**: Runs unattended until work is complete
- **Self-Learning**: Analyzes orchestration decisions to continuously improve

**Key Principle:** Meridian Core is **domain-agnostic** - it works for ANY problem domain (trading, research, customer support, etc.). Domain-specific logic lives in separate adapter repositories.

---

## 1. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MERIDIAN CORE FRAMEWORK                               │
│                    (Domain-Agnostic Orchestration)                            │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                                            │
│  (CLI, Benchmarks, Evaluations, Tools)                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  • CLI commands (orchestrator, learning-dashboard, meta-review)              │
│  • Benchmark tasks for testing                                              │
│  • Quality evaluation tools                                                 │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  LEARNING LAYER                                                               │
│  (Self-Learning, Pattern Detection, Proposal Management)                     │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              LearningEngine (Abstract)                              │      │
│  │  • Abstract base class for self-learning                            │      │
│  │  • Generic workflow: analyze → detect → generate                    │      │
│  │                                                                     │      │
│  │  Implementations:                                                    │      │
│  │  • OrchestrationLearningEngine → Learns from orchestration          │      │
│  │  • MetaReviewLearningEngine → Learns from reviews                   │      │
│  │  • ModelConfigLearningEngine → Learns from model configs            │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              ProposalManager                                        │      │
│  │  • Generic proposal storage (SQLite)                                │      │
│  │  • Status tracking: pending → approved → implemented               │      │
│  │  • Thread-safe with connection pooling                             │      │
│  │  • Database: logs/proposals.db                                     │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              EffectivenessTracker                                   │      │
│  │  • Measures proposal impact                                        │      │
│  │  • Tracks before/after performance                                 │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION LAYER                                                          │
│  (Task Assignment, Voting, Smart Allocation, Meta-Review)                   │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              AIOrchestrator (Base)                                  │      │
│  │  • Base orchestrator class                                         │      │
│  │  • Task queue management                                           │      │
│  │  • Connector initialization                                        │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              AutonomousOrchestrator (Extended)                      │      │
│  │  • Autonomous execution mode                                       │      │
│  │  • Learning cycle integration                                      │      │
│  │  • Session management                                              │      │
│  │                                                                     │      │
│  │  Components:                                                        │      │
│  │  • LearningCycleManager → Manages learning cycles                  │      │
│  │  • AgentSelector → Agent selection and failover                    │      │
│  │  • TaskExecutor → Task execution with retries                      │      │
│  │  • TaskPipelineExecutor → Task routing                             │      │
│  │  • ReviewOrchestrator → Review pipeline coordination               │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              SmartTaskAllocator                                     │      │
│  │  • Intelligent agent-to-task matching                              │      │
│  │  • Capability-based allocation                                     │      │
│  │  • Cost optimization                                               │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              VotingManager                                          │      │
│  │  • Multi-AI consensus voting                                       │      │
│  │  • Convergence detection                                           │      │
│  │  • Voting preferences                                              │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              MetaReviewManager                                      │      │
│  │  • Review pipeline execution                                       │      │
│  │  • Multi-agent review coordination                                 │      │
│  │  • Review quality tracking                                         │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              PreflightManager                                       │      │
│  │  • Resource validation before tasks                                │      │
│  │  • Token availability checks                                       │      │
│  │  • Rate limit validation                                           │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              ProposalApplicator                                     │      │
│  │  • Applies approved proposals                                      │      │
│  │  • Updates allocation weights                                      │      │
│  │  • Updates agent exclusion lists                                   │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  CONNECTOR LAYER                                                              │
│  (8 AI Providers + Local Execution)                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              ConnectorManager                                       │      │
│  │  • Connector initialization                                        │      │
│  │  • Connection pooling                                              │      │
│  │  • Health checks                                                   │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  Cloud AI Connectors:                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  • AnthropicConnector → Claude (Anthropic)                         │      │
│  │  • OpenAIConnector → GPT-4 (OpenAI)                                │      │
│  │  • GeminiConnector → Gemini (Google)                               │      │
│  │  • GrokConnector → Grok (X.AI)                                     │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  Local AI Connectors:                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  • LocalLLMConnector → LM Studio / Ollama                          │      │
│  │  • LocalExecConnector → Local script execution                     │      │
│  │  • CopilotConnector → GitHub Copilot                               │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  Domain-Specific Connectors:                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  • IGConnector → IG Markets (trading domain)                       │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  Supporting:                                                                  │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  • CredentialHelper → Unified credential management                │      │
│  │  • ModelConfigTracker → Tracks model configurations                │      │
│  │  • RateLimiter → Rate limit management                             │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  UTILITY LAYER                                                                │
│  (Shared Utilities, Database, Monitoring)                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              credential_store                                       │      │
│  │  • Unified credential management (keyring)                          │      │
│  │  • Service: meridian-suite (shared across repos)                    │      │
│  │  • Fallback to legacy services                                      │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              Database Models                                        │      │
│  │  • Task, TaskExecution, OrchestrationDecision                      │      │
│  │  • Proposal, LearningProposal                                      │      │
│  │  • SQLAlchemy ORM with connection pooling                          │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              Monitoring                                             │      │
│  │  • Health checks                                                   │      │
│  │  • Metrics collection                                              │      │
│  │  • Performance tracking                                            │      │
│  └────────────────────────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 Orchestration Components

#### AIOrchestrator (Base)
```
Location: src/meridian_core/orchestration/ai_orchestrator.py
Purpose: Base orchestrator class providing core functionality

Key Features:
• Task queue management
• Connector initialization
• Basic task execution
• Configuration management

Methods:
• initialize_connectors()
• execute_task()
• get_task_status()
```

#### AutonomousOrchestrator (Extended)
```
Location: src/meridian_core/orchestration/autonomous_orchestrator.py
Purpose: Extended orchestrator with autonomous capabilities

Key Features:
• Autonomous session execution
• Learning cycle integration
• Advanced task routing
• Multi-agent coordination

Components:
• LearningCycleManager → Manages self-learning cycles
• AgentSelector → Agent selection and failover
• TaskExecutor → Task execution with retries
• TaskPipelineExecutor → Task type routing
• ReviewOrchestrator → Review pipeline coordination

Methods:
• run_autonomous_session()
• should_run_learning_cycle()
• run_learning_cycle()
• select_next_agent()
• failover()
```

### 2.2 Learning Components

#### LearningEngine (Abstract Base)
```
Location: src/meridian_core/learning/learning_engine.py
Purpose: Abstract base class for self-learning

Abstract Methods:
• analyze_performance(period_days) → Dict[str, Any]
• detect_patterns(decisions) → List[Dict[str, Any]]
• generate_hypothesis(pattern) → str

Generic Workflow:
1. analyze_performance() → Metrics
2. detect_patterns() → Patterns
3. generate_hypothesis() → Hypotheses
4. Create proposals via ProposalManager
```

#### OrchestrationLearningEngine (Implementation)
```
Location: src/meridian_core/learning/orchestration_learning_engine.py
Purpose: Learns from orchestration decisions

Data Source:
• logs/orchestration_decisions.db

Analysis:
• Agent success rates
• Task type performance
• Allocation effectiveness

Pattern Detection:
• Agent-task failures
• Task type failures
• Agent overall failures

Hypothesis Generation:
• "Exclude agent X from task type Y"
• "Increase tokens for task type Z"
• "Route task type W to agent V"
```

#### ProposalManager
```
Location: src/meridian_core/learning/proposal_manager.py
Purpose: Generic proposal storage and management

Features:
• SQLite database (logs/proposals.db)
• Status tracking: pending → approved → rejected → implemented → failed
• Thread-safe with connection pooling
• Performance data storage (JSON)

Methods:
• add_proposal(hypothesis, rationale, pattern_id, performance_data)
• get_proposals(status=None)
• update_status(proposal_id, status)
• get_proposal(proposal_id)
```

### 2.3 Connector Components

#### ConnectorManager
```
Location: src/meridian_core/orchestration/connector_manager.py
Purpose: Manages all AI connectors

Features:
• Connector initialization
• Connection pooling
• Health checks
• Credential management

Connectors Managed:
• AnthropicConnector (Claude)
• OpenAIConnector (GPT-4)
• GeminiConnector (Gemini)
• GrokConnector (Grok)
• LocalLLMConnector (LM Studio/Ollama)
• LocalExecConnector (Local execution)
• CopilotConnector (GitHub Copilot)
• IGConnector (IG Markets - domain-specific)
```

#### CredentialHelper / credential_store
```
Location: src/meridian_core/utils/credential_store.py
Purpose: Unified credential management

Features:
• Keyring service: meridian-suite (shared across repos)
• Fallback to legacy services
• Environment variable support (optional)
• Service name mapping (grok → GROK_API_KEY)

Methods:
• get_secret(key_name) → Optional[str]
• set_secret(key_name, value) → bool
• get_secret_by_service(service) → Optional[str]
```

### 2.4 Voting Components

#### VotingManager
```
Location: src/meridian_core/orchestration/voting_manager.py
Purpose: Multi-AI consensus voting

Features:
• Configurable voting system
• Convergence detection
• Voting preferences
• Agent selection via voting

Methods:
• enable_voting(config)
• conduct_vote(question, options, voters)
• vote_select_agent(task, agents)
```

#### VotingSystem
```
Location: src/meridian_core/orchestration/voting.py
Purpose: Core voting logic

Features:
• Borda count voting
• Consensus calculation
• Convergence detection
• Vote result aggregation

Vote Types:
• Agent selection
• Task routing
• Strategy selection
```

---

## 3. Data Flow

### 3.1 Task Execution Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      TASK EXECUTION FLOW                                      │
└──────────────────────────────────────────────────────────────────────────────┘

1. TASK QUEUE INPUT
   ┌──────────────────┐
   │  TASK-QUEUE.json │  → Task queue loaded
   │  or API request  │
   └────────┬─────────┘
            │
            ▼
2. PREFLIGHT CHECKS
   ┌──────────────────┐
   │ PreflightManager │  → Validates resources
   │                  │  → Checks token availability
   │                  │  → Validates rate limits
   └────────┬─────────┘
            │
            ▼
3. AGENT SELECTION
   ┌──────────────────┐
   │  AgentSelector   │  → Selects best agent
   │  or Voting       │  → Based on capabilities
   │                  │  → Cost optimization
   └────────┬─────────┘
            │
            ▼
4. TASK EXECUTION
   ┌──────────────────┐
   │  TaskExecutor    │  → Executes task
   │                  │  → Retries on failure
   │                  │  → Failover logic
   └────────┬─────────┘
            │
            ▼
5. CONNECTOR CALL
   ┌──────────────────┐
   │  Connector       │  → Calls AI provider
   │  (Claude/GPT/etc)│  → Returns response
   └────────┬─────────┘
            │
            ▼
6. RESULT PROCESSING
   ┌──────────────────┐
   │ Result Parser    │  → Parses response
   │                  │  → Validates format
   └────────┬─────────┘
            │
            ▼
7. DECISION LOGGING
   ┌──────────────────┐
   │ Decision Logger  │  → Logs decision
   │                  │  → Stores in database
   └────────┬─────────┘
            │
            ▼
8. LEARNING TRIGGER
   ┌──────────────────┐
   │ Learning Cycle   │  → Checks if learning needed
   │ Manager          │  → Triggers learning cycle
   └──────────────────┘
```

### 3.2 Learning Cycle Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      LEARNING CYCLE FLOW                                      │
└──────────────────────────────────────────────────────────────────────────────┘

1. LEARNING TRIGGER
   ┌──────────────────┐
   │ Learning Cycle   │  → Every 10 tasks (configurable)
   │ Manager          │  → Or after 24 hours
   └────────┬─────────┘
            │
            ▼
2. PERFORMANCE ANALYSIS
   ┌──────────────────┐
   │ Orchestration    │  → Analyzes recent decisions
   │ Learning Engine  │  → Calculates metrics
   │                  │  → Reads from database
   └────────┬─────────┘
            │
            ▼
3. PATTERN DETECTION
   ┌──────────────────┐
   │ Learning Engine  │  → Detects patterns
   │                  │  → Identifies failures
   │                  │  → Finds correlations
   └────────┬─────────┘
            │
            ▼
4. HYPOTHESIS GENERATION
   ┌──────────────────┐
   │ Learning Engine  │  → Generates hypotheses
   │                  │  → Creates proposals
   └────────┬─────────┘
            │
            ▼
5. PROPOSAL STORAGE
   ┌──────────────────┐
   │ ProposalManager  │  → Stores proposals
   │                  │  → Status: pending
   └────────┬─────────┘
            │
            ▼
6. HUMAN REVIEW (Optional)
   ┌──────────────────┐
   │ Human Reviewer   │  → Reviews proposals
   │                  │  → Approves/rejects
   └────────┬─────────┘
            │
            ▼
7. PROPOSAL APPLICATION
   ┌──────────────────┐
   │ ProposalApplicator│ → Applies approved proposals
   │                  │  → Updates configuration
   └────────┬─────────┘
            │
            ▼
8. EFFECTIVENESS TRACKING
   ┌──────────────────┐
   │ Effectiveness    │  → Measures impact
   │ Tracker          │  → Updates metadata
   └──────────────────┘
```

---

## 4. Database Architecture

### 4.1 Main Database (meridian.db)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          meridian.db (SQLite)                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Tables:                                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  Task                                                               │      │
│  │  • id (PK)                                                          │      │
│  │  • title, description                                               │      │
│  │  • status (pending/in_progress/completed/failed)                   │      │
│  │  • created_at, updated_at                                           │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  TaskExecution                                                      │      │
│  │  • id (PK)                                                          │      │
│  │  • task_id (FK)                                                     │      │
│  │  • agent_id                                                         │      │
│  │  • success (boolean)                                                │      │
│  │  • tokens_used                                                      │      │
│  │  • duration_seconds                                                 │      │
│  │  • timestamp                                                        │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  OrchestrationDecision                                              │      │
│  │  • id (PK)                                                          │      │
│  │  • task_id                                                          │      │
│  │  • agent_id                                                         │      │
│  │  • task_type                                                        │      │
│  │  • success (boolean)                                                │      │
│  │  • tokens_used                                                      │      │
│  │  • duration_seconds                                                 │      │
│  │  • timestamp                                                        │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Learning Database (logs/proposals.db)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      logs/proposals.db (SQLite)                               │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Tables:                                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  proposals                                                          │      │
│  │  • id (PK, UUID)                                                    │      │
│  │  • hypothesis (text)                                                │      │
│  │  • rationale (text)                                                 │      │
│  │  • pattern_id (text)                                                │      │
│  │  • status (pending/approved/rejected/implemented/failed)           │      │
│  │  • performance_data (JSON)                                          │      │
│  │  • created_at                                                       │      │
│  │  • reviewed_at                                                      │      │
│  │  • implemented_at                                                   │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Decision Database (logs/orchestration_decisions.db)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│              logs/orchestration_decisions.db (SQLite)                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Tables:                                                                      │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │  orchestration_decisions                                            │      │
│  │  • id (PK)                                                          │      │
│  │  • task_id                                                          │      │
│  │  • agent_id                                                         │      │
│  │  • task_type                                                        │      │
│  │  • success (boolean)                                                │      │
│  │  • tokens_used                                                      │      │
│  │  • duration_seconds                                                 │      │
│  │  • timestamp                                                        │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Component Relationships

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    COMPONENT RELATIONSHIP DIAGRAM                             │
└──────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────┐
                    │  AutonomousOrchestrator │
                    │      (Main Entry)       │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ LearningCycle    │ │ AgentSelector│ │ TaskExecutor │
    │ Manager          │ │              │ │              │
    └────────┬─────────┘ └──────┬───────┘ └──────┬───────┘
             │                  │                 │
             ▼                  ▼                 ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Orchestration    │ │ SmartTask    │ │ Connector    │
    │ Learning Engine  │ │ Allocator    │ │ Manager      │
    └────────┬─────────┘ └──────────────┘ └──────┬───────┘
             │                                     │
             ▼                                     ▼
    ┌──────────────────┐                  ┌──────────────┐
    │ ProposalManager  │                  │ Connectors   │
    │                  │                  │ (8 providers)│
    └────────┬─────────┘                  └──────────────┘
             │
             ▼
    ┌──────────────────┐
    │ ProposalApplicator│
    └──────────────────┘

                    ┌─────────────────────────┐
                    │   VotingManager         │
                    │   (When enabled)        │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   VotingSystem          │
                    │   (Core voting logic)   │
                    └─────────────────────────┘
```

---

## 6. Key Design Patterns

### Pattern 1: Strategy Pattern
```
Task allocation strategies:
• Capability-based allocation
• Cost-optimized allocation
• Load-balanced allocation
• Pluggable scoring algorithms
```

### Pattern 2: Template Method Pattern
```
LearningEngine.run_learning_cycle() (template)
  ├─> analyze_performance() (abstract - domain implements)
  ├─> detect_patterns() (abstract - domain implements)
  └─> generate_hypothesis() (abstract - domain implements)
```

### Pattern 3: Factory Pattern
```
Connector instantiation:
• ConnectorManager.create_connector(type, config)
• Credential management via factory
• Configuration-based connector selection
```

### Pattern 4: Repository Pattern
```
Decision and proposal persistence:
• OrchestrationDecisionRepository
• ProposalRepository
• Database abstraction layer
```

### Pattern 5: Observer Pattern
```
Learning cycle triggers:
• Task completion events
• Time-based triggers
• Configurable thresholds
```

---

## 7. Configuration Management

### Configuration Files

```
meridian-core/
├── allocation_policy.yaml      → Task allocation rules
├── honesty_policy.yaml         → AI honesty framework
├── learning_config.yaml        → Learning cycle configuration
└── connectors_config.yaml      → Connector configurations
```

### Environment Variables

```
# Credential management (via keyring - meridian-suite)
GROK_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
GOOGLE_GEMINI_API_KEY=...
LOCAL_LLM_URL=...

# Optional fallback (ALLOW_ENV_FALLBACK=1)
ALLOW_ENV_FALLBACK=0  # Default: disabled for security
```

---

## 8. CLI Commands

```
meridian-core orchestrator
  → Main orchestrator command
  → Runs autonomous sessions
  → Processes task queues

meridian-core learning dashboard
  → Learning system dashboard
  → Shows proposals
  → Performance metrics

meridian-core meta-review
  → Meta-review system
  → Multi-agent reviews
  → Review quality tracking
```

---

## 9. Integration with Domain Adapters

### How Domain Adapters Use Core

```
Domain Adapter (meridian-trading, meridian-research)
    │
    │ imports from
    ▼
┌─────────────────────────────────────┐
│      meridian-core                  │
│                                     │
│  • AIOrchestrator                   │
│  • LearningEngine (abstract)        │
│  • ProposalManager                  │
│  • Connectors                       │
└─────────────────────────────────────┘
    │
    │ Domain adapter implements
    ▼
┌─────────────────────────────────────┐
│  Domain-Specific Implementation     │
│                                     │
│  • TradingLearningEngine            │
│  • ResearchLearningEngine           │
│  • Domain-specific prompts          │
│  • Domain-specific data             │
└─────────────────────────────────────┘
```

### Dependency Direction

```
✅ CORRECT:
meridian-trading → imports from → meridian-core

❌ WRONG:
meridian-core → imports from → meridian-trading
```

**Rule:** Core never imports from domain adapters. Domain adapters always import from core.

---

## 10. Current Status

### ✅ Completed Components

1. **Core Orchestration**
   - ✅ AIOrchestrator (base)
   - ✅ AutonomousOrchestrator (extended)
   - ✅ SmartTaskAllocator
   - ✅ VotingSystem / VotingManager
   - ✅ PreflightManager

2. **Connectors (8 providers)**
   - ✅ AnthropicConnector (Claude)
   - ✅ OpenAIConnector (GPT-4)
   - ✅ GeminiConnector (Gemini)
   - ✅ GrokConnector (Grok)
   - ✅ LocalLLMConnector (LM Studio/Ollama)
   - ✅ LocalExecConnector
   - ✅ CopilotConnector
   - ✅ IGConnector (domain-specific)

3. **Self-Learning Framework**
   - ✅ LearningEngine (abstract)
   - ✅ ProposalManager
   - ✅ OrchestrationLearningEngine
   - ✅ OrchestrationDataAccess
   - ✅ EffectivenessTracker

4. **Credential Management**
   - ✅ Unified credential_store (meridian-suite)
   - ✅ Keyring integration
   - ✅ Migration scripts

5. **Infrastructure**
   - ✅ Database models (SQLAlchemy)
   - ✅ Connection pooling
   - ✅ Health checks
   - ✅ Monitoring

### ⏳ In Progress / Planned

1. **Learning Integration**
   - ⏳ Automatic learning cycles in orchestrator workflow
   - ⏳ Proposal application mechanism
   - ⏳ Learning effectiveness tracking

2. **Enhanced Features**
   - ⏳ Real-time learning (learn during execution)
   - ⏳ Cross-domain learning
   - ⏳ Dynamic agent capability discovery

---

## 11. Summary

### ✅ Strengths

1. **Domain-Agnostic** - Works for any problem domain
2. **Modular Architecture** - Clean separation of concerns
3. **Self-Learning** - Continuously improves from decisions
4. **Multi-AI Support** - Orchestrates 8+ AI providers
5. **Production Ready** - Comprehensive testing and documentation

### 🎯 Key Principles

1. **Domain-Agnostic Core** - No domain-specific code
2. **Abstract Interfaces** - Domain adapters implement interfaces
3. **Shared Credentials** - Unified credential management
4. **Data-Driven Learning** - All learning based on actual performance
5. **Human-in-the-Loop** - Proposals require approval

### 📋 Next Steps

1. Complete learning integration (TASK-SL-001)
2. Enhanced reporting and dashboards
3. Performance optimization
4. Documentation improvements

---

**Last Updated:** 2025-11-20  
**Status:** ✅ Production Ready  
**Version:** Current State

