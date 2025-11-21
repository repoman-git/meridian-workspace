"""
REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Workspace database manager for workspace tracking
DOMAIN: Cross-repo workspace management

Manages workspace-level tracking database using SQLAlchemy + SQLite.
Follows meridian-core patterns for connection pooling, WAL mode, etc.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import json
import logging

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .models import (
    Base,
    WorkspaceTask,
    WorkspaceSession,
    CrossRepoIssue,
    ArchitectureDecision,
    ArchitectureState,
    ComponentPlacement,
    DriftDetection,
    ContextSwitch,
    SessionActivity,
    SessionDecision,
    SessionIssue,
    ArchitectureTask,
    DriftScan,
    ConfigurationSnapshot,
    ConfigurationChange,
)

logger = logging.getLogger(__name__)


class WorkspaceDB:
    """
    Workspace database manager.
    
    Manages workspace-level tracking: tasks, sessions, issues, architecture decisions,
    drift detections, and more.
    
    Uses SQLAlchemy + SQLite following meridian-core patterns:
    - Connection pooling
    - WAL mode
    - Thread-safe
    - Automatic schema management
    """
    
    def __init__(self, db_path: Optional[str] = None, workspace_root: Optional[Path] = None):
        """
        Initialize workspace database.
        
        Args:
            db_path: Path to SQLite database. Defaults to workspace.db in workspace_root
            workspace_root: Workspace root directory. Defaults to current directory parent
        """
        if workspace_root is None:
            workspace_root = Path.cwd()
        
        if db_path is None:
            db_path = str(workspace_root / "workspace.db")
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.workspace_root = workspace_root
        
        # Create engine with WAL mode (following meridian-core pattern)
        database_url = f'sqlite:///{db_path}'
        self.engine = create_engine(
            database_url,
            # Connection pooling (thread-safe!)
            poolclass=QueuePool,
            pool_size=5,              # 5 connections ready
            max_overflow=10,          # Can create 10 more (15 total)
            pool_pre_ping=True,       # Check connections before use
            pool_recycle=3600,        # Recycle after 1 hour
            
            # SQLite-specific optimizations
            connect_args={
                'check_same_thread': False,  # Allow multi-threading
                'timeout': 30.0              # 30s timeout
            },
            
            # Enable SQLite optimizations
            execution_options={
                'isolation_level': 'AUTOCOMMIT' if database_url.startswith('sqlite') else None
            }
        )
        
        # Enable WAL mode (following meridian-core pattern)
        with self.engine.connect() as conn:
            conn.execute(text('PRAGMA journal_mode=WAL;'))
            conn.execute(text('PRAGMA busy_timeout=30000;'))
            conn.execute(text('PRAGMA synchronous=NORMAL;'))
            conn.execute(text('PRAGMA foreign_keys=ON;'))
            conn.commit()
            logger.info("SQLite WAL mode enabled")
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        # Ensure tables exist
        Base.metadata.create_all(self.engine)
        
        logger.info(f"Workspace database initialized: {db_path}")
    
    def _get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    # ========================================================================
    # WORKSPACE TASK METHODS
    # ========================================================================
    
    def add_task(
        self,
        task_id: str,
        title: str,
        status: str = "pending",
        priority: Optional[str] = None,
        repos_affected: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        description: Optional[str] = None,
        session_created: Optional[str] = None,
        assigned_to: Optional[str] = None,
        notes: Optional[str] = None,
        related_files: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkspaceTask:
        """
        Add a workspace task.
        
        Args:
            task_id: Task ID (e.g., "WS-TASK-001")
            title: Task title
            status: Task status (pending, in_progress, completed, blocked)
            priority: Priority (HIGH, MEDIUM, LOW)
            repos_affected: List of repos affected
            dependencies: List of task IDs this depends on
            description: Task description
            session_created: Session ID where task was created
            assigned_to: Who task is assigned to
            notes: Task notes
            related_files: List of related file paths
            metadata: Additional metadata (JSON-serializable dict)
        
        Returns:
            WorkspaceTask instance
        """
        with self._get_session() as session:
            task = WorkspaceTask(
                id=task_id,
                title=title,
                description=description,
                status=status,
                priority=priority,
                repos_affected=json.dumps(repos_affected) if repos_affected else None,
                dependencies=json.dumps(dependencies) if dependencies else None,
                session_created=session_created,
                assigned_to=assigned_to,
                notes=notes,
                related_files=json.dumps(related_files) if related_files else None,
                extra_metadata=json.dumps(metadata) if metadata else None,
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            return task
    
    def get_task(self, task_id: str) -> Optional[WorkspaceTask]:
        """Get task by ID."""
        with self._get_session() as session:
            return session.query(WorkspaceTask).filter(WorkspaceTask.id == task_id).first()
    
    def get_tasks(
        self,
        status: Optional[str] = None,
        repo: Optional[str] = None,
        priority: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[WorkspaceTask]:
        """
        Get tasks with optional filtering.
        
        Args:
            status: Filter by status
            repo: Filter by repo (checks repos_affected JSON array)
            priority: Filter by priority
            limit: Limit number of results
        
        Returns:
            List of WorkspaceTask instances
        """
        with self._get_session() as session:
            query = session.query(WorkspaceTask)
            
            if status:
                query = query.filter(WorkspaceTask.status == status)
            
            if priority:
                query = query.filter(WorkspaceTask.priority == priority)
            
            if repo:
                # Filter by JSON array in repos_affected
                query = query.filter(WorkspaceTask.repos_affected.like(f'%"{repo}"%'))
            
            query = query.order_by(WorkspaceTask.created.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
    
    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status."""
        with self._get_session() as session:
            task = session.query(WorkspaceTask).filter(WorkspaceTask.id == task_id).first()
            if not task:
                return False
            task.status = status
            task.updated = datetime.utcnow()
            session.commit()
            return True
    
    # ========================================================================
    # SESSION METHODS
    # ========================================================================
    
    def add_session(
        self,
        session_id: str,
        user: Optional[str] = None,
        ai_assistant: Optional[str] = None,
        handoff_notes: Optional[str] = None,
    ) -> WorkspaceSession:
        """Add a new workspace session."""
        with self._get_session() as session:
            ws_session = WorkspaceSession(
                id=session_id,
                start_time=datetime.utcnow(),
                status="in_progress",
                user=user,
                ai_assistant=ai_assistant,
                handoff_notes=handoff_notes,
            )
            session.add(ws_session)
            session.commit()
            session.refresh(ws_session)
            return ws_session
    
    def end_session(self, session_id: str) -> bool:
        """End a session."""
        with self._get_session() as session:
            ws_session = session.query(WorkspaceSession).filter(WorkspaceSession.id == session_id).first()
            if not ws_session:
                return False
            ws_session.end_time = datetime.utcnow()
            ws_session.status = "completed"
            session.commit()
            return True
    
    def get_current_session(self) -> Optional[WorkspaceSession]:
        """Get current (in-progress) session."""
        with self._get_session() as session:
            return session.query(WorkspaceSession).filter(
                WorkspaceSession.status == "in_progress"
            ).order_by(WorkspaceSession.start_time.desc()).first()
    
    def add_session_activity(
        self,
        session_id: str,
        activity_type: str,
        description: str,
        files_created: Optional[List[str]] = None,
        files_modified: Optional[List[str]] = None,
        outcome: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionActivity:
        """Add activity to a session."""
        with self._get_session() as session:
            activity = SessionActivity(
                id=f"{session_id}-{datetime.utcnow().timestamp()}",
                session_id=session_id,
                activity_type=activity_type,
                description=description,
                files_created=json.dumps(files_created) if files_created else None,
                files_modified=json.dumps(files_modified) if files_modified else None,
                outcome=outcome,
                extra_metadata=json.dumps(metadata) if metadata else None,
            )
            session.add(activity)
            session.commit()
            session.refresh(activity)
            return activity
    
    # ========================================================================
    # ISSUE METHODS
    # ========================================================================
    
    def add_issue(
        self,
        issue_id: str,
        issue_type: str,
        severity: str,
        title: str,
        description: Optional[str] = None,
        repos_affected: Optional[List[str]] = None,
        detected_by: Optional[str] = None,
        action_required: Optional[str] = None,
        related_task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CrossRepoIssue:
        """Add a cross-repo issue."""
        with self._get_session() as session:
            issue = CrossRepoIssue(
                id=issue_id,
                issue_type=issue_type,
                severity=severity,
                title=title,
                description=description,
                repos_affected=json.dumps(repos_affected) if repos_affected else None,
                detected_by=detected_by or "manual",
                action_required=action_required,
                related_task_id=related_task_id,
                metadata=json.dumps(metadata) if metadata else None,
            )
            session.add(issue)
            session.commit()
            session.refresh(issue)
            return issue
    
    def get_issues(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        issue_type: Optional[str] = None,
        repo: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[CrossRepoIssue]:
        """Get issues with optional filtering."""
        with self._get_session() as session:
            query = session.query(CrossRepoIssue)
            
            if status:
                query = query.filter(CrossRepoIssue.status == status)
            
            if severity:
                query = query.filter(CrossRepoIssue.severity == severity)
            
            if issue_type:
                query = query.filter(CrossRepoIssue.issue_type == issue_type)
            
            if repo:
                query = query.filter(CrossRepoIssue.repos_affected.like(f'%"{repo}"%'))
            
            query = query.order_by(CrossRepoIssue.detected.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
    
    # ========================================================================
    # ARCHITECTURE DECISION METHODS
    # ========================================================================
    
    def add_decision(
        self,
        decision_id: str,
        session: str,
        decision: str,
        repos_affected: Optional[List[str]] = None,
        rationale: Optional[str] = None,
        status: str = "implemented",
        impact: Optional[str] = None,
        related_files: Optional[List[str]] = None,
        documentation: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ArchitectureDecision:
        """Add an architecture decision."""
        with self._get_session() as db_session:
            arch_decision = ArchitectureDecision(
                id=decision_id,
                date=datetime.utcnow(),
                session=session,
                decision=decision,
                repos_affected=json.dumps(repos_affected) if repos_affected else None,
                rationale=rationale,
                status=status,
                impact=impact,
                related_files=json.dumps(related_files) if related_files else None,
                documentation=json.dumps(documentation) if documentation else None,
                metadata=json.dumps(metadata) if metadata else None,
            )
            db_session.add(arch_decision)
            db_session.commit()
            db_session.refresh(arch_decision)
            return arch_decision
    
    def get_decisions(
        self,
        status: Optional[str] = None,
        repo: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[ArchitectureDecision]:
        """Get architecture decisions with optional filtering."""
        with self._get_session() as session:
            query = session.query(ArchitectureDecision)
            
            if status:
                query = query.filter(ArchitectureDecision.status == status)
            
            if repo:
                query = query.filter(ArchitectureDecision.repos_affected.like(f'%"{repo}"%'))
            
            query = query.order_by(ArchitectureDecision.date.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
    
    # ========================================================================
    # CONTEXT SWITCH METHODS
    # ========================================================================
    
    def log_context_switch(
        self,
        repo: str,
        repo_path: str,
        context_id: str,
        previous_context: Optional[str] = None,
        context_notes: Optional[str] = None,
        activated_by: Optional[str] = None,
    ) -> ContextSwitch:
        """Log a context switch."""
        with self._get_session() as session:
            # End previous context if exists
            if previous_context:
                prev = session.query(ContextSwitch).filter(
                    ContextSwitch.repo == previous_context,
                    ContextSwitch.deactivated_at.is_(None)
                ).order_by(ContextSwitch.activated_at.desc()).first()
                
                if prev:
                    prev.deactivated_at = datetime.utcnow()
                    if prev.activated_at:
                        duration = (datetime.utcnow() - prev.activated_at).total_seconds()
                        prev.duration_seconds = duration
            
            # Create new context switch
            context_switch = ContextSwitch(
                id=f"ctx-{datetime.utcnow().timestamp()}",
                repo=repo,
                repo_path=repo_path,
                activated_by=activated_by,
                context_id=context_id,
                previous_context=previous_context,
                context_notes=context_notes,
            )
            session.add(context_switch)
            session.commit()
            session.refresh(context_switch)
            return context_switch
    
    # ========================================================================
    # DRIFT DETECTION METHODS
    # ========================================================================
    
    def add_drift_detection(
        self,
        detection_id: str,
        repo: str,
        violation_type: str,
        severity: str,
        file_path: str,
        violation_details: str,
        expected_location: Optional[str] = None,
        actual_location: Optional[str] = None,
        component_name: Optional[str] = None,
        detected_rule: Optional[str] = None,
        detected_by: str = "automated",
        related_task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DriftDetection:
        """Add a drift detection."""
        with self._get_session() as session:
            detection = DriftDetection(
                id=detection_id,
                repo=repo,
                violation_type=violation_type,
                severity=severity,
                file_path=file_path,
                violation_details=violation_details,
                expected_location=expected_location,
                actual_location=actual_location,
                component_name=component_name,
                detected_rule=detected_rule,
                detected_by=detected_by,
                related_task_id=related_task_id,
                metadata=json.dumps(metadata) if metadata else None,
            )
            session.add(detection)
            session.commit()
            session.refresh(detection)
            return detection
    
    def get_drift_detections(
        self,
        repo: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        violation_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[DriftDetection]:
        """Get drift detections with optional filtering."""
        with self._get_session() as session:
            query = session.query(DriftDetection)
            
            if repo:
                query = query.filter(DriftDetection.repo == repo)
            
            if status:
                query = query.filter(DriftDetection.status == status)
            
            if severity:
                query = query.filter(DriftDetection.severity == severity)
            
            if violation_type:
                query = query.filter(DriftDetection.violation_type == violation_type)
            
            query = query.order_by(DriftDetection.detected_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
    
    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics."""
        with self._get_session() as session:
            total = session.query(func.count(WorkspaceTask.id)).scalar()
            pending = session.query(func.count(WorkspaceTask.id)).filter(
                WorkspaceTask.status == "pending"
            ).scalar()
            in_progress = session.query(func.count(WorkspaceTask.id)).filter(
                WorkspaceTask.status == "in_progress"
            ).scalar()
            completed = session.query(func.count(WorkspaceTask.id)).filter(
                WorkspaceTask.status == "completed"
            ).scalar()
            blocked = session.query(func.count(WorkspaceTask.id)).filter(
                WorkspaceTask.status == "blocked"
            ).scalar()
            
            return {
                "total": total or 0,
                "pending": pending or 0,
                "in_progress": in_progress or 0,
                "completed": completed or 0,
                "blocked": blocked or 0,
            }
    
    def get_issue_statistics(self) -> Dict[str, Any]:
        """Get issue statistics."""
        with self._get_session() as session:
            total = session.query(func.count(CrossRepoIssue.id)).scalar()
            open_count = session.query(func.count(CrossRepoIssue.id)).filter(
                CrossRepoIssue.status == "open"
            ).scalar()
            high = session.query(func.count(CrossRepoIssue.id)).filter(
                CrossRepoIssue.severity == "HIGH"
            ).scalar()
            medium = session.query(func.count(CrossRepoIssue.id)).filter(
                CrossRepoIssue.severity == "MEDIUM"
            ).scalar()
            low = session.query(func.count(CrossRepoIssue.id)).filter(
                CrossRepoIssue.severity == "LOW"
            ).scalar()
            
            return {
                "total": total or 0,
                "open": open_count or 0,
                "resolved": (total or 0) - (open_count or 0),
                "high": high or 0,
                "medium": medium or 0,
                "low": low or 0,
            }
    
    # ========================================================================
    # JSON EXPORT/IMPORT
    # ========================================================================
    
    def export_to_json(self) -> Dict[str, Any]:
        """
        Export all data to JSON structure.
        
        Returns:
            Dictionary with all workspace data
        """
        with self._get_session() as session:
            return {
                "version": "1.0",
                "workspace": str(self.workspace_root),
                "exported_at": datetime.utcnow().isoformat(),
                "tasks": [task.to_dict() for task in session.query(WorkspaceTask).all()],
                "sessions": [s.to_dict() for s in session.query(WorkspaceSession).all()],
                "issues": [issue.to_dict() for issue in session.query(CrossRepoIssue).all()],
                "decisions": [dec.to_dict() for dec in session.query(ArchitectureDecision).all()],
                "statistics": {
                    "tasks": self.get_task_statistics(),
                    "issues": self.get_issue_statistics(),
                }
            }
    
    def import_from_json(self, data: Dict[str, Any], merge: bool = False) -> Dict[str, int]:
        """
        Import data from JSON structure.
        
        Args:
            data: JSON data dictionary
            merge: If True, merge with existing data. If False, replace.
        
        Returns:
            Dictionary with import counts
        """
        counts = {"tasks": 0, "sessions": 0, "issues": 0, "decisions": 0}
        
        with self._get_session() as session:
            # Import tasks
            if "tasks" in data:
                for task_data in data["tasks"]:
                    if not merge or not session.query(WorkspaceTask).filter(
                        WorkspaceTask.id == task_data["id"]
                    ).first():
                        task = WorkspaceTask(
                            id=task_data["id"],
                            title=task_data["title"],
                            description=task_data.get("description"),
                            status=task_data.get("status", "pending"),
                            priority=task_data.get("priority"),
                            repos_affected=json.dumps(task_data.get("repos_affected", [])),
                            dependencies=json.dumps(task_data.get("dependencies", [])),
                            session_created=task_data.get("session_created"),
                            assigned_to=task_data.get("assigned_to"),
                            notes=task_data.get("notes"),
                            related_files=json.dumps(task_data.get("related_files", [])),
                            metadata=json.dumps(task_data.get("metadata", {})),
                        )
                        session.add(task)
                        counts["tasks"] += 1
            
            # Import issues
            if "issues" in data:
                for issue_data in data["issues"]:
                    if not merge or not session.query(CrossRepoIssue).filter(
                        CrossRepoIssue.id == issue_data["id"]
                    ).first():
                        issue = CrossRepoIssue(
                            id=issue_data["id"],
                            issue_type=issue_data.get("issue_type", "unknown"),
                            severity=issue_data.get("severity", "MEDIUM"),
                            title=issue_data["title"],
                            description=issue_data.get("description"),
                            repos_affected=json.dumps(issue_data.get("repos_affected", [])),
                            detected_by=issue_data.get("detected_by", "manual"),
                            status=issue_data.get("status", "open"),
                            action_required=issue_data.get("action_required"),
                            related_task_id=issue_data.get("related_task_id"),
                            metadata=json.dumps(issue_data.get("metadata", {})),
                        )
                        session.add(issue)
                        counts["issues"] += 1
            
            session.commit()
        
        return counts
    
    def export_to_json_files(self, output_dir: Optional[Path] = None):
        """
        Export database to JSON files (for human readability).
        
        Args:
            output_dir: Directory to write JSON files (defaults to workspace_root)
        """
        if output_dir is None:
            output_dir = self.workspace_root
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        data = self.export_to_json()
        
        # Write separate files
        (output_dir / "WORKSPACE-TASKS.json").write_text(json.dumps(data["tasks"], indent=2))
        (output_dir / "SESSION-LOG.json").write_text(json.dumps({"sessions": data["sessions"]}, indent=2))
        (output_dir / "CROSS-REPO-ISSUES.json").write_text(json.dumps({"issues": data["issues"]}, indent=2))
        (output_dir / "ARCHITECTURE-DECISIONS.json").write_text(json.dumps({"decisions": data["decisions"]}, indent=2))
        
        logger.info(f"Exported database to JSON files in {output_dir}")

