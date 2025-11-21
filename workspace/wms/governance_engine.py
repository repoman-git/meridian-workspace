"""
Governance Engine - Enforces architectural rules.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Architecture enforcement for WMS
DOMAIN: Cross-repo workspace management
"""

from pathlib import Path
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from workspace.db.models import (
    ArchitectureDecision,
    ComponentPlacement,
    ImportRule,
    Violation,
    WorkspaceTask,
)
from workspace.wms.architecture_validator import ArchitectureValidator
from pathlib import Path


class GovernanceEngine:
    """Enforces architectural decisions and rules."""
    
    def __init__(self, db_session: Session, workspace_root: Optional[Path] = None):
        self.db = db_session
        self.workspace_root = workspace_root or Path.cwd()
        self.architecture_validator = ArchitectureValidator(db_session, self.workspace_root)
    
    def validate_task_placement(self, task: WorkspaceTask, proposed_repo: str) -> List[Violation]:
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
                    id=f"viol-{task.id}-{len(violations)+1}",
                    task_id=task.id,
                    violation_type="component_placement",
                    severity="CRITICAL",
                    message=f"Component belongs in {rule.correct_repo}, not {proposed_repo}",
                    rule_violated=f"Component placement: {rule.component_name}",
                    fix_required=f"Move to {rule.correct_repo}/{rule.correct_location}"
                ))
        
        return violations
    
    def validate_scale_appropriateness(
        self,
        task: WorkspaceTask,
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
                        id=f"viol-{task.id}-scale-{len(violations)+1}",
                        task_id=task.id,
                        violation_type="over_engineering",
                        severity="HIGH",
                        message=f"Over-engineering: {keyword} for {actual_users} user(s)",
                        rule_violated="Start Small, Scale Smart principle",
                        fix_required=f"Use Tier 1 solution for {actual_users} users"
                    ))
        
        return violations
    
    def determine_correct_repo(self, task_description: str) -> Optional[str]:
        """
        Determine which repo task belongs in based on ADRs.
        
        Args:
            task_description: Task description
        
        Returns:
            Repo name where task should be implemented, or None if unclear
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
    
    def _get_placement_rules(self) -> List[ComponentPlacement]:
        """Get all component placement rules."""
        return self.db.query(ComponentPlacement).all()
    
    def _violates_placement(
        self,
        task: WorkspaceTask,
        repo: str,
        rule: ComponentPlacement
    ) -> bool:
        """Check if task violates placement rule."""
        # Check if task mentions the component type
        task_text = (task.title + " " + (task.description or "")).lower()
        if rule.component_name.lower() in task_text:
            # Check if repo is not the required one
            if rule.correct_repo and repo != rule.correct_repo:
                return True
        
        return False
    
    def validate_task_files(self, task: WorkspaceTask) -> List[Violation]:
        """
        Validate files related to a task are mapped to architecture components.
        
        Args:
            task: Task to validate
        
        Returns:
            List of violations
        """
        return self.architecture_validator.validate_task_files(task)
    
    def validate_file_alignment(self, file_path: str, repo: str) -> Tuple[bool, List[str]]:
        """
        Validate a file is aligned with architecture components.
        
        Args:
            file_path: Path to file
            repo: Repository name
        
        Returns:
            Tuple of (is_aligned, violations)
        """
        is_mapped, component_id, violations = self.architecture_validator.validate_file_mapping(file_path, repo)
        return is_mapped, violations

