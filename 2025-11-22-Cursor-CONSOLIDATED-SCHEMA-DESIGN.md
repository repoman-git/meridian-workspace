# Consolidated Schema Design

**Date:** 2025-11-22  
**Phase:** 1.1 - Schema Design  
**Status:** ✅ COMPLETE

---

## Executive Summary

**Target Database:** `workspace.db` (consolidated)  
**Source Databases:** 
- `workspace.db` (existing, keep as base)
- `proposals.db` (add proposals table)
- `task_queue.db` (add tasks and task_queue_metadata tables)
- `orchestration_decisions.db` (add orchestration_decisions table if exists)

**Strategy:** Add missing tables to existing workspace.db schema

---

## Schema Analysis

### Existing workspace.db Tables (26 tables)

**Core WMS Tables:**
- `workspace_tasks` - Workspace-level task tracking (62 records)
- `workspace_sessions` - Session management (3 records)
- `architecture_decisions` - Architecture decision tracking (4 records)
- `architecture_components` - Component tracking (53 records)
- `code_component_mappings` - File-to-component mappings (183 records)
- `unregistered_files` - Unregistered file tracking (289 records)
- `bastard_reports` - Bastard validation reports (8 records)
- `cross_repo_issues` - Cross-repo issue tracking (4 records)
- `work_contexts` - Work context tracking (4 records)
- `session_activities` - Session activity log (4 records)

**Supporting Tables:**
- `architecture_states` - Architecture state tracking (0 records)
- `drift_scans` - Drift scan results (0 records)
- `context_switches` - Context switch tracking (0 records)
- `configuration_snapshots` - Configuration snapshots (0 records)
- `session_decisions` - Session decision tracking (0 records)
- `component_placements` - Component placement rules (0 records)
- `drift_detections` - Drift detection results (0 records)
- `session_issues` - Session issue tracking (0 records)
- `architecture_tasks` - Architecture task tracking (0 records)
- `configuration_changes` - Configuration change tracking (0 records)
- `workflows` - Workflow definitions (0 records)
- `violations` - Violation tracking (0 records)
- `import_rules` - Import rule tracking (0 records)
- `scale_tiers` - Scale tier definitions (0 records)
- `workflow_stages` - Workflow stage tracking (0 records)
- `architecture_states_old` - Old architecture states (0 records)
- `code_changes` - Code change tracking (0 records)

---

### Tables to Add from proposals.db

**Primary Table:**
- `proposals` - Learning proposals (1 record)

**Schema:**
```sql
CREATE TABLE proposals (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    hypothesis TEXT NOT NULL,
    rationale TEXT NOT NULL,
    pattern_id VARCHAR(255),
    performance_data TEXT,  -- JSON string
    implementation_result TEXT,
    metadata TEXT,  -- JSON string
    status VARCHAR(50) NOT NULL,
    created_at FLOAT NOT NULL,
    reviewed_at FLOAT,
    implemented_at FLOAT,
    review_notes TEXT
);
```

**Note:** This table uses FLOAT for timestamps (Unix timestamp), while workspace.db uses DATETIME. We'll keep FLOAT for compatibility.

---

### Tables to Add from task_queue.db

**Primary Tables:**
- `tasks` - Task queue tasks (85 records)
- `task_queue_metadata` - Task queue metadata (5 records)

**Schema - tasks:**
```sql
CREATE TABLE tasks (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    capability_required VARCHAR(255),
    estimated_tokens INTEGER,
    tags TEXT,  -- JSON array string
    dependencies TEXT,  -- JSON array string
    failures TEXT,  -- JSON array string
    metadata TEXT,  -- JSON string
    file VARCHAR(500),
    created_by VARCHAR(255),
    created_at VARCHAR(100),  -- ISO format string
    updated_at VARCHAR(100),  -- ISO format string
    version INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks(tags);
CREATE INDEX idx_tasks_updated_at ON tasks(updated_at);
```

**Schema - task_queue_metadata:**
```sql
CREATE TABLE task_queue_metadata (
    key VARCHAR(255) NOT NULL PRIMARY KEY,
    value TEXT,  -- JSON string
    updated_at VARCHAR(100)  -- ISO format string
);
```

**Note:** 
- `tasks` table conflicts with `workspace_tasks` conceptually but has different schema
- Keep both tables (different purposes: workspace_tasks = WMS tasks, tasks = orchestrator task queue)
- Consider renaming `tasks` to `orchestrator_tasks` to avoid confusion (but this requires code changes)

---

### Tables to Add from orchestration_decisions.db

**Primary Table:**
- `orchestration_decisions` - Orchestration decision history (may not exist yet)

**Schema:**
```sql
CREATE TABLE orchestration_decisions (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    timestamp FLOAT NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255),
    task_type VARCHAR(255),
    success INTEGER,  -- 0 = False, 1 = True, NULL = Unknown
    failure_reason TEXT,
    tokens_used INTEGER,
    duration_seconds FLOAT,
    dry_run INTEGER DEFAULT 0,
    decision_process TEXT,  -- JSON string
    metadata TEXT  -- JSON string
);

CREATE INDEX idx_decisions_timestamp ON orchestration_decisions(timestamp);
CREATE INDEX idx_decisions_task_id ON orchestration_decisions(task_id);
CREATE INDEX idx_decisions_agent_id ON orchestration_decisions(agent_id);
CREATE INDEX idx_decisions_task_type ON orchestration_decisions(task_type);
CREATE INDEX idx_decisions_success ON orchestration_decisions(success);
CREATE INDEX idx_decisions_dry_run ON orchestration_decisions(dry_run);
```

---

## Unified Schema Design

### Strategy: Add Tables, Don't Modify Existing

**Approach:**
1. Keep all existing workspace.db tables unchanged
2. Add new tables from other databases
3. Use table prefixes if needed to avoid conflicts
4. Maintain backward compatibility

### Table Naming Strategy

**Option A: Keep Original Names (Recommended)**
- `proposals` - Keep as-is (no conflict)
- `tasks` - Keep as-is (different from workspace_tasks)
- `task_queue_metadata` - Keep as-is (no conflict)
- `orchestration_decisions` - Keep as-is (no conflict)

**Option B: Add Prefixes (If Conflicts)**
- `orchestrator_tasks` instead of `tasks` (requires code changes)
- `orchestrator_metadata` instead of `task_queue_metadata`

**Recommendation:** Use Option A (keep original names). The `tasks` table is conceptually different from `workspace_tasks`:
- `workspace_tasks` = WMS workspace-level tasks (WS-TASK-XXX)
- `tasks` = Orchestrator task queue tasks (internal task IDs)

---

## Complete Unified Schema

### A. Existing workspace.db Tables (Keep As-Is)

All 26 existing tables remain unchanged:
- workspace_tasks
- workspace_sessions
- architecture_decisions
- architecture_components
- code_component_mappings
- unregistered_files
- bastard_reports
- cross_repo_issues
- work_contexts
- session_activities
- architecture_states
- drift_scans
- context_switches
- configuration_snapshots
- session_decisions
- component_placements
- drift_detections
- session_issues
- architecture_tasks
- configuration_changes
- workflows
- violations
- import_rules
- scale_tiers
- workflow_stages
- architecture_states_old
- code_changes

---

### B. New Tables from proposals.db

**Table: proposals**
```sql
CREATE TABLE proposals (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    hypothesis TEXT NOT NULL,
    rationale TEXT NOT NULL,
    pattern_id VARCHAR(255),
    performance_data TEXT,
    implementation_result TEXT,
    metadata TEXT,
    status VARCHAR(50) NOT NULL,
    created_at FLOAT NOT NULL,
    reviewed_at FLOAT,
    implemented_at FLOAT,
    review_notes TEXT
);

CREATE INDEX idx_proposals_status ON proposals(status);
CREATE INDEX idx_proposals_created_at ON proposals(created_at);
```

---

### C. New Tables from task_queue.db

**Table: tasks**
```sql
CREATE TABLE tasks (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    capability_required VARCHAR(255),
    estimated_tokens INTEGER,
    tags TEXT,
    dependencies TEXT,
    failures TEXT,
    metadata TEXT,
    file VARCHAR(500),
    created_by VARCHAR(255),
    created_at VARCHAR(100),
    updated_at VARCHAR(100),
    version INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tags ON tasks(tags);
CREATE INDEX idx_tasks_updated_at ON tasks(updated_at);
CREATE INDEX idx_tasks_capability_required ON tasks(capability_required);
```

**Table: task_queue_metadata**
```sql
CREATE TABLE task_queue_metadata (
    key VARCHAR(255) NOT NULL PRIMARY KEY,
    value TEXT,
    updated_at VARCHAR(100)
);

CREATE INDEX idx_task_queue_metadata_updated_at ON task_queue_metadata(updated_at);
```

---

### D. New Tables from orchestration_decisions.db

**Table: orchestration_decisions**
```sql
CREATE TABLE orchestration_decisions (
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    timestamp FLOAT NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255),
    task_type VARCHAR(255),
    success INTEGER,
    failure_reason TEXT,
    tokens_used INTEGER,
    duration_seconds FLOAT,
    dry_run INTEGER DEFAULT 0,
    decision_process TEXT,
    metadata TEXT
);

CREATE INDEX idx_decisions_timestamp ON orchestration_decisions(timestamp);
CREATE INDEX idx_decisions_task_id ON orchestration_decisions(task_id);
CREATE INDEX idx_decisions_agent_id ON orchestration_decisions(agent_id);
CREATE INDEX idx_decisions_task_type ON orchestration_decisions(task_type);
CREATE INDEX idx_decisions_success ON orchestration_decisions(success);
CREATE INDEX idx_decisions_dry_run ON orchestration_decisions(dry_run);
```

---

## Relationships

### Existing Relationships (workspace.db)

- `workspace_tasks` ↔ `cross_repo_issues` (via related_task_id)
- `workspace_tasks` ↔ `architecture_tasks` (via workspace_task_id)
- `workspace_tasks` ↔ `workflows` (via workflow_id)

### New Relationships (Potential)

**Option 1: No Foreign Keys (Recommended)**
- Keep tables independent
- Use application-level joins if needed
- More flexible, less rigid

**Option 2: Add Foreign Keys**
- `tasks.id` → `orchestration_decisions.task_id` (optional FK)
- `workspace_tasks.id` → `tasks.id` (if we want to link WMS tasks to orchestrator tasks)

**Recommendation:** Option 1 (no foreign keys). Keep tables independent for flexibility.

---

## Data Integrity Rules

### Constraints

1. **Primary Keys:** All tables have primary keys (enforced)
2. **NOT NULL:** Critical fields marked NOT NULL
3. **Indexes:** Performance indexes on frequently queried columns
4. **JSON Fields:** Stored as TEXT, validated at application level

### Validation Rules

1. **Status Values:** 
   - `proposals.status` must be valid enum value
   - `tasks.status` must be valid enum value
   - `workspace_tasks.status` must be valid enum value

2. **Timestamp Formats:**
   - `proposals.created_at` = FLOAT (Unix timestamp)
   - `tasks.created_at` = VARCHAR (ISO format string)
   - `workspace_tasks.created` = DATETIME (SQLite DATETIME)

3. **JSON Fields:**
   - `tasks.tags` = JSON array string
   - `tasks.dependencies` = JSON array string
   - `tasks.failures` = JSON array string
   - `tasks.metadata` = JSON object string
   - `orchestration_decisions.decision_process` = JSON object string
   - `orchestration_decisions.metadata` = JSON object string

---

## Migration Strategy for Each Table

### 1. proposals Table

**Source:** `proposals.db` → `proposals` table  
**Target:** `workspace.db` → `proposals` table  
**Strategy:** Direct copy (same schema)  
**Risk:** LOW (1 record, simple copy)

**Migration SQL:**
```sql
-- Create table in workspace.db
CREATE TABLE proposals (...);

-- Copy data
INSERT INTO proposals SELECT * FROM proposals_source.proposals;
```

---

### 2. tasks Table

**Source:** `task_queue.db` → `tasks` table  
**Target:** `workspace.db` → `tasks` table  
**Strategy:** Direct copy (same schema)  
**Risk:** MEDIUM (85 records, need to verify no conflicts)

**Migration SQL:**
```sql
-- Create table in workspace.db
CREATE TABLE tasks (...);

-- Copy data
INSERT INTO tasks SELECT * FROM task_queue_source.tasks;
```

---

### 3. task_queue_metadata Table

**Source:** `task_queue.db` → `task_queue_metadata` table  
**Target:** `workspace.db` → `task_queue_metadata` table  
**Strategy:** Direct copy (same schema)  
**Risk:** LOW (5 records, simple copy)

**Migration SQL:**
```sql
-- Create table in workspace.db
CREATE TABLE task_queue_metadata (...);

-- Copy data
INSERT INTO task_queue_metadata SELECT * FROM task_queue_source.task_queue_metadata;
```

---

### 4. orchestration_decisions Table

**Source:** `orchestration_decisions.db` → `orchestration_decisions` table (may not exist)  
**Target:** `workspace.db` → `orchestration_decisions` table  
**Strategy:** Create table if doesn't exist, copy data if exists  
**Risk:** LOW (optional table, may be empty)

**Migration SQL:**
```sql
-- Create table in workspace.db (if doesn't exist)
CREATE TABLE IF NOT EXISTS orchestration_decisions (...);

-- Copy data (if source exists and has data)
INSERT INTO orchestration_decisions SELECT * FROM orch_source.orchestration_decisions;
```

---

## Indexes Summary

### Existing Indexes (workspace.db)
- All existing indexes remain unchanged

### New Indexes to Create

**proposals:**
- `idx_proposals_status`
- `idx_proposals_created_at`

**tasks:**
- `idx_tasks_status`
- `idx_tasks_priority`
- `idx_tasks_tags`
- `idx_tasks_updated_at`
- `idx_tasks_capability_required`

**task_queue_metadata:**
- `idx_task_queue_metadata_updated_at`

**orchestration_decisions:**
- `idx_decisions_timestamp`
- `idx_decisions_task_id`
- `idx_decisions_agent_id`
- `idx_decisions_task_type`
- `idx_decisions_success`
- `idx_decisions_dry_run`

---

## Schema Compatibility

### SQLAlchemy Models

**workspace.db models:**
- Uses `workspace/db/models.py` with independent Base
- Models: WorkspaceTask, WorkspaceSession, ArchitectureDecision, etc.

**meridian-core models:**
- Uses `meridian-core/src/meridian_core/db/models.py` with Base
- Models: Proposal, TaskQueueTask, TaskQueueMetadata, OrchestrationDecision

**Compatibility Strategy:**
- Both can use same database file
- Different Base classes (workspace Base vs meridian-core Base)
- Tables are independent (no shared foreign keys)
- Works fine as long as both Base classes create tables in same database

---

## Final Schema Summary

**Total Tables:** 30 (26 existing + 4 new)

**New Tables:**
1. `proposals` - Learning proposals
2. `tasks` - Orchestrator task queue
3. `task_queue_metadata` - Task queue metadata
4. `orchestration_decisions` - Orchestration decision history

**Total Records to Migrate:** ~91 records
- proposals: 1
- tasks: 85
- task_queue_metadata: 5
- orchestration_decisions: 0 (may not exist)

---

## Next Steps

1. ✅ **Phase 1.1 Complete** - Schema design created
2. ⏳ **Phase 1.2** - Plan migration strategy

---

**Status:** Ready for Phase 1.2 - Migration Strategy Planning

