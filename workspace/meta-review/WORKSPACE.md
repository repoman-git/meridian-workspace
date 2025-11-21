# Meta Review Prompt — Workspace Root Tasks

**Context:**  
The workspace management plane (WMS) has numerous governance/ops tasks imported from the 2025‑11‑20 reviews. Many were effectively satisfied by recent automation (session_start enforcement, doc mirroring, architecture index, component mappings), but the tasks in `workspace.db` remain “approved/pending” with no Bastard plan grades. We need a multi-AI review to decide what to keep, close, or rewrite.

**Tasks in Scope**
- `WS-TASK-001` – Implement unified workspace task tracking system.
- `WS-TASK-002/003` – Consolidate task tracking across repos.
- `WS-TASK-010`–`WS-TASK-025` – Governance reminders (component placement, import rules, session protocol, communication patterns, etc.).
- `WS-TASK-025` – Overlaps with `session_start` automation.
- `WS-TASK-051`–`WS-TASK-052` – Governance context + checklist enforcement (likely complete).
- `WS-TEST-001` – Placeholder test task.

**Questions for Reviewers**
1. Which tasks remain actionable after the latest WMS improvements (session checklist, architecture index, doc sync)?
2. For tasks already satisfied, should we close them or replace them with automated verification tests?
3. Are there new workspace-level gaps the old tasks don’t cover (e.g., off-workspace backups, CLI dependency path) that warrant rewriting the backlog?
4. Should tasks 002/003 be reassigned or merged with existing governance tasks?

Please provide recommended statuses (start/close/rewrite) plus any new tasks needed.


