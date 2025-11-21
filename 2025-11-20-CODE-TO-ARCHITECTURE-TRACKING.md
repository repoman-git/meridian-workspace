# Code-to-Architecture Component Tracking System

**Date:** November 20, 2025  
**Purpose:** Track all code/files and updates back to agreed architecture components to prevent scope creep before deployment

---

## Executive Summary

**Problem:** 
- Code changes aren't linked to architecture components
- No way to validate changes align with agreed architecture before deployment
- Scope creep can occur without detection
- Files can be added that don't map to any architectural component

**Solution:**
A comprehensive **Code-to-Architecture Mapping System** that:
1. **Maps files/modules to architecture components** - Every file linked to an architectural component
2. **Tracks changes against components** - Git commits linked to components
3. **Pre-deployment validation** - Blocks deployment if changes aren't traceable
4. **Change authorization** - Requires architecture component assignment for new files
5. **Scope drift detection** - Detects files not linked to agreed architecture

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                  CODE-TO-ARCHITECTURE TRACKING SYSTEM                          │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  ARCHITECTURE COMPONENT REGISTRY                                               │
│  (Single Source of Truth - What Components Exist)                             │
├──────────────────────────────────────────────────────────────────────────────┤
│  • Registered architecture components (from master architecture)               │
│  • Component definitions (name, type, repo, path)                             │
│  • Component relationships (dependencies, interfaces)                          │
│  • Approved component scope (what's allowed in each component)                │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  FILE-TO-COMPONENT MAPPING                                                     │
│  (What Files Belong to Which Component)                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  • code_component_mappings → File → Component mapping                         │
│  • code_changes → Git commits → Component tracking                            │
│  • component_files → All files in each component                              │
│  • file_history → Change history per file                                     │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  CHANGE TRACKING                                                               │
│  (Track All Changes Against Components)                                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  • Git commit → Component mapping                                             │
│  • File changes → Component impact                                            │
│  • Change validation → Approved/Unapproved                                    │
│  • Scope validation → Within component scope                                  │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────────────────┐
│  PRE-DEPLOYMENT VALIDATION                                                     │
│  (Gate Before Deployment)                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│  • Validate all changed files map to components                               │
│  • Check no unregistered files                                                │
│  • Verify changes within component scope                                      │
│  • Block deployment if violations detected                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema Extensions

### New Models for Code-to-Component Tracking

```python
# workspace/db/models.py (additions)

# ============================================================================
# CODE-TO-ARCHITECTURE COMPONENT MAPPING
# ============================================================================

class ArchitectureComponent(Base):
    """Registered architecture components (from master architecture)."""
    
    __tablename__ = 'architecture_components'
    
    id = Column(String(50), primary_key=True)
    component_name = Column(String(200), nullable=False, unique=True)
    component_type = Column(String(50), nullable=False)  # module, class, service, package
    repo = Column(String(100), nullable=False, index=True)
    expected_path = Column(String(500))  # Where it should be (from architecture)
    description = Column(Text)
    
    # Component scope
    approved_scope = Column(Text)  # JSON: What's allowed in this component
    boundaries = Column(Text)  # JSON: What's NOT allowed
    
    # Status
    status = Column(String(50), nullable=False, default="active")  # active, deprecated, planned
    version = Column(String(50))  # Architecture version this belongs to
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    registered_by = Column(String(100))
    architecture_state_id = Column(String(50), ForeignKey('architecture_states.id'))
    
    # Relationships
    architecture_state = relationship("ArchitectureState", foreign_keys=[architecture_state_id])
    code_mappings = relationship("CodeComponentMapping", back_populates="component", cascade="all, delete-orphan")
    code_changes = relationship("CodeChange", back_populates="component")
    
    __table_args__ = (
        Index('idx_components_repo', 'repo'),
        Index('idx_components_status', 'status'),
        UniqueConstraint('component_name', 'repo', name='uq_component_name_repo'),
    )


class CodeComponentMapping(Base):
    """Maps files/modules to architecture components."""
    
    __tablename__ = 'code_component_mappings'
    
    id = Column(String(50), primary_key=True)
    file_path = Column(String(500), nullable=False)
    component_id = Column(String(50), ForeignKey('architecture_components.id'), nullable=False)
    
    # Mapping details
    mapping_type = Column(String(50))  # direct, indirect, dependency
    mapping_reason = Column(Text)  # Why this file belongs to this component
    
    # Validation
    is_validated = Column(Boolean, default=False)  # Manually validated
    validated_by = Column(String(100))
    validated_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(100))
    
    # Relationships
    component = relationship("ArchitectureComponent", back_populates="code_mappings")
    file_changes = relationship("CodeChange", back_populates="mapping")
    
    __table_args__ = (
        Index('idx_mappings_file', 'file_path'),
        Index('idx_mappings_component', 'component_id'),
        UniqueConstraint('file_path', name='uq_file_path'),
    )


class CodeChange(Base):
    """Tracks code changes and links to components."""
    
    __tablename__ = 'code_changes'
    
    id = Column(String(50), primary_key=True)
    commit_hash = Column(String(100), nullable=False, index=True)
    repo = Column(String(100), nullable=False, index=True)
    
    # Change details
    change_type = Column(String(50), nullable=False)  # added, modified, deleted, renamed
    file_path = Column(String(500), nullable=False)
    component_id = Column(String(50), ForeignKey('architecture_components.id'), nullable=True)
    mapping_id = Column(String(50), ForeignKey('code_component_mappings.id'), nullable=True)
    
    # Validation
    is_tracked = Column(Boolean, default=False)  # Mapped to component
    is_validated = Column(Boolean, default=False)  # Pre-deployment validated
    validation_status = Column(String(50))  # approved, rejected, pending, untracked
    validation_notes = Column(Text)
    
    # Scope check
    within_component_scope = Column(Boolean)  # Change is within component approved scope
    scope_violations = Column(Text)  # JSON: List of scope violations
    
    # Change impact
    lines_added = Column(Integer)
    lines_removed = Column(Integer)
    lines_modified = Column(Integer)
    
    # Metadata
    changed_at = Column(DateTime, nullable=False, index=True)
    changed_by = Column(String(100))
    commit_message = Column(Text)
    branch = Column(String(200))
    
    # Deployment tracking
    deployment_id = Column(String(50), ForeignKey('deployments.id'), nullable=True)
    deployment_status = Column(String(50))  # pending, deployed, rolled_back
    
    # Relationships
    component = relationship("ArchitectureComponent", back_populates="code_changes")
    mapping = relationship("CodeComponentMapping", back_populates="file_changes")
    
    __table_args__ = (
        Index('idx_changes_commit', 'commit_hash'),
        Index('idx_changes_repo', 'repo'),
        Index('idx_changes_file', 'file_path'),
        Index('idx_changes_component', 'component_id'),
        Index('idx_changes_validated', 'is_validated'),
        Index('idx_changes_tracked', 'is_tracked'),
    )


class UnregisteredFile(Base):
    """Files that don't map to any architecture component."""
    
    __tablename__ = 'unregistered_files'
    
    id = Column(String(50), primary_key=True)
    file_path = Column(String(500), nullable=False, unique=True)
    repo = Column(String(100), nullable=False, index=True)
    
    # Detection
    first_detected = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    detection_count = Column(Integer, default=1)
    
    # Status
    status = Column(String(50), default="unregistered")  # unregistered, under_review, mapped, ignored
    assigned_component_id = Column(String(50), ForeignKey('architecture_components.id'), nullable=True)
    
    # Review
    review_notes = Column(Text)
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime)
    
    # Relationships
    assigned_component = relationship("ArchitectureComponent")
    
    __table_args__ = (
        Index('idx_unregistered_repo', 'repo'),
        Index('idx_unregistered_status', 'status'),
    )


class DeploymentValidation(Base):
    """Pre-deployment validation results."""
    
    __tablename__ = 'deployment_validations'
    
    id = Column(String(50), primary_key=True)
    deployment_id = Column(String(50), nullable=False, index=True)
    validation_run = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Validation results
    status = Column(String(50), nullable=False)  # passed, failed, warning
    total_files = Column(Integer, default=0)
    tracked_files = Column(Integer, default=0)
    untracked_files = Column(Integer, default=0)
    violations = Column(Integer, default=0)
    
    # Details
    untracked_file_list = Column(Text)  # JSON: List of untracked files
    violation_details = Column(Text)  # JSON: List of violations
    validation_report = Column(Text)  # Full validation report
    
    # Metadata
    validated_by = Column(String(100))
    deployment_blocked = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_validations_deployment', 'deployment_id'),
        Index('idx_validations_status', 'status'),
        Index('idx_validations_run', 'validation_run'),
    )
```

---

## Workflow: Registering Components

### Step 1: Register Architecture Components

When architecture is defined/updated, register components:

```python
# workspace/tracking/component_registry.py

from workspace.db import WorkspaceDB

def register_component(
    component_name: str,
    component_type: str,
    repo: str,
    expected_path: str,
    approved_scope: dict = None,
    boundaries: dict = None
):
    """Register a new architecture component."""
    db = WorkspaceDB()
    
    component = ArchitectureComponent(
        component_name=component_name,
        component_type=component_type,
        repo=repo,
        expected_path=expected_path,
        approved_scope=json.dumps(approved_scope) if approved_scope else None,
        boundaries=json.dumps(boundaries) if boundaries else None,
        status="active",
        registered_by="architecture_setup"
    )
    
    db.session.add(component)
    db.session.commit()
    
    return component
```

### Step 2: Map Existing Files to Components

```python
def map_file_to_component(file_path: str, component_id: str, mapping_reason: str):
    """Map a file to an architecture component."""
    db = WorkspaceDB()
    
    mapping = CodeComponentMapping(
        file_path=file_path,
        component_id=component_id,
        mapping_type="direct",
        mapping_reason=mapping_reason,
        created_by="manual_mapping"
    )
    
    db.session.add(mapping)
    db.session.commit()
```

---

## Workflow: Tracking Changes

### Step 1: Git Commit Hook

```python
# workspace/tracking/git_tracker.py

import subprocess
from pathlib import Path

def track_git_changes(repo_path: Path, commit_hash: str) -> List[CodeChange]:
    """Track git commit changes and map to components."""
    db = WorkspaceDB()
    
    # Get changed files from git
    result = subprocess.run(
        ['git', 'show', '--name-status', '--pretty=format:%s', commit_hash],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    changes = []
    for line in result.stdout.split('\n'):
        if not line.strip() or line.startswith('commit'):
            continue
            
        # Parse: M    path/to/file.py
        change_type_code, file_path = line.split(None, 1)
        change_type_map = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed'
        }
        change_type = change_type_map.get(change_type_code[0], 'modified')
        
        # Find component mapping
        mapping = db.session.query(CodeComponentMapping).filter_by(
            file_path=file_path
        ).first()
        
        if mapping:
            component_id = mapping.component_id
            is_tracked = True
        else:
            component_id = None
            is_tracked = False
            # Mark as unregistered
            unregistered = UnregisteredFile(
                file_path=file_path,
                repo=repo_path.name
            )
            db.session.add(unregistered)
        
        change = CodeChange(
            commit_hash=commit_hash,
            repo=repo_path.name,
            change_type=change_type,
            file_path=file_path,
            component_id=component_id,
            mapping_id=mapping.id if mapping else None,
            is_tracked=is_tracked,
            validation_status="untracked" if not mapping else "pending",
            changed_at=datetime.utcnow(),
            changed_by=get_git_author(commit_hash)
        )
        
        changes.append(change)
        db.session.add(change)
    
    db.session.commit()
    return changes
```

### Step 2: Pre-Commit Hook

```bash
#!/bin/bash
# workspace/.git/hooks/pre-commit

# Track changes before commit
python workspace/tracking/git_tracker.py --pre-commit

# Check for unregistered files
UNTRACKED=$(python workspace/tracking/git_tracker.py --check-unregistered)

if [ -n "$UNTRACKED" ]; then
    echo "⚠️  Warning: Files not mapped to architecture components:"
    echo "$UNTRACKED"
    echo ""
    echo "Map files to components with:"
    echo "  python workspace/tracking/cli.py map-file <file> <component>"
    echo ""
    read -p "Continue with commit? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
```

---

## Pre-Deployment Validation

### Validation Command

```python
# workspace/tracking/pre_deployment_validator.py

class PreDeploymentValidator:
    """Validate all changes are tracked before deployment."""
    
    def validate_deployment(self, repo: str, branch: str, target_commit: str) -> DeploymentValidation:
        """Validate all files in deployment are mapped to components."""
        db = WorkspaceDB()
        
        # Get all changed files in deployment
        changed_files = self.get_changed_files(repo, branch, target_commit)
        
        validation = DeploymentValidation(
            deployment_id=f"{repo}-{target_commit}",
            total_files=len(changed_files),
            status="pending"
        )
        
        untracked = []
        violations = []
        
        for file_path in changed_files:
            # Check if file is mapped
            mapping = db.session.query(CodeComponentMapping).filter_by(
                file_path=file_path
            ).first()
            
            if not mapping:
                untracked.append(file_path)
                continue
            
            # Check if change is within component scope
            component = mapping.component
            if not self.is_within_scope(file_path, component):
                violations.append({
                    "file": file_path,
                    "component": component.component_name,
                    "violation": "Outside component scope"
                })
        
        validation.untracked_files = len(untracked)
        validation.violations = len(violations)
        validation.untracked_file_list = json.dumps(untracked)
        validation.violation_details = json.dumps(violations)
        
        if untracked or violations:
            validation.status = "failed"
            validation.deployment_blocked = True
        else:
            validation.status = "passed"
            validation.deployment_blocked = False
        
        # Mark all changes as validated
        for file_path in changed_files:
            change = db.session.query(CodeChange).filter_by(
                file_path=file_path,
                commit_hash=target_commit
            ).first()
            if change:
                change.is_validated = True
                change.validation_status = validation.status
        
        db.session.add(validation)
        db.session.commit()
        
        return validation
    
    def is_within_scope(self, file_path: str, component: ArchitectureComponent) -> bool:
        """Check if file change is within component approved scope."""
        # Validate against component boundaries
        # Check against approved_scope and boundaries JSON
        # ... implementation ...
        return True
```

### CLI Command

```bash
# workspace/tracking/cli.py

@click.command()
@click.argument('repo')
@click.argument('branch')
@click.argument('commit')
def validate_deployment(repo, branch, commit):
    """Validate deployment before release."""
    validator = PreDeploymentValidator()
    result = validator.validate_deployment(repo, branch, commit)
    
    if result.status == "failed":
        click.echo(f"❌ Deployment validation FAILED")
        click.echo(f"   Untracked files: {result.untracked_files}")
        click.echo(f"   Violations: {result.violations}")
        click.echo("")
        click.echo("Untracked files:")
        for file in json.loads(result.untracked_file_list):
            click.echo(f"  • {file}")
        click.echo("")
        click.echo("❌ Deployment BLOCKED. Map files to components first.")
        sys.exit(1)
    else:
        click.echo(f"✅ Deployment validation PASSED")
        click.echo(f"   All {result.total_files} files mapped to components")
```

---

## Usage Examples

### 1. Register Components from Architecture

```python
# After creating architecture docs, register components

register_component(
    component_name="LearningEngine",
    component_type="abstract_base_class",
    repo="meridian-core",
    expected_path="src/meridian_core/learning/learning_engine.py",
    approved_scope={
        "purpose": "Abstract learning interface",
        "allowed_imports": ["typing", "abc"],
        "forbidden_imports": ["pandas", "numpy"]
    }
)

register_component(
    component_name="TradingLearningEngine",
    component_type="concrete_implementation",
    repo="meridian-trading",
    expected_path="src/meridian_trading/learning/trading_learning_engine.py",
    approved_scope={
        "purpose": "Trading domain learning implementation",
        "inherits_from": "LearningEngine",
        "allowed_imports": ["meridian_core", "pandas"]
    }
)
```

### 2. Map Existing Files

```python
# Map existing files to components

map_file_to_component(
    file_path="src/meridian_core/learning/learning_engine.py",
    component_id="LearningEngine",
    mapping_reason="Primary implementation file for LearningEngine component"
)

map_file_to_component(
    file_path="src/meridian_core/learning/proposal_manager.py",
    component_id="ProposalManager",
    mapping_reason="Supporting file for proposal management"
)
```

### 3. Pre-Deployment Validation

```bash
# Before deploying, validate all changes

python workspace/tracking/cli.py validate-deployment \
    meridian-core \
    main \
    abc123def

# Output:
# ✅ Deployment validation PASSED
#    All 12 files mapped to components
#    No violations detected
```

### 4. Automatic Tracking (Git Hook)

```bash
# Git commit automatically tracks changes

git commit -m "Add new learning feature"

# Pre-commit hook runs:
# ⚠️  Warning: Files not mapped to architecture components:
#   src/meridian_core/new_feature.py
#   
# Map files to components with:
#   python workspace/tracking/cli.py map-file src/meridian_core/new_feature.py LearningEngine
```

### 5. Check Unregistered Files

```bash
# Find files not mapped to components

python workspace/tracking/cli.py check-unregistered meridian-core

# Output:
# Found 5 unregistered files:
#   • src/meridian_core/utils/helper.py
#   • tests/test_helper.py
#   • docs/guide.md
#   
# Map them with:
#   python workspace/tracking/cli.py map-file <file> <component>
```

---

## Integration with WMS

### Workflow: Create Task → Map Files → Validate → Deploy

```
1. CREATE TASK
   ├─ wms task create "Add feature X"
   ├─ Task assigned to component Y
   └─ Files created/modified: file1.py, file2.py

2. IMPLEMENT FEATURE
   ├─ Edit files
   ├─ Pre-commit hook tracks changes
   └─ Files automatically mapped to component Y

3. VALIDATE BEFORE DEPLOYMENT
   ├─ wms deployment validate
   ├─ Check all files mapped to components
   ├─ Check changes within component scope
   └─ Status: PASSED or BLOCKED

4. DEPLOY (if validated)
   ├─ Deployment allowed
   └─ Changes marked as deployed
```

---

## Benefits

### Prevents Scope Creep
- ✅ **All files must map to architecture** - No orphaned files
- ✅ **Changes tracked to components** - Clear traceability
- ✅ **Deployment blocked if untracked** - Prevents drift

### Enforces Architecture
- ✅ **Component boundaries enforced** - Changes within scope
- ✅ **Architecture decisions respected** - ADR compliance
- ✅ **Violations detected early** - Pre-deployment gates

### Provides Traceability
- ✅ **File → Component mapping** - Know what belongs where
- ✅ **Change → Component tracking** - See impact of changes
- ✅ **Deployment history** - Track what was deployed when

### Improves Governance
- ✅ **Pre-commit validation** - Catch issues early
- ✅ **Pre-deployment gates** - Final validation
- ✅ **Audit trail** - Full change history

---

## Implementation Plan

### Phase 1: Database Schema (Week 1)
1. Add new models to `workspace/db/models.py`
2. Create migration script
3. Test database operations

### Phase 2: Component Registration (Week 2)
1. Create component registry
2. Register existing components from architecture docs
3. Map existing files to components

### Phase 3: Change Tracking (Week 3)
1. Create git tracker
2. Implement pre-commit hook
3. Test change tracking

### Phase 4: Pre-Deployment Validation (Week 4)
1. Create pre-deployment validator
2. Create CLI commands
3. Integrate with deployment process

---

## Next Steps

1. ✅ **Design complete** (this document)
2. ⏳ **Extend database schema** - Add new models
3. ⏳ **Create component registry** - Register components
4. ⏳ **Map existing files** - Initial mapping
5. ⏳ **Implement git tracking** - Track changes
6. ⏳ **Create validation** - Pre-deployment gates
7. ⏳ **Deploy hooks** - Pre-commit and pre-deployment

---

**Status:** Design Complete - Ready for Implementation  
**Created:** 2025-11-20  
**Related:** Configuration Drift Tracking System, WMS Integration

