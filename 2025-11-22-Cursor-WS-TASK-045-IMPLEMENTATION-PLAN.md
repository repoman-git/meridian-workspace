# WS-TASK-045: SQLite Task Queue Migration - Implementation Plan

**Date:** 2025-11-22  
**Status:** ⚠️ **PARTIALLY IMPLEMENTED** - Needs Migration & Default Enablement  
**Priority:** CRITICAL  
**Effort:** 2 days

---

## Current State Analysis

### ✅ What's Already Done

1. **TaskQueueDB Class** - Fully implemented (`src/meridian_core/orchestration/task_queue_db.py`)
   - SQLite backend with WAL mode
   - Thread-safe with connection pooling
   - Query methods for filtering
   - Version control for optimistic concurrency

2. **Migration Script** - Exists (`scripts/migrate_task_queue_json_to_sqlite.py`)
   - Converts JSON → SQLite
   - Creates backups
   - Verifies migration

3. **Hybrid Support** - Orchestrator supports both backends
   - `use_sqlite_task_queue=True` flag
   - Backward compatible (defaults to JSON)
   - Seamless switching

4. **Documentation** - Complete (`docs/TASK_QUEUE_SQLITE.md`)
   - Usage examples
   - Migration guide
   - Troubleshooting

### ❌ What's Missing

1. **Not Default** - Still uses JSON by default
2. **No Migration Run** - Existing `task-queue.json` not migrated
3. **Registry Still JSON** - `ai_registry.json` still file-based (separate task)
4. **No Rollout Plan** - No systematic migration of existing deployments

---

## Implementation Plan

### Phase 1: Validate Current Implementation (2 hours)

**Goal:** Verify TaskQueueDB works correctly before migration

**Tasks:**
1. ✅ Review TaskQueueDB code for completeness
2. ✅ Test TaskQueueDB with sample data
3. ✅ Verify migration script works
4. ✅ Check for any edge cases or bugs

**Deliverable:** Validation report confirming implementation is ready

---

### Phase 2: Create Migration Strategy (2 hours)

**Goal:** Plan safe migration path

**Tasks:**
1. **Audit Current Usage**
   - Find all `task-queue.json` files in workspace
   - Check for active orchestrator instances
   - Document current task counts

2. **Create Migration Checklist**
   - Pre-migration backup strategy
   - Rollback plan
   - Verification steps

3. **Update Documentation**
   - Migration runbook
   - Rollback procedures
   - Troubleshooting guide

**Deliverable:** Migration runbook document

---

### Phase 3: Execute Migration (4 hours)

**Goal:** Migrate existing task queues to SQLite

**Tasks:**
1. **Backup All Task Queues**
   ```bash
   # Find all task-queue.json files
   find . -name "task-queue.json" -o -name "task_queue.json"
   
   # Backup each
   for file in $(find . -name "*task*queue*.json"); do
       cp "$file" "${file}.backup.$(date +%Y%m%d)"
   done
   ```

2. **Run Migration Script**
   ```bash
   cd meridian-core
   python scripts/migrate_task_queue_json_to_sqlite.py task-queue.json
   ```

3. **Verify Migration**
   - Check task counts match
   - Verify task data integrity
   - Test query operations

4. **Update Orchestrator Initialization**
   - Change default to `use_sqlite_task_queue=True`
   - Update all orchestrator instantiations
   - Update tests

**Deliverable:** Migrated databases, updated code

---

### Phase 4: Make SQLite Default (2 hours)

**Goal:** Switch default backend to SQLite

**Tasks:**
1. **Update AutonomousOrchestrator**
   - Change default `use_sqlite_task_queue=False` → `True`
   - Keep JSON as fallback option
   - Add deprecation warning for JSON usage

2. **Update All Initialization Points**
   - Find all orchestrator instantiations
   - Update to use SQLite (or remove flag to use default)
   - Update examples in docs

3. **Update Tests**
   - Ensure tests work with SQLite
   - Add tests for migration path
   - Test backward compatibility

**Deliverable:** SQLite as default, JSON as optional fallback

---

### Phase 5: Cleanup & Documentation (2 hours)

**Goal:** Finalize migration and document

**Tasks:**
1. **Remove Old JSON Files** (after verification period)
   - Keep backups for 30 days
   - Archive old task-queue.json files
   - Document retention policy

2. **Update All Documentation**
   - Mark JSON as deprecated
   - Update all examples to use SQLite
   - Add migration notes to changelog

3. **Create Migration Summary**
   - What was migrated
   - Any issues encountered
   - Performance improvements observed

**Deliverable:** Complete documentation, migration summary

---

## Risk Mitigation

### Risk 1: Data Loss During Migration
**Mitigation:**
- Automatic backups before migration
- Verification checks after migration
- Rollback script ready

### Risk 2: Breaking Existing Code
**Mitigation:**
- Keep JSON as fallback option
- Gradual rollout (test → staging → production)
- Comprehensive testing before full migration

### Risk 3: Performance Regression
**Mitigation:**
- Benchmark before/after
- Monitor query performance
- Keep in-memory caching strategy

### Risk 4: Concurrent Access Issues
**Mitigation:**
- WAL mode already enabled
- Connection pooling configured
- Test with multiple processes

---

## Success Criteria

- ✅ All existing task queues migrated to SQLite
- ✅ SQLite is default backend
- ✅ No data loss during migration
- ✅ All tests pass
- ✅ Performance equal or better than JSON
- ✅ Documentation updated
- ✅ Rollback plan tested

---

## Timeline

**Day 1:**
- Morning: Phase 1 (Validation) + Phase 2 (Strategy)
- Afternoon: Phase 3 (Migration) start

**Day 2:**
- Morning: Phase 3 (Migration) complete
- Afternoon: Phase 4 (Default) + Phase 5 (Cleanup)

**Total:** 2 days as estimated

---

## Next Steps

1. **Immediate:** Run validation tests on TaskQueueDB
2. **Today:** Create migration runbook
3. **Tomorrow:** Execute migration
4. **Day 3:** Make SQLite default and cleanup

---

## Related Tasks

- **WS-TASK-005:** Database Consolidation (merge multiple DBs)
- **WS-TASK-026:** Unified Persistence Layer (registry.json migration)

**Note:** This task focuses on task_queue only. Registry migration is separate.

---

**Status:** Ready to execute  
**Blockers:** None  
**Dependencies:** None









