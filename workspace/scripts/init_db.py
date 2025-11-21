#!/usr/bin/env python3
"""
Initialize workspace database.

Usage:
    python workspace/scripts/init_db.py
"""

import sys
from pathlib import Path

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from sqlalchemy import inspect


def check_database_status(db: WorkspaceDB) -> dict:
    """Check database status and return information."""
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    status = {
        "exists": Path(db.db_path).exists(),
        "path": db.db_path,
        "tables": tables,
        "table_count": len(tables),
    }
    
    # Get row counts for each table
    status["row_counts"] = {}
    with db._get_session() as session:
        from sqlalchemy import text
        for table in tables:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                status["row_counts"][table] = count
            except Exception as e:
                status["row_counts"][table] = f"Error: {e}"
    
    return status


def main():
    """Initialize and verify workspace database."""
    print("=" * 70)
    print("  WORKSPACE DATABASE INITIALIZATION")
    print("=" * 70)
    print()
    
    workspace_root = Path.cwd()
    db_path = workspace_root / "workspace.db"
    
    # Initialize database
    print(f"1. Initializing database: {db_path}")
    try:
        db = WorkspaceDB(workspace_root=workspace_root)
        print("   ✅ Database initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize database: {e}")
        return 1
    print()
    
    # Check database status
    print("2. Checking database status...")
    try:
        status = check_database_status(db)
        print(f"   ✅ Database file exists: {status['exists']}")
        print(f"   ✅ Database path: {status['path']}")
        print(f"   ✅ Tables created: {status['table_count']}")
        print(f"   ✅ Tables: {', '.join(status['tables'])}")
        print()
        
        # Show row counts
        print("   Table row counts:")
        for table, count in status['row_counts'].items():
            if isinstance(count, int):
                print(f"      • {table}: {count} rows")
            else:
                print(f"      • {table}: {count}")
        print()
    except Exception as e:
        print(f"   ❌ Failed to check status: {e}")
        return 1
    
    # Get task statistics
    print("3. Checking task statistics...")
    try:
        stats = db.get_task_statistics()
        print(f"   ✅ Task statistics:")
        print(f"      Total: {stats['total']}")
        print(f"      Pending: {stats['pending']}")
        print(f"      In Progress: {stats['in_progress']}")
        print(f"      Completed: {stats['completed']}")
        print(f"      Blocked: {stats.get('blocked', 0)}")
        print()
    except Exception as e:
        print(f"   ⚠️  Could not get task statistics: {e}")
        print()
    
    # Test database operations
    print("4. Testing database operations...")
    try:
        # Test query
        with db._get_session() as session:
            from workspace.db.models import WorkspaceTask
            tasks = session.query(WorkspaceTask).limit(3).all()
            print(f"   ✅ Query test: Found {len(tasks)} task(s)")
            if tasks:
                print(f"      Sample tasks:")
                for task in tasks[:3]:
                    print(f"         • {task.id}: {task.title} ({task.status})")
        print()
    except Exception as e:
        print(f"   ❌ Query test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Verify schema
    print("5. Verifying database schema...")
    expected_tables = [
        'workspace_tasks',
        'workspace_sessions',
        'cross_repo_issues',
        'architecture_decisions',
        'architecture_states',
        'component_placements',
        'drift_detections',
        'context_switches',
    ]
    
    missing_tables = [t for t in expected_tables if t not in status['tables']]
    if missing_tables:
        print(f"   ⚠️  Missing tables: {', '.join(missing_tables)}")
        print("   The database schema may need to be updated.")
    else:
        print(f"   ✅ All expected tables present ({len(expected_tables)} tables)")
    print()
    
    print("=" * 70)
    print("  ✅ DATABASE INITIALIZATION COMPLETE")
    print("=" * 70)
    print()
    print(f"Database location: {db_path}")
    print("Database is ready to use!")
    print()
    print("Next steps:")
    print("  1. Migrate existing JSON data: python workspace/scripts/migrate_json_to_db.py")
    print("  2. Use database in code: from workspace.db import WorkspaceDB")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

