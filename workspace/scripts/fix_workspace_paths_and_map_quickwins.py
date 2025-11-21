#!/usr/bin/env python3
"""
Fix workspace path mismatch and map quick wins.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: 
  1. Fix workspace file path prefix mismatch
  2. Map quick wins: benchmarks, CLI, config, core files
DOMAIN: Cross-repo workspace management

Usage:
    python workspace/scripts/fix_workspace_paths_and_map_quickwins.py [--dry-run]
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.architecture_validator import ArchitectureValidator
from workspace.db.models import ArchitectureComponent, CodeComponentMapping


# Quick wins mappings - file patterns to component names
QUICK_WINS_MAPPINGS = {
    'meridian-core': {
        # Benchmarks → EffectivenessTracker
        'src/meridian_core/benchmarks/': 'EffectivenessTracker',
        
        # CLI files → Appropriate components
        'src/meridian_core/cli/learning_dashboard.py': 'LearningEngine',
        'src/meridian_core/cli/meta_review.py': 'ReviewOrchestrator',
        'src/meridian_core/cli/orchestrator.py': 'AIOrchestrator',
        
        # Config files
        'src/meridian_core/config/rate_limits.py': 'ConnectorManager',
        
        # Core/Module files
        'src/meridian_core/core/auto_register_tools.py': 'AIOrchestrator',
    },
    'meridian-research': {
        # CLI files
        'src/meridian_research/cli/db.py': 'ResearchSessionStore',
        'src/meridian_research/cli/knowledge.py': 'KnowledgeProvider',
        
        # Config files
        'src/meridian_research/config.py': 'ResearchEngine',
    },
    'meridian-trading': {
        # Config files
        'src/meridian_trading/config/credentials.py': 'TradingCredentialManager',
        
        # Core/Module files
        'src/meridian_trading/orchestration/autonomous_orchestrator.py': 'OrchestratorBridge',
        'src/meridian_trading/orchestration/validate_task_queue.py': 'OrchestratorBridge',
    },
}


def find_component_by_name(session, component_name: str, repo: Optional[str] = None) -> Optional[ArchitectureComponent]:
    """Find component by name (partial match)."""
    query = session.query(ArchitectureComponent).filter(
        ArchitectureComponent.component_name.ilike(f'%{component_name}%'),
        ArchitectureComponent.status == 'active'
    )
    if repo:
        query = query.filter(ArchitectureComponent.repo == repo)
    return query.first()


def fix_workspace_paths(session, dry_run: bool = False) -> Dict[str, int]:
    """Fix workspace file path prefix mismatch."""
    print("\n🔧 Fixing workspace path prefix mismatch...")
    
    # Get all workspace mappings
    workspace_mappings = session.query(CodeComponentMapping).join(
        ArchitectureComponent
    ).filter(
        ArchitectureComponent.repo == 'workspace'
    ).all()
    
    fixed_count = 0
    skipped_count = 0
    
    for mapping in workspace_mappings:
        old_path = mapping.file_path
        if old_path.startswith('workspace/'):
            new_path = old_path.replace('workspace/', '', 1)
            
            # Check if new path already exists
            existing = session.query(CodeComponentMapping).filter_by(file_path=new_path).first()
            if existing:
                print(f"   ⚠️  New path already exists: {new_path} (skipping)")
                skipped_count += 1
                continue
            
            if dry_run:
                print(f"   [DRY RUN] Would update: {old_path} → {new_path}")
            else:
                mapping.file_path = new_path
                print(f"   ✅ Fixed: {old_path} → {new_path}")
            fixed_count += 1
    
    if not dry_run:
        session.commit()
    
    print(f"\n   Fixed: {fixed_count} paths")
    if skipped_count > 0:
        print(f"   Skipped: {skipped_count} paths (already exist)")
    
    return {'fixed': fixed_count, 'skipped': skipped_count}


def map_quick_wins(
    repo: str,
    validator: ArchitectureValidator,
    session,
    dry_run: bool = False
) -> Dict[str, int]:
    """Map quick wins for a repository."""
    print(f"\n📂 Mapping quick wins for {repo}...")
    
    repo_path = workspace_root / repo
    if not repo_path.exists():
        print(f"   ⚠️  Repository not found: {repo}")
        return {'mapped': 0, 'skipped': 0, 'errors': 0}
    
    repo_mappings = QUICK_WINS_MAPPINGS.get(repo, {})
    
    if not repo_mappings:
        print(f"   ⚠️  No quick wins defined for {repo}")
        return {'mapped': 0, 'skipped': 0, 'errors': 0}
    
    mapped_count = 0
    skipped_count = 0
    error_count = 0
    
    # Map benchmark files
    if 'src/meridian_core/benchmarks/' in repo_mappings:
        comp_name = repo_mappings['src/meridian_core/benchmarks/']
        comp = find_component_by_name(session, comp_name, repo)
        
        if comp:
            benchmarks_dir = repo_path / 'src' / 'meridian_core' / 'benchmarks'
            if benchmarks_dir.exists():
                for path in benchmarks_dir.glob('*.py'):
                    if path.name == '__init__.py':
                        continue
                    rel_path = str(path.relative_to(repo_path))
                    
                    # Check if already mapped
                    existing = session.query(CodeComponentMapping).filter_by(file_path=rel_path).first()
                    if existing:
                        skipped_count += 1
                        continue
                    
                    if dry_run:
                        print(f"   [DRY RUN] Would map: {rel_path} → {comp.component_name}")
                        mapped_count += 1
                    else:
                        try:
                            validator.map_file_to_component(
                                file_path=rel_path,
                                component_id=comp.id,
                                mapping_reason=f"Benchmark file - maps to {comp_name}",
                                mapping_type="direct",
                                created_by="quickwins_script"
                            )
                            print(f"   ✅ Mapped: {rel_path} → {comp.component_name}")
                            mapped_count += 1
                        except Exception as e:
                            print(f"   ❌ Error: {rel_path} - {e}")
                            error_count += 1
    
    # Map specific files from mappings
    for pattern, comp_name in repo_mappings.items():
        if pattern.endswith('/'):
            # Already handled as directory above
            continue
        
        # Check if file exists
        file_path = repo_path / pattern
        if not file_path.exists():
            # Try with src prefix
            if not pattern.startswith('src/'):
                file_path = repo_path / 'src' / pattern
            if not file_path.exists():
                continue
        
        rel_path = str(file_path.relative_to(repo_path))
        
        # Check if already mapped
        existing = session.query(CodeComponentMapping).filter_by(file_path=rel_path).first()
        if existing:
            skipped_count += 1
            continue
        
        # Find component
        comp = find_component_by_name(session, comp_name, repo)
        if not comp:
            print(f"   ⚠️  Component not found: {comp_name} for {rel_path}")
            skipped_count += 1
            continue
        
        if dry_run:
            print(f"   [DRY RUN] Would map: {rel_path} → {comp.component_name}")
            mapped_count += 1
        else:
            try:
                # Determine mapping reason
                if 'cli' in rel_path.lower():
                    reason = f"CLI file - maps to {comp_name}"
                elif 'config' in rel_path.lower():
                    reason = f"Config file - maps to {comp_name}"
                elif 'core' in rel_path.lower() or 'orchestration' in rel_path.lower():
                    reason = f"Core/Module file - maps to {comp_name}"
                else:
                    reason = f"File - maps to {comp_name}"
                
                validator.map_file_to_component(
                    file_path=rel_path,
                    component_id=comp.id,
                    mapping_reason=reason,
                    mapping_type="direct",
                    created_by="quickwins_script"
                )
                print(f"   ✅ Mapped: {rel_path} → {comp.component_name}")
                mapped_count += 1
            except Exception as e:
                print(f"   ❌ Error: {rel_path} - {e}")
                error_count += 1
    
    if not dry_run:
        session.commit()
    
    return {'mapped': mapped_count, 'skipped': skipped_count, 'errors': error_count}


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Fix workspace paths and map quick wins')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t update database)')
    
    args = parser.parse_args()
    
    # Initialize database and validator
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        validator = ArchitectureValidator(session, workspace_root)
        
        print("=" * 80)
        print("🔧 FIX WORKSPACE PATHS & MAP QUICK WINS")
        print("=" * 80)
        print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
        
        # Step 1: Fix workspace paths
        path_fix_result = fix_workspace_paths(session, dry_run=args.dry_run)
        
        # Step 2: Map quick wins
        print("\n" + "=" * 80)
        print("📋 MAPPING QUICK WINS")
        print("=" * 80)
        
        repos = ['meridian-core', 'meridian-research', 'meridian-trading']
        results = []
        total_mapped = 0
        total_skipped = 0
        total_errors = 0
        
        for repo in repos:
            result = map_quick_wins(repo, validator, session, dry_run=args.dry_run)
            results.append((repo, result))
            total_mapped += result['mapped']
            total_skipped += result['skipped']
            total_errors += result['errors']
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        
        print(f"\nWorkspace Path Fixes:")
        print(f"   ✅ Fixed: {path_fix_result['fixed']}")
        if path_fix_result['skipped'] > 0:
            print(f"   ⏭️  Skipped: {path_fix_result['skipped']}")
        
        print(f"\nQuick Wins Mapping:")
        for repo, result in results:
            print(f"   {repo}: {result['mapped']} mapped, {result['skipped']} skipped")
            if result['errors'] > 0:
                print(f"      Errors: {result['errors']}")
        
        print(f"\nOverall Quick Wins:")
        print(f"   ✅ Mapped: {total_mapped}")
        print(f"   ⏭️  Skipped: {total_skipped}")
        if total_errors > 0:
            print(f"   ❌ Errors: {total_errors}")
        
        if args.dry_run:
            print("\n💡 This was a DRY RUN. Run without --dry-run to apply changes.")
        else:
            print("\n✅ Workspace paths fixed and quick wins mapped!")
        
        print()
        
        return 0 if total_errors == 0 else 1
        
    finally:
        session.close()


if __name__ == '__main__':
    sys.exit(main())

