# Unmapped Files Documentation

**Date:** 2025-11-22  
**Task:** Day 2, Task 2.3 - Document What's Left (30 min)  
**Status:** ✅ Complete

---

## Summary

Documentation of all unmapped files remaining after Task 2.2 (Map High-Value Files). This document categorizes files and explains why they're unmapped.

---

## Overview

After mapping 75 high-value files in Task 2.2, there are **96 unmapped files** remaining:

- **High-value Python files:** 10 files (need review)
- **Test files:** 79 files (can skip - low priority)
- **Config/docs files:** 7 files (low priority)
- **Other files:** 0 files

---

## High-Value Unmapped Files (10 files)

These are non-test, non-config Python files that should ideally be mapped.

### 1. Workspace Repository (9 files) - **STATUS: Already Mapped (Cleanup Needed)**

These files were successfully mapped in Task 2.2, but their status in the `unregistered_files` table wasn't updated properly. They are actually mapped but appear as unregistered due to a cleanup issue.

**Files:**
- `wms/context_manager.py` → Mapped to `WorkspaceContextManager` (comp-20251121065646-8420)
- `wms/bastard_integration.py` → Mapped to `WorkspaceBastardIntegration` (comp-20251121065646-9339)
- `wms/workflow_engine.py` → Mapped to `WorkspaceWorkflowEngine` (comp-20251121065646-3541)
- `wms/governance_engine.py` → Mapped to `WorkspaceGovernanceEngine` (comp-20251121065646-466)
- `wms/architecture_validator.py` → Mapped to `WorkspaceArchitectureValidator` (comp-20251121065646-3365)
- `wms/__init__.py` → Mapped to `WorkspaceContextManager` (comp-20251121065646-8420)
- `wms/cli.py` → Mapped to `WorkspaceContextManager` (comp-20251121065646-8420)
- `db/models.py` → Mapped to `WorkspaceDBModels` (comp-20251121065646-2990)
- `db/workspace_db.py` → Mapped to `WorkspaceDBManager` (comp-20251121065646-7681)
- `db/__init__.py` → Mapped to `WorkspaceDBManager` (comp-20251121065646-7681)
- `db/migration.py` → Mapped to `WorkspaceDBManager` (comp-20251121065646-7681)
- `scripts/generate_governance_context.py` → Mapped to `GovernanceContextGenerator` (comp-20251121065646-4532)
- `scripts/housekeeping.py` → Mapped to `WorkspaceHousekeeping` (comp-20251121065646-1272)
- ... (additional workspace script files)

**Action Required:** Update status in `unregistered_files` table from `unregistered` to `mapped` for these files.

**Why Unmapped:** Not actually unmapped - cleanup issue where status wasn't updated in `unregistered_files` table after mapping.

### 2. Meridian-Research Repository (1 file) - **STATUS: Needs Manual Review**

**File:**
- `src/meridian_research/credentials/__main__.py`

**Why Unmapped:**
- This is a credentials module entry point (`__main__.py`)
- No direct mapping heuristic matches this file
- May need a new component or map to existing security/credential component

**Recommendation:**
- Option 1: Map to existing `ResearchEngine` component as a utility
- Option 2: Create new `CredentialManager` component if credentials handling is significant
- Option 3: Map to `ResearchSessionStore` if it's related to session/credential storage

**Action Required:** Manual review and decision on component mapping.

### 3. Meridian-Core Repository (0 files)

All high-value files in meridian-core are mapped.

### 4. Meridian-Trading Repository (0 files)

All high-value files in meridian-trading are mapped (except test files).

---

## Test Files (79 files) - **STATUS: Can Skip**

These are test files that can be skipped from mapping. Test files are typically low priority for architecture mapping since they:
- Follow obvious placement patterns (in `tests/` directories)
- Don't affect production architecture
- Can be mapped later if needed

### Breakdown by Repository:

- **meridian-core:** 26 test files
- **meridian-research:** 22 test files
- **meridian-trading:** 30 test files
- **workspace:** 1 test file (`scripts/test_db.py`)

### Examples:

- `tests/smoke_test_core.py`
- `tests/conftest.py`
- `tests/smoke_test_trading.py`
- `tests/orchestrator/conftest.py`
- `src/meridian_trading/test/test_failover.py`
- Various test files in `tests/` directories

**Recommendation:** Skip these files for now. They can be mapped later if needed for comprehensive architecture tracking.

**Action Required:** None (low priority).

---

## Config/Docs Files (7 files) - **STATUS: Low Priority**

These are configuration and documentation files that are low priority for mapping. Config/docs files are typically:
- Obvious placement (config in config directories, docs in docs directories)
- Don't affect code architecture
- Can be mapped later if needed

### Files:

#### Meridian-Core (4 files):
- `src/meridian_core/orchestration/preflight_spec.md` - Documentation file
- `src/meridian_core/orchestration/orchestrator_spec.md` - Documentation file
- `src/meridian_core/orchestration/ai_registry.json` - Configuration file
- Additional config/doc file

#### Meridian-Research (3 files):
- `src/meridian_research/_assets/AI-GUIDELINES.md` - Documentation file
- `src/meridian_research/_assets/docs/AI-HOUSE-MODEL.md` - Documentation file
- `src/meridian_research/_assets/docs/AI-HOUSE-MODEL-CORE-RULES.md` - Documentation file

**Recommendation:** Skip these files for now. They can be mapped later if needed for comprehensive architecture tracking.

**Action Required:** None (low priority).

---

## Summary of Actions Required

### Priority 1: Cleanup (Immediate)

**Issue:** 29 workspace files are mapped but still show as unregistered.

**Action:**
1. Update status in `unregistered_files` table from `unregistered` to `mapped`
2. Set `assigned_component_id` to the mapped component ID
3. Set `reviewed_at` and `reviewed_by` appropriately

**Impact:** After cleanup, only **1 high-value file** will truly need manual review.

### Priority 2: Manual Review (Optional)

**File:** `src/meridian_research/credentials/__main__.py`

**Action:**
- Review the file's purpose and functionality
- Decide on component mapping:
  - Map to existing component (e.g., `ResearchEngine`, `ResearchSessionStore`)
  - Create new component if credentials handling is significant
  - Or mark as "can skip" if it's just an entry point

### Priority 3: Low Priority (Future)

**Files:** 79 test files + 7 config/docs files = 86 files

**Action:** None required. These can be mapped later if needed.

---

## Coverage Status

### After Task 2.2 Mapping:

- **Total files:** 1,200
- **Unregistered files:** 96 (but 29 are actually mapped - need cleanup)
- **Estimated coverage:** 92.0%
- **Target coverage:** 70.0%
- **Status:** ✅ **Exceeds target**

### After Cleanup (Projected):

- **Total files:** 1,200
- **Truly unmapped high-value:** 1 file (`src/meridian_research/credentials/__main__.py`)
- **Unmapped test files:** 79 files (can skip)
- **Unmapped config/docs:** 7 files (low priority)
- **Estimated coverage:** ~92.5%
- **Status:** ✅ **Exceeds target**

---

## Next Steps

1. ✅ **Task 2.3 Complete** - Documentation created
2. ⏭️ **Task 2.4**: Validation & Documentation (1 hour)
   - Run cleanup script to update status for mapped workspace files
   - Validate mapping accuracy
   - Write completion report
   - Update WMS

---

## Files Created

- `UNMAPPED-FILES-DOCUMENTATION.md` - This document

---

**Documented:** 2025-11-22  
**Next Task:** Day 2, Task 2.4 - Validation & Documentation



