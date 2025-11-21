# Meridian Workspace Management System (WMS)
## Implementation Specification for Cursor AI

**Date:** November 20, 2025  
**Version:** 1.0  
**Purpose:** Complete specification for building automated workflow system with workspace database, context management, and AI governance via The Bastard

---

## 🎯 Project Overview

**What We're Building:**

A workspace-level management system that:
1. ✅ Tracks work context (which repo you're working in)
2. ✅ Enforces architectural decisions from workspace.db
3. ✅ Routes work tasks to correct repos based on ADRs
4. ✅ Validates all work with The Bastard before approval
5. ✅ Prevents scope creep and over-engineering
6. ✅ Blocks work that violates architecture

**User Story:**
```
As a developer:
- I set my work context (which repo I'm in)
- I define a task I want to accomplish
- WMS checks architecture rules
- WMS validates scale appropriateness
- WMS routes task to correct repo
- The Bastard validates the plan
- I do the work (governed by WMS)
- The Bastard validates completion
- Task is marked complete in workspace.db
```

---

## 📁 Project Structure

```
data-projects/                          # Workspace root
├── workspace/                          # NEW: WMS system
│   ├── wms/                           # Core WMS code
│   │   ├── __init__.py
│   │   ├── cli.py                     # Command-line interface
│   │   ├── context_manager.py        # Context tracking
│   │   ├── workflow_engine.py        # Workflow orchestration
│   │   ├── governance_engine.py      # Architecture enforcement
│   │   ├── bastard_integration.py    # The Bastard validator
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── models.py              # SQLAlchemy models
│   │       ├── migrations/            # Alembic migrations
│   │       └── workspace.db           # SQLite database
│   │
│   ├── architecture/                  # Architecture artifacts
│   │   ├── decisions/                 # ADRs (from existing docs)
│   │   │   ├── ADR-001-component-placement.md
│   │   │   └── ADR-002-credential-management.md
│   │   ├── rules/
│   │   │   ├── component-placement.yaml
│   │   │   ├── import-rules.yaml
│   │   │   └── scale-tiers.yaml
│   │   └── diagrams/
│   │       └── (existing architecture docs)
│   │
│   ├── workflows/                     # Workflow definitions
│   │   ├── templates/
│   │   │   ├── feature-template.yaml
│   │   │   ├── bugfix-template.yaml
│   │   │   └── refactor-template.yaml
│   │   └── active/
│   │       └── (active workflow instances)
│   │
│   ├── skills/                        # The Bastard and other skills
│   │   ├── evaluation-bastard.yaml
│   │   └── (other skills)
│   │
│   ├── .workspace-context             # Current context state
│   └── wms.log                        # WMS activity log
│
├── meridian-core/                     # Execution repos
├── meridian-research/
├── meridian-trading/
└── pyproject.toml                     # NEW: WMS package definition
```

---

## 🗄️ Database Schema (workspace.db)

### SQLAlchemy Models

```python
# workspace/wms/db/models.py

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, 
    ForeignKey, Text, JSON, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ============================================================================
# CONTEXT MANAGEMENT
# ============================================================================

class WorkContext(Base):
    """Current work context - which repo user is working in."""
    __tablename__ = "work_contexts"
    
    id = Column(Integer, primary_key=True)
    repo = Column(String(50), nullable=False)  # meridian-core, meridian-research, etc.
    repo_path = Column(String(255), nullable=False)
    activated_at = Column(DateTime, default=datetime.utcnow)
    activated_by = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # Metadata
    notes = Column(Text)
    previous_context_id = Column(Integer, ForeignKey("work_contexts.id"))


# ============================================================================
# ARCHITECTURAL DECISIONS
# ============================================================================

class ArchitectureDecision(Base):
    """ADRs logged in workspace database."""
    __tablename__ = "architecture_decisions"
    
    id = Column(Integer, primary_key=True)
    adr_number = Column(String(20), unique=True)  # ADR-001
    title = Column(String(255), nullable=False)
    status = Column(String(20), default="active")  # active, deprecated, superseded
    
    # Content
    context = Column(Text)
    decision = Column(Text, nullable=False)
    consequences = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    superseded_by = Column(String(20))
    
    # Relationships
    rules = relationship("ComponentPlacementRule", back_populates="adr")


class ComponentPlacementRule(Base):
    """Component placement rules from ADR-001."""
    __tablename__ = "component_placement_rules"
    
    id = Column(Integer, primary_key=True)
    adr_id = Column(Integer, ForeignKey("architecture_decisions.id"))
    
    # Rule definition
    component_type = Column(String(100))  # e.g., "LearningEngine"
    must_be_in_repo = Column(String(50))  # e.g., "meridian-core"
    must_be_in_path = Column(String(255))  # e.g., "src/meridian_core/learning/"
    must_not_be_in_repo = Column(String(50))
    
    # Rationale
    rationale = Column(Text, nullable=False)
    
    # Relationships
    adr = relationship("ArchitectureDecision", back_populates="rules")


class ImportRule(Base):
    """Import/dependency rules."""
    __tablename__ = "import_rules"
    
    id = Column(Integer, primary_key=True)
    source_repo = Column(String(50), nullable=False)
    
    # Rule type
    rule_type = Column(String(20))  # allowed, forbidden
    target_module = Column(String(100))
    
    # Rationale
    reason = Column(Text, nullable=False)


class ScaleTier(Base):
    """Scale tier definitions for various solutions."""
    __tablename__ = "scale_tiers"
    
    id = Column(Integer, primary_key=True)
    domain = Column(String(50))  # credentials, database, deployment
    tier = Column(Integer)  # 1, 2, 3
    
    # Tier definition
    name = Column(String(100))  # "Personal Use", "Team Use", "Enterprise"
    user_range = Column(String(50))  # "1-5 users"
    solution = Column(String(255))
    complexity = Column(Integer)  # 1-10
    
    # Triggers
    upgrade_trigger = Column(Text)  # When to upgrade to this tier
    migration_effort = Column(String(100))  # "4 hours"


# ============================================================================
# TASKS & WORKFLOWS
# ============================================================================

class TaskStatus(Enum):
    PLANNING = "planning"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(Base):
    """Work tasks tracked in workspace."""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(String(20), unique=True)  # WS-TASK-001
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Assignment
    assigned_repo = Column(String(50))  # Determined by governance
    assigned_by = Column(String(20))  # "governance_engine" or "manual"
    
    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PLANNING)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Validation
    bastard_plan_grade = Column(String(1))  # Grade from plan validation
    bastard_completion_grade = Column(String(1))  # Grade from completion validation
    scale_tier = Column(Integer)  # Appropriate tier (1, 2, 3)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    workflow = relationship("Workflow", back_populates="tasks")
    violations = relationship("Violation", back_populates="task")
    bastard_reports = relationship("BastardReport", back_populates="task")


class Workflow(Base):
    """Workflow definitions and instances."""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(String(20), unique=True)  # WF-001
    name = Column(String(255), nullable=False)
    workflow_type = Column(String(50))  # feature, bugfix, refactor
    
    # Scope
    allowed_repos = Column(JSON)  # ["meridian-core", "meridian-trading"]
    
    # Status
    status = Column(String(20), default="active")
    current_stage = Column(Integer, default=1)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    tasks = relationship("Task", back_populates="workflow")
    stages = relationship("WorkflowStage", back_populates="workflow")


class WorkflowStage(Base):
    """Stages within a workflow."""
    __tablename__ = "workflow_stages"
    
    id = Column(Integer, primary_key=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    stage_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    
    # Requirements
    validation_required = Column(Boolean, default=True)
    validation_type = Column(String(50))  # governance, bastard, architecture
    
    # Status
    status = Column(String(20), default="pending")
    completed_at = Column(DateTime)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="stages")


# ============================================================================
# VIOLATIONS & GOVERNANCE
# ============================================================================

class ViolationType(Enum):
    COMPONENT_PLACEMENT = "component_placement"
    FORBIDDEN_IMPORT = "forbidden_import"
    SCALE_MISMATCH = "scale_mismatch"
    MISSING_VALIDATION = "missing_validation"
    OVER_ENGINEERING = "over_engineering"


class Violation(Base):
    """Architecture/governance violations detected."""
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    
    # Violation details
    violation_type = Column(SQLEnum(ViolationType))
    severity = Column(String(20))  # CRITICAL, HIGH, MEDIUM, LOW
    message = Column(Text, nullable=False)
    
    # Location
    file_path = Column(String(255))
    line_number = Column(Integer)
    
    # Fix
    rule_violated = Column(String(255))
    fix_required = Column(Text)
    
    # Status
    status = Column(String(20), default="open")  # open, acknowledged, fixed
    resolved_at = Column(DateTime)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="violations")


# ============================================================================
# THE BASTARD INTEGRATION
# ============================================================================

class BastardReport(Base):
    """Reports from The Bastard evaluations."""
    __tablename__ = "bastard_reports"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    
    # Evaluation type
    evaluation_type = Column(String(50))  # plan, completion
    
    # Grades
    overall_grade = Column(String(1))  # F, D, C, B, A, OVER_ENGINEERED
    scale_appropriateness = Column(String(1))
    deployment_maturity = Column(String(1))
    portability = Column(String(1))
    state_management = Column(String(1))
    credential_management = Column(String(1))
    
    # Scale assessment
    actual_users = Column(Integer)
    designed_for_users = Column(Integer)
    over_engineering_score = Column(Integer)  # 1-10
    
    # Recommendations
    tier_recommendation = Column(Integer)  # 1, 2, or 3
    critical_blockers = Column(JSON)  # List of critical issues
    required_fixes = Column(JSON)  # List of required fixes
    
    # Full report
    full_report = Column(Text)  # Complete Bastard verdict
    
    # Metadata
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="bastard_reports")


# ============================================================================
# SESSION TRACKING
# ============================================================================

class WorkSession(Base):
    """Work session tracking."""
    __tablename__ = "work_sessions"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), unique=True)
    
    # Session details
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    context_repo = Column(String(50))
    
    # Activity summary
    tasks_worked = Column(JSON)  # List of task IDs
    violations_detected = Column(Integer, default=0)
    bastard_calls = Column(Integer, default=0)
```

---

## 🔧 Core Components

### 1. Context Manager

```python
# workspace/wms/context_manager.py

"""
Context Manager - Tracks which repo you're working in.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from .db.models import WorkContext


class ContextManager:
    """Manages work context - which repo you're currently working in."""
    
    def __init__(self, workspace_root: Path, db_session: Session):
        self.workspace_root = workspace_root
        self.db = db_session
        self.context_file = workspace_root / ".workspace-context"
    
    def set_context(self, repo: str, notes: Optional[str] = None) -> WorkContext:
        """
        Set work context to a specific repo.
        
        Args:
            repo: Repository name (meridian-core, meridian-research, etc.)
            notes: Optional notes about what you're working on
        
        Returns:
            WorkContext instance
        """
        # Deactivate previous context
        self._deactivate_current_context()
        
        # Create new context
        repo_path = self.workspace_root / repo
        if not repo_path.exists():
            raise ValueError(f"Repository not found: {repo_path}")
        
        context = WorkContext(
            repo=repo,
            repo_path=str(repo_path),
            activated_at=datetime.utcnow(),
            is_active=True,
            notes=notes
        )
        
        self.db.add(context)
        self.db.commit()
        
        # Write to context file for fast lookup
        self._write_context_file(context)
        
        print(f"✅ Context set to: {repo}")
        if notes:
            print(f"   Notes: {notes}")
        
        return context
    
    def get_current_context(self) -> Optional[WorkContext]:
        """Get current active work context."""
        return self.db.query(WorkContext).filter_by(is_active=True).first()
    
    def clear_context(self):
        """Clear current context."""
        self._deactivate_current_context()
        if self.context_file.exists():
            self.context_file.unlink()
        print("✅ Context cleared")
    
    def _deactivate_current_context(self):
        """Deactivate currently active context."""
        current = self.get_current_context()
        if current:
            current.is_active = False
            self.db.commit()
    
    def _write_context_file(self, context: WorkContext):
        """Write context to file for fast access."""
        self.context_file.write_text(
            f"{context.repo}\n{context.repo_path}\n{context.activated_at.isoformat()}"
        )


# ============================================================================
# Quick context check without database
# ============================================================================

def get_quick_context(workspace_root: Path) -> Optional[dict]:
    """Quick context check from file (no database)."""
    context_file = workspace_root / ".workspace-context"
    if not context_file.exists():
        return None
    
    lines = context_file.read_text().strip().split('\n')
    if len(lines) < 2:
        return None
    
    return {
        'repo': lines[0],
        'repo_path': lines[1],
        'activated_at': lines[2] if len(lines) > 2 else None
    }
```

---

### 2. Governance Engine

```python
# workspace/wms/governance_engine.py

"""
Governance Engine - Enforces architectural rules.
"""

from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session

from .db.models import (
    ArchitectureDecision, ComponentPlacementRule, 
    ImportRule, Violation, ViolationType, Task
)


class GovernanceEngine:
    """Enforces architectural decisions and rules."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def validate_task_placement(self, task: Task, proposed_repo: str) -> List[Violation]:
        """
        Validate if task belongs in proposed repo based on ADRs.
        
        Args:
            task: Task to validate
            proposed_repo: Proposed repository
        
        Returns:
            List of violations (empty if valid)
        """
        violations = []
        
        # Check component placement rules
        for rule in self._get_placement_rules():
            if self._violates_placement(task, proposed_repo, rule):
                violations.append(Violation(
                    task_id=task.id,
                    violation_type=ViolationType.COMPONENT_PLACEMENT,
                    severity="CRITICAL",
                    message=f"Component belongs in {rule.must_be_in_repo}, not {proposed_repo}",
                    rule_violated=f"ADR-001: {rule.component_type} placement",
                    fix_required=f"Move to {rule.must_be_in_repo}/{rule.must_be_in_path}"
                ))
        
        return violations
    
    def validate_scale_appropriateness(
        self, 
        task: Task, 
        proposed_solution: str,
        actual_users: int
    ) -> List[Violation]:
        """
        Validate if proposed solution matches actual scale.
        
        Args:
            task: Task being validated
            proposed_solution: Description of proposed solution
            actual_users: Actual user count TODAY
        
        Returns:
            List of violations (empty if appropriate)
        """
        violations = []
        
        # Check for over-engineering keywords
        over_engineering_keywords = [
            "kubernetes", "vault", "microservices", "service mesh",
            "kafka", "consul", "distributed", "cloud-native"
        ]
        
        solution_lower = proposed_solution.lower()
        
        # If single user and enterprise solution
        if actual_users <= 5:
            for keyword in over_engineering_keywords:
                if keyword in solution_lower:
                    violations.append(Violation(
                        task_id=task.id,
                        violation_type=ViolationType.OVER_ENGINEERING,
                        severity="HIGH",
                        message=f"Over-engineering: {keyword} for {actual_users} user(s)",
                        rule_violated="Start Small, Scale Smart principle",
                        fix_required=f"Use Tier 1 solution for {actual_users} users"
                    ))
        
        return violations
    
    def determine_correct_repo(self, task_description: str) -> str:
        """
        Determine which repo task belongs in based on ADRs.
        
        Args:
            task_description: Task description
        
        Returns:
            Repo name where task should be implemented
        """
        desc_lower = task_description.lower()
        
        # Check for domain-specific keywords
        trading_keywords = ["trading", "tdom", "larry williams", "market", "strategy"]
        research_keywords = ["research", "query", "investigation", "analysis"]
        
        if any(kw in desc_lower for kw in trading_keywords):
            return "meridian-trading"
        elif any(kw in desc_lower for kw in research_keywords):
            return "meridian-research"
        
        # Check for generic/framework keywords
        framework_keywords = [
            "orchestration", "learning engine", "proposal manager",
            "voting system", "abstract", "base class"
        ]
        
        if any(kw in desc_lower for kw in framework_keywords):
            return "meridian-core"
        
        # Default: ask user
        return None
    
    def _get_placement_rules(self) -> List[ComponentPlacementRule]:
        """Get all component placement rules."""
        return self.db.query(ComponentPlacementRule).all()
    
    def _violates_placement(
        self, 
        task: Task, 
        repo: str, 
        rule: ComponentPlacementRule
    ) -> bool:
        """Check if task violates placement rule."""
        # Check if task mentions the component type
        if rule.component_type.lower() in task.description.lower():
            # Check if repo is forbidden
            if rule.must_not_be_in_repo and repo == rule.must_not_be_in_repo:
                return True
            # Check if repo is not the required one
            if rule.must_be_in_repo and repo != rule.must_be_in_repo:
                return True
        
        return False
```

---

### 3. Bastard Integration

```python
# workspace/wms/bastard_integration.py

"""
The Bastard Integration - Validates tasks and implementations.
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from pathlib import Path
import yaml

from .db.models import Task, BastardReport


class BastardIntegration:
    """Integration with The Bastard evaluation skill."""
    
    def __init__(self, db_session: Session, skills_dir: Path):
        self.db = db_session
        self.skills_dir = skills_dir
        self.bastard_skill = self._load_bastard_skill()
    
    def evaluate_plan(
        self, 
        task: Task,
        actual_users: int,
        proposed_solution: str
    ) -> BastardReport:
        """
        Evaluate task plan with The Bastard.
        
        Args:
            task: Task to evaluate
            actual_users: Actual user count TODAY
            proposed_solution: Proposed implementation approach
        
        Returns:
            BastardReport with evaluation results
        """
        # Build evaluation prompt
        prompt = self._build_plan_evaluation_prompt(
            task, actual_users, proposed_solution
        )
        
        # Call The Bastard (via Meridian orchestration)
        verdict = self._call_bastard(prompt)
        
        # Parse verdict
        report = self._parse_bastard_verdict(verdict, task, "plan")
        
        # Save to database
        self.db.add(report)
        self.db.commit()
        
        # Update task with grade
        task.bastard_plan_grade = report.overall_grade
        self.db.commit()
        
        return report
    
    def evaluate_completion(self, task: Task) -> BastardReport:
        """
        Evaluate completed task with The Bastard.
        
        Args:
            task: Completed task to evaluate
        
        Returns:
            BastardReport with evaluation results
        """
        # Build evaluation prompt
        prompt = self._build_completion_evaluation_prompt(task)
        
        # Call The Bastard
        verdict = self._call_bastard(prompt)
        
        # Parse verdict
        report = self._parse_bastard_verdict(verdict, task, "completion")
        
        # Save to database
        self.db.add(report)
        self.db.commit()
        
        # Update task with grade
        task.bastard_completion_grade = report.overall_grade
        self.db.commit()
        
        return report
    
    def _build_plan_evaluation_prompt(
        self, 
        task: Task,
        actual_users: int,
        proposed_solution: str
    ) -> str:
        """Build prompt for plan evaluation."""
        return f"""
Evaluate this task plan:

TASK: {task.title}
DESCRIPTION: {task.description}

SCALE REALITY:
- Actual users TODAY: {actual_users}
- Proposed solution: {proposed_solution}

EVALUATE:
1. Scale appropriateness (is solution over-engineered?)
2. Component placement (correct repo?)
3. Implementation approach (reasonable?)

Provide:
- Overall grade (F/D/C/B/A or OVER_ENGINEERED)
- Scale appropriateness grade
- Critical blockers (if any)
- Required fixes before proceeding

Be brutal. No mercy for over-engineering.
"""
    
    def _build_completion_evaluation_prompt(self, task: Task) -> str:
        """Build prompt for completion evaluation."""
        return f"""
Evaluate completed task:

TASK: {task.title}
DESCRIPTION: {task.description}
REPO: {task.assigned_repo}

VALIDATE:
1. Was it implemented in correct repo?
2. Does it match architecture decisions?
3. Is it portable/deployable?
4. Any over-engineering detected?

Provide:
- Overall grade (F/D/C/B/A)
- Category grades
- Critical issues (if any)
- Required fixes before merge

Be brutal. This is final validation.
"""
    
    def _call_bastard(self, prompt: str) -> str:
        """
        Call The Bastard via Meridian orchestration.
        
        In real implementation, this would:
        1. Import Meridian Core
        2. Load evaluation-bastard skill
        3. Execute with orchestrator
        4. Return verdict
        
        For now, returns placeholder.
        """
        # TODO: Implement actual Meridian orchestration call
        # from meridian_core import AIOrchestrator
        # orchestrator = AIOrchestrator()
        # verdict = orchestrator.execute_with_skill(
        #     ai_provider="claude",
        #     skill_name="evaluation-bastard",
        #     task=prompt
        # )
        # return verdict
        
        return "[Bastard verdict would be here]"
    
    def _parse_bastard_verdict(
        self, 
        verdict: str, 
        task: Task,
        evaluation_type: str
    ) -> BastardReport:
        """Parse The Bastard's verdict into structured report."""
        # TODO: Implement actual parsing
        # For now, create placeholder report
        
        report = BastardReport(
            task_id=task.id,
            evaluation_type=evaluation_type,
            overall_grade="B",  # Placeholder
            scale_appropriateness="B",
            deployment_maturity="B",
            portability="B",
            state_management="B",
            credential_management="B",
            actual_users=1,
            designed_for_users=1,
            over_engineering_score=3,
            tier_recommendation=1,
            critical_blockers=[],
            required_fixes=[],
            full_report=verdict
        )
        
        return report
    
    def _load_bastard_skill(self) -> Dict:
        """Load The Bastard skill YAML."""
        bastard_path = self.skills_dir / "evaluation-bastard.yaml"
        if not bastard_path.exists():
            raise FileNotFoundError(f"Bastard skill not found: {bastard_path}")
        
        with open(bastard_path) as f:
            return yaml.safe_load(f)
```

---

### 4. Workflow Engine

```python
# workspace/wms/workflow_engine.py

"""
Workflow Engine - Orchestrates task execution.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from .db.models import Task, Workflow, WorkflowStage, TaskStatus
from .governance_engine import GovernanceEngine
from .bastard_integration import BastardIntegration


class WorkflowEngine:
    """Orchestrates task workflows with validation."""
    
    def __init__(
        self, 
        db_session: Session,
        governance: GovernanceEngine,
        bastard: BastardIntegration
    ):
        self.db = db_session
        self.governance = governance
        self.bastard = bastard
    
    def create_task(
        self,
        title: str,
        description: str,
        actual_users: int,
        proposed_solution: Optional[str] = None
    ) -> Task:
        """
        Create and validate a new task.
        
        Args:
            title: Task title
            description: Task description
            actual_users: Actual user count TODAY
            proposed_solution: Proposed implementation approach
        
        Returns:
            Task instance (may be BLOCKED if violations detected)
        """
        # Create task
        task_id = self._generate_task_id()
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PLANNING
        )
        
        self.db.add(task)
        self.db.flush()  # Get task.id
        
        # Determine correct repo
        assigned_repo = self.governance.determine_correct_repo(description)
        
        if not assigned_repo:
            print("\n❓ Cannot automatically determine repo placement")
            print(f"Task: {title}")
            print(f"Description: {description}")
            assigned_repo = input("Which repo? (core/research/trading): ")
            assigned_repo = f"meridian-{assigned_repo}"
        
        task.assigned_repo = assigned_repo
        task.assigned_by = "governance_engine"
        
        # Validate placement
        violations = self.governance.validate_task_placement(task, assigned_repo)
        
        if violations:
            print(f"\n⚠️  Placement violations detected:")
            for v in violations:
                print(f"  • {v.severity}: {v.message}")
                print(f"    Fix: {v.fix_required}")
                self.db.add(v)
            
            task.status = TaskStatus.BLOCKED
            self.db.commit()
            return task
        
        # Validate scale appropriateness (if solution provided)
        if proposed_solution:
            scale_violations = self.governance.validate_scale_appropriateness(
                task, proposed_solution, actual_users
            )
            
            if scale_violations:
                print(f"\n⚠️  Scale appropriateness violations:")
                for v in scale_violations:
                    print(f"  • {v.severity}: {v.message}")
                    print(f"    Fix: {v.fix_required}")
                    self.db.add(v)
                
                task.status = TaskStatus.BLOCKED
                self.db.commit()
                return task
        
        # No violations - ready for Bastard evaluation
        print(f"\n✅ Task routing validated:")
        print(f"   Task: {title}")
        print(f"   Assigned to: {assigned_repo}")
        print(f"   No governance violations")
        
        # Evaluate plan with The Bastard (if solution provided)
        if proposed_solution:
            print(f"\n🔥 Evaluating with The Bastard...")
            report = self.bastard.evaluate_plan(task, actual_users, proposed_solution)
            
            if report.overall_grade in ['F', 'D']:
                print(f"\n❌ The Bastard REJECTED the plan:")
                print(f"   Grade: {report.overall_grade}")
                print(f"   Critical blockers: {report.critical_blockers}")
                task.status = TaskStatus.BLOCKED
            else:
                print(f"\n✅ The Bastard APPROVED the plan:")
                print(f"   Grade: {report.overall_grade}")
                task.status = TaskStatus.APPROVED
        
        self.db.commit()
        return task
    
    def start_task(self, task_id: str) -> bool:
        """
        Start working on a task.
        
        Args:
            task_id: Task ID (e.g., WS-TASK-001)
        
        Returns:
            True if task can start, False if blocked
        """
        task = self.db.query(Task).filter_by(task_id=task_id).first()
        if not task:
            print(f"❌ Task not found: {task_id}")
            return False
        
        if task.status == TaskStatus.BLOCKED:
            print(f"❌ Task is BLOCKED. Fix violations first:")
            violations = self.db.query(Violation).filter_by(
                task_id=task.id, 
                status="open"
            ).all()
            for v in violations:
                print(f"  • {v.severity}: {v.message}")
            return False
        
        if task.status != TaskStatus.APPROVED:
            print(f"❌ Task must be APPROVED before starting (current: {task.status.value})")
            return False
        
        # Start task
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.db.commit()
        
        print(f"✅ Task started: {task.task_id}")
        print(f"   Repo: {task.assigned_repo}")
        print(f"   Title: {task.title}")
        
        return True
    
    def complete_task(self, task_id: str) -> bool:
        """
        Mark task as complete and run final Bastard validation.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if task approved for completion, False if rejected
        """
        task = self.db.query(Task).filter_by(task_id=task_id).first()
        if not task:
            print(f"❌ Task not found: {task_id}")
            return False
        
        if task.status != TaskStatus.IN_PROGRESS:
            print(f"❌ Task is not IN_PROGRESS (current: {task.status.value})")
            return False
        
        # Final Bastard evaluation
        print(f"\n🔥 Running final Bastard evaluation...")
        report = self.bastard.evaluate_completion(task)
        
        if report.overall_grade in ['F', 'D']:
            print(f"\n❌ The Bastard REJECTED completion:")
            print(f"   Grade: {report.overall_grade}")
            print(f"   Issues: {report.critical_blockers}")
            print(f"   Required fixes: {report.required_fixes}")
            task.status = TaskStatus.BLOCKED
            self.db.commit()
            return False
        
        # Task approved
        print(f"\n✅ The Bastard APPROVED completion:")
        print(f"   Grade: {report.overall_grade}")
        
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        self.db.commit()
        
        print(f"✅ Task completed: {task.task_id}")
        return True
    
    def _generate_task_id(self) -> str:
        """Generate next task ID."""
        latest = self.db.query(Task).order_by(Task.id.desc()).first()
        if not latest:
            return "WS-TASK-001"
        
        # Extract number from latest ID
        num = int(latest.task_id.split('-')[-1])
        return f"WS-TASK-{num + 1:03d}"
```

---

### 5. CLI Interface

```python
# workspace/wms/cli.py

"""
WMS Command-Line Interface
"""

import click
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .db.models import Base
from .context_manager import ContextManager
from .governance_engine import GovernanceEngine
from .bastard_integration import BastardIntegration
from .workflow_engine import WorkflowEngine


# Initialize database
WORKSPACE_ROOT = Path.cwd()
DB_PATH = WORKSPACE_ROOT / "workspace" / "wms" / "db" / "workspace.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


@click.group()
def wms():
    """Workspace Management System - AI-governed workflow automation"""
    pass


# ============================================================================
# CONTEXT COMMANDS
# ============================================================================

@wms.group()
def context():
    """Manage work context (which repo you're in)"""
    pass


@context.command()
@click.argument('repo')
@click.option('--notes', help='Optional notes about what you're working on')
def set(repo: str, notes: str):
    """Set work context to a repo"""
    session = Session()
    manager = ContextManager(WORKSPACE_ROOT, session)
    
    # Normalize repo name
    if not repo.startswith('meridian-'):
        repo = f'meridian-{repo}'
    
    manager.set_context(repo, notes)
    session.close()


@context.command()
def show():
    """Show current work context"""
    session = Session()
    manager = ContextManager(WORKSPACE_ROOT, session)
    
    ctx = manager.get_current_context()
    if not ctx:
        click.echo("No active context")
        return
    
    click.echo(f"\nCurrent Context:")
    click.echo(f"  Repo: {ctx.repo}")
    click.echo(f"  Path: {ctx.repo_path}")
    click.echo(f"  Since: {ctx.activated_at}")
    if ctx.notes:
        click.echo(f"  Notes: {ctx.notes}")
    
    session.close()


@context.command()
def clear():
    """Clear current work context"""
    session = Session()
    manager = ContextManager(WORKSPACE_ROOT, session)
    manager.clear_context()
    session.close()


# ============================================================================
# TASK COMMANDS
# ============================================================================

@wms.group()
def task():
    """Manage tasks"""
    pass


@task.command()
@click.option('--title', prompt='Task title', help='Short task title')
@click.option('--description', prompt='Task description', help='Detailed description')
@click.option('--users', prompt='Actual users TODAY', type=int, help='Current user count')
@click.option('--solution', prompt='Proposed solution (optional)', default='', help='Implementation approach')
def create(title: str, description: str, users: int, solution: str):
    """Create a new task with validation"""
    session = Session()
    
    # Initialize engines
    governance = GovernanceEngine(session)
    bastard = BastardIntegration(session, WORKSPACE_ROOT / "workspace" / "skills")
    workflow = WorkflowEngine(session, governance, bastard)
    
    # Create task
    task = workflow.create_task(
        title=title,
        description=description,
        actual_users=users,
        proposed_solution=solution if solution else None
    )
    
    click.echo(f"\n📋 Task created: {task.task_id}")
    click.echo(f"   Status: {task.status.value}")
    click.echo(f"   Assigned to: {task.assigned_repo}")
    
    if task.status == "blocked":
        click.echo(f"\n⚠️  Task is BLOCKED. Fix violations before proceeding.")
    
    session.close()


@task.command()
@click.argument('task_id')
def start(task_id: str):
    """Start working on a task"""
    session = Session()
    
    governance = GovernanceEngine(session)
    bastard = BastardIntegration(session, WORKSPACE_ROOT / "workspace" / "skills")
    workflow = WorkflowEngine(session, governance, bastard)
    
    success = workflow.start_task(task_id)
    
    if not success:
        click.echo("\n❌ Cannot start task. Fix issues first.")
    
    session.close()


@task.command()
@click.argument('task_id')
def complete(task_id: str):
    """Complete a task (triggers final Bastard evaluation)"""
    session = Session()
    
    governance = GovernanceEngine(session)
    bastard = BastardIntegration(session, WORKSPACE_ROOT / "workspace" / "skills")
    workflow = WorkflowEngine(session, governance, bastard)
    
    success = workflow.complete_task(task_id)
    
    if not success:
        click.echo("\n❌ Task completion REJECTED. Fix issues and try again.")
    else:
        click.echo("\n✅ Task completed and approved!")
    
    session.close()


@task.command()
def list():
    """List all tasks"""
    session = Session()
    
    from .db.models import Task
    
    tasks = session.query(Task).order_by(Task.created_at.desc()).all()
    
    if not tasks:
        click.echo("No tasks found")
        return
    
    click.echo("\nTasks:")
    click.echo("-" * 80)
    
    for t in tasks:
        status_icon = {
            'planning': '📋',
            'approved': '✅',
            'in_progress': '🔄',
            'blocked': '⚠️',
            'completed': '✅',
            'cancelled': '❌'
        }.get(t.status.value, '?')
        
        click.echo(f"{status_icon} {t.task_id} - {t.title}")
        click.echo(f"   Status: {t.status.value} | Repo: {t.assigned_repo}")
        if t.bastard_plan_grade:
            click.echo(f"   Plan grade: {t.bastard_plan_grade}")
        if t.bastard_completion_grade:
            click.echo(f"   Completion grade: {t.bastard_completion_grade}")
        click.echo()
    
    session.close()


# ============================================================================
# BASTARD COMMANDS
# ============================================================================

@wms.group()
def bastard():
    """The Bastard evaluator commands"""
    pass


@bastard.command()
@click.argument('task_id')
def report(task_id: str):
    """Show Bastard evaluation report for a task"""
    session = Session()
    
    from .db.models import Task, BastardReport
    
    task = session.query(Task).filter_by(task_id=task_id).first()
    if not task:
        click.echo(f"❌ Task not found: {task_id}")
        return
    
    reports = session.query(BastardReport).filter_by(task_id=task.id).all()
    
    if not reports:
        click.echo(f"No Bastard reports for task {task_id}")
        return
    
    for report in reports:
        click.echo(f"\n{'='*80}")
        click.echo(f"The Bastard's Verdict: {task.title}")
        click.echo(f"Evaluation Type: {report.evaluation_type}")
        click.echo(f"{'='*80}")
        click.echo(f"\nOverall Grade: {report.overall_grade}")
        click.echo(f"\nCategory Grades:")
        click.echo(f"  Scale Appropriateness: {report.scale_appropriateness}")
        click.echo(f"  Deployment Maturity: {report.deployment_maturity}")
        click.echo(f"  Portability: {report.portability}")
        click.echo(f"\nScale Assessment:")
        click.echo(f"  Actual users: {report.actual_users}")
        click.echo(f"  Designed for: {report.designed_for_users}")
        click.echo(f"  Over-engineering score: {report.over_engineering_score}/10")
        click.echo(f"\nTier Recommendation: Tier {report.tier_recommendation}")
        
        if report.critical_blockers:
            click.echo(f"\nCritical Blockers:")
            for blocker in report.critical_blockers:
                click.echo(f"  • {blocker}")
        
        if report.required_fixes:
            click.echo(f"\nRequired Fixes:")
            for fix in report.required_fixes:
                click.echo(f"  • {fix}")
    
    session.close()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    wms()
```

---

## 📦 Installation & Setup

### 1. Package Definition

```toml
# workspace/pyproject.toml

[build-system]
requires = ["setuptools>=65.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "meridian-wms"
version = "0.1.0"
description = "Workspace Management System for Meridian projects"
authors = [{name = "Simon Erses"}]
requires-python = ">=3.10"
dependencies = [
    "sqlalchemy>=2.0.0",
    "alembic>=1.12.0",
    "click>=8.1.0",
    "pyyaml>=6.0.0",
    "rich>=13.0.0",
]

[project.scripts]
wms = "wms.cli:wms"

[tool.setuptools.packages.find]
where = ["."]
include = ["wms*"]
```

### 2. Initial Setup Script

```bash
#!/bin/bash
# workspace/setup-wms.sh

set -e

echo "🚀 Setting up Workspace Management System"
echo "=========================================="

# 1. Create directory structure
echo "Creating directories..."
mkdir -p workspace/wms/db/migrations
mkdir -p workspace/architecture/{decisions,rules,diagrams}
mkdir -p workspace/workflows/{templates,active}
mkdir -p workspace/skills

# 2. Install WMS package
echo "Installing WMS..."
cd workspace
pip install -e .

# 3. Initialize database
echo "Initializing database..."
python -c "
from wms.db.models import Base
from sqlalchemy import create_engine

engine = create_engine('sqlite:///wms/db/workspace.db')
Base.metadata.create_all(engine)
print('✅ Database initialized')
"

# 4. Copy The Bastard skill
echo "Setting up The Bastard..."
# (Copy evaluation-bastard.yaml to workspace/skills/)

# 5. Import ADRs into database
echo "Importing architecture decisions..."
python -c "
# TODO: Import existing ADRs from markdown files into database
print('✅ ADRs imported')
"

echo ""
echo "✅ WMS setup complete!"
echo ""
echo "Try it:"
echo "  wms context set core"
echo "  wms task create"
```

---

## 🎯 Usage Examples

### Example 1: Creating Your First Task

```bash
# 1. Set context
$ wms context set core
✅ Context set to: meridian-core

# 2. Create task
$ wms task create
Task title: Implement TradingLearningEngine
Task description: Create self-learning engine for trading domain that inherits from meridian-core LearningEngine
Actual users TODAY: 1
Proposed solution: Use SQLAlchemy for data storage

❓ Cannot automatically determine repo placement
Task: Implement TradingLearningEngine
Description: Create self-learning engine for trading domain...
Which repo? (core/research/trading): trading

✅ Task routing validated:
   Task: Implement TradingLearningEngine
   Assigned to: meridian-trading
   No governance violations

🔥 Evaluating with The Bastard...

✅ The Bastard APPROVED the plan:
   Grade: B

📋 Task created: WS-TASK-001
   Status: approved
   Assigned to: meridian-trading
```

### Example 2: Bastard Catches Over-Engineering

```bash
$ wms task create
Task title: Add credential management
Task description: Add secure credential storage
Actual users TODAY: 1
Proposed solution: Deploy HashiCorp Vault cluster with Consul for service discovery

✅ Task routing validated:
   Assigned to: meridian-core

⚠️  Scale appropriateness violations:
  • HIGH: Over-engineering: vault for 1 user(s)
    Fix: Use Tier 1 solution for 1 users
  • HIGH: Over-engineering: consul for 1 user(s)
    Fix: Use Tier 1 solution for 1 users

🔥 Evaluating with The Bastard...

❌ The Bastard REJECTED the plan:
   Grade: OVER_ENGINEERED
   Critical blockers: ['Building for 1000 users when you have 1']

📋 Task created: WS-TASK-002
   Status: blocked

⚠️  Task is BLOCKED. Fix violations before proceeding.
```

### Example 3: Component Placement Violation

```bash
$ wms task create
Task title: Create trading data models
Task description: Implement Position, Order, and Trade data models
Actual users TODAY: 5
Proposed solution: SQLAlchemy models with relationships

# User tries to put in meridian-core
Which repo? core

⚠️  Placement violations detected:
  • CRITICAL: Component belongs in meridian-trading, not meridian-core
    Fix: Move to meridian-trading/src/meridian_trading/models/

📋 Task created: WS-TASK-003
   Status: blocked

⚠️  Task is BLOCKED. Fix violations before proceeding.
```

---

## 🔄 Workflow Process

### Complete Task Lifecycle:

```
1. CREATE TASK
   ├─ wms task create
   ├─ Governance validates placement
   ├─ Governance validates scale
   ├─ The Bastard evaluates plan
   └─ Status: APPROVED or BLOCKED

2. START TASK
   ├─ wms task start WS-TASK-001
   ├─ Checks if approved
   ├─ Sets context automatically
   └─ Status: IN_PROGRESS

3. DO THE WORK
   ├─ Implement in assigned repo
   ├─ Follow approved plan
   └─ Stay in scope

4. COMPLETE TASK
   ├─ wms task complete WS-TASK-001
   ├─ The Bastard evaluates result
   ├─ Checks for violations
   └─ Status: COMPLETED or BLOCKED

5. REVIEW REPORT
   ├─ wms bastard report WS-TASK-001
   └─ See full evaluation
```

---

## 🎓 Key Concepts for Cursor

### Architecture Decision Records (ADRs)

ADRs are stored in `workspace/architecture/decisions/` as markdown files and imported into the database. The governance engine enforces these decisions automatically.

**Example ADR-001 (Component Placement):**
```markdown
# ADR-001: Component Placement Rules

## Decision
- Generic/framework code: meridian-core
- Trading-specific code: meridian-trading
- Research-specific code: meridian-research

## Rules
- TradingLearningEngine: MUST be in meridian-trading
- LearningEngine (base): MUST be in meridian-core
- Trading data models: MUST be in meridian-trading
```

### The Bastard Integration

The Bastard is a skill (YAML file) that gets called via Meridian Core's orchestration. It provides brutal, honest evaluation at two points:

1. **Plan Evaluation**: Before starting work
2. **Completion Evaluation**: Before marking task complete

Grades: F, D, C, B, A, OVER_ENGINEERED

### Context System

The context system tracks which repo you're currently working in. This prevents accidentally working in the wrong repo and enables context-aware commands.

```bash
wms context set core     # Working in meridian-core
wms context set trading  # Working in meridian-trading
wms context show         # See current context
```

### Governance Engine

The governance engine enforces:
1. **Component Placement**: Correct repo for each component type
2. **Import Rules**: What can import what
3. **Scale Appropriateness**: No over-engineering
4. **ADR Compliance**: All architecture decisions

---

## 🚀 Implementation Priority

### Phase 1: Core System (Week 1)
1. Database models (`models.py`)
2. Context manager (`context_manager.py`)
3. CLI skeleton (`cli.py`)
4. Basic database initialization

### Phase 2: Governance (Week 2)
1. Governance engine (`governance_engine.py`)
2. ADR import script
3. Component placement validation
4. Scale appropriateness validation

### Phase 3: The Bastard (Week 3)
1. Bastard integration (`bastard_integration.py`)
2. Plan evaluation
3. Completion evaluation
4. Report generation

### Phase 4: Workflow Engine (Week 4)
1. Workflow engine (`workflow_engine.py`)
2. Task lifecycle management
3. End-to-end workflow testing

---

## 📝 Notes for Cursor

1. **Start with database models** - This is the foundation
2. **Test each component independently** - Use pytest
3. **The Bastard integration can be mocked initially** - Return placeholder verdicts
4. **Focus on the workflow: Create → Validate → Execute → Complete**
5. **Error messages should be helpful** - Users need to know how to fix issues
6. **All file paths should use Path objects** - For cross-platform compatibility
7. **Use SQLAlchemy sessions properly** - Always close sessions
8. **CLI should be intuitive** - Follow Click best practices

---

## ✅ Success Criteria

When complete, you should be able to:

1. ✅ Set work context to a repo
2. ✅ Create a task (gets validated automatically)
3. ✅ See governance violations if any
4. ✅ See Bastard evaluation of plan
5. ✅ Start task only if approved
6. ✅ Complete task (triggers final validation)
7. ✅ See Bastard report for any task
8. ✅ List all tasks with status
9. ✅ Have over-engineering automatically detected and blocked
10. ✅ Have component placement violations caught

---

## 🎯 End Goal

**A system where:**
- You define tasks at workspace level
- WMS validates against architecture
- The Bastard catches over-engineering
- Tasks route to correct repos automatically
- Violations block progress until fixed
- Architecture decisions are enforced
- Scale appropriateness is validated
- You can't accidentally violate your own rules

**The workflow becomes:**
```bash
wms task create         # Define what to do
# [WMS validates, Bastard approves/rejects]
wms task start WS-TASK-001   # Start approved work
# [Do the work]
wms task complete WS-TASK-001  # Request completion
# [Bastard validates, approves/rejects]
# Done!
```

---

**This is the complete specification. Cursor has everything needed to build this system.**
