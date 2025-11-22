# File Mapping Coverage Analysis

**Date:** 2025-11-22 16:28:15  
**Task:** Day 2 Task 2.1 - Current State Analysis  
**Status:** Analysis Complete

---

## Summary

- **Total Files:** 1200
- **Unregistered Files:** 162
- **Mapped Files (estimated):** 1038
- **Current Coverage:** 86.5%
- **Target Coverage:** 70.0%
- **Gap to Target:** 0.0%

---

## Breakdown by Repository

### meridian-core
- **Total files:** 364
- **Unregistered:** 48
- **Mapped:** 316
- **Coverage:** 86.8%

### meridian-research
- **Total files:** 207
- **Unregistered:** 50
- **Mapped:** 157
- **Coverage:** 75.8%

### meridian-trading
- **Total files:** 588
- **Unregistered:** 34
- **Mapped:** 554
- **Coverage:** 94.2%

### workspace
- **Total files:** 41
- **Unregistered:** 30
- **Mapped:** 11
- **Coverage:** 26.8%


---

## Pattern Analysis

### By File Extension

- **.py**: 155 files (95.7%)
- **.md**: 6 files (3.7%)
- **.json**: 1 files (0.6%)

### By Top-Level Directory

- **tests**: 78 files (48.1%)
- **src**: 54 files (33.3%)
- **scripts**: 19 files (11.7%)
- **wms**: 7 files (4.3%)
- **db**: 4 files (2.5%)

### Special Categories

- **Test files:** 76 (46.9%)
- **Config/docs files:** 7 (4.3%)
- **Core Python files:** 79 (48.8%)

---

## High-Value Files to Map (Priority 1)

These are core Python files (non-test, non-config) that should be mapped first.

### Total High-Value Files: 79

### meridian-core (19 files)

- `src/meridian_core/evaluations/book_prompt_evaluator.py`
- `src/meridian_core/db/models.py`
- `src/meridian_core/db/pool_monitor.py`
- `src/meridian_core/api/server.py`
- `src/meridian_core/monitoring/metrics.py`
- `src/meridian_core/monitoring/cost_tracker.py`
- `src/meridian_core/monitoring/health.py`
- `src/meridian_core/extraction/vector_index.py`
- `src/meridian_core/extraction/book_chunker.py`
- `src/meridian_core/extraction/embedding_helper.py`
- `src/meridian_core/orchestrator/convergence.py`
- `src/meridian_core/orchestrator/tool_access_controller.py`
- `src/meridian_core/orchestrator/lmstudio_master.py`
- `src/meridian_core/orchestrator/meta_review.py`
- `src/meridian_core/orchestrator/voting.py`
- `src/meridian_core/orchestrator/allocation.py`
- `src/meridian_core/orchestrator/decision_memory.py`
- `src/meridian_core/orchestrator/preflight.py`
- `tests/smoke_test_core.py`

### meridian-research (26 files)

- `src/meridian_research/utils/logging.py`
- `src/meridian_research/utils/metrics.py`
- `src/meridian_research/utils/structured_logging.py`
- `src/meridian_research/utils/encryption.py`
- `src/meridian_research/utils/rate_limiter.py`
- `src/meridian_research/utils/credential_store.py`
- `src/meridian_research/utils/secret_manager.py`
- `src/meridian_research/utils/alerting.py`
- `src/meridian_research/utils/validation.py`
- `src/meridian_research/db/backend.py`
- `src/meridian_research/db/models.py`
- `src/meridian_research/db/embeddings.py`
- `src/meridian_research/db/storage.py`
- `src/meridian_research/db/vector_utils.py`
- `src/meridian_research/templates/models.py`
- `src/meridian_research/templates/loader.py`
- `src/meridian_research/templates/executor.py`
- `src/meridian_research/export/json_formatter.py`
- `src/meridian_research/export/csv_formatter.py`
- `src/meridian_research/export/factory.py`
- ... and 6 more

### meridian-trading (5 files)

- `src/meridian_trading/data/gold_data_pipeline.py`
- `src/meridian_trading/data/cot_fetcher.py`
- `src/meridian_trading/reviews/multi_ai_project_review.py`
- `tests/smoke_test_trading.py`
- `tests/orchestrator/conftest.py`

### workspace (29 files)

- `wms/context_manager.py`
- `wms/bastard_integration.py`
- `wms/workflow_engine.py`
- `wms/governance_engine.py`
- `wms/__init__.py`
- `wms/cli.py`
- `wms/architecture_validator.py`
- `db/models.py`
- `db/__init__.py`
- `db/workspace_db.py`
- `db/migration.py`
- `scripts/create_housekeeping_task.py`
- `scripts/scan_unregistered_files.py`
- `scripts/sync_workspace_docs.py`
- `scripts/import_architecture_tasks.py`
- `scripts/db_status.py`
- `scripts/commit_all_repos.py`
- `scripts/generate_governance_context.py`
- `scripts/housekeeping.py`
- `scripts/import_architecture_tasks_v2.py`
- ... and 9 more


---

## Top 20 Unmapped Files (All Categories)

1. **meridian-core**: `src/meridian_core/evaluations/book_prompt_evaluator.py`
1. **meridian-core**: `src/meridian_core/orchestration/preflight_spec.md`
1. **meridian-core**: `src/meridian_core/orchestration/orchestrator_spec.md`
1. **meridian-core**: `src/meridian_core/orchestration/ai_registry.json`
1. **meridian-core**: `src/meridian_core/db/models.py`
1. **meridian-research**: `src/meridian_research/_assets/AI-GUIDELINES.md`
1. **meridian-research**: `src/meridian_research/utils/logging.py`
1. **meridian-research**: `src/meridian_research/utils/metrics.py`
1. **meridian-research**: `src/meridian_research/utils/structured_logging.py`
1. **meridian-research**: `src/meridian_research/utils/encryption.py`
1. **meridian-trading**: `src/meridian_trading/test/test_failover.py`
1. **meridian-trading**: `src/meridian_trading/data/gold_data_pipeline.py`
1. **meridian-trading**: `src/meridian_trading/data/cot_fetcher.py`
1. **meridian-trading**: `src/meridian_trading/reviews/multi_ai_project_review.py`
1. **meridian-trading**: `tests/test_ig_connection.py`
1. **workspace**: `wms/context_manager.py`
1. **workspace**: `wms/bastard_integration.py`
1. **workspace**: `wms/workflow_engine.py`
1. **workspace**: `wms/governance_engine.py`
1. **workspace**: `wms/__init__.py`

---

## Mapping Strategy

### Target: 70% Coverage

**Current:** 86.5%  
**Target:** 70.0%  
**Gap:** 0.0%

### Recommended Approach

1. **Priority 1: Map High-Value Core Files** (79 files)
   - Focus on non-test, non-config Python files
   - Files in `src/` directories
   - Files you actually work with

2. **Priority 2: Map Frequently Used Files**
   - Files in `scripts/` directories
   - Files in `wms/` directories (workspace management)
   - Files in `db/` directories (database access)

3. **Priority 3: Skip Low-Priority Files**
   - Test files (unless blocking something)
   - Config files (usually obvious placement)
   - Documentation files (not code)

### Estimated Effort

- **High-value files to map:** ~79 files
- **Estimated time:** 2 hours (Task 2.2)
- **Expected coverage after mapping:** ~70%+

---

## Files to Skip (Low Priority)

These can be mapped later or skipped:

- **Test files:** 76 files (obvious placement)
- **Config/docs:** 7 files (obvious placement)

**Total skip:** 83 files

---

## Next Steps

1. ✅ Task 2.1 Complete - Analysis done
2. ⏭️  Task 2.2: Map High-Value Files (2 hours)
   - Map 79 high-value core files
   - Target: 70% coverage
   - Focus on files you actually work with

---

**Analysis Generated:** 2025-11-22 16:28:15  
**Next Task:** Day 2 Task 2.2 - Map High-Value Files
