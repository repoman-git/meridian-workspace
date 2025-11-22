# Database Dependency Map

**Date:** 2025-11-22  
**Phase:** 0.2 - Dependency Analysis  
**Status:** ✅ COMPLETE

---

## Component → Database Mapping

### Workspace Management System (WMS)

**Primary Database:** `workspace.db`

**Components:**
- `workspace/wms/cli.py` - CLI commands
- `workspace/db/workspace_db.py` - Database manager
- `workspace/wms/governance_engine.py` - Governance enforcement
- `workspace/wms/architecture_validator.py` - Architecture validation
- `workspace/wms/bastard_integration.py` - Bastard integration
- `workspace/wms/context_manager.py` - Context management
- `workspace/wms/workflow_engine.py` - Workflow management

**Operations:**
- Task CRUD (create, read, update, delete)
- Architecture decision tracking
- Component placement tracking
- File mapping management
- Drift detection
- Session management

**Critical Dependencies:** HIGH - WMS cannot function without workspace.db

---

### Core Orchestrator

**Primary Databases:**
- `logs/task_queue.db` - Task queue storage
- `logs/orchestration_decisions.db` - Decision history (optional)
- `logs/proposals.db` - Proposal tracking (optional)

**Components:**
- `meridian-core/src/meridian_core/orchestration/orchestrator.py` - Main orchestrator
- `meridian-core/src/meridian_core/orchestration/task_queue_db.py` - TaskQueueDB
- `meridian-core/src/meridian_core/orchestration/orchestration_decision_db.py` - DecisionDB
- `meridian-core/src/meridian_core/learning/proposal_manager.py` - ProposalManager

**Operations:**
- Task queue management (load, save, query)
- Orchestration decision logging
- Proposal tracking for learning

**Critical Dependencies:** 
- task_queue.db: HIGH (required for task execution)
- orchestration_decisions.db: MEDIUM (optional logging)
- proposals.db: LOW (optional learning feature)

---

## File-by-File Dependency Analysis

### workspace.db Dependencies

**Files (20+):**

1. **workspace/db/workspace_db.py**
   - **Usage:** Main database class, all operations
   - **Operations:** CRUD for all workspace tables
   - **Critical:** YES

2. **workspace/wms/cli.py**
   - **Usage:** CLI commands (list-tasks, show-task, etc.)
   - **Operations:** Read/write tasks, components, decisions
   - **Critical:** YES

3. **workspace/scripts/*.py** (15+ files)
   - **Usage:** Various maintenance scripts
   - **Operations:** Import, cleanup, backup, housekeeping
   - **Critical:** MEDIUM (scripts can be updated)

---

### proposals.db Dependencies

**Files (2-3):**

1. **meridian-core/src/meridian_core/learning/proposal_manager.py**
   - **Usage:** ProposalManager class initialization
   - **Operations:** Add proposals, query proposals
   - **Critical:** MEDIUM (learning feature, optional)

2. **meridian-core/src/meridian_core/learning/orchestration_data.py**
   - **Usage:** Data access for learning engine
   - **Operations:** Read proposals for analysis
   - **Critical:** LOW (optional feature)

---

### orchestration_decisions.db Dependencies

**Files (2-3):**

1. **meridian-core/src/meridian_core/orchestration/orchestrator.py**
   - **Usage:** Initialize OrchestrationDecisionDB if enabled
   - **Operations:** Log decisions during orchestration
   - **Critical:** LOW (optional logging feature)

2. **meridian-core/src/meridian_core/orchestration/orchestration_decision_db.py**
   - **Usage:** DecisionDB class
   - **Operations:** Add decisions, query history
   - **Critical:** LOW (optional feature)

---

### task_queue.db Dependencies

**Files (2-3):**

1. **meridian-core/src/meridian_core/orchestration/task_queue_db.py**
   - **Usage:** TaskQueueDB class
   - **Operations:** Load/save tasks, query tasks
   - **Critical:** HIGH (required for task execution)

2. **meridian-core/src/meridian_core/orchestration/orchestrator.py**
   - **Usage:** Initialize TaskQueueDB if enabled
   - **Operations:** Use TaskQueueDB for task storage
   - **Critical:** MEDIUM (can fallback to JSON)

---

## Migration Risk Assessment

### Critical Dependencies (Must Update)

**HIGH RISK:**
- `workspace/db/workspace_db.py` - Core database class
- `workspace/wms/cli.py` - CLI commands
- `meridian-core/src/meridian_core/orchestration/task_queue_db.py` - Task queue

**Migration Impact:** HIGH - These must be updated for consolidation

---

### Medium Dependencies (Should Update)

**MEDIUM RISK:**
- `workspace/scripts/*.py` - Maintenance scripts
- `meridian-core/src/meridian_core/orchestration/orchestrator.py` - Orchestrator init

**Migration Impact:** MEDIUM - Update for consistency

---

### Low Dependencies (Optional Update)

**LOW RISK:**
- `meridian-core/src/meridian_core/learning/proposal_manager.py` - Optional feature
- `meridian-core/src/meridian_core/orchestration/orchestration_decision_db.py` - Optional logging

**Migration Impact:** LOW - Can update later if needed

---

## Schema Definitions Location

### SQLAlchemy Models

**Found in:**
- `workspace/db/models.py` - WorkspaceDB models
- `meridian-core/src/meridian_core/db/models.py` - Core Base models
- `meridian-core/src/meridian_core/orchestration/task_queue_db.py` - TaskQueueTask, TaskQueueMetadata
- `meridian-core/src/meridian_core/learning/proposal_manager.py` - Proposal model

**Total Model Files:** 4-5 files

---

## Dependency Summary

| Component | Database | Critical | Files to Update |
|-----------|----------|----------|-----------------|
| WMS CLI | workspace.db | HIGH | 20+ files |
| Orchestrator | task_queue.db | HIGH | 2-3 files |
| Orchestrator | orchestration_decisions.db | LOW | 2-3 files |
| Learning Engine | proposals.db | MEDIUM | 2-3 files |

**Total Files to Update:** ~25-30 files

---

## Migration Strategy by Component

### 1. Workspace Management (HIGH PRIORITY)

**Current:** `workspace.db`  
**Target:** `workspace.db` (consolidated)

**Changes Needed:**
- Add tables from other databases
- Update WorkspaceDB to handle new tables
- No path changes needed (same database)

**Risk:** LOW (adding tables, not changing existing)

---

### 2. Task Queue (HIGH PRIORITY)

**Current:** `logs/task_queue.db`  
**Target:** `workspace.db` (consolidated)

**Changes Needed:**
- Update TaskQueueDB to use workspace.db
- Change default path from `logs/task_queue.db` to `workspace.db`
- Update orchestrator initialization

**Risk:** MEDIUM (path change required)

---

### 3. Proposals (MEDIUM PRIORITY)

**Current:** `logs/proposals.db`  
**Target:** `workspace.db` (consolidated)

**Changes Needed:**
- Update ProposalManager to use workspace.db
- Change default path from `logs/proposals.db` to `workspace.db`
- Migrate proposals table

**Risk:** LOW (only 1 record, optional feature)

---

### 4. Orchestration Decisions (LOW PRIORITY)

**Current:** `logs/orchestration_decisions.db` (may not exist)  
**Target:** `workspace.db` (consolidated)

**Changes Needed:**
- Update OrchestrationDecisionDB to use workspace.db
- Change default path
- Create table if doesn't exist

**Risk:** LOW (optional feature, may not be used)

---

## Code Update Strategy

### Phase 1: Update Database Paths

**Pattern:** Find and replace database paths

```python
# Before
db_path = "logs/proposals.db"
db_path = "logs/task_queue.db"
db_path = "logs/orchestration_decisions.db"

# After
db_path = "../workspace.db"  # or use workspace_root
```

### Phase 2: Update Initialization

**Pattern:** Update default paths in classes

```python
# ProposalManager.__init__()
if db_path is None:
    db_path = str(workspace_root / "workspace.db")

# TaskQueueDB.__init__()
if db_path is None:
    db_path = str(workspace_root / "workspace.db")
```

### Phase 3: Update Tests

**Pattern:** Update test database paths

---

## Rollback Strategy

### If Migration Fails

1. **Restore from backup** (original databases preserved)
2. **Revert code changes** (git reset)
3. **Re-run with fixes**

### If Issues Found After Migration

1. **Keep original databases** for 30 days
2. **Monitor consolidated database** for issues
3. **Rollback code** if critical issues found

---

## Next Steps

1. ✅ **Phase 0.1 Complete** - Database inventory
2. ✅ **Phase 0.2 Complete** - Dependency analysis
3. ⏳ **Phase 1** - Design unified schema

---

**Status:** Ready for Phase 1 - Schema Design

