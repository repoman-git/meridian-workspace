# WMS Implementation Specification - Integration Analysis

**Date:** November 20, 2025  
**Purpose:** Compare the WMS Implementation Specification with existing workspace database implementation and plan integration approach

---

## Executive Summary

The **Workspace Management System (WMS) Implementation Specification** (`workspace/WMS-IMPLEMENTATION-SPEC-FOR-CURSOR.md`) provides a comprehensive specification for an AI-governed workflow automation system. This document compares it with what has already been implemented and outlines an integration plan.

---

## What We Already Have

### ✅ Completed Components

1. **Database Foundation** (`workspace/db/`)
   - SQLAlchemy models for workspace tracking
   - Workspace database manager (`workspace_db.py`)
   - Migration scripts for JSON → Database
   - Database schema includes:
     - `WorkspaceTask` - Task tracking
     - `WorkspaceSession` - Session management
     - `CrossRepoIssue` - Cross-repo issues
     - `ArchitectureDecision` - ADR tracking
     - `ArchitectureState` - Architecture state snapshots
     - `ComponentPlacement` - Component placement rules
     - `DriftDetection` - Configuration drift tracking
     - `ContextSwitch` - Context switching history

2. **Documentation**
   - Architecture documents for each repo
   - Credential management documentation
   - Database technology analysis
   - Configuration drift tracking system design
   - Workspace context system design

3. **Initial Task Tracking**
   - JSON-based task tracking (`WORKSPACE-TASKS.json`)
   - Session logging (`SESSION-LOG.json`)
   - Cross-repo issues (`CROSS-REPO-ISSUES.json`)
   - Architecture decisions (`ARCHITECTURE-DECISIONS.json`)

---

## What the WMS Spec Adds

### 🆕 New Components Required

1. **Context Manager** (`wms/context_manager.py`)
   - **Status:** Partially implemented (context switches tracked in DB, but no manager)
   - **Need:** Full context manager class with `.workspace-context` file support
   - **Integration:** Build on top of existing `ContextSwitch` model

2. **Governance Engine** (`wms/governance_engine.py`)
   - **Status:** Not implemented
   - **Need:** Engine to enforce ADRs and validate task placement
   - **Integration:** Use existing `ArchitectureDecision` and `ComponentPlacement` models
   - **Features:**
     - Validate task placement against ADRs
     - Check scale appropriateness
     - Detect over-engineering
     - Determine correct repo for tasks

3. **Workflow Engine** (`wms/workflow_engine.py`)
   - **Status:** Not implemented
   - **Need:** Task lifecycle management with validation gates
   - **Integration:** Extend existing `WorkspaceTask` model with workflow status
   - **Features:**
     - Task creation with validation
     - Task start/complete with gates
     - Violation tracking
     - Integration with Governance and Bastard

4. **Bastard Integration** (`wms/bastard_integration.py`)
   - **Status:** Not implemented
   - **Need:** AI evaluation system integration
   - **Integration:** New model needed: `BastardReport`
   - **Features:**
     - Plan evaluation (before starting work)
     - Completion evaluation (before marking done)
     - Grade assignment (F/D/C/B/A/OVER_ENGINEERED)
     - Report generation

5. **CLI Interface** (`wms/cli.py`)
   - **Status:** Not implemented
   - **Need:** Click-based CLI for all WMS operations
   - **Commands Needed:**
     - `wms context set/show/clear` - Context management
     - `wms task create/start/complete/list` - Task management
     - `wms bastard report` - Bastard evaluation reports

---

## Database Schema Comparison

### Existing Models vs. WMS Spec Models

| Component | Existing Implementation | WMS Spec | Status |
|-----------|------------------------|----------|--------|
| **Tasks** | `WorkspaceTask` | `Task` | ✅ Compatible (needs extension) |
| **Sessions** | `WorkspaceSession` | `WorkSession` | ✅ Compatible |
| **Context** | `ContextSwitch` | `WorkContext` | ✅ Compatible (needs manager) |
| **ADRs** | `ArchitectureDecision` | `ArchitectureDecision` | ✅ Compatible |
| **Component Rules** | `ComponentPlacement` | `ComponentPlacementRule` | ✅ Compatible |
| **Violations** | `DriftDetection` | `Violation` | ⚠️ Similar but different purpose |
| **Bastard Reports** | ❌ Not implemented | `BastardReport` | ❌ Need to add |
| **Workflows** | ❌ Not implemented | `Workflow`, `WorkflowStage` | ❌ Need to add |
| **Scale Tiers** | ❌ Not implemented | `ScaleTier` | ❌ Need to add |
| **Import Rules** | ❌ Not implemented | `ImportRule` | ❌ Need to add |

### Model Extensions Needed

1. **WorkspaceTask** → Extend with:
   - `bastard_plan_grade` (String)
   - `bastard_completion_grade` (String)
   - `scale_tier` (Integer)
   - `assigned_repo` (String) - Already have `repos_affected`, might need to clarify
   - `assigned_by` (String) - Governance vs. manual
   - `started_at` (DateTime)
   - `completed_at` (DateTime) - Already have timestamps, check alignment

2. **New Models Needed:**
   - `BastardReport` - Evaluation reports
   - `Violation` - Governance violations (different from `DriftDetection`)
   - `Workflow` - Workflow definitions
   - `WorkflowStage` - Workflow stages
   - `ScaleTier` - Scale tier definitions
   - `ImportRule` - Import/dependency rules

---

## Integration Approach

### Phase 1: Database Schema Extension (Week 1)

**Goal:** Extend existing database to support WMS features

1. **Add New Models:**
   ```python
   # workspace/db/models.py additions:
   - BastardReport
   - Violation (separate from DriftDetection)
   - Workflow
   - WorkflowStage
   - ScaleTier
   - ImportRule
   ```

2. **Extend Existing Models:**
   ```python
   # WorkspaceTask additions:
   - bastard_plan_grade
   - bastard_completion_grade
   - scale_tier
   - assigned_by
   - workflow relationship
   - violation relationships
   - bastard_report relationships
   ```

3. **Create Migration Script:**
   - Add new tables
   - Add new columns to existing tables
   - Preserve existing data

### Phase 2: Core Components (Week 2)

**Goal:** Build core WMS components

1. **Context Manager** (`wms/context_manager.py`)
   - Build on existing `ContextSwitch` model
   - Add `.workspace-context` file support
   - Provide set/get/clear context methods

2. **Governance Engine** (`wms/governance_engine.py`)
   - Read ADRs from database (`ArchitectureDecision`)
   - Read component rules (`ComponentPlacement`)
   - Validate task placement
   - Detect scale mismatches
   - Determine correct repo

3. **Bastard Integration** (`wms/bastard_integration.py`)
   - Create integration layer for Meridian orchestration
   - Implement plan evaluation
   - Implement completion evaluation
   - Parse and store verdicts

### Phase 3: Workflow Engine (Week 3)

**Goal:** Build workflow orchestration

1. **Workflow Engine** (`wms/workflow_engine.py`)
   - Task creation with validation
   - Task lifecycle management
   - Integration with Governance and Bastard
   - Violation tracking and blocking

2. **Workflow Templates**
   - Feature template
   - Bugfix template
   - Refactor template

### Phase 4: CLI Interface (Week 4)

**Goal:** User-facing CLI

1. **CLI** (`wms/cli.py`)
   - Context commands
   - Task commands
   - Bastard commands
   - Rich output formatting

2. **Package Setup**
   - `pyproject.toml` for WMS package
   - Installation script
   - CLI entry point

---

## Key Integration Decisions

### 1. Model Naming

**Decision:** Keep existing model names where compatible, add WMS-specific models

- Keep `WorkspaceTask` (more descriptive than `Task`)
- Keep `ArchitectureDecision` (matches ADR convention)
- Add `BastardReport` (WMS-specific)
- Add `Violation` (separate from `DriftDetection` - violations are governance, drift is configuration)

### 2. Database Location

**Decision:** Use existing `workspace.db` location

- Current: `workspace_root/workspace.db`
- WMS spec: `workspace/wms/db/workspace.db`
- **Resolution:** Keep current location for consistency, or move to WMS-specific location

### 3. Violation vs. Drift Detection

**Decision:** Keep both models (different purposes)

- `Violation`: Governance violations (wrong repo, over-engineering, forbidden imports)
- `DriftDetection`: Configuration drift (actual vs. intended architecture state)
- They serve different purposes and can coexist

### 4. WorkContext vs. ContextSwitch

**Decision:** Extend `ContextSwitch` with manager functionality

- Current `ContextSwitch` tracks history
- WMS `WorkContext` tracks active context
- **Resolution:** Add `is_active` flag to `ContextSwitch` and create manager

### 5. Task Status Enum

**Decision:** Align with WMS spec

- WMS spec: `PLANNING`, `APPROVED`, `IN_PROGRESS`, `BLOCKED`, `COMPLETED`, `CANCELLED`
- Current: `pending`, `in_progress`, `completed`, `blocked`
- **Resolution:** Standardize on WMS enum values

---

## Migration Path

### Step 1: Schema Migration

```python
# workspace/db/migrations/add_wms_models.py
1. Add new models to models.py
2. Create Alembic migration
3. Run migration
4. Verify data integrity
```

### Step 2: Component Development

```python
# Build components in order:
1. Context Manager (simplest)
2. Governance Engine (uses existing models)
3. Bastard Integration (new capability)
4. Workflow Engine (orchestrates everything)
5. CLI (user interface)
```

### Step 3: Integration Testing

```python
# Test workflow:
1. wms context set core
2. wms task create
3. Verify governance validation
4. Verify Bastard evaluation
5. wms task start
6. wms task complete
7. Verify end-to-end flow
```

---

## Dependencies

### External Dependencies Needed

```toml
# Add to workspace/requirements.txt or pyproject.toml:
sqlalchemy>=2.0.0  # ✅ Already have
alembic>=1.12.0     # ❌ Need for migrations
click>=8.1.0        # ❌ Need for CLI
pyyaml>=6.0.0       # ❌ Need for skill/config files
rich>=13.0.0        # ❌ Need for pretty CLI output
```

### Internal Dependencies

- **meridian-core**: Required for Bastard integration (AI orchestration)
- **workspace/db**: Already implemented, just need extensions

---

## Success Criteria

Integration is complete when:

1. ✅ All WMS database models implemented
2. ✅ Context Manager functional
3. ✅ Governance Engine validates tasks
4. ✅ Bastard Integration evaluates plans and completions
5. ✅ Workflow Engine orchestrates full task lifecycle
6. ✅ CLI provides all commands
7. ✅ Existing data migrated successfully
8. ✅ End-to-end workflow tested

---

## Risks and Considerations

### Risk 1: Database Schema Changes

**Risk:** Migrating existing data might break current tracking  
**Mitigation:** Create comprehensive migration script with rollback capability

### Risk 2: Bastard Integration Complexity

**Risk:** Bastard integration requires Meridian Core orchestration which might be complex  
**Mitigation:** Start with mocked Bastard responses, integrate real calls later

### Risk 3: Model Conflicts

**Risk:** WMS spec models might conflict with existing models  
**Mitigation:** Keep separate namespaces, extend existing models where appropriate

### Risk 4: ADR Import

**Risk:** Importing existing ADRs from markdown files might be manual  
**Mitigation:** Create import script to parse ADR markdown files

---

## Next Steps

1. ✅ **Review spec** (current task)
2. ⏳ **Create detailed implementation plan**
3. ⏳ **Extend database schema** (add new models)
4. ⏳ **Build Context Manager**
5. ⏳ **Build Governance Engine**
6. ⏳ **Build Bastard Integration** (mocked initially)
7. ⏳ **Build Workflow Engine**
8. ⏳ **Build CLI**
9. ⏳ **Test end-to-end**
10. ⏳ **Document usage**

---

## Conclusion

The WMS Implementation Specification provides a comprehensive blueprint for adding governance and validation layers to the existing workspace database. The existing implementation provides a solid foundation:

- ✅ Database models and manager already exist
- ✅ Task tracking infrastructure in place
- ✅ Architecture decision tracking implemented
- ⚠️ Need to extend with WMS-specific features
- ⚠️ Need to add Governance and Bastard validation
- ⚠️ Need to add CLI interface

**Recommendation:** Proceed with integration in phases, building on existing foundation while adding WMS-specific capabilities.

---

**Status:** Analysis Complete - Ready for Implementation Planning  
**Created:** 2025-11-20  
**Related:** WS-TASK-005
