# Meta Review Prompt — Meridian Core Backlog

**Context:**  
Meridian Core carries a backlog of critical/high tasks (SQLite migrations, tests, refactors, security) that never received Bastard plan grades. We must determine which are still relevant, how to sequence them, and whether any should be closed or rewritten before we begin execution.

**Tasks in Scope**
- Critical debt: `WS-TASK-026`, `WS-TASK-045`, `WS-TASK-053`.
- Core quality/reliability: `WS-TASK-027`–`WS-TASK-033`, `WS-TASK-046`–`WS-TASK-050`.
- Legacy TODO cleanup: `WS-TASK-034`–`WS-TASK-037`.
- Database/schema: `WS-TASK-005`, `WS-TASK-043`, `WS-TASK-044`.

**Questions for Reviewers**
1. Which tasks remain top priority versus outdated recommendations?
2. What execution order unlocks the most value (e.g., migrate persistence before security hardening)?
3. Can any tasks be merged or rewritten to reduce duplication?
4. For the legacy TODO tasks, should they be converted into new actionable work or closed?
5. Are there prerequisite decisions (e.g., architecture states, tooling) needed before starting each item?

Return a prioritized, modernized plan plus any suggested task closures or rewrites.


