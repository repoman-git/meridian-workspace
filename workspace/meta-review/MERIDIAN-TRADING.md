# Meta Review Prompt — Meridian Trading Self-Learning

**Context:**  
The trading adapter lacks the self-learning stack defined in the architecture reviews. Multiple overlapping tasks (WS-TASK-002/004/007/038–041) remain “approved” with no plan. We need a consolidated, up-to-date execution plan before starting.

**Tasks in Scope**
- `WS-TASK-002`, `WS-TASK-004`, `WS-TASK-007` – High-level “implement trading self-learning.”
- `WS-TASK-038` – Implement TradingLearningEngine extending LearningEngine.
- `WS-TASK-039` – Trading data access layer (`src/meridian_trading/learning/trading_data.py`).
- `WS-TASK-040` – Trading pattern detector.
- `WS-TASK-041` – Nightly learning analysis script.

**Questions for Reviewers**
1. How should we phase the implementation (data access, learning engine, pattern detection, nightly analysis)?
2. What data sources and dependencies must be confirmed (e.g., positions DB, COT feeds, core LearningEngine updates)?
3. Should the existing tasks be merged into a single program with milestones?
4. Are there updated architecture requirements that change scope since 2025-11-20?
5. What acceptance criteria/test strategy ensures the trading learning stack is production-ready?

Return a consolidated plan plus recommendations on merging or closing redundant tasks.


