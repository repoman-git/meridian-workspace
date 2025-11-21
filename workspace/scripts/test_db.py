#!/usr/bin/env python3
"""
Test script for workspace database.

Usage:
    python workspace/scripts/test_db.py
"""

import sys
from pathlib import Path

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB


def main():
    """Test workspace database."""
    print("=" * 70)
    print("  WORKSPACE DATABASE TEST")
    print("=" * 70)
    print()
    
    workspace_root = Path.cwd()
    db_path = workspace_root / "workspace.db"
    
    # Initialize database
    print(f"1. Initializing database: {db_path}")
    db = WorkspaceDB(workspace_root=workspace_root)
    print("   ✅ Database initialized")
    print()
    
    # Test adding a task
    print("2. Testing task creation...")
    task = db.add_task(
        task_id="WS-TEST-001",
        title="Test Task",
        status="pending",
        priority="HIGH",
        repos_affected=["meridian-core"],
        description="Test task for database",
    )
    print(f"   ✅ Task created: {task.id} - {task.title}")
    print()
    
    # Test getting tasks
    print("3. Testing task retrieval...")
    tasks = db.get_tasks(status="pending", limit=5)
    print(f"   ✅ Found {len(tasks)} pending task(s)")
    for t in tasks:
        print(f"      - {t.id}: {t.title} ({t.status})")
    print()
    
    # Test statistics
    print("4. Testing statistics...")
    task_stats = db.get_task_statistics()
    print(f"   ✅ Task statistics:")
    print(f"      Total: {task_stats['total']}")
    print(f"      Pending: {task_stats['pending']}")
    print(f"      In Progress: {task_stats['in_progress']}")
    print()
    
    # Test JSON export
    print("5. Testing JSON export...")
    export_data = db.export_to_json()
    print(f"   ✅ JSON export: {len(export_data.get('tasks', []))} tasks, {len(export_data.get('issues', []))} issues")
    print()
    
    print("=" * 70)
    print("  ✅ ALL TESTS PASSED")
    print("=" * 70)
    print()
    print(f"Database location: {db_path}")
    print("You can now use the workspace database for tracking!")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

