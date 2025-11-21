"""
Architecture Validator - Validates code files align with architecture components.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Enforce code-to-architecture alignment
DOMAIN: Cross-repo workspace management
"""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import json
import re

from workspace.db.models import (
    ArchitectureComponent,
    CodeComponentMapping,
    CodeChange,
    UnregisteredFile,
    Violation,
    WorkspaceTask,
)


class ArchitectureValidator:
    """Validates code files and changes align with architecture components."""
    
    def __init__(self, db_session: Session, workspace_root: Path):
        self.db = db_session
        self.workspace_root = workspace_root
    
    def validate_file_mapping(self, file_path: str, repo: str) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate if a file is mapped to an architecture component.
        
        Args:
            file_path: Path to file (relative to repo root)
            repo: Repository name
        
        Returns:
            Tuple of (is_mapped, component_id, violations)
        """
        violations = []
        
        # Check if file is mapped
        mapping = self.db.query(CodeComponentMapping).filter_by(
            file_path=file_path
        ).first()
        
        if not mapping:
            # Check if it's in unregistered files
            unregistered = self.db.query(UnregisteredFile).filter_by(
                file_path=file_path
            ).first()
            
            if not unregistered:
                # Generate unique ID using file_path hash (more unique than timestamp)
                file_hash = abs(hash(file_path)) % 100000
                timestamp_str = datetime.utcnow().strftime('%Y%m%d%H%M%S')
                unregistered_id = f"unreg-{timestamp_str}-{file_hash:05d}"
                
                # Check if ID already exists (unlikely but possible)
                existing = self.db.query(UnregisteredFile).filter_by(id=unregistered_id).first()
                if existing:
                    # Use a different ID with more entropy
                    import time
                    unregistered_id = f"unreg-{timestamp_str}-{file_hash:05d}-{int(time.time() * 1000000) % 100000}"
                
                # Add to unregistered files
                unregistered = UnregisteredFile(
                    id=unregistered_id,
                    file_path=file_path,
                    repo=repo,
                    status="unregistered",
                    first_detected=datetime.utcnow(),
                    last_seen=datetime.utcnow(),
                    detection_count=1
                )
                self.db.add(unregistered)
                self.db.commit()
            else:
                # Update existing unregistered file
                unregistered.last_seen = datetime.utcnow()
                unregistered.detection_count += 1
                self.db.commit()
            
            violations.append(f"File '{file_path}' is not mapped to any architecture component")
            return False, None, violations
        
        # File is mapped - validate against component
        component = mapping.component
        violations.extend(self._validate_file_scope(file_path, component))
        
        return True, component.id, violations
    
    def validate_changed_files(
        self,
        changed_files: List[str],
        repo: str,
        commit_hash: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Validate all changed files are mapped to components.
        
        Args:
            changed_files: List of file paths (relative to repo root)
            repo: Repository name
            commit_hash: Optional commit hash
        
        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'total_files': len(changed_files),
            'tracked_files': 0,
            'untracked_files': 0,
            'violations': [],
            'untracked_list': []
        }
        
        for file_path in changed_files:
            is_mapped, component_id, violations = self.validate_file_mapping(file_path, repo)
            
            if is_mapped:
                results['tracked_files'] += 1
            else:
                results['untracked_files'] += 1
                results['untracked_list'].append(file_path)
                results['valid'] = False
            
            if violations:
                results['violations'].extend(violations)
            
            # Track code change
            if commit_hash:
                self._track_code_change(file_path, repo, commit_hash, component_id, violations)
        
        return results
    
    def map_file_to_component(
        self,
        file_path: str,
        component_id: str,
        mapping_reason: str,
        mapping_type: str = "direct",
        created_by: str = "manual"
    ) -> CodeComponentMapping:
        """
        Map a file to an architecture component.
        
        Args:
            file_path: Path to file
            component_id: Component ID
            mapping_reason: Reason for mapping
            mapping_type: Type of mapping (direct, indirect, dependency)
            created_by: Who created the mapping
        
        Returns:
            CodeComponentMapping instance
        """
        # Check if already mapped
        existing = self.db.query(CodeComponentMapping).filter_by(
            file_path=file_path
        ).first()
        
        if existing:
            # Update existing mapping
            existing.component_id = component_id
            existing.mapping_reason = mapping_reason
            existing.mapping_type = mapping_type
            self.db.commit()
            return existing
        
        # Create new mapping
        mapping = CodeComponentMapping(
            id=f"mapping-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(file_path) % 10000}",
            file_path=file_path,
            component_id=component_id,
            mapping_type=mapping_type,
            mapping_reason=mapping_reason,
            is_validated=False,
            created_at=datetime.utcnow(),
            created_by=created_by
        )
        
        self.db.add(mapping)
        
        # Remove from unregistered if exists
        unregistered = self.db.query(UnregisteredFile).filter_by(
            file_path=file_path
        ).first()
        if unregistered:
            unregistered.status = "mapped"
            unregistered.assigned_component_id = component_id
            unregistered.reviewed_at = datetime.utcnow()
            unregistered.reviewed_by = created_by
        
        self.db.commit()
        return mapping
    
    def register_component(
        self,
        component_name: str,
        component_type: str,
        repo: str,
        expected_path: Optional[str] = None,
        description: Optional[str] = None,
        approved_scope: Optional[Dict] = None,
        boundaries: Optional[Dict] = None,
        registered_by: str = "manual"
    ) -> ArchitectureComponent:
        """
        Register a new architecture component.
        
        Args:
            component_name: Component name
            component_type: Component type (module, class, service, package)
            repo: Repository name
            expected_path: Expected file path
            description: Component description
            approved_scope: Approved scope (dict)
            boundaries: Boundaries (dict)
            registered_by: Who registered it
        
        Returns:
            ArchitectureComponent instance
        """
        # Check if already exists
        existing = self.db.query(ArchitectureComponent).filter_by(
            component_name=component_name,
            repo=repo
        ).first()
        
        if existing:
            # Update existing
            existing.component_type = component_type
            existing.expected_path = expected_path or existing.expected_path
            existing.description = description or existing.description
            existing.approved_scope = json.dumps(approved_scope) if approved_scope else existing.approved_scope
            existing.boundaries = json.dumps(boundaries) if boundaries else existing.boundaries
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing
        
        # Create new component
        component = ArchitectureComponent(
            id=f"comp-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(component_name) % 10000}",
            component_name=component_name,
            component_type=component_type,
            repo=repo,
            expected_path=expected_path,
            description=description,
            approved_scope=json.dumps(approved_scope) if approved_scope else None,
            boundaries=json.dumps(boundaries) if boundaries else None,
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            registered_by=registered_by
        )
        
        self.db.add(component)
        self.db.commit()
        return component
    
    def get_unregistered_files(self, repo: Optional[str] = None) -> List[UnregisteredFile]:
        """Get all unregistered files."""
        query = self.db.query(UnregisteredFile).filter_by(status="unregistered")
        if repo:
            query = query.filter_by(repo=repo)
        return query.all()
    
    def get_component_files(self, component_id: str) -> List[CodeComponentMapping]:
        """Get all files mapped to a component."""
        return self.db.query(CodeComponentMapping).filter_by(
            component_id=component_id
        ).all()
    
    def _validate_file_scope(self, file_path: str, component: ArchitectureComponent) -> List[str]:
        """Validate file is within component scope."""
        violations = []
        
        # Check boundaries if defined
        if component.boundaries:
            try:
                boundaries = json.loads(component.boundaries)
                # Simple validation - can be extended
                if 'forbidden_paths' in boundaries:
                    for forbidden in boundaries['forbidden_paths']:
                        if forbidden in file_path:
                            violations.append(f"File path violates component boundaries: {forbidden}")
            except:
                pass
        
        return violations
    
    def _track_code_change(
        self,
        file_path: str,
        repo: str,
        commit_hash: str,
        component_id: Optional[str],
        violations: List[str]
    ):
        """Track a code change."""
        # Check if change already tracked
        existing = self.db.query(CodeChange).filter_by(
            commit_hash=commit_hash,
            file_path=file_path
        ).first()
        
        if existing:
            return existing
        
        # Get mapping
        mapping = None
        if component_id:
            mapping = self.db.query(CodeComponentMapping).filter_by(
                file_path=file_path
            ).first()
        
        change = CodeChange(
            id=f"change-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{hash(file_path + commit_hash) % 10000}",
            commit_hash=commit_hash,
            repo=repo,
            change_type="modified",  # Default - should be determined from git
            file_path=file_path,
            component_id=component_id,
            mapping_id=mapping.id if mapping else None,
            is_tracked=component_id is not None,
            is_validated=False,
            validation_status="untracked" if not component_id else "pending",
            within_component_scope=len(violations) == 0,
            scope_violations=json.dumps(violations) if violations else None,
            changed_at=datetime.utcnow()
        )
        
        self.db.add(change)
        self.db.commit()
        return change
    
    def validate_task_files(self, task: WorkspaceTask) -> List[Violation]:
        """
        Validate files related to a task are mapped to components.
        
        Args:
            task: WorkspaceTask instance
        
        Returns:
            List of violations
        """
        violations = []
        
        # Get related files from task
        related_files = []
        if task.related_files:
            try:
                related_files = json.loads(task.related_files)
            except:
                pass
        
        if not related_files:
            return violations
        
        # Validate each file
        for file_path in related_files:
            is_mapped, component_id, file_violations = self.validate_file_mapping(
                file_path,
                task.assigned_repo or "unknown"
            )
            
            if not is_mapped:
                violations.append(Violation(
                    id=f"viol-{task.id}-file-{len(violations)+1}",
                    task_id=task.id,
                    violation_type="unmapped_file",
                    severity="HIGH",
                    message=f"File '{file_path}' is not mapped to any architecture component",
                    rule_violated="Code-to-architecture mapping requirement",
                    fix_required=f"Map file to component: python workspace/wms/cli.py map-file {file_path} <component_id>"
                ))
            
            if file_violations:
                for v in file_violations:
                    violations.append(Violation(
                        id=f"viol-{task.id}-scope-{len(violations)+1}",
                        task_id=task.id,
                        violation_type="scope_violation",
                        severity="MEDIUM",
                        message=v,
                        rule_violated="Component scope boundaries",
                        fix_required="Review component boundaries and move file if needed"
                    ))
        
        return violations

