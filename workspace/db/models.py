"""
REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: SQLAlchemy models for workspace tracking database
DOMAIN: Cross-repo workspace management

Models for workspace-level tracking:
- Tasks across all repos
- Sessions and activities
- Cross-repo issues
- Architecture decisions and states
- Component placements
- Drift detections
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Integer,
    Float,
    Boolean,
    ForeignKey,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from typing import Optional
import json

# Create declarative base (independent from meridian-core)
Base = declarative_base()


# ============================================================================
# WORKSPACE TASK TRACKING
# ============================================================================

class WorkspaceTask(Base):
    """Workspace-level task tracking (all repos)."""
    
    __tablename__ = 'workspace_tasks'
    
    id = Column(String(50), primary_key=True)  # WS-TASK-XXX
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, index=True)  # pending, in_progress, completed, blocked
    priority = Column(String(20), index=True)  # HIGH, MEDIUM, LOW
    repos_affected = Column(Text)  # JSON array: ["meridian-core", "meridian-trading"]
    dependencies = Column(Text)  # JSON array: ["WS-TASK-001", "WS-TASK-002"]
    created = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_created = Column(String(100))  # Session ID where task was created
    assigned_to = Column(String(100))
    notes = Column(Text)
    related_files = Column(Text)  # JSON array
    extra_metadata = Column(Text)  # JSON object for flexible data (renamed from 'metadata' - SQLAlchemy reserved)
    
    # WMS fields
    workflow_id = Column(String(50), ForeignKey('workflows.id'), nullable=True, index=True)
    assigned_repo = Column(String(100))  # Determined by governance
    assigned_by = Column(String(100))  # "governance_engine" or "manual"
    bastard_plan_grade = Column(String(1))  # Grade from plan validation
    bastard_completion_grade = Column(String(1))  # Grade from completion validation
    scale_tier = Column(Integer)  # Appropriate tier (1, 2, 3)
    started_at = Column(DateTime)  # When task started
    completed_at = Column(DateTime)  # When task completed (already have updated, but this is explicit)
    
    # Relationships
    related_issues = relationship("CrossRepoIssue", back_populates="related_task", foreign_keys="CrossRepoIssue.related_task_id")
    architecture_tasks = relationship("ArchitectureTask", back_populates="workspace_task")
    
    # WMS relationships (optional - added after WMS models are defined)
    # workflow_id = Column(String(50), ForeignKey('workflows.id'), nullable=True)
    # violations = relationship("Violation", back_populates="task")
    # bastard_reports = relationship("BastardReport", back_populates="task")
    
    __table_args__ = (
        Index('idx_tasks_status', 'status'),
        Index('idx_tasks_priority', 'priority'),
        Index('idx_tasks_created', 'created'),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "repos_affected": json.loads(self.repos_affected) if self.repos_affected else [],
            "dependencies": json.loads(self.dependencies) if self.dependencies else [],
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None,
            "session_created": self.session_created,
            "assigned_to": self.assigned_to,
            "notes": self.notes,
            "related_files": json.loads(self.related_files) if self.related_files else [],
            "metadata": json.loads(self.extra_metadata) if self.extra_metadata else {},
        }


# ============================================================================
# SESSION TRACKING
# ============================================================================

class WorkspaceSession(Base):
    """Workspace session tracking."""
    
    __tablename__ = 'workspace_sessions'
    
    id = Column(String(100), primary_key=True)  # session ID: 2025-11-20-session-001
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    status = Column(String(50), nullable=False, index=True)  # in_progress, completed
    user = Column(String(100))
    ai_assistant = Column(String(100))
    handoff_notes = Column(Text)
    
    # Relationships
    activities = relationship("SessionActivity", back_populates="session", cascade="all, delete-orphan")
    decisions = relationship("SessionDecision", back_populates="session", cascade="all, delete-orphan")
    issues_found = relationship("SessionIssue", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_sessions_start', 'start_time'),
        Index('idx_sessions_status', 'status'),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "session_id": self.id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "user": self.user,
            "ai_assistant": self.ai_assistant,
            "handoff_notes": self.handoff_notes,
        }


class SessionActivity(Base):
    """Activities within a session."""
    
    __tablename__ = 'session_activities'
    
    id = Column(String(50), primary_key=True)
    session_id = Column(String(100), ForeignKey('workspace_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    activity_type = Column(String(50), nullable=False)  # documentation, analysis, governance, etc.
    description = Column(Text, nullable=False)
    files_created = Column(Text)  # JSON array
    files_modified = Column(Text)  # JSON array
    outcome = Column(Text)
    time = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    extra_metadata = Column(Text)  # JSON object (renamed from 'metadata' - SQLAlchemy reserved)
    
    # Relationships
    session = relationship("WorkspaceSession", back_populates="activities")
    
    __table_args__ = (
        Index('idx_activities_session', 'session_id'),
        Index('idx_activities_type', 'activity_type'),
        Index('idx_activities_time', 'time'),
    )


class SessionDecision(Base):
    """Decisions made during a session."""
    
    __tablename__ = 'session_decisions'
    
    id = Column(String(50), primary_key=True)
    session_id = Column(String(100), ForeignKey('workspace_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    decision_id = Column(String(50), ForeignKey('architecture_decisions.id'), nullable=True)
    
    # Relationships
    session = relationship("WorkspaceSession", back_populates="decisions")
    decision = relationship("ArchitectureDecision", back_populates="sessions")
    
    __table_args__ = (
        Index('idx_session_decisions_session', 'session_id'),
    )


class SessionIssue(Base):
    """Issues found during a session."""
    
    __tablename__ = 'session_issues'
    
    id = Column(String(50), primary_key=True)
    session_id = Column(String(100), ForeignKey('workspace_sessions.id', ondelete='CASCADE'), nullable=False, index=True)
    issue_id = Column(String(50), ForeignKey('cross_repo_issues.id'), nullable=True)
    
    # Relationships
    session = relationship("WorkspaceSession", back_populates="issues_found")
    issue = relationship("CrossRepoIssue", back_populates="sessions")
    
    __table_args__ = (
        Index('idx_session_issues_session', 'session_id'),
    )


# ============================================================================
# CROSS-REPO ISSUE TRACKING
# ============================================================================

class CrossRepoIssue(Base):
    """Cross-repo issues (drift, violations, etc.)."""
    
    __tablename__ = 'cross_repo_issues'
    
    id = Column(String(50), primary_key=True)  # ISSUE-XXX
    issue_type = Column(String(50), nullable=False, index=True)  # code_creep, governance, task_tracking, etc.
    severity = Column(String(20), nullable=False, index=True)  # HIGH, MEDIUM, LOW
    title = Column(String(500), nullable=False)
    description = Column(Text)
    repos_affected = Column(Text)  # JSON array
    detected = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    detected_by = Column(String(100))  # automated, manual, ci_cd
    status = Column(String(50), nullable=False, default='open', index=True)  # open, resolved, closed
    action_required = Column(Text)
    assigned_to = Column(String(100))
    related_task_id = Column(String(50), ForeignKey('workspace_tasks.id'), nullable=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    resolution_notes = Column(Text)
    extra_metadata = Column(Text)  # JSON object (renamed from 'metadata' - SQLAlchemy reserved)
    
    # Relationships
    related_task = relationship("WorkspaceTask", back_populates="related_issues", foreign_keys=[related_task_id])
    sessions = relationship("SessionIssue", back_populates="issue")
    
    __table_args__ = (
        Index('idx_issues_type', 'issue_type'),
        Index('idx_issues_severity', 'severity'),
        Index('idx_issues_status', 'status'),
        Index('idx_issues_detected', 'detected'),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "repos_affected": json.loads(self.repos_affected) if self.repos_affected else [],
            "detected": self.detected.isoformat() if self.detected else None,
            "detected_by": self.detected_by,
            "status": self.status,
            "action_required": self.action_required,
            "assigned_to": self.assigned_to,
            "related_task_id": self.related_task_id,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "metadata": json.loads(self.extra_metadata) if self.extra_metadata else {},
        }


# ============================================================================
# ARCHITECTURE DECISION TRACKING
# ============================================================================

class ArchitectureDecision(Base):
    """Architecture decisions made."""
    
    __tablename__ = 'architecture_decisions'
    
    id = Column(String(50), primary_key=True)  # DEC-XXX
    date = Column(DateTime, nullable=False, index=True)
    session = Column(String(100), nullable=False, index=True)  # Session ID
    decision = Column(Text, nullable=False)
    repos_affected = Column(Text)  # JSON array
    rationale = Column(Text)
    status = Column(String(50), nullable=False, index=True)  # implemented, in_progress, maintained
    impact = Column(String(20))  # HIGH, MEDIUM, LOW
    related_files = Column(Text)  # JSON array
    documentation = Column(Text)  # JSON array
    extra_metadata = Column(Text)  # JSON object (renamed from 'metadata' - SQLAlchemy reserved)
    
    # Relationships
    sessions = relationship("SessionDecision", back_populates="decision")
    
    __table_args__ = (
        Index('idx_decisions_date', 'date'),
        Index('idx_decisions_status', 'status'),
        Index('idx_decisions_session', 'session'),
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "session": self.session,
            "decision": self.decision,
            "repos_affected": json.loads(self.repos_affected) if self.repos_affected else [],
            "rationale": self.rationale,
            "status": self.status,
            "impact": self.impact,
            "related_files": json.loads(self.related_files) if self.related_files else [],
            "documentation": json.loads(self.documentation) if self.documentation else [],
            "metadata": json.loads(self.extra_metadata) if self.extra_metadata else {},
        }


# ============================================================================
# ARCHITECTURE STATE TRACKING
# ============================================================================

class ArchitectureState(Base):
    """Architecture state snapshots."""
    
    __tablename__ = 'architecture_states'
    
    id = Column(String(50), primary_key=True)
    state_name = Column(String(200), nullable=False, unique=True)
    state_type = Column(String(50), nullable=False)  # master, current, target
    repo = Column(String(100), nullable=False, index=True)
    architecture_doc_path = Column(String(500))  # Path to architecture document
    state_data = Column(Text)  # JSON with architecture state
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    version = Column(String(50))
    
    # Relationships
    components = relationship("ArchitectureComponent", back_populates="architecture_state", foreign_keys="ArchitectureComponent.architecture_state_id")
    tasks = relationship("ArchitectureTask", back_populates="architecture_state")
    
    __table_args__ = (
        Index('idx_states_repo', 'repo'),
        Index('idx_states_type', 'state_type'),
    )


# NOTE: ArchitectureState is defined above. The old definition below has been removed
# to avoid conflicts. If you need the old structure, migrate the data first.


class ComponentPlacement(Base):
    """Component placement rules (where components SHOULD be)."""
    
    __tablename__ = 'component_placements'
    
    id = Column(String(50), primary_key=True)
    component_name = Column(String(200), nullable=False)
    component_type = Column(String(50), nullable=False)  # class, module, package
    correct_repo = Column(String(100), nullable=False, index=True)
    correct_location = Column(String(500))  # Path where it should be
    architecture_state_id = Column(String(50), ForeignKey('architecture_states.id'), nullable=True)
    rationale = Column(Text)
    rules = Column(Text)  # JSON object with allowed/forbidden imports
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    architecture_state = relationship("ArchitectureState", foreign_keys=[architecture_state_id])
    
    __table_args__ = (
        Index('idx_components_repo', 'correct_repo'),
        Index('idx_components_name', 'component_name'),
        UniqueConstraint('component_name', 'architecture_state_id', name='uq_component_placement'),
    )


class ArchitectureTask(Base):
    """Tasks linked to architectural goals."""
    
    __tablename__ = 'architecture_tasks'
    
    id = Column(String(50), primary_key=True)
    task_id = Column(String(50), ForeignKey('workspace_tasks.id'), nullable=False, index=True)
    architecture_state_id = Column(String(50), ForeignKey('architecture_states.id'), nullable=True)
    architectural_goal = Column(Text)
    component_id = Column(String(50), ForeignKey('component_placements.id'), nullable=True)
    milestone = Column(String(200))  # Future state milestone
    priority = Column(String(20))  # HIGH, MEDIUM, LOW
    status = Column(String(50), nullable=False, index=True)  # pending, in_progress, completed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    workspace_task = relationship("WorkspaceTask", back_populates="architecture_tasks")
    architecture_state = relationship("ArchitectureState", back_populates="tasks")
    component = relationship("ComponentPlacement")
    
    __table_args__ = (
        Index('idx_arch_tasks_task', 'task_id'),
        Index('idx_arch_tasks_state', 'architecture_state_id'),
        Index('idx_arch_tasks_status', 'status'),
    )


# ============================================================================
# DRIFT DETECTION
# ============================================================================

class DriftDetection(Base):
    """Detected configuration drift violations."""
    
    __tablename__ = 'drift_detections'
    
    id = Column(String(50), primary_key=True)
    repo = Column(String(100), nullable=False, index=True)
    violation_type = Column(String(50), nullable=False, index=True)  # component_placement, dependency, scope, pattern
    severity = Column(String(20), nullable=False, index=True)  # HIGH, MEDIUM, LOW
    file_path = Column(String(500), nullable=False)
    component_name = Column(String(200))
    detected_rule = Column(String(200))  # Which rule was violated
    expected_location = Column(String(500))  # Where it SHOULD be
    actual_location = Column(String(500))  # Where it actually is
    violation_details = Column(Text)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    detected_by = Column(String(100))  # automated, manual, ci_cd
    status = Column(String(50), nullable=False, default='open', index=True)  # open, resolved, ignored
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))
    resolution_notes = Column(Text)
    related_task_id = Column(String(50), ForeignKey('workspace_tasks.id'), nullable=True)
    extra_metadata = Column(Text)  # JSON object (renamed from 'metadata' - SQLAlchemy reserved)
    
    # Relationships
    related_task = relationship("WorkspaceTask", foreign_keys=[related_task_id])
    
    __table_args__ = (
        Index('idx_drift_repo', 'repo'),
        Index('idx_drift_type', 'violation_type'),
        Index('idx_drift_severity', 'severity'),
        Index('idx_drift_status', 'status'),
        Index('idx_drift_detected', 'detected_at'),
    )


class DriftScan(Base):
    """Drift scan history."""
    
    __tablename__ = 'drift_scans'
    
    id = Column(String(50), primary_key=True)
    scan_type = Column(String(50), nullable=False)  # full, incremental, pre_commit
    scan_start = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    scan_end = Column(DateTime)
    repos_scanned = Column(Text)  # JSON array
    violations_found = Column(Integer, default=0)
    violations_high = Column(Integer, default=0)
    violations_medium = Column(Integer, default=0)
    violations_low = Column(Integer, default=0)
    status = Column(String(50), nullable=False, index=True)  # running, completed, failed
    triggered_by = Column(String(100))  # user, ci_cd, scheduled
    results_file = Column(String(500))  # Path to detailed results
    
    __table_args__ = (
        Index('idx_scans_start', 'scan_start'),
        Index('idx_scans_status', 'status'),
    )


# ============================================================================
# CONTEXT MANAGEMENT
# ============================================================================

class ContextSwitch(Base):
    """Context switching history."""
    
    __tablename__ = 'context_switches'
    
    id = Column(String(50), primary_key=True)
    repo = Column(String(100), nullable=False, index=True)
    repo_path = Column(String(500), nullable=False)
    activated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    deactivated_at = Column(DateTime)
    activated_by = Column(String(100))
    context_id = Column(String(50), unique=True)
    previous_context = Column(String(100))  # Previous repo name
    context_notes = Column(Text)
    duration_seconds = Column(Float)  # How long context was active
    operations_count = Column(Integer, default=0)  # Number of operations in context
    
    __table_args__ = (
        Index('idx_context_repo', 'repo'),
        Index('idx_context_activated', 'activated_at'),
    )


# ============================================================================
# CONFIGURATION STATE TRACKING
# ============================================================================

class ConfigurationSnapshot(Base):
    """Configuration snapshots (for tracking changes)."""
    
    __tablename__ = 'configuration_snapshots'
    
    id = Column(String(50), primary_key=True)
    repo = Column(String(100), nullable=False, index=True)
    snapshot_type = Column(String(50), nullable=False)  # full, incremental
    configuration_hash = Column(String(64), nullable=False)  # Hash of configuration state
    snapshot_data = Column(Text)  # JSON object with full configuration state
    taken_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    taken_by = Column(String(100))
    notes = Column(Text)
    
    __table_args__ = (
        Index('idx_snapshots_repo', 'repo'),
        Index('idx_snapshots_taken', 'taken_at'),
    )


class ConfigurationChange(Base):
    """Configuration changes (diff tracking)."""
    
    __tablename__ = 'configuration_changes'
    
    id = Column(String(50), primary_key=True)
    repo = Column(String(100), nullable=False, index=True)
    change_type = Column(String(50), nullable=False)  # added, removed, modified
    component_name = Column(String(200))
    file_path = Column(String(500))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    changed_by = Column(String(100))
    commit_hash = Column(String(100))
    drift_detection_id = Column(String(50), ForeignKey('drift_detections.id'), nullable=True)
    
    # Relationships
    drift_detection = relationship("DriftDetection", foreign_keys=[drift_detection_id])
    
    __table_args__ = (
        Index('idx_changes_repo', 'repo'),
        Index('idx_changes_type', 'change_type'),
        Index('idx_changes_time', 'changed_at'),
    )


# ============================================================================
# CODE-TO-ARCHITECTURE COMPONENT TRACKING
# ============================================================================

class ArchitectureComponent(Base):
    """Registered architecture components (from master architecture)."""
    
    __tablename__ = 'architecture_components'
    
    id = Column(String(50), primary_key=True)
    component_name = Column(String(200), nullable=False)
    component_type = Column(String(50), nullable=False)  # module, class, service, package
    repo = Column(String(100), nullable=False, index=True)
    expected_path = Column(String(500))  # Where it should be (from architecture)
    description = Column(Text)
    
    # Component scope
    approved_scope = Column(Text)  # JSON: What's allowed in this component
    boundaries = Column(Text)  # JSON: What's NOT allowed
    
    # Status
    status = Column(String(50), nullable=False, default="active", index=True)  # active, deprecated, planned
    version = Column(String(50))  # Architecture version this belongs to
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    registered_by = Column(String(100))
    architecture_state_id = Column(String(50), ForeignKey('architecture_states.id'), nullable=True)
    
    # Relationships
    architecture_state = relationship("ArchitectureState", foreign_keys=[architecture_state_id], back_populates="components")
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
    file_path = Column(String(500), nullable=False, index=True)
    component_id = Column(String(50), ForeignKey('architecture_components.id'), nullable=False, index=True)
    
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
    file_path = Column(String(500), nullable=False, index=True)
    component_id = Column(String(50), ForeignKey('architecture_components.id'), nullable=True)
    mapping_id = Column(String(50), ForeignKey('code_component_mappings.id'), nullable=True)
    
    # Validation
    is_tracked = Column(Boolean, default=False, index=True)  # Mapped to component
    is_validated = Column(Boolean, default=False, index=True)  # Pre-deployment validated
    validation_status = Column(String(50), index=True)  # approved, rejected, pending, untracked
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
    file_path = Column(String(500), nullable=False, unique=True, index=True)
    repo = Column(String(100), nullable=False, index=True)
    
    # Detection
    first_detected = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=False, default=datetime.utcnow)
    detection_count = Column(Integer, default=1)
    
    # Status
    status = Column(String(50), default="unregistered", index=True)  # unregistered, under_review, mapped, ignored
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


# ============================================================================
# WMS: CONTEXT MANAGEMENT
# ============================================================================

class WorkContext(Base):
    """Current work context - which repo user is working in (WMS)."""
    
    __tablename__ = 'work_contexts'
    
    id = Column(String(50), primary_key=True)
    repo = Column(String(100), nullable=False, index=True)  # meridian-core, meridian-research, etc.
    repo_path = Column(String(500), nullable=False)
    activated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    activated_by = Column(String(100))
    is_active = Column(Boolean, default=True, index=True)
    
    # Metadata
    notes = Column(Text)
    previous_context_id = Column(String(50), ForeignKey('work_contexts.id'), nullable=True)
    
    # Relationships
    previous_context = relationship("WorkContext", remote_side=[id], foreign_keys=[previous_context_id])
    
    __table_args__ = (
        Index('idx_work_context_repo', 'repo'),
        Index('idx_work_context_active', 'is_active'),
        Index('idx_work_context_activated', 'activated_at'),
    )


# ============================================================================
# WMS: TASKS & WORKFLOWS
# ============================================================================

class Workflow(Base):
    """Workflow definitions and instances (WMS)."""
    
    __tablename__ = 'workflows'
    
    id = Column(String(50), primary_key=True)
    workflow_id = Column(String(20), unique=True)  # WF-001
    name = Column(String(500), nullable=False)
    workflow_type = Column(String(50))  # feature, bugfix, refactor
    allowed_repos = Column(Text)  # JSON array: ["meridian-core", "meridian-trading"]
    status = Column(String(20), default="active", index=True)
    current_stage = Column(Integer, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships (will be defined after WorkflowStage)
    # tasks = relationship("WorkspaceTask", back_populates="workflow")
    # stages = relationship("WorkflowStage", back_populates="workflow")
    
    __table_args__ = (
        Index('idx_workflows_status', 'status'),
        Index('idx_workflows_type', 'workflow_type'),
    )


class WorkflowStage(Base):
    """Stages within a workflow (WMS)."""
    
    __tablename__ = 'workflow_stages'
    
    id = Column(String(50), primary_key=True)
    workflow_id = Column(String(50), ForeignKey('workflows.id'), nullable=False, index=True)
    stage_number = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    validation_required = Column(Boolean, default=True)
    validation_type = Column(String(50))  # governance, bastard, architecture
    status = Column(String(20), default="pending", index=True)
    completed_at = Column(DateTime)
    
    # Relationships
    workflow = relationship("Workflow", foreign_keys=[workflow_id])
    
    __table_args__ = (
        Index('idx_workflow_stages_workflow', 'workflow_id'),
        Index('idx_workflow_stages_status', 'status'),
    )


# ============================================================================
# WMS: VIOLATIONS & GOVERNANCE
# ============================================================================

class Violation(Base):
    """Architecture/governance violations detected (WMS)."""
    
    __tablename__ = 'violations'
    
    id = Column(String(50), primary_key=True)
    task_id = Column(String(50), ForeignKey('workspace_tasks.id'), nullable=True, index=True)
    violation_type = Column(String(50), nullable=False, index=True)  # component_placement, forbidden_import, scale_mismatch, over_engineering
    severity = Column(String(20), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    message = Column(Text, nullable=False)
    file_path = Column(String(500))
    line_number = Column(Integer)
    rule_violated = Column(String(500))
    fix_required = Column(Text)
    status = Column(String(20), default="open", index=True)  # open, acknowledged, fixed
    resolved_at = Column(DateTime)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    task = relationship("WorkspaceTask", foreign_keys=[task_id])
    
    __table_args__ = (
        Index('idx_violations_task', 'task_id'),
        Index('idx_violations_type', 'violation_type'),
        Index('idx_violations_severity', 'severity'),
        Index('idx_violations_status', 'status'),
    )


class ImportRule(Base):
    """Import/dependency rules (WMS)."""
    
    __tablename__ = 'import_rules'
    
    id = Column(String(50), primary_key=True)
    source_repo = Column(String(100), nullable=False, index=True)
    rule_type = Column(String(20), nullable=False)  # allowed, forbidden
    target_module = Column(String(200))
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_import_rules_repo', 'source_repo'),
        Index('idx_import_rules_type', 'rule_type'),
    )


class ScaleTier(Base):
    """Scale tier definitions for various solutions (WMS)."""
    
    __tablename__ = 'scale_tiers'
    
    id = Column(String(50), primary_key=True)
    domain = Column(String(50), nullable=False, index=True)  # credentials, database, deployment
    tier = Column(Integer, nullable=False)  # 1, 2, 3
    name = Column(String(200), nullable=False)  # "Personal Use", "Team Use", "Enterprise"
    user_range = Column(String(100))  # "1-5 users"
    solution = Column(String(500))
    complexity = Column(Integer)  # 1-10
    upgrade_trigger = Column(Text)  # When to upgrade to this tier
    migration_effort = Column(String(100))  # "4 hours"
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_scale_tiers_domain', 'domain'),
        Index('idx_scale_tiers_tier', 'tier'),
        UniqueConstraint('domain', 'tier', name='uq_scale_tier_domain'),
    )


# ============================================================================
# WMS: THE BASTARD INTEGRATION
# ============================================================================

class BastardReport(Base):
    """Reports from The Bastard evaluations (WMS)."""
    
    __tablename__ = 'bastard_reports'
    
    id = Column(String(50), primary_key=True)
    task_id = Column(String(50), ForeignKey('workspace_tasks.id'), nullable=True, index=True)
    evaluation_type = Column(String(50), nullable=False)  # plan, completion
    overall_grade = Column(String(1))  # F, D, C, B, A, OVER_ENGINEERED
    scale_appropriateness = Column(String(1))
    deployment_maturity = Column(String(1))
    portability = Column(String(1))
    state_management = Column(String(1))
    credential_management = Column(String(1))
    actual_users = Column(Integer)
    designed_for_users = Column(Integer)
    over_engineering_score = Column(Integer)  # 1-10
    tier_recommendation = Column(Integer)  # 1, 2, or 3
    critical_blockers = Column(Text)  # JSON array
    required_fixes = Column(Text)  # JSON array
    full_report = Column(Text)  # Complete Bastard verdict
    evaluated_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    task = relationship("WorkspaceTask", foreign_keys=[task_id])
    
    __table_args__ = (
        Index('idx_bastard_reports_task', 'task_id'),
        Index('idx_bastard_reports_type', 'evaluation_type'),
        Index('idx_bastard_reports_grade', 'overall_grade'),
        Index('idx_bastard_reports_evaluated', 'evaluated_at'),
    )

