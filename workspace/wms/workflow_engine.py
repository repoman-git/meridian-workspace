"""
Workflow Engine - Orchestrates task execution.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Task workflow orchestration for WMS
DOMAIN: Cross-repo workspace management
"""

from typing import List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime
from workspace.db.models import WorkspaceTask, Violation
from workspace.wms.governance_engine import GovernanceEngine
from workspace.wms.bastard_integration import BastardIntegration
from pathlib import Path


class WorkflowEngine:
    """Orchestrates task workflows with validation."""
    
    def __init__(
        self,
        db_session: Session,
        governance: GovernanceEngine,
        bastard: BastardIntegration,
        workspace_root: Optional[Path] = None
    ):
        self.db = db_session
        self.governance = governance
        self.bastard = bastard
        self.workspace_root = workspace_root or Path.cwd()
    
    def create_task(
        self,
        title: str,
        description: str,
        actual_users: int,
        proposed_solution: Optional[str] = None,
        priority: str = "medium"
    ) -> WorkspaceTask:
        """
        Create and validate a new task.
        
        Args:
            title: Task title
            description: Task description
            actual_users: Actual user count TODAY
            proposed_solution: Proposed implementation approach
            priority: Task priority (low, medium, high, critical)
        
        Returns:
            Task instance (may be BLOCKED if violations detected)
        """
        # Generate task ID
        task_id = self._generate_task_id()
        
        # Determine correct repo
        assigned_repo = self.governance.determine_correct_repo(description)
        if not assigned_repo:
            # Default to meridian-core if unclear
            assigned_repo = "meridian-core"
        
        # Create task
        task = WorkspaceTask(
            id=task_id,
            title=title,
            description=description,
            status="planning",
            priority=priority.upper(),
            assigned_repo=assigned_repo,
            assigned_by="governance_engine",
            repos_affected=json.dumps([assigned_repo]) if assigned_repo else None
        )
        
        self.db.add(task)
        self.db.flush()  # Get task.id
        
        # Validate placement
        violations = self.governance.validate_task_placement(task, assigned_repo)
        
        if violations:
            print(f"\n⚠️  Placement violations detected:")
            for v in violations:
                print(f"  • {v.severity}: {v.message}")
                print(f"    Fix: {v.fix_required}")
                self.db.add(v)
            
            task.status = "blocked"
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
                
                task.status = "blocked"
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
            
            if report.overall_grade in ['F', 'D', 'OVER_ENGINEERED']:
                print(f"\n❌ The Bastard REJECTED the plan:")
                print(f"   Grade: {report.overall_grade}")
                task.status = "blocked"
            else:
                print(f"\n✅ The Bastard APPROVED the plan:")
                print(f"   Grade: {report.overall_grade}")
                task.status = "approved"
        else:
            task.status = "approved"
        
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
        task = self.db.query(WorkspaceTask).filter_by(id=task_id).first()
        if not task:
            print(f"❌ Task not found: {task_id}")
            return False
        
        if task.status == "blocked":
            print(f"❌ Task is BLOCKED. Fix violations first:")
            violations = self.db.query(Violation).filter_by(
                task_id=task.id,
                status="open"
            ).all()
            for v in violations:
                print(f"  • {v.severity}: {v.message}")
            return False
        
        if task.status not in ["approved", "planning"]:
            print(f"❌ Task must be APPROVED before starting (current: {task.status})")
            return False
        
        # Start task
        task.status = "in_progress"
        task.started_at = datetime.utcnow()
        self.db.commit()
        
        print(f"✅ Task started: {task.id}")
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
        task = self.db.query(WorkspaceTask).filter_by(id=task_id).first()
        if not task:
            print(f"❌ Task not found: {task_id}")
            return False
        
        if task.status != "in_progress":
            print(f"❌ Task is not IN_PROGRESS (current: {task.status})")
            return False
        
        # Final Bastard evaluation
        print(f"\n🔥 Running final Bastard evaluation...")
        report = self.bastard.evaluate_completion(task)
        
        if report.overall_grade in ['F', 'D']:
            print(f"\n❌ The Bastard REJECTED completion:")
            print(f"   Grade: {report.overall_grade}")
            task.status = "blocked"
            self.db.commit()
            return False
        
        # Task approved
        print(f"\n✅ The Bastard APPROVED completion:")
        print(f"   Grade: {report.overall_grade}")
        
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        self.db.commit()
        
        print(f"✅ Task completed: {task.id}")
        return True
    
    def _generate_task_id(self) -> str:
        """Generate next task ID."""
        latest = self.db.query(WorkspaceTask).order_by(WorkspaceTask.created.desc()).first()
        if not latest:
            return "WS-TASK-001"
        
        # Extract number from latest ID
        try:
            num = int(latest.id.split('-')[-1])
            return f"WS-TASK-{num + 1:03d}"
        except (ValueError, IndexError):
            # If parsing fails, start from 001
            return "WS-TASK-001"


# Import json for serialization
import json

