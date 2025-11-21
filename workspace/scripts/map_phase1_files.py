#!/usr/bin/env python3
"""
Map Phase 1 files to components.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Systematically map Phase 1 files (entry points, connectors, configs)
DOMAIN: Cross-repo workspace management

Usage:
    python workspace/scripts/map_phase1_files.py [--dry-run] [--repo REPO]
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
from datetime import datetime

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.architecture_validator import ArchitectureValidator
from workspace.db.models import ArchitectureComponent, CodeComponentMapping


# Component mapping rules for Phase 1 files
PHASE1_MAPPING_RULES = {
    # Entry points
    'src/meridian_core/__init__.py': {
        'component_search': 'LearningEngine',
        'fallback_type': 'package',
        'description': 'Main package init file'
    },
    'src/meridian_core/main.py': {
        'component_search': 'AIOrchestrator',
        'fallback_type': 'core_class',
        'description': 'Main entry point for meridian-core'
    },
    
    # Connector files -> ConnectorManager
    'connectors/': {
        'component_search': 'ConnectorManager',
        'fallback_type': 'integration_component',
        'description': 'AI connector implementation'
    },
    
    # Config files -> Component that uses them
    '*_config.py': {
        'component_search': 'ConnectorManager',
        'fallback_type': 'config',
        'description': 'Configuration file'
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


def get_component_for_file(
    validator: ArchitectureValidator,
    session,
    file_path: str,
    repo: str
) -> Optional[Tuple[ArchitectureComponent, str]]:
    """
    Determine which component a file should map to.
    
    Returns:
        Tuple of (component, mapping_reason) or None
    """
    # Skip build directories and generated files
    if '/build/' in file_path or '/dist/' in file_path or file_path.startswith('build/') or file_path.startswith('dist/'):
        return None  # Skip generated files
    
    # Check if already mapped
    existing = session.query(CodeComponentMapping).filter_by(file_path=file_path).first()
    if existing:
        return (existing.component, "Already mapped")
    
    # Entry points mapping
    if file_path.endswith('/__init__.py'):
        # Connector __init__.py files map to ConnectorManager
        if '/connectors/' in file_path:
            comp = find_component_by_name(session, 'ConnectorManager', repo)
            if comp:
                return (comp, "Connector package init - maps to ConnectorManager")
            # If ConnectorManager not in this repo, try meridian-core
            if repo != 'meridian-core':
                comp = find_component_by_name(session, 'ConnectorManager', 'meridian-core')
                if comp:
                    return (comp, "Connector package init - maps to meridian-core ConnectorManager")
        
        # Map to primary component in that directory
        dir_path = Path(file_path).parent
        # Try to find component in same directory
        for comp in session.query(ArchitectureComponent).filter_by(repo=repo, status='active').all():
            if comp.expected_path:
                comp_dir = Path(comp.expected_path).parent
                if str(comp_dir) == str(dir_path):
                    return (comp, f"Init file for {comp.component_name} component")
        
        # Special cases for module __init__.py files
        if file_path == 'src/meridian_core/connectors/__init__.py':
            comp = find_component_by_name(session, 'ConnectorManager', repo)
            if comp:
                return (comp, "Connector package init - maps to ConnectorManager")
        elif file_path == 'src/meridian_core/orchestration/__init__.py':
            comp = find_component_by_name(session, 'AIOrchestrator', repo)
            if comp:
                return (comp, "Orchestration package init - maps to AIOrchestrator")
        elif file_path == 'src/meridian_core/learning/__init__.py':
            comp = find_component_by_name(session, 'LearningEngine', repo)
            if comp:
                return (comp, "Learning package init - maps to LearningEngine")
        elif file_path == 'src/meridian_core/utils/__init__.py':
            comp = find_component_by_name(session, 'CredentialStore', repo)
            if comp:
                return (comp, "Utils package init - maps to CredentialStore")
        elif file_path == 'src/meridian_research/connectors/__init__.py':
            # Research connectors use meridian-core adapters
            comp = find_component_by_name(session, 'MeridianCoreAdapter', repo)
            if comp:
                return (comp, "Research connector package - maps to MeridianCoreAdapter")
        elif file_path == 'src/meridian_trading/connectors/__init__.py':
            comp = find_component_by_name(session, 'OrchestratorBridge', repo)
            if comp:
                return (comp, "Trading connector package - maps to OrchestratorBridge")
        
        # Module __init__.py files - map to parent components
        # meridian-core modules
        if repo == 'meridian-core':
            module_mappings = {
                'src/meridian_core/api/__init__.py': 'AIOrchestrator',
                'src/meridian_core/benchmarks/__init__.py': 'EffectivenessTracker',
                'src/meridian_core/cli/__init__.py': 'AIOrchestrator',
                'src/meridian_core/core/__init__.py': 'AIOrchestrator',
                'src/meridian_core/db/__init__.py': 'AIOrchestrator',  # DB support for orchestrator
                'src/meridian_core/evaluations/__init__.py': 'EffectivenessTracker',
                'src/meridian_core/extraction/__init__.py': 'EffectivenessTracker',  # Data extraction for analytics
                'src/meridian_core/models/__init__.py': 'AIOrchestrator',  # Data models for orchestrator
                'src/meridian_core/monitoring/__init__.py': 'EffectivenessTracker',
                'src/meridian_core/orchestrator/__init__.py': 'AIOrchestrator',  # Alternative orchestrator location
            }
            if file_path in module_mappings:
                comp = find_component_by_name(session, module_mappings[file_path], repo)
                if comp:
                    return (comp, f"Module init - maps to {module_mappings[file_path]}")
        
        # meridian-research modules
        elif repo == 'meridian-research':
            module_mappings = {
                'src/meridian_research/credentials/__init__.py': 'ResearchEngine',
                'src/meridian_research/db/__init__.py': 'ResearchSessionStore',
                'src/meridian_research/export/__init__.py': 'ResearchEngine',
                'src/meridian_research/templates/__init__.py': 'SkillLoader',
                'src/meridian_research/utils/__init__.py': 'ResearchEngine',
                'src/meridian_research/_assets/__init__.py': 'ResearchEngine',  # Assets for research engine
            }
            if file_path in module_mappings:
                comp = find_component_by_name(session, module_mappings[file_path], repo)
                if comp:
                    return (comp, f"Module init - maps to {module_mappings[file_path]}")
        
        # meridian-trading modules (most mapped already)
        
        # If main package init, map to core engine
        if file_path == 'src/meridian_core/__init__.py':
            comp = find_component_by_name(session, 'LearningEngine', repo)
            if comp:
                return (comp, "Main package init - maps to core engine")
        elif file_path == 'src/meridian_research/__init__.py':
            comp = find_component_by_name(session, 'ResearchEngine', repo)
            if comp:
                return (comp, "Main package init - maps to research engine")
        elif file_path == 'src/meridian_trading/__init__.py':
            comp = find_component_by_name(session, 'OrchestratorBridge', repo)
            if comp:
                return (comp, "Main package init - maps to trading adapter")
        
        # Root-level __init__.py files (likely old/test directories)
        # Map to main engine if they're in root
        if file_path.endswith('/__init__.py') and file_path.count('/') <= 1:
            if repo == 'meridian-core':
                comp = find_component_by_name(session, 'AIOrchestrator', repo)
                if comp:
                    return (comp, "Root-level module init - maps to AIOrchestrator")
            elif repo == 'meridian-research':
                comp = find_component_by_name(session, 'ResearchEngine', repo)
                if comp:
                    return (comp, "Root-level module init - maps to ResearchEngine")
            elif repo == 'meridian-trading':
                comp = find_component_by_name(session, 'OrchestratorBridge', repo)
                if comp:
                    return (comp, "Root-level module init - maps to OrchestratorBridge")
    
    # Main entry point
    if file_path.endswith('/main.py'):
        if 'meridian_core' in file_path:
            comp = find_component_by_name(session, 'AIOrchestrator', repo)
            if comp:
                return (comp, "Main entry point - maps to AIOrchestrator")
    
    # CLI entry point
    if file_path.endswith('/cli.py'):
        if 'meridian_core' in file_path:
            comp = find_component_by_name(session, 'AIOrchestrator', repo)
            if comp:
                return (comp, "CLI entry point - maps to AIOrchestrator")
        elif 'meridian_research' in file_path:
            comp = find_component_by_name(session, 'ResearchEngine', repo)
            if comp:
                return (comp, "CLI entry point - maps to ResearchEngine")
    
    # Connector files
    if '/connectors/' in file_path and file_path.endswith('.py'):
        # Skip __init__.py (handled above)
        if not file_path.endswith('/__init__.py'):
            # For meridian-core, map to ConnectorManager
            if repo == 'meridian-core':
                comp = find_component_by_name(session, 'ConnectorManager', repo)
                if comp:
                    return (comp, f"Connector file - maps to ConnectorManager")
            # For meridian-research, connectors use MeridianCoreAdapter
            elif repo == 'meridian-research':
                comp = find_component_by_name(session, 'MeridianCoreAdapter', repo)
                if comp:
                    return (comp, f"Research connector - maps to MeridianCoreAdapter")
            # For meridian-trading, connectors use OrchestratorBridge or specific trading connector
            elif repo == 'meridian-trading':
                # Check if it's IG connector (domain-specific)
                if 'ig_connector' in file_path.lower():
                    comp = find_component_by_name(session, 'OrchestratorBridge', repo)
                    if comp:
                        return (comp, "Trading IG connector - maps to OrchestratorBridge")
                else:
                    comp = find_component_by_name(session, 'OrchestratorBridge', repo)
                    if comp:
                        return (comp, "Trading connector - maps to OrchestratorBridge")
    
    # Config files
    if file_path.endswith('_config.py'):
        # Try to find component in same directory or parent
        dir_path = Path(file_path).parent
        # Check if there's a component in this directory
        for comp in session.query(ArchitectureComponent).filter_by(repo=repo, status='active').all():
            if comp.expected_path:
                comp_dir = Path(comp.expected_path).parent
                if str(comp_dir) == str(dir_path) or str(comp_dir) in str(dir_path):
                    return (comp, f"Config file for {comp.component_name}")
        
        # Default to ConnectorManager for connector configs
        if 'connector' in file_path.lower():
            comp = find_component_by_name(session, 'ConnectorManager', repo)
            if comp:
                return (comp, "Connector config file - maps to ConnectorManager")
    
    return None


def map_phase1_files(
    repo: str,
    validator: ArchitectureValidator,
    session,
    dry_run: bool = False
) -> Dict[str, any]:
    """
    Map Phase 1 files for a repository.
    
    Returns:
        Dictionary with mapping results
    """
    print(f"\n📂 Mapping Phase 1 files for {repo}...")
    
    repo_path = workspace_root / repo
    if not repo_path.exists():
        print(f"   ⚠️  Repository not found: {repo}")
        return {'repo': repo, 'mapped': 0, 'skipped': 0, 'errors': 0}
    
    # Find Phase 1 files
    entry_points = []
    connectors = []
    configs = []
    
    # Entry points
    for pattern in ['__init__.py', 'main.py', 'cli.py']:
        for path in repo_path.rglob(pattern):
            if path.is_file():
                rel_path = str(path.relative_to(repo_path))
                # Skip build directories, venv, .git, etc.
                if any(skip in str(path) for skip in ['venv', '.git', '/build/', '/dist/', '/.pytest_cache/', '/.mypy_cache/']):
                    continue
                if rel_path.endswith('__init__.py'):
                    entry_points.append(rel_path)
                elif rel_path.endswith('main.py'):
                    entry_points.append(rel_path)
                elif rel_path.endswith('cli.py'):
                    entry_points.append(rel_path)
    
    # Connectors
    connectors_dir = repo_path / 'src' / repo.replace('meridian-', 'meridian_') / 'connectors'
    if connectors_dir.exists():
        for path in connectors_dir.rglob('*.py'):
            rel_path = str(path.relative_to(repo_path))
            connectors.append(rel_path)
    
    # Config files
    for path in repo_path.rglob('*_config.py'):
        if path.is_file():
            rel_path = str(path.relative_to(repo_path))
            # Skip build directories, venv, .git, etc.
            if any(skip in str(path) for skip in ['venv', '.git', '/build/', '/dist/', '/.pytest_cache/', '/.mypy_cache/']):
                continue
            configs.append(rel_path)
    
    all_files = list(set(entry_points + connectors + configs))
    
    print(f"   Found {len(entry_points)} entry points, {len(connectors)} connector files, {len(configs)} config files")
    print(f"   Total Phase 1 files: {len(all_files)}")
    
    mapped_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path in sorted(all_files):
        result = get_component_for_file(validator, session, file_path, repo)
        
        if result:
            component, reason = result
            
            if dry_run:
                print(f"   [DRY RUN] Would map: {file_path}")
                print(f"              → {component.component_name} ({component.id})")
                print(f"              Reason: {reason}")
                mapped_count += 1
            else:
                try:
                    mapping = validator.map_file_to_component(
                        file_path=file_path,
                        component_id=component.id,
                        mapping_reason=reason,
                        mapping_type="direct",
                        created_by="phase1_mapping_script"
                    )
                    print(f"   ✅ Mapped: {file_path} → {component.component_name}")
                    mapped_count += 1
                except Exception as e:
                    print(f"   ❌ Error mapping {file_path}: {e}")
                    error_count += 1
        else:
            skipped_count += 1
            print(f"   ⏭️  Skipped: {file_path} (no component match found)")
    
    if not dry_run:
        session.commit()
    
    return {
        'repo': repo,
        'total_files': len(all_files),
        'mapped': mapped_count,
        'skipped': skipped_count,
        'errors': error_count
    }


def main():
    """Main mapping function."""
    parser = argparse.ArgumentParser(description='Map Phase 1 files to components')
    parser.add_argument('--repo', help='Map specific repository only')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t update database)')
    
    args = parser.parse_args()
    
    # Initialize database and validator
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        validator = ArchitectureValidator(session, workspace_root)
        
        print("=" * 80)
        print("🗺️  PHASE 1 FILE MAPPING")
        print("=" * 80)
        print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
        
        # Determine which repos to map
        repos_to_map = [args.repo] if args.repo else ['meridian-core', 'meridian-research', 'meridian-trading']
        
        results = []
        total_mapped = 0
        total_skipped = 0
        total_errors = 0
        
        for repo in repos_to_map:
            result = map_phase1_files(repo, validator, session, dry_run=args.dry_run)
            results.append(result)
            total_mapped += result['mapped']
            total_skipped += result['skipped']
            total_errors += result['errors']
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 MAPPING SUMMARY")
        print("=" * 80)
        
        for result in results:
            print(f"\n{result['repo']}:")
            print(f"   Total files: {result['total_files']}")
            print(f"   ✅ Mapped: {result['mapped']}")
            print(f"   ⏭️  Skipped: {result['skipped']}")
            if result['errors'] > 0:
                print(f"   ❌ Errors: {result['errors']}")
        
        print(f"\nOverall:")
        print(f"   ✅ Mapped: {total_mapped}")
        print(f"   ⏭️  Skipped: {total_skipped}")
        if total_errors > 0:
            print(f"   ❌ Errors: {total_errors}")
        
        if args.dry_run:
            print("\n💡 This was a DRY RUN. Run without --dry-run to apply mappings.")
        else:
            print("\n✅ Phase 1 mapping complete!")
        
        print()
        
        return 0 if total_errors == 0 else 1
        
    finally:
        session.close()


if __name__ == '__main__':
    sys.exit(main())

