#!/usr/bin/env python3
"""
REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Migrate existing JSON files to workspace database
DOMAIN: Cross-repo workspace management

Migration script to import existing JSON tracking files into database.

Usage:
    python workspace/scripts/migrate_json_to_db.py
"""

import sys
from pathlib import Path

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.db.migration import migrate_json_to_database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main migration function."""
    print("=" * 70)
    print("  WORKSPACE DATABASE MIGRATION")
    print("=" * 70)
    print()
    
    workspace_root = Path.cwd()
    print(f"Workspace root: {workspace_root}")
    print()
    
    # Initialize database
    print("Initializing workspace database...")
    db = WorkspaceDB(workspace_root=workspace_root)
    print(f"✅ Database initialized: {db.db_path}")
    print()
    
    # Migrate JSON files
    print("Migrating JSON files to database...")
    counts = migrate_json_to_database(workspace_root=workspace_root, db=db)
    
    print()
    print("=" * 70)
    print("  MIGRATION SUMMARY")
    print("=" * 70)
    print()
    print(f"✅ Tasks migrated:     {counts.get('tasks', 0)}")
    print(f"✅ Sessions migrated:  {counts.get('sessions', 0)}")
    print(f"✅ Issues migrated:    {counts.get('issues', 0)}")
    print(f"✅ Decisions migrated: {counts.get('decisions', 0)}")
    print()
    
    # Show statistics
    print("Database statistics:")
    task_stats = db.get_task_statistics()
    issue_stats = db.get_issue_statistics()
    
    print(f"  Tasks: {task_stats['total']} total ({task_stats['pending']} pending, {task_stats['in_progress']} in progress)")
    print(f"  Issues: {issue_stats['total']} total ({issue_stats['open']} open, {issue_stats['high']} high severity)")
    print()
    
    print("✅ Migration complete!")
    print()
    print("You can now use the workspace database instead of JSON files.")
    print("JSON files can be kept as backups/exports.")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        sys.exit(1)

