#!/usr/bin/env python3
"""
Quick database status check.

Usage:
    python workspace/scripts/db_status.py
"""

import sys
from pathlib import Path

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.db.models import WorkspaceTask, ArchitectureDecision, CrossRepoIssue


def main():
    """Show database status."""
    db = WorkspaceDB(workspace_root=Path.cwd())
    
    db_path = Path(db.db_path)
    db_size_kb = db_path.stat().st_size / 1024 if db_path.exists() else 0
    
    print("📊 WORKSPACE DATABASE STATUS")
    print("=" * 70)
    print()
    print(f"Database Path: {db.db_path}")
    print(f"Database Size: {db_size_kb:.2f} KB")
    print()
    
    # Get statistics
    stats = db.get_task_statistics()
    print("📋 TASK STATISTICS")
    print(f"   Total: {stats['total']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   In Progress: {stats['in_progress']}")
    print(f"   Completed: {stats['completed']}")
    print(f"   Blocked: {stats.get('blocked', 0)}")
    print()
    
    # Get recent tasks
    with db._get_session() as session:
        tasks = session.query(WorkspaceTask).order_by(WorkspaceTask.created.desc()).limit(5).all()
        if tasks:
            print("📋 RECENT TASKS")
            for task in tasks:
                print(f"   • {task.id}: {task.title}")
                print(f"     Status: {task.status} | Priority: {task.priority or 'N/A'}")
            print()
        
        # Get architecture decisions
        decisions = session.query(ArchitectureDecision).count()
        print(f"🏗️  ARCHITECTURE DECISIONS: {decisions}")
        print()
        
        # Get issues
        issues = session.query(CrossRepoIssue).count()
        print(f"⚠️  CROSS-REPO ISSUES: {issues}")
        print()
    
    print("=" * 70)
    print("✅ Database is operational and ready to use!")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

