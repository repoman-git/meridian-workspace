# 2025-11-20 - Configuration Drift Tracking System

**Date:** 2025-11-20  
**Purpose:** Comprehensive system for tracking architecture, preventing configuration drift, and managing scope across repos  
**Context:** Master architecture governance and drift prevention

---

## Executive Summary

**Problem:** Multiple repos can drift from intended architecture, causing:
- Code placed in wrong repos (domain code in core)
- Dependencies violating ADR-001 rules
- Scope creep beyond intended architecture
- Inconsistent patterns across repos
- Loss of alignment with master architecture

**Solution:** Multi-layered drift tracking system:
1. **Master Architecture Repository** (workspace-level)
2. **Architecture State Tracking** (database)
3. **Drift Detection Engine** (automated scanning)
4. **Architecture Roadmap** (future state planning)
5. **Task-to-Architecture Mapping** (traceability)

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    CONFIGURATION DRIFT TRACKING SYSTEM                        │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  MASTER ARCHITECTURE LAYER                                                    │
│  (Single Source of Truth - Workspace Level)                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│  • Master architecture diagrams (all repos)                                   │
│  • Current state architecture (as-designed)                                   │
│  • Future state architecture (roadmap)                                        │
│  • Architecture decision records (ADR-XXX)                                    │
│  • Component placement rules (ADR-001)                                        │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  ARCHITECTURE STATE DATABASE                                                  │
│  (workspace.db - architecture_tracking schema)                                │
├──────────────────────────────────────────────────────────────────────────────┤
│  Tables:                                                                      │
│  • master_architectures → Master diagrams and specs                           │
│  • architecture_states → Current vs Future state                              │
│  • component_placements → Where components SHOULD be                         │
│  • drift_detections → Detected violations                                     │
│  • architecture_tasks → Tasks linked to architectural goals                   │
│  • scope_bounds → Repository scope definitions                                │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  DRIFT DETECTION ENGINE                                                       │
│  (Automated Scanning & Monitoring)                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│  Scans for:                                                                   │
│  • Component placement violations (domain code in core)                       │
│  • Dependency violations (core importing domain)                              │
│  • Import violations (domain-specific libraries in core)                      │
│  • Scope violations (features outside repo scope)                             │
│  • Pattern violations (inconsistent architectural patterns)                   │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  PREVENTION MECHANISMS                                                        │
│  (Pre-commit Hooks, CI/CD, Governance Checks)                                │
├──────────────────────────────────────────────────────────────────────────────┤
│  • Pre-commit hooks (block violations)                                        │
│  • Pre-push checks (validate architecture)                                    │
│  • CI/CD pipeline (automated drift detection)                                 │
│  • Manual audits (periodic reviews)                                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Master Architecture Repository

### Location: `data-projects/architecture/`

**Structure:**
```
data-projects/
├── architecture/                    ← NEW: Master architecture repository
│   ├── master/
│   │   ├── meridian-core/
│   │   │   ├── architecture.md                    ← Master architecture
│   │   │   ├── component-map.json                 ← Component placement rules
│   │   │   └── dependencies.json                  ← Allowed dependencies
│   │   ├── meridian-research/
│   │   │   ├── architecture.md
│   │   │   ├── component-map.json
│   │   │   └── scope-boundaries.json
│   │   └── meridian-trading/
│   │       ├── architecture.md
│   │       ├── component-map.json
│   │       └── scope-boundaries.json
│   │
│   ├── roadmaps/
│   │   ├── meridian-core-roadmap.md              ← Future state
│   │   ├── meridian-research-roadmap.md
│   │   ├── meridian-trading-roadmap.md
│   │   └── cross-repo-roadmap.md                 ← Cross-repo roadmap
│   │
│   ├── diagrams/
│   │   ├── 2025-11-20-MERIDIAN-CORE-ARCHITECTURE.md
│   │   ├── 2025-11-20-MERIDIAN-RESEARCH-ARCHITECTURE.md
│   │   ├── 2025-11-20-MERIDIAN-TRADING-ARCHITECTURE.md
│   │   └── system-overview.md                    ← Overall system diagram
│   │
│   ├── decisions/
│   │   ├── ADR-001-COMPONENT-PLACEMENT.md        ← Architectural decisions
│   │   ├── ADR-002-CREDENTIAL-MANAGEMENT.md
│   │   └── ADR-XXX-*.md                          ← Future ADRs
│   │
│   └── rules/
│       ├── placement-rules.json                  ← Automated rules
│       ├── dependency-rules.json                 ← Dependency rules
│       └── scope-rules.json                      ← Scope boundaries
│
└── workspace.db                                   ← Architecture state tracking
```

### Master Architecture Files

#### `architecture/master/meridian-core/architecture.md`

```markdown
# Meridian Core - Master Architecture

**Version:** 2.0
**Status:** Current
**Last Updated:** 2025-11-20

## Architecture Principles
- Domain-agnostic framework
- Abstract interfaces for domain adapters
- NO domain-specific code
- Generic orchestration logic only

## Component Placement Rules
See ADR-001-COMPONENT-PLACEMENT.md

## Allowed Dependencies
- Python stdlib
- Generic libraries (filelock, pydantic)
- AI provider SDKs (for connectors only)
- NO domain-specific libraries (pandas, numpy)

## Scope Boundaries
- Framework and orchestration only
- Learning engine (abstract)
- Connectors (generic)
- NO trading/research-specific logic
```

#### `architecture/master/meridian-core/component-map.json`

```json
{
  "version": "1.0",
  "repo": "meridian-core",
  "components": [
    {
      "name": "LearningEngine",
      "location": "src/meridian_core/learning/learning_engine.py",
      "type": "abstract_base_class",
      "domain": "agnostic",
      "allowed_imports": ["typing", "abc", "dataclasses"],
      "forbidden_imports": ["pandas", "numpy", "meridian_trading", "meridian_research"]
    },
    {
      "name": "ProposalManager",
      "location": "src/meridian_core/learning/proposal_manager.py",
      "type": "generic_utility",
      "domain": "agnostic",
      "allowed_imports": ["sqlalchemy", "sqlite3", "json"],
      "forbidden_imports": ["pandas", "trading_libraries"]
    }
  ],
  "rules": {
    "no_domain_imports": true,
    "no_domain_specific_libraries": true,
    "abstract_interfaces_only": true
  }
}
```

#### `architecture/master/meridian-core/dependencies.json`

```json
{
  "version": "1.0",
  "repo": "meridian-core",
  "allowed_imports": {
    "stdlib": ["typing", "abc", "dataclasses", "json", "sqlite3", "datetime"],
    "generic_libraries": ["filelock", "pydantic"],
    "ai_sdks": ["anthropic", "openai", "google.generativeai"],
    "database": ["sqlalchemy"]
  },
  "forbidden_imports": {
    "domain_libraries": ["pandas", "numpy", "yfinance", "openbb"],
    "domain_adapters": ["meridian_trading", "meridian_research"],
    "trading_specific": ["backtrader", "zipline"]
  },
  "rules": {
    "core_cannot_import_domain": true,
    "no_domain_specific_data_structures": true
  }
}
```

### Architecture Roadmaps

#### `architecture/roadmaps/meridian-core-roadmap.md`

```markdown
# Meridian Core - Architecture Roadmap

**Current State:** v2.0 (2025-11-20)
**Future State:** v3.0 (Q1 2026)

## Future State Architecture

### Planned Enhancements
1. **Enhanced Learning Integration** (Q4 2025)
   - Automatic learning cycles
   - Proposal application mechanism
   - Effectiveness tracking

2. **Real-time Learning** (Q1 2026)
   - Learn during execution
   - Dynamic agent capability discovery
   - Cross-domain learning

### Tasks Linked to Roadmap
- WS-TASK-XXX: Implement automatic learning cycles → Future State 1
- WS-TASK-YYY: Add real-time learning → Future State 2

## Migration Path
- Phase 1: Complete learning integration
- Phase 2: Add real-time capabilities
- Phase 3: Cross-domain learning
```

---

## 2. Architecture State Database Schema

### Database: `workspace.db` (extends existing schema)

```sql
-- ============================================================================
-- MASTER ARCHITECTURE TRACKING
-- ============================================================================

-- Master architecture definitions
CREATE TABLE master_architectures (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,                    -- meridian-core, meridian-research, etc.
    version TEXT NOT NULL,                 -- 2.0, 3.0, etc.
    architecture_file TEXT NOT NULL,       -- Path to architecture.md
    component_map_file TEXT,               -- Path to component-map.json
    dependencies_file TEXT,                -- Path to dependencies.json
    scope_boundaries_file TEXT,            -- Path to scope-boundaries.json
    status TEXT NOT NULL,                  -- current, deprecated, future
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    created_by TEXT,                       -- session/user
    notes TEXT
);

-- Architecture states (current vs future)
CREATE TABLE architecture_states (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    state_type TEXT NOT NULL,              -- current, future, deprecated
    version TEXT NOT NULL,
    architecture_id TEXT,                  -- FK to master_architectures
    description TEXT,
    roadmap_file TEXT,                     -- Path to roadmap.md
    target_date DATE,
    status TEXT NOT NULL,                  -- planned, in_progress, completed
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (architecture_id) REFERENCES master_architectures(id)
);

-- Component placement rules (where components SHOULD be)
CREATE TABLE component_placements (
    id TEXT PRIMARY KEY,
    component_name TEXT NOT NULL,
    component_type TEXT NOT NULL,          -- class, module, package
    correct_repo TEXT NOT NULL,            -- Where it SHOULD be
    correct_location TEXT,                 -- Path where it should be
    architecture_id TEXT,                  -- FK to master_architectures
    rationale TEXT,
    rules JSON,                            -- Placement rules (allowed/forbidden imports)
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (architecture_id) REFERENCES master_architectures(id),
    UNIQUE(component_name, architecture_id)
);

-- Architecture task mapping (tasks linked to architectural goals)
CREATE TABLE architecture_tasks (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,                 -- WS-TASK-XXX or repo task ID
    architecture_state_id TEXT,            -- FK to architecture_states
    architectural_goal TEXT,               -- What architecture goal this achieves
    component_id TEXT,                     -- FK to component_placements (optional)
    milestone TEXT,                        -- Future state milestone
    priority TEXT,                         -- HIGH, MEDIUM, LOW
    status TEXT NOT NULL,                  -- pending, in_progress, completed
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (architecture_state_id) REFERENCES architecture_states(id),
    FOREIGN KEY (component_id) REFERENCES component_placements(id)
);

-- Repository scope definitions
CREATE TABLE scope_bounds (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    scope_name TEXT NOT NULL,              -- e.g., "orchestration", "learning"
    description TEXT,
    included TEXT,                         -- What's IN scope
    excluded TEXT,                         -- What's OUT of scope
    boundaries JSON,                       -- Detailed boundaries
    architecture_id TEXT,                  -- FK to master_architectures
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (architecture_id) REFERENCES master_architectures(id)
);

-- ============================================================================
-- DRIFT DETECTION
-- ============================================================================

-- Detected drift violations
CREATE TABLE drift_detections (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    violation_type TEXT NOT NULL,          -- component_placement, dependency, scope, pattern
    severity TEXT NOT NULL,                -- HIGH, MEDIUM, LOW
    file_path TEXT NOT NULL,               -- File with violation
    component_name TEXT,                   -- Component that violates
    detected_rule TEXT,                    -- Which rule was violated
    expected_location TEXT,                -- Where it SHOULD be
    actual_location TEXT,                  -- Where it actually is
    violation_details TEXT,                -- Detailed description
    detected_at TIMESTAMP NOT NULL,
    detected_by TEXT,                      -- automated, manual, ci_cd
    status TEXT NOT NULL,                  -- open, resolved, ignored
    resolved_at TIMESTAMP,
    resolved_by TEXT,
    resolution_notes TEXT,
    related_task_id TEXT,                  -- Task to fix this
    FOREIGN KEY (related_task_id) REFERENCES workspace_tasks(id)
);

-- Drift scan history
CREATE TABLE drift_scans (
    id TEXT PRIMARY KEY,
    scan_type TEXT NOT NULL,               -- full, incremental, pre_commit
    scan_start TIMESTAMP NOT NULL,
    scan_end TIMESTAMP,
    repos_scanned TEXT,                    -- JSON array
    violations_found INTEGER DEFAULT 0,
    violations_high INTEGER DEFAULT 0,
    violations_medium INTEGER DEFAULT 0,
    violations_low INTEGER DEFAULT 0,
    status TEXT NOT NULL,                  -- running, completed, failed
    triggered_by TEXT,                     -- user, ci_cd, scheduled
    results_file TEXT                      -- Path to detailed results
);

-- ============================================================================
-- CONFIGURATION STATE TRACKING
-- ============================================================================

-- Configuration snapshots (for tracking changes)
CREATE TABLE configuration_snapshots (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    snapshot_type TEXT NOT NULL,           -- full, incremental
    configuration_hash TEXT,               -- Hash of configuration state
    snapshot_data JSON,                    -- Full configuration state
    taken_at TIMESTAMP NOT NULL,
    taken_by TEXT,
    notes TEXT
);

-- Configuration changes (diff tracking)
CREATE TABLE configuration_changes (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    change_type TEXT NOT NULL,             -- added, removed, modified
    component_name TEXT,
    file_path TEXT,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP NOT NULL,
    changed_by TEXT,
    commit_hash TEXT,
    drift_detection_id TEXT,               -- FK if this caused a drift detection
    FOREIGN KEY (drift_detection_id) REFERENCES drift_detections(id)
);
```

---

## 3. Drift Detection Engine

### Automated Scanner

```python
# workspace/drift_detector.py

class DriftDetector:
    """Automated configuration drift detection."""
    
    def scan_repo(self, repo_path: str, repo_name: str) -> List[DriftViolation]:
        """
        Scan repository for drift violations.
        
        Checks:
        1. Component placement violations
        2. Dependency violations
        3. Import violations
        4. Scope violations
        5. Pattern violations
        """
        violations = []
        
        # Get master architecture
        master_arch = self.get_master_architecture(repo_name)
        
        # Check component placement
        violations.extend(self.check_component_placement(repo_path, master_arch))
        
        # Check dependencies
        violations.extend(self.check_dependencies(repo_path, master_arch))
        
        # Check imports
        violations.extend(self.check_imports(repo_path, master_arch))
        
        # Check scope boundaries
        violations.extend(self.check_scope(repo_path, master_arch))
        
        return violations
    
    def check_component_placement(self, repo_path: str, master_arch: dict) -> List[DriftViolation]:
        """Check if components are in correct repos."""
        violations = []
        
        for component in master_arch['components']:
            actual_location = self.find_component(repo_path, component['name'])
            expected_location = component['location']
            
            if actual_location != expected_location:
                violations.append(DriftViolation(
                    type="component_placement",
                    component=component['name'],
                    expected=expected_location,
                    actual=actual_location,
                    severity="HIGH"
                ))
        
        return violations
    
    def check_dependencies(self, repo_path: str, master_arch: dict) -> List[DriftViolation]:
        """Check for forbidden dependencies."""
        violations = []
        
        for file_path in self.find_python_files(repo_path):
            imports = self.extract_imports(file_path)
            
            for imp in imports:
                if imp in master_arch['forbidden_imports']:
                    violations.append(DriftViolation(
                        type="dependency",
                        file=file_path,
                        violation=f"Forbidden import: {imp}",
                        severity="HIGH"
                    ))
        
        return violations
    
    def check_imports(self, repo_path: str, master_arch: dict) -> List[DriftViolation]:
        """Check for import rule violations."""
        violations = []
        
        # Check core doesn't import domain adapters
        if repo_path.endswith("meridian-core"):
            for file_path in self.find_python_files(repo_path):
                imports = self.extract_imports(file_path)
                
                if any("meridian_trading" in imp or "meridian_research" in imp 
                       for imp in imports):
                    violations.append(DriftViolation(
                        type="import",
                        file=file_path,
                        violation="Core importing from domain adapter",
                        severity="HIGH"
                    ))
        
        return violations
    
    def check_scope(self, repo_path: str, master_arch: dict) -> List[DriftViolation]:
        """Check for scope violations."""
        violations = []
        
        scope_bounds = master_arch.get('scope_bounds', {})
        
        for file_path in self.find_python_files(repo_path):
            file_scope = self.analyze_file_scope(file_path)
            
            if not self.is_in_scope(file_scope, scope_bounds):
                violations.append(DriftViolation(
                    type="scope",
                    file=file_path,
                    violation="File outside repository scope",
                    severity="MEDIUM"
                ))
        
        return violations
```

### Detection Rules

#### `architecture/rules/placement-rules.json`

```json
{
  "version": "1.0",
  "rules": [
    {
      "name": "core_no_domain_imports",
      "repo": "meridian-core",
      "type": "import",
      "pattern": "from meridian_trading|from meridian_research",
      "severity": "HIGH",
      "message": "Core cannot import from domain adapters"
    },
    {
      "name": "core_no_domain_libraries",
      "repo": "meridian-core",
      "type": "dependency",
      "forbidden": ["pandas", "numpy", "yfinance", "openbb"],
      "severity": "HIGH",
      "message": "Core cannot use domain-specific libraries"
    },
    {
      "name": "domain_imports_core_ok",
      "repo": "meridian-*",
      "type": "import",
      "pattern": "from meridian_core",
      "severity": "INFO",
      "message": "Domain adapters can import from core",
      "allowed": true
    }
  ]
}
```

---

## 4. Prevention Mechanisms

### Pre-commit Hook

```bash
#!/bin/bash
# workspace/.git/hooks/pre-commit

# Run drift detection
python workspace/drift_detector.py --pre-commit

# If violations found, block commit
if [ $? -ne 0 ]; then
    echo "❌ Drift violations detected. Commit blocked."
    echo "Run: python workspace/drift_detector.py --show-violations"
    exit 1
fi
```

### CI/CD Pipeline

```yaml
# .github/workflows/drift-detection.yml

name: Drift Detection

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  detect-drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Drift Detection
        run: |
          python workspace/drift_detector.py --scan-all
      
      - name: Report Violations
        if: failure()
        run: |
          python workspace/drift_detector.py --report-violations
```

---

## 5. Task-to-Architecture Mapping

### Link Tasks to Architectural Goals

```json
{
  "architecture_tasks": [
    {
      "task_id": "WS-TASK-002",
      "title": "Implement TradingLearningEngine",
      "architectural_goal": "Complete self-learning for trading domain",
      "architecture_state": "future_state_v3.0",
      "milestone": "Phase 2: Domain Learning",
      "component": {
        "name": "TradingLearningEngine",
        "correct_repo": "meridian-trading",
        "correct_location": "src/meridian_trading/learning/trading_learning_engine.py"
      },
      "scope": "meridian-trading/learning",
      "dependencies": [],
      "priority": "HIGH"
    }
  ]
}
```

---

## Implementation Plan

### Phase 1: Master Architecture Setup

1. **Create architecture directory structure**
   - `architecture/master/` - Master specs
   - `architecture/roadmaps/` - Future state
   - `architecture/diagrams/` - Architecture diagrams
   - `architecture/rules/` - Automated rules

2. **Move existing architecture docs**
   - Move `2025-11-20-*-ARCHITECTURE.md` to `architecture/diagrams/`
   - Create master architecture specs

3. **Create component maps**
   - Define where each component should be
   - Define allowed/forbidden imports per repo

### Phase 2: Database Schema

1. **Extend workspace.db**
   - Add architecture tracking tables
   - Add drift detection tables
   - Add configuration snapshot tables

2. **Create migration script**
   - Import existing architecture data
   - Import component placements from ADR-001

### Phase 3: Drift Detection Engine

1. **Create drift detector**
   - Automated scanning
   - Rule-based detection
   - Violation reporting

2. **Create prevention mechanisms**
   - Pre-commit hooks
   - CI/CD integration
   - Periodic scans

### Phase 4: Task Mapping

1. **Link tasks to architecture**
   - Map tasks to architectural goals
   - Link to future state milestones
   - Track progress toward architecture goals

---

## Usage Examples

### Track Architecture State

```python
from workspace.db.workspace_db import WorkspaceDB

db = WorkspaceDB()

# Register master architecture
db.register_master_architecture(
    repo="meridian-core",
    version="2.0",
    architecture_file="architecture/master/meridian-core/architecture.md"
)

# Define component placement
db.define_component_placement(
    component_name="LearningEngine",
    correct_repo="meridian-core",
    correct_location="src/meridian_core/learning/learning_engine.py"
)
```

### Detect Drift

```python
from workspace.drift_detector import DriftDetector

detector = DriftDetector()

# Scan all repos
violations = detector.scan_all_repos()

# Report violations
for violation in violations:
    print(f"❌ {violation.type}: {violation.component}")
    print(f"   Expected: {violation.expected_location}")
    print(f"   Actual: {violation.actual_location}")
```

### Link Task to Architecture

```python
# Link task to architectural goal
db.link_task_to_architecture(
    task_id="WS-TASK-002",
    architecture_state_id="future_state_v3.0",
    architectural_goal="Complete self-learning for trading domain",
    milestone="Phase 2: Domain Learning"
)
```

---

## Summary

### What We're Tracking

1. **Master Architecture** - Single source of truth for all repos
2. **Architecture States** - Current vs Future state
3. **Component Placements** - Where components SHOULD be
4. **Scope Boundaries** - What's in/out of scope per repo
5. **Drift Violations** - Detected deviations from architecture
6. **Configuration Changes** - Track what changed and when
7. **Task Mapping** - Link tasks to architectural goals

### Prevention Mechanisms

1. **Automated Scanning** - Detect drift automatically
2. **Pre-commit Hooks** - Block violations before commit
3. **CI/CD Checks** - Validate on push/PR
4. **Periodic Audits** - Scheduled scans
5. **Task Traceability** - Ensure tasks align with architecture

---

**Last Updated:** 2025-11-20  
**Status:** Design Complete - Awaiting Implementation

