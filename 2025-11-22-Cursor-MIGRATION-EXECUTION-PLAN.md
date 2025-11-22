# Migration Execution Plan

**Date:** 2025-11-22  
**Phase:** 1.2 - Migration Strategy Planning  
**Status:** ✅ COMPLETE

---

## Executive Summary

**Migration Goal:** Consolidate 3-4 databases into single `workspace.db`  
**Total Records:** ~91 records  
**Estimated Time:** 2 hours  
**Risk Level:** MEDIUM (manageable with backups)

---

## Table Migration Priority

### CRITICAL (Must Migrate First)

**Priority 1: workspace.db (Base)**
- **Status:** Already exists, keep as-is
- **Action:** No migration needed
- **Risk:** NONE (this is our target)

---

### HIGH (Migrate Second)

**Priority 2: task_queue.db → workspace.db**
- **Tables:** `tasks` (85 records), `task_queue_metadata` (5 records)
- **Reason:** Active task queue, critical for orchestrator
- **Risk:** MEDIUM (85 records, active system)
- **Dependencies:** Orchestrator uses this daily

**Priority 3: proposals.db → workspace.db**
- **Tables:** `proposals` (1 record)
- **Reason:** Learning engine data
- **Risk:** LOW (1 record, simple)
- **Dependencies:** Learning engine (optional feature)

---

### MEDIUM (Migrate If Time Permits)

**Priority 4: orchestration_decisions.db → workspace.db**
- **Tables:** `orchestration_decisions` (may not exist)
- **Reason:** Optional logging feature
- **Risk:** LOW (may not exist, optional)
- **Dependencies:** Orchestrator logging (optional)

---

## Risk Assessment

### Data Volume Risk

| Database | Records | Risk Level | Mitigation |
|----------|---------|------------|------------|
| workspace.db | ~610 | NONE | Keep as-is |
| task_queue.db | 90 | MEDIUM | Verify counts before/after |
| proposals.db | 1 | LOW | Simple copy |
| orchestration_decisions.db | 0 | LOW | Create table if needed |

**Overall:** LOW-MEDIUM (small data volume)

---

### Schema Change Risk

| Table | Schema Change | Risk Level | Mitigation |
|-------|---------------|------------|------------|
| proposals | None (direct copy) | LOW | Same schema |
| tasks | None (direct copy) | LOW | Same schema |
| task_queue_metadata | None (direct copy) | LOW | Same schema |
| orchestration_decisions | Create if missing | LOW | Schema already defined |

**Overall:** LOW (no schema changes needed)

---

### Dependency Risk

| Component | Database | Risk Level | Mitigation |
|-----------|----------|------------|------------|
| WMS CLI | workspace.db | NONE | No changes needed |
| Orchestrator | task_queue.db | MEDIUM | Update path, test thoroughly |
| Learning Engine | proposals.db | LOW | Update path, optional feature |
| Decision Logging | orchestration_decisions.db | LOW | Update path, optional feature |

**Overall:** MEDIUM (need to update code paths)

---

### Data Integrity Risk

| Risk | Level | Mitigation |
|------|-------|------------|
| Foreign key violations | LOW | No foreign keys between tables |
| Duplicate records | LOW | Primary keys prevent duplicates |
| Data corruption | LOW | SQLite ATTACH ensures integrity |
| Missing data | MEDIUM | Verify counts before/after migration |

**Overall:** LOW (SQLite handles integrity)

---

## Rollback Strategy

### For Each Migration Step

**Step 1: Backup**
```bash
# Backup original database
cp <source_db> <source_db>.backup.$(date +%Y%m%d_%H%M%S)

# SQL dump backup
sqlite3 <source_db> ".dump" > <source_db>.sql.backup.$(date +%Y%m%d_%H%M%S)
```

**Step 2: Validation Check**
```bash
# Count records before migration
sqlite3 <source_db> "SELECT COUNT(*) FROM <table>;"

# Count records after migration
sqlite3 workspace.db "SELECT COUNT(*) FROM <table>;"

# Verify counts match
```

**Step 3: Rollback Command**
```bash
# If migration fails, restore backup
cp <source_db>.backup.* <source_db>

# Or restore from SQL dump
sqlite3 <source_db> < <source_db>.sql.backup.*
```

**Step 4: Success Criteria**
- ✅ Record counts match
- ✅ Data integrity check passes
- ✅ No errors during migration
- ✅ Code can read from new location

---

## Migration Steps

### Step 1: Backup Everything

**Commands:**
```bash
# Create backup directory
BACKUP_DIR=~/data-projects/backups/db-consolidation-$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup workspace.db
cp workspace.db $BACKUP_DIR/workspace.db.backup
sqlite3 workspace.db ".dump" > $BACKUP_DIR/workspace.db.sql

# Backup proposals.db
cp meridian-core/logs/proposals.db $BACKUP_DIR/proposals.db.backup
sqlite3 meridian-core/logs/proposals.db ".dump" > $BACKUP_DIR/proposals.db.sql

# Backup task_queue.db
cp meridian-core/logs/task_queue.db $BACKUP_DIR/task_queue.db.backup
sqlite3 meridian-core/logs/task_queue.db ".dump" > $BACKUP_DIR/task_queue.db.sql

# Backup orchestration_decisions.db (if exists)
if [ -f meridian-core/logs/orchestration_decisions.db ]; then
    cp meridian-core/logs/orchestration_decisions.db $BACKUP_DIR/orchestration_decisions.db.backup
    sqlite3 meridian-core/logs/orchestration_decisions.db ".dump" > $BACKUP_DIR/orchestration_decisions.db.sql
fi
```

**Validation:**
- [ ] All backups created
- [ ] Backup sizes match originals
- [ ] SQL dumps are valid

---

### Step 2: Create Consolidated Schema

**Commands:**
```bash
cd ~/data-projects

# Create new tables in workspace.db
sqlite3 workspace.db <<EOF
-- Create proposals table
CREATE TABLE IF NOT EXISTS proposals (
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

CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(status);
CREATE INDEX IF NOT EXISTS idx_proposals_created_at ON proposals(created_at);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
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

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks(tags);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);
CREATE INDEX IF NOT EXISTS idx_tasks_capability_required ON tasks(capability_required);

-- Create task_queue_metadata table
CREATE TABLE IF NOT EXISTS task_queue_metadata (
    key VARCHAR(255) NOT NULL PRIMARY KEY,
    value TEXT,
    updated_at VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_task_queue_metadata_updated_at ON task_queue_metadata(updated_at);

-- Create orchestration_decisions table
CREATE TABLE IF NOT EXISTS orchestration_decisions (
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

CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON orchestration_decisions(timestamp);
CREATE INDEX IF NOT EXISTS idx_decisions_task_id ON orchestration_decisions(task_id);
CREATE INDEX IF NOT EXISTS idx_decisions_agent_id ON orchestration_decisions(agent_id);
CREATE INDEX IF NOT EXISTS idx_decisions_task_type ON orchestration_decisions(task_type);
CREATE INDEX IF NOT EXISTS idx_decisions_success ON orchestration_decisions(success);
CREATE INDEX IF NOT EXISTS idx_decisions_dry_run ON orchestration_decisions(dry_run);
EOF
```

**Validation:**
- [ ] All tables created
- [ ] Indexes created
- [ ] Schema matches design document

---

### Step 3: Migrate proposals.db

**Commands:**
```bash
cd ~/data-projects

# Attach proposals.db
sqlite3 workspace.db <<EOF
ATTACH 'meridian-core/logs/proposals.db' AS proposals_source;

-- Copy proposals table
INSERT INTO proposals 
SELECT * FROM proposals_source.proposals;

-- Verify count
SELECT 'Proposals migrated:', COUNT(*) FROM proposals;

DETACH proposals_source;
EOF
```

**Validation:**
```bash
# Count in source
sqlite3 meridian-core/logs/proposals.db "SELECT COUNT(*) FROM proposals;"

# Count in target
sqlite3 workspace.db "SELECT COUNT(*) FROM proposals;"

# Verify counts match (should be 1)
```

**Rollback:**
```bash
# If counts don't match, rollback
sqlite3 workspace.db "DELETE FROM proposals;"
# Then retry migration
```

---

### Step 4: Migrate task_queue.db

**Commands:**
```bash
cd ~/data-projects

# Attach task_queue.db
sqlite3 workspace.db <<EOF
ATTACH 'meridian-core/logs/task_queue.db' AS task_queue_source;

-- Copy tasks table
INSERT INTO tasks 
SELECT * FROM task_queue_source.tasks;

-- Copy task_queue_metadata table
INSERT INTO task_queue_metadata 
SELECT * FROM task_queue_source.task_queue_metadata;

-- Verify counts
SELECT 'Tasks migrated:', COUNT(*) FROM tasks;
SELECT 'Metadata migrated:', COUNT(*) FROM task_queue_metadata;

DETACH task_queue_source;
EOF
```

**Validation:**
```bash
# Count in source
sqlite3 meridian-core/logs/task_queue.db "SELECT COUNT(*) FROM tasks;"
sqlite3 meridian-core/logs/task_queue.db "SELECT COUNT(*) FROM task_queue_metadata;"

# Count in target
sqlite3 workspace.db "SELECT COUNT(*) FROM tasks;"
sqlite3 workspace.db "SELECT COUNT(*) FROM task_queue_metadata;"

# Verify counts match (tasks: 85, metadata: 5)
```

**Rollback:**
```bash
# If counts don't match, rollback
sqlite3 workspace.db "DELETE FROM tasks; DELETE FROM task_queue_metadata;"
# Then retry migration
```

---

### Step 5: Migrate orchestration_decisions.db (If Exists)

**Commands:**
```bash
cd ~/data-projects

# Check if database exists
if [ -f meridian-core/logs/orchestration_decisions.db ]; then
    sqlite3 workspace.db <<EOF
    ATTACH 'meridian-core/logs/orchestration_decisions.db' AS orch_source;
    
    -- Copy orchestration_decisions table
    INSERT INTO orchestration_decisions 
    SELECT * FROM orch_source.orchestration_decisions;
    
    -- Verify count
    SELECT 'Decisions migrated:', COUNT(*) FROM orchestration_decisions;
    
    DETACH orch_source;
    EOF
else
    echo "orchestration_decisions.db not found - skipping migration"
fi
```

**Validation:**
```bash
# If database exists, verify counts
if [ -f meridian-core/logs/orchestration_decisions.db ]; then
    sqlite3 meridian-core/logs/orchestration_decisions.db "SELECT COUNT(*) FROM orchestration_decisions;"
    sqlite3 workspace.db "SELECT COUNT(*) FROM orchestration_decisions;"
fi
```

---

### Step 6: Update Code References

**Files to Update:**

1. **meridian-core/src/meridian_core/learning/proposal_manager.py**
   - Change default path from `logs/proposals.db` to `../workspace.db`
   - Update `__init__` method

2. **meridian-core/src/meridian_core/orchestration/task_queue_db.py**
   - Change default path from `logs/task_queue.db` to `../workspace.db`
   - Update `__init__` method

3. **meridian-core/src/meridian_core/orchestration/orchestration_decision_db.py**
   - Change default path from `logs/orchestration_decisions.db` to `../workspace.db`
   - Update `__init__` method

**Commands:**
```bash
# Update ProposalManager
sed -i.bak 's|get_logs_dir() / "proposals.db"|Path(workspace_root) / "workspace.db"|g' \
    meridian-core/src/meridian_core/learning/proposal_manager.py

# Update TaskQueueDB
sed -i.bak 's|get_logs_dir() / "task_queue.db"|Path(workspace_root) / "workspace.db"|g' \
    meridian-core/src/meridian_core/orchestration/task_queue_db.py

# Update OrchestrationDecisionDB
sed -i.bak 's|get_logs_dir() / "orchestration_decisions.db"|Path(workspace_root) / "workspace.db"|g' \
    meridian-core/src/meridian_core/orchestration/orchestration_decision_db.py
```

**Note:** Actual implementation will need proper workspace_root detection. This is a simplified example.

---

### Step 7: Test Everything

**Test Commands:**
```bash
# Test WMS CLI
cd ~/data-projects
python -m workspace.wms.cli task list --limit 5

# Test database queries
sqlite3 workspace.db "SELECT COUNT(*) FROM workspace_tasks;"
sqlite3 workspace.db "SELECT COUNT(*) FROM proposals;"
sqlite3 workspace.db "SELECT COUNT(*) FROM tasks;"
sqlite3 workspace.db "SELECT COUNT(*) FROM task_queue_metadata;"

# Test orchestrator (if possible)
cd meridian-core
python -c "from meridian_core.orchestration.task_queue_db import TaskQueueDB; db = TaskQueueDB(); print('✅ TaskQueueDB OK')"
```

**Validation:**
- [ ] WMS CLI works
- [ ] All record counts match
- [ ] Orchestrator can read tasks
- [ ] No errors in logs

---

### Step 8: Archive Old Databases

**Commands:**
```bash
cd ~/data-projects

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Archive old databases
mv meridian-core/logs/proposals.db meridian-core/logs/proposals.db.archived_$TIMESTAMP
mv meridian-core/logs/task_queue.db meridian-core/logs/task_queue.db.archived_$TIMESTAMP

if [ -f meridian-core/logs/orchestration_decisions.db ]; then
    mv meridian-core/logs/orchestration_decisions.db meridian-core/logs/orchestration_decisions.db.archived_$TIMESTAMP
fi
```

**Validation:**
- [ ] Old databases archived
- [ ] New database works
- [ ] Can restore from archive if needed

---

## Execution Checklist

### Pre-Migration

- [ ] **Backup all databases** (Step 1)
  - [ ] workspace.db backed up
  - [ ] proposals.db backed up
  - [ ] task_queue.db backed up
  - [ ] orchestration_decisions.db backed up (if exists)
  - [ ] SQL dumps created
  - [ ] Backup directory documented

- [ ] **Verify current state**
  - [ ] Record counts documented
  - [ ] Database sizes noted
  - [ ] No active operations running

### Migration

- [ ] **Create consolidated schema** (Step 2)
  - [ ] proposals table created
  - [ ] tasks table created
  - [ ] task_queue_metadata table created
  - [ ] orchestration_decisions table created
  - [ ] All indexes created
  - [ ] Schema verified

- [ ] **Migrate proposals.db** (Step 3)
  - [ ] proposals table migrated
  - [ ] Record count verified (1 record)
  - [ ] Data integrity checked

- [ ] **Migrate task_queue.db** (Step 4)
  - [ ] tasks table migrated
  - [ ] task_queue_metadata table migrated
  - [ ] Record counts verified (85 tasks, 5 metadata)
  - [ ] Data integrity checked

- [ ] **Migrate orchestration_decisions.db** (Step 5)
  - [ ] Checked if database exists
  - [ ] If exists, migrated orchestration_decisions table
  - [ ] Record count verified

### Post-Migration

- [ ] **Update code references** (Step 6)
  - [ ] ProposalManager updated
  - [ ] TaskQueueDB updated
  - [ ] OrchestrationDecisionDB updated
  - [ ] All changes tested

- [ ] **Test everything** (Step 7)
  - [ ] WMS CLI works
  - [ ] Orchestrator can read tasks
  - [ ] Learning engine can read proposals
  - [ ] All record counts match
  - [ ] No errors in logs

- [ ] **Archive old databases** (Step 8)
  - [ ] Old databases renamed with timestamp
  - [ ] Archive location documented
  - [ ] Can restore if needed

### Final Validation

- [ ] **Data integrity check**
  - [ ] All record counts match
  - [ ] No duplicate records
  - [ ] Foreign key integrity (if applicable)
  - [ ] Database size reasonable

- [ ] **Functionality check**
  - [ ] WMS CLI works
  - [ ] Orchestrator works
  - [ ] Learning engine works (if enabled)
  - [ ] No regressions

- [ ] **Documentation**
  - [ ] Migration documented
  - [ ] Backup locations noted
  - [ ] Rollback procedure documented

---

## Success Criteria

**Migration is successful when ALL of these are true:**

- ✅ All original databases backed up
- ✅ All tables created in workspace.db
- ✅ All record counts match 100%
- ✅ Code updated to use workspace.db
- ✅ WMS CLI works with new database
- ✅ Orchestrator works with new database
- ✅ No data loss or corruption
- ✅ Old databases archived
- ✅ Tests passing

---

## Time Estimates

| Step | Estimated Time | Actual Time |
|------|----------------|-------------|
| Step 1: Backup | 5 min | |
| Step 2: Create Schema | 10 min | |
| Step 3: Migrate proposals | 5 min | |
| Step 4: Migrate task_queue | 15 min | |
| Step 5: Migrate orchestration_decisions | 5 min | |
| Step 6: Update Code | 30 min | |
| Step 7: Test | 20 min | |
| Step 8: Archive | 5 min | |
| **TOTAL** | **1.5 hours** | |

---

## Next Steps

1. ✅ **Phase 1.1 Complete** - Schema design
2. ✅ **Phase 1.2 Complete** - Migration plan
3. ⏳ **Phase 2** - Execute migration

---

**Status:** Ready for Phase 2 - Migration Implementation









