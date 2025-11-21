# Workspace Task Triage — 2025-11-21

Goal: identify tasks without a Bastard plan grade, decide whether to **start immediately** or **route to meta-review**. Tasks with existing Bastard grades (WS-TASK-055/056/057) are excluded.

## Triage Summary

| Bucket | Task IDs | Priority | Recommended Action | Rationale |
| --- | --- | --- | --- | --- |
| Critical architecture debt | WS-TASK-026, 045, 053 | CRITICAL / HIGH | Start immediately | These unblock code-to-architecture enforcement and core stability. They already have clear scope; no meta review needed. |
| Core quality & reliability | WS-TASK-027‒033, 046‒050 | HIGH | Meta review first | Large refactors/tests need updated scope before starting; run meta review to confirm relevance and sequence. |
| Trading learning backlog | WS-TASK-002, 004, 007, 038‒041 | HIGH | Meta review | Requirements pre-date recent architecture work. Meta review across multiple AIs to confirm data sources and plan. |
| Research integration tasks | WS-TASK-006, 008, 042 | MEDIUM | Meta review | Need validation of current integration state before committing work. |
| Governance reminders (2025-11-20 recommendations) | WS-TASK-010‒025, 051‒052 | MEDIUM | Close or mark as completed after verification | Many already satisfied (session checklist, doc index, governance enforcement). Verify quickly; if satisfied, complete. |
| Database / documentation | WS-TASK-005, 043, 044 | MEDIUM | Start (mini-spike) | Small scoped analysis/documentation updates still needed to finish the migration story. |
| Legacy TODO tracking | WS-TASK-034‒037 | HIGH | Meta review → close or rewrite | Items reference TODO_REVIEW.md; confirm relevance via meta review, then either drop or convert to modern tasks. |
| Misc governance/ops | WS-TASK-017‒024, 025 | MEDIUM | Close or merge into newer tasks | Redundant with current session protocols. Quick audit then close. |
| Test placeholder | WS-TEST-001 | HIGH (test) | Close | Only a DB test seed; mark complete. |

## Immediate Next Steps
1. **Start critical tasks** (26, 45, 53): draft plans and run `workflow.start_task` to capture Bastard grades.
2. **Prepare meta review packets** for:
   - Trading learning suite (002/004/007/038‒041)
   - Research integration (006/008/042)
   - Core quality set (027‒033, 046‒050)
   - Legacy TODOs (034‒037)
3. **Audit governance reminders** (010‒025, 051‒052) against current implementation (session_start, doc index, sync scripts). Mark completed where applicable.
4. **Close WS-TEST-001** after confirming it’s purely a seed record.

Document any decisions and update task statuses in WMS so the backlog reflects reality. Once plans are ready, use the helper workflow (start/complete) to engage Bastard for each live task.***


