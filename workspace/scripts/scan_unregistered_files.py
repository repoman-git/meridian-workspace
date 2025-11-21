#!/usr/bin/env python3
"""
Scan repositories for unregistered files.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Scan repos for code files and detect unregistered/mapped files
DOMAIN: Cross-repo workspace management

Usage:
    python workspace/scripts/scan_unregistered_files.py [--repo REPO] [--dry-run]
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
import argparse
from collections import defaultdict

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.architecture_validator import ArchitectureValidator
from workspace.db.models import CodeComponentMapping


# Repositories to scan
REPOSITORIES = {
    'meridian-core': ['src', 'tests'],
    'meridian-research': ['src', 'tests'],
    'meridian-trading': ['src', 'tests'],
    'workspace': ['wms', 'db', 'scripts'],
}

# File extensions to scan
CODE_EXTENSIONS = {'.py', '.md', '.yaml', '.yml', '.json'}

# Directories to ignore
IGNORE_DIRS = {
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    'node_modules',
    '.git',
    'venv',
    'env',
    '.venv',
    'build',
    'dist',
    '*.egg-info',
    'site-packages',
}


def should_scan_file(file_path: Path, repo_path: Path) -> bool:
    """Check if a file should be scanned."""
    # Check extension
    if file_path.suffix not in CODE_EXTENSIONS:
        return False
    
    # Check if in ignore directory
    relative = file_path.relative_to(repo_path)
    parts = relative.parts
    
    for ignore_dir in IGNORE_DIRS:
        if ignore_dir in parts:
            return False
    
    # Ignore hidden files (but allow .env, .gitignore, etc.)
    if parts[-1].startswith('.') and parts[-1] not in ['.env', '.gitignore', '.python-version']:
        return False
    
    return True


def get_repo_files(repo_path: Path, subdirs: List[str] = None) -> List[Tuple[Path, str]]:
    """
    Get all code files from a repository.
    
    Args:
        repo_path: Path to repository root
        subdirs: List of subdirectories to scan (defaults to all)
    
    Returns:
        List of (file_path, relative_path) tuples
    """
    files = []
    
    if not repo_path.exists():
        return files
    
    # If subdirs specified, scan only those
    if subdirs:
        scan_dirs = [repo_path / subdir for subdir in subdirs if (repo_path / subdir).exists()]
    else:
        # Scan all subdirectories except ignored ones
        scan_dirs = [d for d in repo_path.iterdir() 
                    if d.is_dir() and d.name not in IGNORE_DIRS and not d.name.startswith('.')]
    
    for scan_dir in scan_dirs:
        for file_path in scan_dir.rglob('*'):
            if file_path.is_file() and should_scan_file(file_path, repo_path):
                try:
                    relative = file_path.relative_to(repo_path)
                    files.append((file_path, str(relative)))
                except ValueError:
                    # File outside repo, skip
                    pass
    
    return files


def scan_repo(
    repo_name: str,
    repo_path: Path,
    validator: ArchitectureValidator,
    db_session,
    dry_run: bool = False
) -> Dict[str, any]:
    """
    Scan a repository for unregistered files.
    
    Args:
        repo_name: Repository name
        repo_path: Path to repository
        validator: ArchitectureValidator instance
        db_session: Database session
        dry_run: If True, don't update database
    
    Returns:
        Dictionary with scan results
    """
    print(f"\n📂 Scanning {repo_name}...")
    
    # Get subdirectories to scan
    subdirs = REPOSITORIES.get(repo_name, None)
    
    # Get all files
    all_files = get_repo_files(repo_path, subdirs)
    print(f"   Found {len(all_files)} code files")
    
    # Check which are mapped
    mapped_files = set()
    existing_mappings = db_session.query(CodeComponentMapping).all()
    for mapping in existing_mappings:
        mapped_files.add(mapping.file_path)
    
    # Categorize files
    unmapped = []
    mapped_count = 0
    
    for file_path, relative_path in all_files:
        # Check if mapped (use relative path)
        is_mapped, component_id, violations = validator.validate_file_mapping(
            relative_path,
            repo_name
        )
        
        if is_mapped:
            mapped_count += 1
        else:
            unmapped.append((relative_path, file_path))
    
    print(f"   ✅ Mapped: {mapped_count}")
    print(f"   ⚠️  Unmapped: {len(unmapped)}")
    
    # Show sample unmapped files
    if unmapped:
        print(f"\n   Unmapped files (showing first 10):")
        for relative_path, _ in unmapped[:10]:
            print(f"      • {relative_path}")
        if len(unmapped) > 10:
            print(f"      ... and {len(unmapped) - 10} more")
    
    return {
        'repo': repo_name,
        'total_files': len(all_files),
        'mapped_files': mapped_count,
        'unmapped_files': len(unmapped),
        'unmapped_list': [rel for rel, _ in unmapped],
    }


def main():
    """Main scanning function."""
    parser = argparse.ArgumentParser(description='Scan repositories for unregistered files')
    parser.add_argument('--repo', help='Scan specific repository only')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t update database)')
    parser.add_argument('--summary-only', action='store_true', help='Show summary only')
    
    args = parser.parse_args()
    
    # Initialize database and validator
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        validator = ArchitectureValidator(session, workspace_root)
        
        print("=" * 80)
        print("🔍 SCANNING REPOSITORIES FOR UNREGISTERED FILES")
        print("=" * 80)
        
        # Determine which repos to scan
        repos_to_scan = [args.repo] if args.repo else list(REPOSITORIES.keys())
        
        results = []
        total_files = 0
        total_mapped = 0
        total_unmapped = 0
        
        for repo_name in repos_to_scan:
            repo_path = workspace_root / repo_name
            if not repo_path.exists():
                print(f"\n⚠️  Repository not found: {repo_name}")
                continue
            
            result = scan_repo(
                repo_name,
                repo_path,
                validator,
                session,
                dry_run=args.dry_run
            )
            
            results.append(result)
            total_files += result['total_files']
            total_mapped += result['mapped_files']
            total_unmapped += result['unmapped_files']
            
            # Commit after each repo (if not dry-run)
            if not args.dry_run:
                session.commit()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 SCAN SUMMARY")
        print("=" * 80)
        
        print(f"\nTotal Files Scanned: {total_files}")
        print(f"✅ Mapped: {total_mapped}")
        print(f"⚠️  Unmapped: {total_unmapped}")
        
        if total_files > 0:
            coverage_pct = (total_mapped / total_files) * 100
            print(f"\nCoverage: {coverage_pct:.1f}%")
            
            if coverage_pct >= 95:
                print("   ✅ Excellent coverage!")
            elif coverage_pct >= 80:
                print("   ⚠️  Good coverage, but some files unmapped")
            else:
                print("   ❌ Low coverage - many files unmapped")
        
        # Detailed breakdown by repo
        if not args.summary_only:
            print("\n" + "=" * 80)
            print("📋 DETAILED BREAKDOWN BY REPOSITORY")
            print("=" * 80)
            
            for result in results:
                print(f"\n{result['repo']}:")
                print(f"   Total: {result['total_files']}")
                print(f"   Mapped: {result['mapped_files']}")
                print(f"   Unmapped: {result['unmapped_files']}")
                
                if result['unmapped_files'] > 0 and not args.summary_only:
                    print(f"\n   Top unregistered files:")
                    for file_path in result['unmapped_list'][:5]:
                        print(f"      • {file_path}")
                    if len(result['unmapped_list']) > 5:
                        print(f"      ... and {len(result['unmapped_list']) - 5} more")
        
        # Next steps
        if total_unmapped > 0:
            print("\n" + "=" * 80)
            print("💡 NEXT STEPS")
            print("=" * 80)
            print("\nTo map unregistered files:")
            print("   1. Review architecture documents to identify components")
            print("   2. Register components if needed:")
            print("      python -m workspace.wms.cli arch register <name> <type> <repo>")
            print("   3. Map files to components:")
            print("      python -m workspace.wms.cli arch map-file <file_path> <component_id>")
            print("\nOr check current status:")
            print("   python -m workspace.wms.cli arch status")
            print("   python -m workspace.wms.cli arch unregistered")
        
        print()
        
        return 0 if total_unmapped == 0 else 1
        
    finally:
        session.close()


if __name__ == '__main__':
    sys.exit(main())

