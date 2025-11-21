# Workspace Management Plane

**Management plane database for cross-repo workspace tracking.**

REPO: workspace (management plane)  
LAYER: Management Plane  
PURPOSE: Workspace-level task tracking, architecture tracking, drift detection  
DOMAIN: Cross-repo workspace management

---

## Overview

This module provides the **management plane** database for workspace tracking. It uses SQLAlchemy + SQLite following meridian-core patterns.

### What It Does

- **Unified Task Tracking** - Track tasks across all repos in one place
- **Session Management** - Track workspace sessions and activities
- **Cross-Repo Issues** - Track issues that span multiple repos
- **Architecture Decisions** - Log all architecture decisions
- **Drift Detection** - Track configuration drift violations
- **Context Management** - Track which repo you're working in

---

## Installation

### Dependencies

Because the system Python install is marked as “externally managed” (PEP 668), install the WMS dependencies in a local virtual environment:

```bash
cd /Users/simonerses/data-projects
python3 -m venv workspace/.venv
workspace/.venv/bin/python -m pip install -r workspace/requirements.txt
# WMS CLI also needs click:
workspace/.venv/bin/python -m pip install click
```

All subsequent commands in this README can be run with `workspace/.venv/bin/python …`.

### WMS CLI (Bastard / Task Workflow)

Use the dedicated virtualenv to run the workspace CLI without tripping PEP 668:

```bash
cd /Users/simonerses/data-projects
workspace/.venv/bin/python workspace/wms/cli.py task list
```

This ensures `click` and `sqlalchemy` are available even when the system Python blocks global installs.

---

## Quick Start

### 1. Initialize Database

```python
from pathlib import Path
from workspace.db import WorkspaceDB

workspace_root = Path("/Users/simonerses/data-projects")
db = WorkspaceDB(workspace_root=workspace_root)

# Database will be created at: workspace_root/workspace.db
```

### 2. Migrate Existing JSON Files

```bash
cd /Users/simonerses/data-projects
python workspace/scripts/migrate_json_to_db.py
```

This will:
- Create `workspace.db` database
- Import existing JSON files:
  - `WORKSPACE-TASKS.json` → `workspace_tasks` table
  - `SESSION-LOG.json` → `workspace_sessions` table
  - `CROSS-REPO-ISSUES.json` → `cross_repo_issues` table
  - `ARCHITECTURE-DECISIONS.json` → `architecture_decisions` table

### 3. Test Database

```bash
python workspace/scripts/test_db.py
```

---

## Usage Examples

### Add a Task

```python
from workspace.db import WorkspaceDB

db = WorkspaceDB()

task = db.add_task(
    task_id="WS-TASK-001",
    title="Implement TradingLearningEngine",
    status="pending",
    priority="HIGH",
    repos_affected=["meridian-trading", "meridian-core"],
    description="Self-learning for trading domain",
    session_created="2025-11-20-session-001",
)
```

### Get Tasks

```python
# Get all pending tasks
tasks = db.get_tasks(status="pending")

# Get tasks for a specific repo
tasks = db.get_tasks(repo="meridian-core")

# Get high-priority tasks
tasks = db.get_tasks(priority="HIGH", limit=10)
```

### Add an Issue

```python
issue = db.add_issue(
    issue_id="ISSUE-001",
    issue_type="code_creep",
    severity="HIGH",
    title="Trading-specific code found in meridian-core",
    description="File X imports pandas, violates ADR-001",
    repos_affected=["meridian-core"],
    detected_by="automated",
    action_required="Move to meridian-trading",
)
```

### Track Session

```python
# Start session
session = db.add_session(
    session_id="2025-11-20-session-001",
    user="simonerses",
    ai_assistant="claude-code",
)

# Add activity
db.add_session_activity(
    session_id=session.id,
    activity_type="documentation",
    description="Created architecture documents",
    files_created=["2025-11-20-MERIDIAN-CORE-ARCHITECTURE.md"],
)

# End session
db.end_session(session.id)
```

### Export to JSON

```python
# Export for human readability
db.export_to_json_files()

# Or get as dictionary
data = db.export_to_json()
```

---

## Database Schema

The database includes tables for:

- **workspace_tasks** - Tasks across all repos
- **workspace_sessions** - Session tracking
- **session_activities** - Activities within sessions
- **cross_repo_issues** - Issues spanning repos
- **architecture_decisions** - Architecture decisions
- **architecture_states** - Current vs future state
- **component_placements** - Where components should be
- **drift_detections** - Detected drift violations
- **context_switches** - Context switching history

See `workspace/db/models.py` for full schema.

---

## Architecture

Follows meridian-core patterns:

- ✅ **SQLAlchemy ORM** - Type-safe, relationship-aware
- ✅ **Connection Pooling** - Thread-safe, production-ready
- ✅ **WAL Mode** - Write-Ahead Logging for concurrent access
- ✅ **Automatic Schema** - Tables created automatically
- ✅ **JSON Export** - Human-readable exports

---

## Next Steps

1. ✅ Database created
2. ⏳ Migrate existing JSON data
3. ⏳ Test database operations
4. ⏳ Integrate with workspace context system
5. ⏳ Add drift detection engine

---

**Last Updated:** 2025-11-20  
**Status:** Database Module Complete - Ready for Migration

