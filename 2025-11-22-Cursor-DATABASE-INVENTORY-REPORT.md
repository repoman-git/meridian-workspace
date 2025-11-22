# Database Inventory Report

**Date:** 2025-11-22  
**Phase:** 0.1 - Discovery & Planning  
**Status:** ✅ COMPLETE

---

## Executive Summary

**Total Databases Found:** 20  
**Databases to Consolidate:** 3-4 (primary operational databases)  
**Total Data Volume:** ~2.5MB  
**Migration Complexity:** MEDIUM

---

## Primary Databases (To Consolidate)

### 1. workspace.db (Root)

**Location:** `/Users/simonerses/data-projects/workspace.db`  
**Size:** 1.1MB  
**Status:** ✅ ACTIVE (primary workspace database)

**Tables (26 total):**
- `workspace_tasks`: 62 records
- `architecture_components`: 53 records
- `code_component_mappings`: 183 records
- `unregistered_files`: 289 records
- `bastard_reports`: 8 records
- `cross_repo_issues`: 4 records
- `work_contexts`: 4 records
- `session_activities`: 4 records
- `workspace_sessions`: 3 records
- `architecture_decisions`: 4 records
- `architecture_states`: 0 records
- `drift_scans`: 0 records
- `context_switches`: 0 records
- `configuration_snapshots`: 0 records
- `session_decisions`: 0 records
- `component_placements`: 0 records
- `drift_detections`: 0 records
- `session_issues`: 0 records
- `architecture_tasks`: 0 records
- `configuration_changes`: 0 records
- `workflows`: 0 records
- `violations`: 0 records
- `import_rules`: 0 records
- `scale_tiers`: 0 records
- `workflow_stages`: 0 records
- `architecture_states_old`: 0 records
- `code_changes`: 0 records

**Total Records:** ~610 records

**Purpose:** WMS tasks, components, file mappings, architecture decisions, drift detection

---

### 2. workspace/workspace.db

**Location:** `/Users/simonerses/data-projects/workspace/workspace.db`  
**Size:** 392KB  
**Status:** ⚠️ DUPLICATE/EMPTY (appears to be unused copy)

**Tables (15 total):**
- All tables: 0 records

**Purpose:** Appears to be duplicate/backup - can be ignored or merged

**Recommendation:** Archive or merge if schema differs

---

### 3. meridian-core/logs/proposals.db

**Location:** `/Users/simonerses/data-projects/meridian-core/logs/proposals.db`  
**Size:** 440KB  
**Status:** ✅ ACTIVE

**Tables (26 total):**
- `proposals`: 1 record
- All other tables: 0 records

**Schema:** Uses shared Base model with many tables (orchestration_tasks, agent_allocations, etc.)

**Purpose:** Proposal tracking for learning engine

**Key Table:** `proposals` (1 record)

---

### 4. meridian-core/logs/task_queue.db

**Location:** `/Users/simonerses/data-projects/meridian-core/logs/task_queue.db`  
**Size:** 552KB  
**Status:** ✅ ACTIVE (just migrated from JSON)

**Tables (26 total):**
- `tasks`: 85 records
- `task_queue_metadata`: 5 records
- All other tables: 0 records

**Purpose:** Task queue storage (recently migrated from JSON)

**Key Tables:** `tasks` (85 records), `task_queue_metadata` (5 records)

---

### 5. orchestration_decisions.db

**Location:** NOT FOUND in `meridian-core/logs/`  
**Status:** ⚠️ REFERENCED BUT NOT FOUND

**Code References:**
- `meridian-core/src/meridian_core/orchestration/orchestrator.py` (line 133)
- `meridian-core/src/meridian_core/orchestration/orchestration_decision_db.py` (line 47)

**Default Path:** `logs/orchestration_decisions.db`

**Purpose:** Orchestration decision history

**Note:** Database may be created on-demand, or may not exist yet

---

## Secondary Databases (Not Consolidating)

### Benchmark/Test Databases

- `meridian-core/benchmarks/challenging_test/orchestration_decisions.db` (44KB, 14 records)
- `meridian-core/benchmarks/orchestrator_results/orchestration_decisions.db` (64KB, 72 records)

**Status:** Test data - keep separate

---

### Domain-Specific Databases

- `meridian-trading/data/positions.db` (20KB) - Trading positions
- `meridian-research/meridian_research_sessions.db` (116KB, 44 records) - Research sessions
- `meridian-research/meridian_research_tasks.db` (32KB, 3 records) - Research tasks

**Status:** Domain-specific - keep separate

---

### Empty/Template Databases

- Multiple `meridian.db` files (440KB each, 0 records) - Appear to be templates
- `meridian-core/logs/allocator_state.db` (440KB, minimal data)
- `meridian-core/logs/preflight_state.db` (440KB, 0 records)
- `meridian-core/logs/task_tracking.db` (440KB, 0 records)

**Status:** Empty or minimal - can be archived

---

## JSON Files Inventory

### Task/Proposal/Decision JSON Files

- `meridian-core/task-queue.json` (112KB) - ✅ MIGRATED to SQLite
- `meridian-core/src/meridian_core/orchestration/ai_registry.json` (4.1KB) - AI registry (keep as JSON)
- `meridian-core/benchmarks/*/task_queue.json` - Test data (keep separate)

**Total JSON State:** ~116KB (mostly migrated)

---

## Data Volume Summary

| Database | Size | Records | Status |
|----------|------|---------|--------|
| workspace.db | 1.1MB | ~610 | ✅ Consolidate |
| workspace/workspace.db | 392KB | 0 | ⚠️ Duplicate |
| proposals.db | 440KB | 1 | ✅ Consolidate |
| task_queue.db | 552KB | 90 | ✅ Consolidate |
| orchestration_decisions.db | N/A | ? | ⚠️ May not exist |
| **TOTAL (to consolidate)** | **~2.5MB** | **~701** | |

---

## Migration Complexity Assessment

### Complexity Factors

1. **Schema Overlap:** MEDIUM
   - workspace.db has unique WMS tables
   - proposals.db and task_queue.db share Base model (many common tables)
   - Need to merge schemas carefully

2. **Data Volume:** LOW
   - Only ~701 records total
   - Small database sizes
   - Fast migration expected

3. **Dependencies:** MEDIUM
   - Multiple code references to database paths
   - Need to update all connection strings
   - WMS CLI depends on workspace.db

4. **Risk Level:** MEDIUM
   - Well-tested migration pattern (similar to task_queue)
   - Good backup strategy available
   - Can rollback if needed

---

## Code Dependencies

### Files Using workspace.db

**Workspace Management:**
- `workspace/db/workspace_db.py` - Main database class
- `workspace/wms/cli.py` - CLI commands
- `workspace/scripts/*.py` - Various scripts (15+ files)

**Total References:** 20+ files

---

### Files Using proposals.db

**Core Framework:**
- `meridian-core/src/meridian_core/learning/proposal_manager.py` - ProposalManager class
- `meridian-core/src/meridian_core/learning/orchestration_data.py` - Data access

**Total References:** 2-3 files

---

### Files Using orchestration_decisions.db

**Core Framework:**
- `meridian-core/src/meridian_core/orchestration/orchestrator.py` - Orchestrator initialization
- `meridian-core/src/meridian_core/orchestration/orchestration_decision_db.py` - DecisionDB class

**Total References:** 2-3 files

---

### Files Using task_queue.db

**Core Framework:**
- `meridian-core/src/meridian_core/orchestration/task_queue_db.py` - TaskQueueDB class
- `meridian-core/src/meridian_core/orchestration/orchestrator.py` - Orchestrator initialization

**Total References:** 2-3 files

---

## Migration Strategy Recommendations

### Recommended Approach

1. **Primary Target:** `workspace.db` (already has most WMS data)
2. **Add Tables From:**
   - `proposals` table from proposals.db
   - `tasks` and `task_queue_metadata` from task_queue.db
   - `orchestration_decisions` table (if exists)

3. **Schema Strategy:**
   - Keep workspace.db schema as base
   - Add missing tables from other databases
   - Use table prefixes if needed to avoid conflicts

4. **Migration Order:**
   - Phase 1: Migrate proposals.db → workspace.db
   - Phase 2: Migrate task_queue.db → workspace.db
   - Phase 3: Migrate orchestration_decisions.db → workspace.db (if exists)

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Data Loss | LOW | Comprehensive backups before migration |
| Schema Conflicts | MEDIUM | Careful schema analysis, table prefixes if needed |
| Code Updates | MEDIUM | Find/replace database paths, test thoroughly |
| Performance | LOW | Small data volume, WAL mode enabled |
| Rollback | LOW | Keep original databases, can restore |

**Overall Risk:** MEDIUM (manageable with proper backups)

---

## Next Steps

1. ✅ **Phase 0.1 Complete** - Database inventory created
2. ⏳ **Phase 0.2** - Analyze dependencies and usage patterns
3. ⏳ **Phase 1** - Design unified schema
4. ⏳ **Phase 2** - Execute migration

---

**Status:** Ready for Phase 0.2 - Dependency Analysis

