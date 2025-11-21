"""
Context Manager - Tracks which repo you're working in.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Work context tracking for WMS
DOMAIN: Cross-repo workspace management
"""

from pathlib import Path
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from workspace.db.models import WorkContext


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
        
        # Generate context ID
        context_id = f"ctx-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        context = WorkContext(
            id=context_id,
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
            f"{context.repo}\n{context.repo_path}\n{context.activated_at.isoformat()}\n{context.id}"
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
        'activated_at': lines[2] if len(lines) > 2 else None,
        'context_id': lines[3] if len(lines) > 3 else None
    }

