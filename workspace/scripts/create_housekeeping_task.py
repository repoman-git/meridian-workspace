#!/usr/bin/env python3
"""
Create weekly housekeeping task in WMS.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Create recurring housekeeping task
DOMAIN: Cross-repo workspace management
"""

import sys
from pathlib import Path
from datetime import datetime

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.governance_engine import GovernanceEngine
from workspace.wms.bastard_integration import BastardIntegration
from workspace.wms.workflow_engine import WorkflowEngine


def main():
    """Create weekly housekeeping task."""
    workspace_root = Path.cwd()
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        # Initialize WMS components
        governance = GovernanceEngine(session, workspace_root=workspace_root)
        bastard = BastardIntegration(session, workspace_root / "workspace" / "skills")
        workflow = WorkflowEngine(session, governance, bastard, workspace_root=workspace_root)
        
        # Check if task already exists
        from workspace.db.models import WorkspaceTask
        existing = session.query(WorkspaceTask).filter_by(
            title="Weekly workspace and repository housekeeping"
        ).first()
        
        if existing:
            print(f"✅ Housekeeping task already exists: {existing.id}")
            print(f"   Status: {existing.status}")
            return 0
        
        # Create housekeeping task
        task = workflow.create_task(
            title="Weekly workspace and repository housekeeping",
            description="""Weekly maintenance and cleanup tasks for workspace and repositories.

This task runs weekly to:
1. Clean up old/unused files and sessions
2. Check for orphaned files and stale tasks
3. Validate database integrity
4. Check for unregistered files
5. Validate architecture mappings
6. Clean temporary files and old logs
7. Check for duplicate files

Run with: python workspace/scripts/housekeeping.py

Frequency: Weekly (every Monday recommended)""",
            actual_users=1,
            proposed_solution="Automated housekeeping script that performs maintenance tasks",
            priority="medium"
        )
        
        # Mark as recurring
        task.notes = "Recurring weekly task. Run: python workspace/scripts/housekeeping.py"
        task.related_files = '["workspace/scripts/housekeeping.py"]'
        task.session_created = "housekeeping-setup"
        
        session.commit()
        
        print("✅ Created weekly housekeeping task:")
        print(f"   ID: {task.id}")
        print(f"   Title: {task.title}")
        print(f"   Status: {task.status}")
        print()
        print("To run housekeeping:")
        print("   python workspace/scripts/housekeeping.py")
        print()
        print("To schedule weekly (cron example):")
        print("   0 9 * * 1 cd /Users/simonerses/data-projects && python workspace/scripts/housekeeping.py")
        print("   (Runs every Monday at 9 AM)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())

