# 2025-11-20 - Workspace Database vs JSON Analysis

**Question:** Should workspace tracking use a database instead of JSON files?

**Answer:** **Yes, database is better** - especially given existing SQLAlchemy infrastructure.

---

## Comparison: JSON vs Database

### JSON Files (Current Approach)

**Pros:**
- ✅ Simple - no setup required
- ✅ Human-readable - easy to view/edit
- ✅ Version-control friendly - easy to diff
- ✅ Portable - easy to copy/share

**Cons:**
- ❌ **No queries** - must parse entire file
- ❌ **No relationships** - hard to link tasks→issues→decisions
- ❌ **Concurrency issues** - file locks, race conditions
- ❌ **Manual parsing** - write/read entire file each time
- ❌ **No transactions** - can't rollback changes
- ❌ **Scales poorly** - file grows large over time
- ❌ **No indexing** - slow searches

### Database (Recommended)

**Pros:**
- ✅ **Powerful queries** - SQL for complex filtering
- ✅ **Relationships** - Foreign keys link related data
- ✅ **Concurrent access** - Thread-safe with connection pooling
- ✅ **Transactions** - ACID guarantees, rollback support
- ✅ **Indexing** - Fast searches on any field
- ✅ **Scalability** - Handles large datasets efficiently
- ✅ **Existing infrastructure** - SQLAlchemy already in meridian-core

**Cons:**
- ⚠️ Less human-readable (but SQLite browser exists)
- ⚠️ Requires SQLAlchemy setup (but already exists)

---

## Existing Database Infrastructure

### What We Already Have

1. **SQLAlchemy models** in `meridian-core/src/meridian_core/db/models.py`
2. **Connection pooling** - Thread-safe, production-ready
3. **Multiple databases** already in use:
   - `meridian-core/logs/proposals.db`
   - `meridian-core/logs/orchestration_decisions.db`
   - `meridian-core/logs/task_tracking.db`
   - `meridian-research/meridian.db`
   - `meridian-trading/logs/orchestration_decisions.db`

4. **Proven patterns:**
   - `ProposalManager` - Similar to what we need
   - `OrchestrationDecisionDB` - Similar structure
   - `TaskQueueDB` - Task tracking already exists!

### Database Patterns Already Established

```python
# From meridian-core - proven pattern
class ProposalManager:
    def __init__(self, db_path: Optional[str] = None):
        # SQLite with WAL mode
        # Connection pooling
        # Thread-safe
        # Automatic schema management
```

---

## Recommendation: Workspace-Level Database

### Location: `data-projects/workspace.db`

**Why workspace level:**
- ✅ Cross-repo tracking requires workspace scope
- ✅ Single source of truth for all repos
- ✅ Can be accessed from any repo
- ✅ Matches existing pattern (repos have their own DBs)

### Database Schema

```sql
-- Workspace Tasks
CREATE TABLE workspace_tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,  -- pending, in_progress, completed, blocked
    priority TEXT,  -- HIGH, MEDIUM, LOW
    repos_affected TEXT,  -- JSON array
    dependencies TEXT,  -- JSON array of task IDs
    created TIMESTAMP NOT NULL,
    session_created TEXT,
    assigned_to TEXT,
    notes TEXT,
    related_files TEXT  -- JSON array
);

-- Cross-Repo Issues
CREATE TABLE cross_repo_issues (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- code_creep, governance, missing_component, etc.
    severity TEXT NOT NULL,  -- HIGH, MEDIUM, LOW
    title TEXT NOT NULL,
    description TEXT,
    repos_affected TEXT,  -- JSON array
    detected TIMESTAMP NOT NULL,
    detected_by TEXT,
    status TEXT NOT NULL,  -- open, resolved, closed
    action_required TEXT,
    assigned_to TEXT,
    related_task_id TEXT,  -- FK to workspace_tasks
    FOREIGN KEY (related_task_id) REFERENCES workspace_tasks(id)
);

-- Architecture Decisions
CREATE TABLE architecture_decisions (
    id TEXT PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    session TEXT NOT NULL,
    decision TEXT NOT NULL,
    repos_affected TEXT,  -- JSON array
    rationale TEXT,
    status TEXT NOT NULL,  -- implemented, in_progress, maintained
    impact TEXT,  -- HIGH, MEDIUM, LOW
    related_files TEXT,  -- JSON array
    documentation TEXT  -- JSON array
);

-- Session Logs
CREATE TABLE session_logs (
    id TEXT PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status TEXT NOT NULL,  -- in_progress, completed
    user TEXT,
    ai_assistant TEXT,
    handoff_notes TEXT
);

-- Session Activities
CREATE TABLE session_activities (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    type TEXT NOT NULL,  -- documentation, analysis, governance, etc.
    description TEXT,
    files_created TEXT,  -- JSON array
    outcome TEXT,
    time TIMESTAMP NOT NULL,
    FOREIGN KEY (session_id) REFERENCES session_logs(session_id)
);

-- Session Decisions
CREATE TABLE session_decisions (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    decision_id TEXT,  -- FK to architecture_decisions
    FOREIGN KEY (session_id) REFERENCES session_logs(session_id),
    FOREIGN KEY (decision_id) REFERENCES architecture_decisions(id)
);

-- Session Issues Found
CREATE TABLE session_issues (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    issue_id TEXT,  -- FK to cross_repo_issues
    FOREIGN KEY (session_id) REFERENCES session_logs(session_id),
    FOREIGN KEY (issue_id) REFERENCES cross_repo_issues(id)
);
```

### Relationships

```
workspace_tasks (1) ←→ (many) cross_repo_issues
session_logs (1) ←→ (many) session_activities
session_logs (1) ←→ (many) session_decisions
session_logs (1) ←→ (many) session_issues
session_decisions (many) ←→ (1) architecture_decisions
session_issues (many) ←→ (1) cross_repo_issues
```

**Benefits:**
- ✅ Tasks linked to issues
- ✅ Sessions linked to decisions and issues
- ✅ Can query "all issues for a task"
- ✅ Can query "all decisions in a session"
- ✅ Can query "all tasks affected by a decision"

---

## Implementation Plan

### Option 1: Use Existing meridian-core Infrastructure

**Leverage existing SQLAlchemy models and patterns:**

```python
# workspace/db/models.py
from meridian_core.db.models import Base  # Reuse Base
from sqlalchemy import Column, String, Text, DateTime, ForeignKey

class WorkspaceTask(Base):
    __tablename__ = 'workspace_tasks'
    # ... schema ...

# Reuse connection pooling patterns from meridian-core
```

**Pros:**
- ✅ Reuses proven infrastructure
- ✅ Consistent patterns
- ✅ Can import from meridian-core if needed

**Cons:**
- ⚠️ Creates dependency on meridian-core
- ⚠️ Might be overkill for workspace-level

### Option 2: Standalone Workspace Database

**Create independent workspace database with similar patterns:**

```python
# workspace/db/workspace_db.py
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool

# Similar to meridian-core patterns but standalone
Base = declarative_base()

# Same connection pooling, WAL mode, etc.
```

**Pros:**
- ✅ Independent - no dependencies
- ✅ Can be used by any repo
- ✅ Follows same proven patterns

**Cons:**
- ⚠️ Some code duplication (but minimal)

### Option 3: Hybrid Approach (Recommended)

**Use database for storage, keep JSON for human-readable exports:**

```python
class WorkspaceDB:
    def export_to_json(self) -> Dict[str, Any]:
        """Export to JSON for human readability and version control."""
        return {
            "tasks": [task.to_dict() for task in self.get_all_tasks()],
            "issues": [issue.to_dict() for issue in self.get_all_issues()],
            # ...
        }
    
    def import_from_json(self, data: Dict[str, Any]):
        """Import from JSON (for migration or manual edits)."""
        # ...
```

**Benefits:**
- ✅ Database for queries and concurrency
- ✅ JSON export for human review
- ✅ Best of both worlds

---

## Recommended Solution

### Database: `data-projects/workspace.db`

**Location:** Workspace root (`/Users/simonerses/data-projects/workspace.db`)

**Why:**
- ✅ Cross-repo scope (matches requirements)
- ✅ Single source of truth
- ✅ Accessible from any repo
- ✅ Follows pattern: repos have their own DBs, workspace has workspace DB

**Implementation:**
1. **Create `workspace/db/workspace_db.py`** - Standalone database module
2. **Use SQLAlchemy patterns** - Similar to meridian-core but independent
3. **Add JSON export/import** - For human readability
4. **Reuse existing patterns** - Connection pooling, WAL mode, etc.

**Structure:**
```
data-projects/
├── workspace.db                 ← NEW: Workspace database
├── workspace/                   ← NEW: Workspace database module
│   ├── db/
│   │   ├── __init__.py
│   │   ├── workspace_db.py      ← Database manager
│   │   ├── models.py            ← SQLAlchemy models
│   │   └── queries.py           ← Common queries
│   └── cli/
│       └── workspace_tasks.py   ← CLI commands
│
├── WORKSPACE-TASKS.json         ← KEEP: JSON export (human-readable)
├── CROSS-REPO-ISSUES.json       ← KEEP: JSON export
├── SESSION-LOG.json             ← KEEP: JSON export
└── ARCHITECTURE-DECISIONS.json  ← KEEP: JSON export
```

**Workflow:**
1. **Primary storage:** SQLite database (`workspace.db`)
2. **Queries:** Use SQLAlchemy ORM
3. **Human review:** Export to JSON periodically
4. **Version control:** Commit JSON exports (not DB file)
5. **Manual edits:** Edit JSON, import to database

---

## Migration Path

### Step 1: Create Database Module

Create `workspace/db/workspace_db.py` with:
- SQLAlchemy models
- Connection pooling
- WAL mode
- Migration from existing JSON files

### Step 2: Migrate Existing Data

Import from existing JSON files:
```python
# Migration script
workspace_db = WorkspaceDB()
workspace_db.import_from_json_files([
    "WORKSPACE-TASKS.json",
    "CROSS-REPO-ISSUES.json",
    "SESSION-LOG.json",
    "ARCHITECTURE-DECISIONS.json"
])
```

### Step 3: Update Access Patterns

Replace JSON file reads with database queries:
```python
# Old
with open("WORKSPACE-TASKS.json") as f:
    tasks = json.load(f)

# New
workspace_db = WorkspaceDB()
tasks = workspace_db.get_active_tasks()
```

### Step 4: Add JSON Export

Periodic export for human review:
```python
# Export current state to JSON
workspace_db.export_to_json_files()
```

---

## Comparison Summary

| Feature | JSON Files | Database |
|---------|-----------|----------|
| **Queries** | ❌ Manual parsing | ✅ SQL queries |
| **Relationships** | ❌ Manual linking | ✅ Foreign keys |
| **Concurrency** | ❌ File locks | ✅ Thread-safe |
| **Transactions** | ❌ No rollback | ✅ ACID |
| **Scalability** | ❌ Slow at scale | ✅ Efficient |
| **Human-readable** | ✅ Yes | ⚠️ Use SQLite browser |
| **Version control** | ✅ Easy | ⚠️ Export JSON |
| **Setup** | ✅ None | ⚠️ Minimal (SQLAlchemy) |
| **Existing infra** | ✅ None needed | ✅ SQLAlchemy patterns exist |

**Verdict: Database wins for functionality, JSON for human readability.**

**Solution: Use both - Database for storage/queries, JSON for human review.**

---

## Next Steps

1. **Create workspace database module** (`workspace/db/workspace_db.py`)
2. **Define SQLAlchemy models** (following meridian-core patterns)
3. **Migrate existing JSON data** to database
4. **Add JSON export/import** functions
5. **Update access patterns** to use database
6. **Keep JSON files** as human-readable exports

---

**Last Updated:** 2025-11-20  
**Status:** Recommendation Complete - Database Preferred

