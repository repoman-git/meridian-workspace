"""
The Bastard Integration - Validates tasks and implementations (mocked initially).

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Task validation via The Bastard for WMS
DOMAIN: Cross-repo workspace management
"""

from typing import Dict, Optional
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime

from workspace.db.models import WorkspaceTask, BastardReport


class BastardIntegration:
    """Integration with The Bastard evaluation skill (mocked initially)."""
    
    def __init__(self, db_session: Session, skills_dir: Optional[Path] = None):
        self.db = db_session
        self.skills_dir = skills_dir or Path(__file__).parent.parent / "skills"
    
    def evaluate_plan(
        self,
        task: WorkspaceTask,
        actual_users: int,
        proposed_solution: str
    ) -> BastardReport:
        """
        Evaluate task plan with The Bastard (mocked initially).
        
        Args:
            task: Task to evaluate
            actual_users: Actual user count TODAY
            proposed_solution: Proposed implementation approach
        
        Returns:
            BastardReport with evaluation results
        """
        # TODO: Implement actual Meridian orchestration call
        # For now, return placeholder report
        
        # Build evaluation prompt
        prompt = self._build_plan_evaluation_prompt(
            task, actual_users, proposed_solution
        )
        
        # Call The Bastard (mocked for now)
        verdict = self._call_bastard_mocked(prompt, actual_users, proposed_solution)
        
        # Parse verdict
        report = self._parse_bastard_verdict(verdict, task, "plan", actual_users)
        
        # Save to database
        self.db.add(report)
        self.db.commit()
        
        # Update task with grade
        task.bastard_plan_grade = report.overall_grade
        self.db.commit()
        
        return report
    
    def evaluate_completion(self, task: WorkspaceTask) -> BastardReport:
        """
        Evaluate completed task with The Bastard (mocked initially).
        
        Args:
            task: Completed task to evaluate
        
        Returns:
            BastardReport with evaluation results
        """
        # TODO: Implement actual Meridian orchestration call
        # For now, return placeholder report
        
        # Build evaluation prompt
        prompt = self._build_completion_evaluation_prompt(task)
        
        # Call The Bastard (mocked)
        verdict = self._call_bastard_mocked(prompt, 1, "completed")
        
        # Parse verdict
        report = self._parse_bastard_verdict(verdict, task, "completion", 1)
        
        # Save to database
        self.db.add(report)
        self.db.commit()
        
        # Update task with grade
        task.bastard_completion_grade = report.overall_grade
        self.db.commit()
        
        return report
    
    def _build_plan_evaluation_prompt(
        self,
        task: WorkspaceTask,
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
    
    def _build_completion_evaluation_prompt(self, task: WorkspaceTask) -> str:
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
    
    def _call_bastard_mocked(self, prompt: str, actual_users: int, solution: str) -> str:
        """
        Call The Bastard via Meridian orchestration (MOCKED).
        
        In real implementation, this would:
        1. Import Meridian Core
        2. Load evaluation-bastard skill
        3. Execute with orchestrator
        4. Return verdict
        
        For now, returns placeholder verdict.
        """
        # Mock evaluation - check for over-engineering keywords
        over_engineering_keywords = ["kubernetes", "vault", "microservices"]
        solution_lower = solution.lower()
        
        if any(kw in solution_lower for kw in over_engineering_keywords) and actual_users <= 5:
            return f"""
OVER_ENGINEERED

You're building for 1000 users when you have {actual_users}.
Critical blockers: ['Over-engineering detected']
Required fixes: ['Use Tier 1 solution for {actual_users} users']
"""
        
        # Default: B grade (acceptable)
        return f"""
B

Scale Appropriateness: B
Deployment Maturity: B
Portability: B

No critical blockers. Proceed with caution.
"""
    
    def _parse_bastard_verdict(
        self,
        verdict: str,
        task: WorkspaceTask,
        evaluation_type: str,
        actual_users: int
    ) -> BastardReport:
        """Parse The Bastard's verdict into structured report."""
        # Simple parsing for mocked verdicts
        verdict_lower = verdict.lower()
        
        # Determine grade
        if "over_engineered" in verdict_lower:
            overall_grade = "OVER_ENGINEERED"
        elif "f" in verdict_lower and "grade" in verdict_lower:
            overall_grade = "F"
        elif "b" in verdict_lower:
            overall_grade = "B"
        else:
            overall_grade = "B"  # Default
        
        report_id = f"bastard-{task.id}-{evaluation_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        report = BastardReport(
            id=report_id,
            task_id=task.id,
            evaluation_type=evaluation_type,
            overall_grade=overall_grade,
            scale_appropriateness="B",
            deployment_maturity="B",
            portability="B",
            state_management="B",
            credential_management="B",
            actual_users=actual_users,
            designed_for_users=actual_users,
            over_engineering_score=3 if overall_grade == "B" else 8,
            tier_recommendation=1,
            critical_blockers='[]',
            required_fixes='[]',
            full_report=verdict
        )
        
        return report

