# File-to-Component Mapping Strategy

**Date:** 2025-11-21  
**Status:** Active Strategy  
**Purpose:** Systematically map 290 unregistered files to architecture components

---

## Executive Summary

- **Total Files Scanned:** 333
- **Currently Mapped:** 43 (12.9%)
- **Unmapped Files:** 290 (87.1%)
- **Registered Components:** 53 (across 4 repos)

### Current State by Repository

| Repository | Total Files | Mapped | Unmapped | Coverage |
|-----------|-------------|--------|----------|----------|
| meridian-core | 145 | 15 | 130 | 10.3% |
| meridian-research | 98 | 13 | 85 | 13.3% |
| meridian-trading | 63 | 15 | 48 | 23.8% |
| workspace | 27 | 0 | 27 | 0% |

---

## Component Inventory

### meridian-core (15 components)

**Types:**
- `abstract_base_class` (1): LearningEngine
- `analytics_module` (1): EffectivenessTracker
- `consensus_component` (1): VotingManager
- `core_class` (1): AIOrchestrator
- `execution_component` (1): TaskExecutor
- `integration_component` (1): ConnectorManager
- `learning_implementation` (1): OrchestrationLearningEngine
- `orchestration_extension` (1): AutonomousOrchestrator
- `review_component` (1): ReviewOrchestrator
- `routing_component` (1): AgentSelector
- `safety_component` (1): PreflightManager
- `security_component` (1): CredentialStore
- `service_module` (1): ProposalManager
- `workflow_component` (2): LearningCycleManager, TaskPipelineExecutor

### meridian-research (13 components)

**Types:**
- `adapter` (1): MeridianCoreAdapter
- `core_engine` (1): ResearchEngine
- `feedback_component` (1): ResearchFeedbackCollector
- `knowledge_component` (1): KnowledgeProvider
- `learning_component` (3): ResearchLearningBridge, ResearchPatternDetector, ResearchSessionStore
- `skill_component` (2): SkillLoader, SkillAdapter
- `task_component` (2): ResearchTaskManager, ResearchTaskSync
- `workflow_component` (2): WorkflowOrchestrator, WorkflowEngine

### meridian-trading (15 components)

**Types:**
- `adapter` (1): OrchestratorBridge
- `filter` (3): TDOMFilter, TDOWFilter, TDOYFilter
- `indicator` (3): WilliamsRIndicator, ATRIndicator, COTIndicator
- `risk_component` (2): RiskManager, CorrelationManager
- `scanner` (1): MarketScanner
- `security_component` (1): TradingCredentialManager
- `strategy` (3): WilliamsRReversalStrategy, CombinedTimingStrategy, COTTdomStrategy
- `utility` (1): TradingDataValidator

### workspace (10 components)

**Types:**
- `data_component` (2): WorkspaceDBModels, WorkspaceDBManager
- `management_component` (5): ContextManager, GovernanceEngine, WorkflowEngine, BastardIntegration, ArchitectureValidator
- `script` (3): GovernanceContextGenerator, WorkspaceHousekeeping, WorkspaceSessionStart

---

## File Categorization Patterns

### Pattern 1: Directory-Based Mapping

Files in the same directory typically belong to the same component:

```
src/meridian_core/learning/*.py → LearningEngine component (or related learning components)
src/meridian_core/orchestration/*.py → Orchestration components
src/meridian_core/connectors/*.py → Connector-related component (needs registration)
```

### Pattern 2: File Type Mapping

**Init files (`__init__.py`):**
- Map to the primary component in that directory
- Or create a "Package" component type if the directory has multiple components

**Main entry points (`main.py`, `cli.py`):**
- Map to appropriate root component or create "CLI" component
- Usually belongs to the core engine component

**Config files (`*_config.py`, `config.py`):**
- Map to the component that uses the config
- Or create a "Configuration" component type

**Tests (`test_*.py`, `tests/`):**
- Map to the component they test
- Can create "Test" component type or map directly to tested component

### Pattern 3: Functional Mapping

**Connectors (`*_connector.py`):**
- All connector files should map to a "Connector" component
- May need to register a general ConnectorManager or individual connector components

**Utilities (`*_utils.py`, `utils/`):**
- Map to a "Utilities" component or to the component that uses them
- Generic utilities → shared utility component

**Security (`*_security.py`, `*_credential*.py`):**
- Map to security/credential components
- Already have CredentialStore, TradingCredentialManager registered

---

## Mapping Heuristics

### Heuristic 1: Path-Based Matching

1. **Exact path match:** If component has `expected_path`, map files in that directory
2. **Directory match:** Files in same directory as component's expected path → that component
3. **Parent directory:** Files in parent/child directories → logical parent component

### Heuristic 2: Import-Based Matching

1. If file imports a component, it likely belongs to that component's ecosystem
2. Files that are imported by a component likely belong to it

### Heuristic 3: Naming Conventions

1. Files with component name in their filename → that component
   - `learning_engine.py` → LearningEngine
   - `risk_manager.py` → RiskManager
2. Files with domain prefix → domain component
   - `research_*.py` in meridian-research → ResearchEngine or related
   - `trading_*.py` in meridian-trading → Trading components

### Heuristic 4: Functionality-Based

1. **Orchestration files** → Orchestration components (AIOrchestrator, AutonomousOrchestrator, etc.)
2. **Learning files** → Learning components (LearningEngine, OrchestrationLearningEngine)
3. **Connector files** → ConnectorManager or connector-specific components
4. **Data access files** → Data components or the component they support

---

## Priority Mapping Order

### Phase 1: Core Infrastructure (HIGH PRIORITY)

**Goal:** Map core files that other files depend on

1. **Entry Points**
   - `src/*/__init__.py` → Package components
   - `src/*/main.py` → Core engine components
   - `src/*/cli.py` → CLI/entry components

2. **Connector Files** (meridian-core, meridian-research, meridian-trading)
   - All `connectors/*.py` files
   - **Action:** Register "ConnectorManager" or "AI Connectors" component if not exists

3. **Configuration Files**
   - `*_config.py` files
   - **Action:** Map to components that use them

### Phase 2: Module-Specific Files (MEDIUM PRIORITY)

**Goal:** Map files within existing component directories

1. **Learning Module** (meridian-core)
   - Files in `src/meridian_core/learning/` not yet mapped
   - Map to LearningEngine, OrchestrationLearningEngine, or create new learning components

2. **Orchestration Module** (meridian-core)
   - Files in `src/meridian_core/orchestration/` not yet mapped
   - Map to orchestration components (AIOrchestrator, AgentSelector, etc.)

3. **Research Module** (meridian-research)
   - Files in `src/meridian_research/*/` not yet mapped
   - Map to research components based on subdirectory

4. **Trading Module** (meridian-trading)
   - Files in `src/meridian_trading/*/` not yet mapped
   - Map to trading components based on subdirectory

### Phase 3: Workspace Management (MEDIUM PRIORITY)

**Goal:** Map workspace management files

1. **WMS Files**
   - All files in `workspace/wms/` → Workspace management components
   - May need to register additional workspace components

2. **Database Files**
   - Files in `workspace/db/` → WorkspaceDBModels, WorkspaceDBManager

3. **Scripts**
   - Files in `workspace/scripts/` → Script components

### Phase 4: Utility & Supporting Files (LOW PRIORITY)

**Goal:** Map remaining utility and supporting files

1. **Utility Files**
   - `utils/*.py` → Utility components or to components that use them

2. **Test Files**
   - `tests/*.py` → Test components or to components they test

3. **Documentation**
   - Markdown files → Documentation components (optional)

---

## Mapping Rules

### Rule 1: One Component Per Primary File

- Each `.py` file should map to exactly one primary component
- Mapping type: `direct` (primary component)
- Can have `indirect` mappings if file supports multiple components

### Rule 2: Init Files

- `__init__.py` files map to the primary component of their directory
- If directory has multiple components, map to the "package" or "module" component

### Rule 3: Supporting Files

- Supporting files (configs, utilities) map to the component they support
- If shared across components, map to a "shared" or "common" component

### Rule 4: Component Boundaries

- Files should map to components in the same repository
- Cross-repo mappings indicate potential architecture issue

### Rule 5: Mapping Validation

- After mapping, validate that:
  1. File imports match component boundaries
  2. No circular dependencies
  3. Component scope is respected

---

## Missing Components

### Components That May Need Registration

Based on unmapped file patterns:

1. **Connector Components** (all repos)
   - Generic: "AI Connectors" or "Connector Manager"
   - Specific: Individual connector components (OpenAIConnector, AnthropicConnector, etc.)

2. **Package/Module Components**
   - For `__init__.py` files that don't fit into existing components

3. **CLI Components**
   - For `cli.py` and command-line entry points

4. **Configuration Components**
   - For configuration files that are shared or complex

5. **Utility Components**
   - For generic utility files

6. **Test Components**
   - For test files (optional - can map to tested component)

---

## Mapping Process

### Step 1: Analyze Unmapped Files

```bash
# Get list of unregistered files
python -m workspace.wms.cli arch unregistered --repo <repo>

# Or use scan script
python workspace/scripts/scan_unregistered_files.py --repo <repo>
```

### Step 2: Determine Component

For each file:
1. Check if component exists (via directory, imports, naming)
2. If component exists → proceed to Step 3
3. If component doesn't exist → register component first

### Step 3: Register Component (if needed)

```bash
python -m workspace.wms.cli arch register \
  <component_name> \
  <component_type> \
  <repo> \
  --path <expected_path> \
  --description <description>
```

### Step 4: Map File to Component

```bash
python -m workspace.wms.cli arch map-file \
  <file_path> \
  <component_id> \
  --reason "File belongs to component because..." \
  --type direct
```

### Step 5: Validate Mapping

```bash
# Check mapping status
python -m workspace.wms.cli arch status

# Validate specific file
python -m workspace.wms.cli arch mappings --repo <repo>
```

---

## Automated Mapping Opportunities

### Pattern-Based Auto-Mapping

We can create scripts to automatically map files based on patterns:

1. **Directory-Based Auto-Mapping**
   - Files in `src/meridian_core/learning/` → LearningEngine or related
   - Files in `src/meridian_core/orchestration/` → Orchestration components

2. **Filename-Based Auto-Mapping**
   - Files with component name → that component
   - `*_connector.py` → Connector components

3. **Import-Based Auto-Mapping**
   - Files importing a component → related to that component

### Bulk Mapping Script

Create a script that:
1. Groups files by pattern
2. Suggests component mappings
3. Allows review before applying
4. Batch applies mappings

---

## Success Criteria

### Phase 1 Complete (High Priority Files)

- [ ] All entry points mapped (`__init__.py`, `main.py`, `cli.py`)
- [ ] All connector files mapped or components registered
- [ ] All core engine files mapped

### Phase 2 Complete (Module Files)

- [ ] All files in existing component directories mapped
- [ ] 80%+ coverage for each major module (learning, orchestration, research, trading)

### Phase 3 Complete (Full Coverage)

- [ ] 95%+ overall coverage
- [ ] All critical files mapped
- [ ] All unmapped files reviewed and categorized (mapped, ignored, or component needed)

---

## Tools & Commands

### Status Checking

```bash
# Overall status
python -m workspace.wms.cli arch status

# Unregistered files
python -m workspace.wms.cli arch unregistered [--repo <repo>]

# Existing components
python -m workspace.wms.cli arch components [--repo <repo>]

# File mappings
python -m workspace.wms.cli arch mappings [--repo <repo>] [--component-id <id>]
```

### Scanning

```bash
# Full scan
python workspace/scripts/scan_unregistered_files.py

# Specific repo
python workspace/scripts/scan_unregistered_files.py --repo <repo>

# Summary only
python workspace/scripts/scan_unregistered_files.py --summary-only
```

### Component Management

```bash
# Register component
python -m workspace.wms.cli arch register <name> <type> <repo> [--path <path>] [--description <desc>]

# Map file
python -m workspace.wms.cli arch map-file <file_path> <component_id> [--reason <reason>] [--type <type>]
```

---

## Next Steps

1. **Start with Phase 1:** Map core infrastructure files (entry points, connectors)
2. **Register missing components:** Create connector and package components
3. **Create bulk mapping script:** Automate pattern-based mappings
4. **Validate mappings:** Ensure no boundary violations
5. **Document decisions:** Update architecture docs with mapping decisions

---

**Document Status:** Living document - update as mapping progresses  
**Last Updated:** 2025-11-21  
**Next Review:** After Phase 1 completion

