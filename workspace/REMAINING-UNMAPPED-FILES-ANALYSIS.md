# Remaining Unmapped Files Analysis

**Date:** 2025-11-21  
**Last Updated:** 2025-11-21 (after workspace path fix & quick wins)  
**Current Coverage:** 53.3% (179/336 files mapped)  
**Remaining:** 157 unmapped files

---

## Summary

### Current Status
- **Total Files Scanned:** 336
- **Mapped:** 179 files
- **Unmapped:** 157 files
- **Coverage:** 53.3%

### By Repository

| Repository | Total | Mapped | Unmapped | Coverage |
|-----------|-------|--------|----------|----------|
| meridian-core | 145 | 97 | 48 | 66.9% |
| meridian-research | 98 | 47 | 51 | 48.0% |
| meridian-trading | 63 | 26 | 37 | 41.3% |
| workspace | 29 | 9 | 20 | 31.0% |

**Recent Improvements:**
- ✅ Fixed workspace path prefix mismatch (9 paths normalized)
- ✅ Mapped quick wins: benchmarks (4), CLI (7), config (4), core (2) = 17 files
- ✅ Coverage improved from 46.3% → 53.3% (+7 percentage points)

---

## Remaining Files by Category

### 1. Test Files (76 files - 42% of unmapped)

**meridian-core:** 25 test files
- `tests/integration/test_full_orchestration.py`
- `tests/load/test_load_testing.py`
- `tests/test_allocation.py`
- `tests/test_benchmark_infrastructure.py`
- `tests/test_concurrent_writes.py`
- ... and 20 more

**meridian-research:** 21 test files
- `tests/test_cli_knowledge.py`
- `tests/test_cli_skills.py`
- `tests/test_cli_tasks.py`
- `tests/test_credential_store.py`
- `tests/test_encryption.py`
- ... and 16 more

**meridian-trading:** 29 test files
- `src/meridian_trading/test/test_failover.py`
- `tests/orchestrator/test_agent_selection.py`
- `tests/orchestrator/test_preflight_and_assignment.py`
- `tests/orchestrator/test_retry_and_failover.py`
- `tests/test_atr.py`
- ... and 24 more

**workspace:** 1 test file
- `scripts/test_db.py`

**Strategy:** Map to tested component or create "Test" component type. Low priority for now.

---

### 2. Utils/Support Files (17 files - 9% of unmapped)

**meridian-core:** 3 files
- `src/meridian_core/db/models.py` → Should map to AIOrchestrator (DB support)
- `src/meridian_core/db/pool_monitor.py` → Should map to AIOrchestrator
- `src/meridian_core/extraction/embedding_helper.py` → Should map to EffectivenessTracker

**meridian-research:** 12 files
- `src/meridian_research/db/backend.py` → Should map to ResearchSessionStore
- `src/meridian_research/db/embeddings.py` → Should map to ResearchSessionStore
- `src/meridian_research/db/models.py` → Should map to ResearchSessionStore
- `src/meridian_research/db/storage.py` → Should map to ResearchSessionStore
- `src/meridian_research/db/vector_utils.py` → Should map to ResearchSessionStore
- `src/meridian_research/utils/logging.py` → Should map to ResearchEngine
- `src/meridian_research/utils/metrics.py` → Should map to ResearchEngine
- `src/meridian_research/utils/structured_logging.py` → Should map to ResearchEngine
- `src/meridian_research/utils/encryption.py` → Should map to ResearchEngine
- `src/meridian_research/utils/rate_limiter.py` → Should map to ResearchEngine
- `src/meridian_research/utils/credential_store.py` → Should map to ResearchEngine
- `src/meridian_research/utils/secret_manager.py` → Should map to ResearchEngine
- `src/meridian_research/utils/alerting.py` → Should map to ResearchEngine

**workspace:** 1 file
- `scripts/db_status.py` → Should map to WorkspaceDBManager

**Strategy:** Map to parent component (component that uses them).

---

### 3. CLI/Scripts (7 files - 4% of unmapped)

**meridian-core:** 3 CLI files
- `src/meridian_core/cli/learning_dashboard.py` → Should map to LearningEngine
- `src/meridian_core/cli/meta_review.py` → Should map to ReviewOrchestrator
- `src/meridian_core/cli/orchestrator.py` → Should map to AIOrchestrator

**meridian-research:** 2 CLI files
- `src/meridian_research/cli/db.py` → Should map to ResearchSessionStore
- `src/meridian_research/cli/knowledge.py` → Should map to KnowledgeProvider

**workspace:** 2 files
- `wms/cli.py` → Should map to WorkspaceWorkflowEngine (already mapped with workspace/ prefix)
- `scripts/test_db.py` → Should map to WorkspaceDBManager

**Strategy:** Map to the component they provide interface for.

---

### 4. Config Files (6 files - 3% of unmapped)

**meridian-core:** 1 file
- `src/meridian_core/config/rate_limits.py` → Should map to ConnectorManager

**meridian-research:** 4 files
- `src/meridian_research/config.py` → Should map to ResearchEngine
- `src/meridian_research/credentials/__main__.py` → Should map to ResearchEngine
- `src/meridian_research/utils/credential_store.py` → Should map to ResearchEngine
- `src/meridian_research/utils/rate_limiter.py` → Should map to ResearchEngine

**meridian-trading:** 1 file
- `src/meridian_trading/config/credentials.py` → Should map to TradingCredentialManager

**Strategy:** Map to component that uses the config.

---

### 5. Benchmarks (4 files - 2% of unmapped)

**meridian-core:** 4 files
- `src/meridian_core/benchmarks/benchmark_tasks.py` → Should map to EffectivenessTracker
- `src/meridian_core/benchmarks/complex_benchmark_tasks.py` → Should map to EffectivenessTracker
- `src/meridian_core/benchmarks/connector_benchmark.py` → Should map to EffectivenessTracker
- `src/meridian_core/benchmarks/quality_scorer.py` → Should map to EffectivenessTracker

**Strategy:** All should map to EffectivenessTracker (analytics component).

---

### 6. Documentation (6 files - 3% of unmapped)

**meridian-core:** 3 files
- `src/meridian_core/connectors/mcp/README.md`
- `src/meridian_core/orchestration/orchestrator_spec.md`
- `src/meridian_core/orchestration/preflight_spec.md`

**meridian-research:** 3 files
- `src/meridian_research/_assets/AI-GUIDELINES.md`
- `src/meridian_research/_assets/docs/AI-HOUSE-MODEL-CORE-RULES.md`
- `src/meridian_research/_assets/docs/AI-HOUSE-MODEL.md`

**Strategy:** Optional - can map to related component or create "Documentation" component type. Low priority.

---

### 7. Core/Module Files (10 files - 6% of unmapped)

**meridian-core:** 2 files
- `src/meridian_core/core/auto_register_tools.py` → Should map to AIOrchestrator
- `src/meridian_core/orchestration/ai_registry.json` → Should map to AIOrchestrator

**meridian-research:** 0 files
- All core files mapped

**meridian-trading:** 2 files
- `src/meridian_trading/orchestration/autonomous_orchestrator.py` → Should map to OrchestratorBridge
- `src/meridian_trading/orchestration/validate_task_queue.py` → Should map to OrchestratorBridge

**workspace:** 6 files (path mismatch - should be mapped)
- `wms/context_manager.py` → Already mapped as `workspace/wms/context_manager.py`
- `wms/bastard_integration.py` → Already mapped as `workspace/wms/bastard_integration.py`
- `wms/workflow_engine.py` → Already mapped as `workspace/wms/workflow_engine.py`
- `wms/governance_engine.py` → Already mapped as `workspace/wms/governance_engine.py`
- `wms/architecture_validator.py` → Already mapped as `workspace/wms/architecture_validator.py`
- `wms/__init__.py` → Should map to WorkspaceWorkflowEngine

**Strategy:** Map to appropriate component. Fix workspace path issue.

---

### 8. Other Files (54 files - 30% of unmapped)

**meridian-core:** 16 files
- `src/meridian_core/api/server.py` → Should map to AIOrchestrator (API server)
- `src/meridian_core/evaluations/book_prompt_evaluator.py` → Should map to EffectivenessTracker
- `src/meridian_core/extraction/book_chunker.py` → Should map to EffectivenessTracker
- `src/meridian_core/extraction/vector_index.py` → Should map to EffectivenessTracker
- `src/meridian_core/monitoring/cost_tracker.py` → Should map to EffectivenessTracker
- `src/meridian_core/monitoring/metrics.py` → Should map to EffectivenessTracker
- `src/meridian_core/monitoring/health.py` → Should map to EffectivenessTracker
- `src/meridian_core/models/*.py` → Should map to appropriate component

**meridian-research:** 11 files
- `src/meridian_research/export/*.py` (7 files) → Should map to ResearchEngine
- `src/meridian_research/templates/*.py` (3 files) → Already mapped to SkillLoader
- `src/meridian_research/cli/*.py` → Various components

**meridian-trading:** 5 files
- `src/meridian_trading/data/cot_fetcher.py` → Should map to COTIndicator
- `src/meridian_trading/data/gold_data_pipeline.py` → Should map to MarketScanner
- `src/meridian_trading/reviews/multi_ai_project_review.py` → Should map to OrchestratorBridge

**workspace:** 22 files
- `db/*.py` (4 files) → Already mapped with workspace/ prefix
- `scripts/*.py` (18 files) → Should map to appropriate workspace components
- `wms/*.py` (6 files) → Already mapped with workspace/ prefix (path mismatch in scan)

**Strategy:** Map to related components based on functionality.

---

## Path Issues

### Workspace Path Mismatch
**Issue:** Workspace files are mapped with `workspace/` prefix but scan finds them without prefix.

**Example:**
- Mapped: `workspace/wms/context_manager.py`
- Scan finds: `wms/context_manager.py`

**Impact:** Workspace shows 0% coverage in scan but actually has 10 files mapped.

**Fix Needed:** Update scanning logic to normalize workspace paths OR update mappings to use consistent paths.

---

## Priority Mapping Plan

### Phase 3 (HIGH PRIORITY)
1. **Fix workspace path mismatch** (5-10 files)
2. **Map core/module files** (10 files) - Critical for architecture enforcement
3. **Map CLI files** (7 files) - Entry points, important for governance
4. **Map config files** (6 files) - Configuration management
5. **Map benchmarks** (4 files) - Analytics component

### Phase 4 (MEDIUM PRIORITY)
1. **Map utils/support files** (17 files) - Supporting infrastructure
2. **Map "Other" category files** (54 files) - Module-specific support files

### Phase 5 (LOW PRIORITY)
1. **Map test files** (76 files) - Optional, can map to tested component
2. **Map documentation files** (6 files) - Optional

---

## Quick Wins (Can Map Immediately)

These files have clear component mappings:

1. **Benchmarks → EffectivenessTracker** (4 files)
2. **CLI files → Appropriate components** (7 files)
3. **Config files → Using components** (6 files)
4. **Core files → Parent components** (10 files)

**Estimated Impact:** ~27 files = +8% coverage (would bring us to ~54% overall)

---

## Next Steps

1. **Fix workspace path normalization** in scanning/mapping
2. **Map quick wins** (benchmarks, CLI, config, core files)
3. **Map remaining module support files**
4. **Handle tests and documentation** (optional, lower priority)

---

**Last Updated:** 2025-11-21  
**Status:** Ready for Phase 3 mapping

