#!/usr/bin/env python3
"""
Workspace and Repository Housekeeping Script

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Weekly maintenance and cleanup tasks
DOMAIN: Cross-repo workspace management

This script performs weekly housekeeping:
- Clean up old/unused files
- Check for orphaned files
- Validate database integrity
- Check for unregistered files
- Clean up old sessions/logs
- Check for duplicate files
- Validate architecture mappings
- Check for stale tasks
- Clean up temporary files
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json
import shutil

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.architecture_validator import ArchitectureValidator
from workspace.db.models import (
    WorkspaceTask,
    WorkspaceSession,
    UnregisteredFile,
    CodeComponentMapping,
    ArchitectureComponent,
    CrossRepoIssue,
)


class Housekeeping:
    """Workspace housekeeping operations."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.db = WorkspaceDB(workspace_root=workspace_root)
        self.session = self.db._get_session()
        self.validator = ArchitectureValidator(self.session, workspace_root)
        self.report = {
            'timestamp': datetime.utcnow().isoformat(),
            'tasks_completed': [],
            'issues_found': [],
            'files_cleaned': [],
            'warnings': [],
            'errors': []
        }
    
    def run_all(self) -> Dict:
        """Run all housekeeping tasks."""
        print("=" * 70)
        print("  WORKSPACE HOUSEKEEPING")
        print("=" * 70)
        print()
        print(f"Workspace: {self.workspace_root}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # 1. Clean old sessions
            self.clean_old_sessions()
            
            # 2. Check for stale tasks
            self.check_stale_tasks()
            
            # 3. Find unregistered files
            self.check_unregistered_files()
            
            # 4. Validate architecture mappings
            self.validate_architecture_mappings()
            
            # 5. Clean temporary files
            self.clean_temp_files()
            
            # 6. Check for orphaned files
            self.check_orphaned_files()
            
            # 7. Validate database integrity
            self.validate_database_integrity()
            
            # 8. Clean old logs
            self.clean_old_logs()
            
            # 9. Check for duplicate files
            self.check_duplicate_files()
            
            # 10. Generate report
            self.generate_report()
            
            return self.report
            
        finally:
            self.session.close()
    
    def clean_old_sessions(self, days_old: int = 30):
        """Clean up old completed sessions."""
        print("1. Cleaning old sessions...")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_sessions = self.session.query(WorkspaceSession).filter(
            WorkspaceSession.status == 'completed',
            WorkspaceSession.end_time < cutoff_date
        ).all()
        
        count = len(old_sessions)
        if count > 0:
            for session in old_sessions:
                self.session.delete(session)
            self.session.commit()
            self.report['tasks_completed'].append(f"Cleaned {count} old session(s) (> {days_old} days)")
            print(f"   ✅ Cleaned {count} old session(s)")
        else:
            print(f"   ℹ️  No old sessions to clean")
        print()
    
    def check_stale_tasks(self, days_inactive: int = 90):
        """Check for stale tasks (inactive for a long time)."""
        print("2. Checking for stale tasks...")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        stale_tasks = self.session.query(WorkspaceTask).filter(
            WorkspaceTask.status.in_(['pending', 'in_progress']),
            WorkspaceTask.created < cutoff_date
        ).all()
        
        if stale_tasks:
            self.report['warnings'].append(f"Found {len(stale_tasks)} stale task(s) (> {days_inactive} days inactive)")
            print(f"   ⚠️  Found {len(stale_tasks)} stale task(s):")
            for task in stale_tasks[:10]:
                print(f"      • {task.id}: {task.title[:60]}... ({task.status})")
            if len(stale_tasks) > 10:
                print(f"      ... and {len(stale_tasks) - 10} more")
        else:
            print(f"   ✅ No stale tasks found")
        print()
    
    def check_unregistered_files(self):
        """Check for unregistered files across repos."""
        print("3. Checking for unregistered files...")
        
        repos = ['meridian-core', 'meridian-trading', 'meridian-research', 'workspace']
        total_unregistered = 0
        
        for repo in repos:
            repo_path = self.workspace_root / repo
            if not repo_path.exists():
                continue
            
            unregistered = self.validator.get_unregistered_files(repo=repo)
            count = len(unregistered)
            total_unregistered += count
            
            if count > 0:
                self.report['warnings'].append(f"Found {count} unregistered file(s) in {repo}")
                print(f"   ⚠️  {repo}: {count} unregistered file(s)")
                for uf in unregistered[:5]:
                    print(f"      • {uf.file_path}")
                if count > 5:
                    print(f"      ... and {count - 5} more")
        
        if total_unregistered == 0:
            print(f"   ✅ No unregistered files found")
        else:
            print(f"   ⚠️  Total: {total_unregistered} unregistered file(s) across all repos")
        print()
    
    def validate_architecture_mappings(self):
        """Validate architecture component mappings."""
        print("4. Validating architecture mappings...")
        
        # Check for components without any files
        components = self.session.query(ArchitectureComponent).filter_by(
            status='active'
        ).all()
        
        orphaned_components = []
        for component in components:
            mappings = self.validator.get_component_files(component.id)
            if not mappings:
                orphaned_components.append(component)
        
        if orphaned_components:
            self.report['warnings'].append(f"Found {len(orphaned_components)} component(s) without mapped files")
            print(f"   ⚠️  Found {len(orphaned_components)} component(s) without files:")
            for comp in orphaned_components[:5]:
                print(f"      • {comp.component_name} ({comp.repo})")
        else:
            print(f"   ✅ All components have mapped files")
        
        # Check for mappings to non-existent components
        invalid_mappings = self.session.query(CodeComponentMapping).filter(
            ~CodeComponentMapping.component_id.in_(
                self.session.query(ArchitectureComponent.id)
            )
        ).all()
        
        if invalid_mappings:
            self.report['issues_found'].append(f"Found {len(invalid_mappings)} mapping(s) to non-existent components")
            print(f"   ❌ Found {len(invalid_mappings)} invalid mapping(s)")
            for mapping in invalid_mappings[:5]:
                print(f"      • {mapping.file_path} → {mapping.component_id} (component not found)")
        else:
            print(f"   ✅ All mappings are valid")
        print()
    
    def clean_temp_files(self, days_old: int = 7):
        """Clean temporary files."""
        print("5. Cleaning temporary files...")
        
        temp_patterns = ['*.tmp', '*.bak', '*.swp', '*.pyc', '__pycache__', '*.log']
        temp_dirs = ['.pytest_cache', '.mypy_cache', '.ruff_cache']
        
        cleaned = []
        for pattern in temp_patterns:
            for path in self.workspace_root.rglob(pattern):
                if path.is_file():
                    try:
                        if path.stat().st_mtime < (datetime.now().timestamp() - days_old * 86400):
                            path.unlink()
                            cleaned.append(str(path.relative_to(self.workspace_root)))
                    except:
                        pass
        
        for dir_pattern in temp_dirs:
            for path in self.workspace_root.rglob(dir_pattern):
                if path.is_dir():
                    try:
                        shutil.rmtree(path)
                        cleaned.append(str(path.relative_to(self.workspace_root)))
                    except:
                        pass
        
        if cleaned:
            self.report['files_cleaned'].extend(cleaned)
            self.report['tasks_completed'].append(f"Cleaned {len(cleaned)} temporary file(s)/dir(s)")
            print(f"   ✅ Cleaned {len(cleaned)} temporary file(s)/dir(s)")
        else:
            print(f"   ℹ️  No temporary files to clean")
        print()
    
    def check_orphaned_files(self):
        """Check for orphaned files (referenced but don't exist)."""
        print("6. Checking for orphaned file references...")
        
        # Check task-related files
        tasks = self.session.query(WorkspaceTask).filter(
            WorkspaceTask.related_files.isnot(None)
        ).all()
        
        orphaned_refs = []
        for task in tasks:
            try:
                files = json.loads(task.related_files) if task.related_files else []
                for file_path in files:
                    full_path = self.workspace_root / file_path
                    if not full_path.exists():
                        orphaned_refs.append((task.id, file_path))
            except:
                pass
        
        if orphaned_refs:
            self.report['warnings'].append(f"Found {len(orphaned_refs)} orphaned file reference(s)")
            print(f"   ⚠️  Found {len(orphaned_refs)} orphaned file reference(s):")
            for task_id, file_path in orphaned_refs[:5]:
                print(f"      • Task {task_id}: {file_path}")
        else:
            print(f"   ✅ No orphaned file references")
        print()
    
    def validate_database_integrity(self):
        """Validate database integrity."""
        print("7. Validating database integrity...")
        
        issues = []
        
        # Check for tasks without valid repos
        tasks = self.session.query(WorkspaceTask).filter(
            WorkspaceTask.assigned_repo.isnot(None)
        ).all()
        
        valid_repos = ['meridian-core', 'meridian-trading', 'meridian-research', 'workspace']
        invalid_repos = []
        for task in tasks:
            if task.assigned_repo and task.assigned_repo not in valid_repos:
                invalid_repos.append(task.id)
        
        if invalid_repos:
            issues.append(f"Found {len(invalid_repos)} task(s) with invalid repo assignments")
            print(f"   ⚠️  Found {len(invalid_repos)} task(s) with invalid repos")
        
        # Check for sessions without end time but marked completed
        incomplete_sessions = self.session.query(WorkspaceSession).filter(
            WorkspaceSession.status == 'completed',
            WorkspaceSession.end_time.is_(None)
        ).count()
        
        if incomplete_sessions > 0:
            issues.append(f"Found {incomplete_sessions} completed session(s) without end time")
            print(f"   ⚠️  Found {incomplete_sessions} incomplete session record(s)")
        
        if not issues:
            print(f"   ✅ Database integrity OK")
        else:
            self.report['issues_found'].extend(issues)
        print()
    
    def clean_old_logs(self, days_old: int = 30):
        """Clean old log files."""
        print("8. Cleaning old log files...")
        
        log_dirs = ['logs', '*.log']
        cleaned = []
        
        for log_dir in log_dirs:
            for path in self.workspace_root.rglob(log_dir):
                if path.is_file():
                    try:
                        if path.stat().st_mtime < (datetime.now().timestamp() - days_old * 86400):
                            path.unlink()
                            cleaned.append(str(path.relative_to(self.workspace_root)))
                    except:
                        pass
        
        if cleaned:
            self.report['files_cleaned'].extend(cleaned)
            self.report['tasks_completed'].append(f"Cleaned {len(cleaned)} old log file(s)")
            print(f"   ✅ Cleaned {len(cleaned)} old log file(s)")
        else:
            print(f"   ℹ️  No old log files to clean")
        print()
    
    def check_duplicate_files(self):
        """Check for duplicate files (same name in multiple locations)."""
        print("9. Checking for duplicate files...")
        
        # Simple check: files with same name in different repos
        file_names = {}
        repos = ['meridian-core', 'meridian-trading', 'meridian-research']
        
        for repo in repos:
            repo_path = self.workspace_root / repo
            if not repo_path.exists():
                continue
            
            for py_file in repo_path.rglob('*.py'):
                name = py_file.name
                if name not in file_names:
                    file_names[name] = []
                file_names[name].append(str(py_file.relative_to(self.workspace_root)))
        
        duplicates = {name: paths for name, paths in file_names.items() if len(paths) > 1}
        
        if duplicates:
            count = sum(len(paths) - 1 for paths in duplicates.values())
            self.report['warnings'].append(f"Found {len(duplicates)} duplicate file name(s) ({count} potential duplicates)")
            print(f"   ⚠️  Found {len(duplicates)} duplicate file name(s):")
            for name, paths in list(duplicates.items())[:5]:
                print(f"      • {name}: {len(paths)} locations")
        else:
            print(f"   ✅ No duplicate file names found")
        print()
    
    def generate_report(self):
        """Generate housekeeping report."""
        print("=" * 70)
        print("  HOUSEKEEPING SUMMARY")
        print("=" * 70)
        print()
        
        print(f"✅ Tasks completed: {len(self.report['tasks_completed'])}")
        for task in self.report['tasks_completed']:
            print(f"   • {task}")
        print()
        
        if self.report['warnings']:
            print(f"⚠️  Warnings: {len(self.report['warnings'])}")
            for warning in self.report['warnings']:
                print(f"   • {warning}")
            print()
        
        if self.report['issues_found']:
            print(f"❌ Issues found: {len(self.report['issues_found'])}")
            for issue in self.report['issues_found']:
                print(f"   • {issue}")
            print()
        
        if self.report['files_cleaned']:
            print(f"🧹 Files cleaned: {len(self.report['files_cleaned'])}")
            print()
        
        # Save report
        report_file = self.workspace_root / "workspace" / "reports" / f"housekeeping-{datetime.now().strftime('%Y%m%d')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(self.report, indent=2))
        
        print(f"📄 Report saved: {report_file.relative_to(self.workspace_root)}")
        print()
        print("=" * 70)


def main():
    """Run housekeeping."""
    workspace_root = Path.cwd()
    
    housekeeping = Housekeeping(workspace_root)
    report = housekeeping.run_all()
    
    # Exit with error code if issues found
    if report['errors']:
        return 1
    if report['issues_found']:
        return 2
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Housekeeping cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

