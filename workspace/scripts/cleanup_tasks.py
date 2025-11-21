#!/usr/bin/env python3
"""
Cleanup legacy workspace tasks to align with Strategic Plan Phase 2.5.

This script implements the actions from TASK-CONSOLIDATION-REPORT-2025-11-21
without manually editing SQL.  Run once from the workspace root:

    python workspace/scripts/cleanup_tasks.py
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import sys

SCRIPT_ROOT = Path(__file__).resolve()
WORKSPACE_DIR = SCRIPT_ROOT.parents[1]
PROJECT_ROOT = SCRIPT_ROOT.parents[2]

sys.path.insert(0, str(PROJECT_ROOT))

from workspace.db import WorkspaceDB
from workspace.db.models import WorkspaceTask

TRADING_TASKS = [
    "WS-TASK-002",
    "WS-TASK-004",
    "WS-TASK-007",
    "WS-TASK-038",
    "WS-TASK-039",
    "WS-TASK-040",
    "WS-TASK-041",
]
SUPERSEDED_TASKS = ["WS-TASK-003", "WS-TASK-022", "WS-TASK-025"]
OVERENGINEERED_TASKS = ["WS-TASK-053", "WS-TASK-054"]
MALFORMED_TASKS = ["WS-TASK-010", "WS-TASK-011", "WS-TASK-012", "WS-TASK-013", "WS-TASK-014", "WS-TASK-015", "WS-TASK-016", "WS-TASK-060"]
GOVERNANCE_LOWER_TASKS = ["WS-TASK-017", "WS-TASK-018", "WS-TASK-019", "WS-TASK-020", "WS-TASK-021", "WS-TASK-023", "WS-TASK-024"]
COMPLETED_TODO_TASKS = ["WS-TASK-034", "WS-TASK-035"]


def append_note(task: WorkspaceTask, note: str) -> None:
    existing = task.notes or ""
    if note in existing:
        return
    task.notes = (existing + " | " if existing else "") + note


def update_tasks(
    session,
    ids: Iterable[str],
    *,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    note: Optional[str] = None,
) -> None:
    for task_id in ids:
        task = session.query(WorkspaceTask).filter_by(id=task_id).first()
        if not task:
            continue
        if status:
            task.status = status
        if priority:
            task.priority = priority
        if note:
            append_note(task, note)


def main() -> None:
    workspace_root = PROJECT_ROOT
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()

    try:
        # 1. Delete test data
        test_task = session.query(WorkspaceTask).filter_by(id="WS-TEST-001").first()
        if test_task:
            session.delete(test_task)

        # 2. Mark WS-TASK-001 completed
        tracking_task = session.query(WorkspaceTask).filter_by(id="WS-TASK-001").first()
        if tracking_task:
            tracking_task.status = "completed"
            tracking_task.completed_at = datetime.utcnow()

        # 3. Defer trading tasks
        update_tasks(
            session,
            TRADING_TASKS,
            status="deferred",
            priority="LOW",
            note="DEFERRED: Strategic pivot away from trading. Revisit Phase 3+ if priorities change.",
        )

        # 4. Close superseded tasks
        update_tasks(
            session,
            SUPERSEDED_TASKS,
            status="closed",
            note="CLOSED: Superseded by WMS implementation and workspace database.",
        )

        # 5. Defer over-engineered tasks
        update_tasks(
            session,
            OVERENGINEERED_TASKS,
            status="deferred",
            priority="LOW",
            note="DEFERRED: Over-engineered for current scale. Revisit when team > 5 (Phase 3+).",
        )

        # 6. Close malformed tasks
        update_tasks(
            session,
            MALFORMED_TASKS,
            status="closed",
            note="CLOSED: Malformed task from bulk import. Content captured in governance docs.",
        )

        # 7. Close duplicate testing task
        update_tasks(
            session,
            ["WS-TASK-046"],
            status="closed",
            note="CLOSED: Duplicate of WS-TASK-027.",
        )

        # 8. Close low-priority governance tasks
        update_tasks(
            session,
            GOVERNANCE_LOWER_TASKS,
            status="closed",
            note="CLOSED: WMS governance engine now enforces this automatically.",
        )

        # 9. Close completed TODO tasks
        update_tasks(
            session,
            COMPLETED_TODO_TASKS,
            status="closed",
            note="CLOSED: Already implemented per TODO review.",
        )

        # 10. Update research integration priorities
        update_tasks(
            session,
            ["WS-TASK-006", "WS-TASK-008", "WS-TASK-042"],
            priority="MEDIUM",
        )

        # 11. Close database duplicates and consolidate into WS-TASK-005
        update_tasks(
            session,
            ["WS-TASK-043", "WS-TASK-044"],
            status="closed",
            note="CLOSED: Consolidated into WS-TASK-005 (Database Consolidation).",
        )

        db_task = session.query(WorkspaceTask).filter_by(id="WS-TASK-005").first()
        if db_task:
            db_task.title = "Database Consolidation and WMS Completion"
            db_task.description = (
                "Comprehensive database work: consolidate proposal schemas, migrate JSON sources to SQLAlchemy, "
                "standardize naming, finish WMS CLI/governance integration, and document usage."
            )
            db_task.priority = "HIGH"
            append_note(db_task, "Consolidated task covering WS-TASK-043/044/045 and WMS governance.")

        session.commit()
        print("Cleanup complete.")
    finally:
        session.close()


if __name__ == "__main__":
    main()

