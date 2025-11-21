#!/usr/bin/env python3
"""
Map Phase 2 files - Module-specific files.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Map files within existing component directories (learning, orchestration, research, trading modules)
DOMAIN: Cross-repo workspace management

Usage:
    python workspace/scripts/map_phase2_files.py [--dry-run] [--repo REPO]
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


# Module directory mappings - which components own which directories
MODULE_COMPONENT_MAPPINGS = {
    'meridian-core': {
        'learning/': ['LearningEngine', 'OrchestrationLearningEngine', 'ProposalManager', 'EffectivenessTracker'],
        'orchestration/': ['AIOrchestrator', 'AutonomousOrchestrator', 'TaskExecutor', 'AgentSelector', 
                          'LearningCycleManager', 'TaskPipelineExecutor', 'VotingManager', 'PreflightManager',
                          'ReviewOrchestrator', 'ConnectorManager'],
        'connectors/': ['ConnectorManager'],
        'utils/': ['CredentialStore'],
    },
    'meridian-research': {
        'core/': ['ResearchEngine', 'MeridianCoreAdapter'],
        'learning/': ['ResearchLearningBridge', 'ResearchPatternDetector', 'ResearchSessionStore'],
        'skills/': ['SkillLoader', 'SkillAdapter'],
        'tasks/': ['ResearchTaskManager', 'ResearchTaskSync'],
        'workflows/': ['WorkflowOrchestrator', 'WorkflowEngine'],
        'feedback/': ['ResearchFeedbackCollector'],
        'knowledge/': ['KnowledgeProvider'],
        'connectors/': ['MeridianCoreAdapter'],
    },
    'meridian-trading': {
        'strategies/': ['WilliamsRReversalStrategy', 'CombinedTimingStrategy', 'COTTdomStrategy'],
        'indicators/': ['WilliamsRIndicator', 'ATRIndicator', 'COTIndicator'],
        'filters/': ['TDOMFilter', 'TDOWFilter', 'TDOYFilter'],
        'risk/': ['RiskManager', 'CorrelationManager'],
        'scanners/': ['MarketScanner'],
        'security/': ['TradingCredentialManager'],
        'adapters/': ['OrchestratorBridge'],
        'connectors/': ['OrchestratorBridge'],
        'utils/': ['TradingDataValidator'],
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


def find_component_by_filename(file_name: str, session, repo: str) -> Optional[ArchitectureComponent]:
    """
    Try to find component by filename pattern.
    
    Examples:
    - orchestration_learning_engine.py -> OrchestrationLearningEngine
    - task_executor.py -> TaskExecutor
    - risk_manager.py -> RiskManager
    """
    # Remove .py extension
    base_name = file_name.replace('.py', '')
    
    # Try exact match with component name variations
    # Convert snake_case to PascalCase
    parts = base_name.split('_')
    pascal_name = ''.join(word.capitalize() for word in parts)
    
    # Try finding component
    comp = find_component_by_name(session, pascal_name, repo)
    if comp:
        return comp
    
    # Try partial match
    for word in parts:
        if len(word) > 3:  # Ignore short words like 'the', 'a', etc.
            comp = find_component_by_name(session, word.capitalize(), repo)
            if comp:
                return comp
    
    return None


def get_component_for_phase2_file(
    validator: ArchitectureValidator,
    session,
    file_path: str,
    repo: str
) -> Optional[Tuple[ArchitectureComponent, str]]:
    """
    Determine which component a Phase 2 file should map to.
    
    Phase 2 focuses on module-specific files within component directories.
    
    Returns:
        Tuple of (component, mapping_reason) or None
    """
    # Skip build directories
    if '/build/' in file_path or '/dist/' in file_path or file_path.startswith('build/') or file_path.startswith('dist/'):
        return None
    
    # Check if already mapped
    existing = session.query(CodeComponentMapping).filter_by(file_path=file_path).first()
    if existing:
        return (existing.component, "Already mapped")
    
    # Skip __init__.py, main.py, cli.py (Phase 1 handled these)
    if file_path.endswith('/__init__.py') or file_path.endswith('/main.py') or file_path.endswith('/cli.py'):
        return None
    
    # Skip test files for now (Phase 4)
    if '/test' in file_path.lower() or file_path.startswith('test_'):
        return None
    
    # Get directory path relative to repo
    path_obj = Path(file_path)
    file_name = path_obj.name
    
    # Check module mappings
    repo_mappings = MODULE_COMPONENT_MAPPINGS.get(repo, {})
    
    for module_path, component_names in repo_mappings.items():
        if module_path in file_path:
            # Try to find component by filename first
            comp = find_component_by_filename(file_name, session, repo)
            if comp:
                return (comp, f"Filename matches component: {comp.component_name}")
            
            # Try component names in order
            for comp_name in component_names:
                comp = find_component_by_name(session, comp_name, repo)
                if comp:
                    return (comp, f"File in {module_path} module - maps to {comp_name}")
            
            # If no match, use first component as fallback
            if component_names:
                comp = find_component_by_name(session, component_names[0], repo)
                if comp:
                    return (comp, f"File in {module_path} module - maps to {component_names[0]} (fallback)")
    
    # Try finding component by expected path match
    dir_path = path_obj.parent
    for comp in session.query(ArchitectureComponent).filter_by(repo=repo, status='active').all():
        if comp.expected_path:
            comp_dir = Path(comp.expected_path).parent
            if str(comp_dir) == str(dir_path) or str(comp_dir) in str(dir_path):
                return (comp, f"File in component directory - maps to {comp.component_name}")
    
    # Special case: Check if file name suggests a component
    comp = find_component_by_filename(file_name, session, repo)
    if comp:
        return (comp, f"Filename suggests component: {comp.component_name}")
    
    return None


def map_phase2_files(
    repo: str,
    validator: ArchitectureValidator,
    session,
    dry_run: bool = False
) -> Dict[str, any]:
    """
    Map Phase 2 files for a repository.
    
    Phase 2 focuses on module-specific files.
    
    Returns:
        Dictionary with mapping results
    """
    print(f"\n📂 Mapping Phase 2 files for {repo}...")
    
    repo_path = workspace_root / repo
    if not repo_path.exists():
        print(f"   ⚠️  Repository not found: {repo}")
        return {'repo': repo, 'mapped': 0, 'skipped': 0, 'errors': 0, 'total': 0}
    
    # Get module directories to scan
    module_dirs = list(MODULE_COMPONENT_MAPPINGS.get(repo, {}).keys())
    
    if not module_dirs:
        print(f"   ⚠️  No module mappings defined for {repo}")
        return {'repo': repo, 'mapped': 0, 'skipped': 0, 'errors': 0, 'total': 0}
    
    # Find all Python files in module directories
    files_to_map = []
    
    for module_dir in module_dirs:
        # Construct full path
        if repo == 'meridian-core':
            full_module_path = repo_path / 'src' / 'meridian_core' / module_dir.rstrip('/')
        elif repo == 'meridian-research':
            full_module_path = repo_path / 'src' / 'meridian_research' / module_dir.rstrip('/')
        elif repo == 'meridian-trading':
            full_module_path = repo_path / 'src' / 'meridian_trading' / module_dir.rstrip('/')
        else:
            continue
        
        if not full_module_path.exists():
            continue
        
        # Find all Python files in this module
        for path in full_module_path.rglob('*.py'):
            if path.is_file():
                # Skip build directories
                if any(skip in str(path) for skip in ['venv', '.git', '/build/', '/dist/', '/.pytest_cache/', '/.mypy_cache/']):
                    continue
                
                rel_path = str(path.relative_to(repo_path))
                # Skip Phase 1 files (already mapped)
                if not (rel_path.endswith('/__init__.py') or rel_path.endswith('/main.py') or rel_path.endswith('/cli.py')):
                    files_to_map.append(rel_path)
    
    print(f"   Found {len(files_to_map)} files in module directories")
    
    mapped_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path in sorted(files_to_map):
        result = get_component_for_phase2_file(validator, session, file_path, repo)
        
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
                        created_by="phase2_mapping_script"
                    )
                    print(f"   ✅ Mapped: {file_path} → {component.component_name}")
                    mapped_count += 1
                except Exception as e:
                    print(f"   ❌ Error mapping {file_path}: {e}")
                    error_count += 1
        else:
            skipped_count += 1
            if skipped_count <= 5:  # Show first few skipped files
                print(f"   ⏭️  Skipped: {file_path} (no component match found)")
    
    if skipped_count > 5:
        print(f"   ⏭️  ... and {skipped_count - 5} more skipped files")
    
    if not dry_run:
        session.commit()
    
    return {
        'repo': repo,
        'total_files': len(files_to_map),
        'mapped': mapped_count,
        'skipped': skipped_count,
        'errors': error_count
    }


def main():
    """Main mapping function."""
    parser = argparse.ArgumentParser(description='Map Phase 2 files (module-specific) to components')
    parser.add_argument('--repo', help='Map specific repository only')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (don\'t update database)')
    
    args = parser.parse_args()
    
    # Initialize database and validator
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        validator = ArchitectureValidator(session, workspace_root)
        
        print("=" * 80)
        print("🗺️  PHASE 2 FILE MAPPING (Module-Specific Files)")
        print("=" * 80)
        print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
        
        # Determine which repos to map
        repos_to_map = [args.repo] if args.repo else ['meridian-core', 'meridian-research', 'meridian-trading']
        
        results = []
        total_mapped = 0
        total_skipped = 0
        total_errors = 0
        total_files = 0
        
        for repo in repos_to_map:
            result = map_phase2_files(repo, validator, session, dry_run=args.dry_run)
            results.append(result)
            total_mapped += result['mapped']
            total_skipped += result['skipped']
            total_errors += result['errors']
            total_files += result['total_files']
        
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
        print(f"   Total files scanned: {total_files}")
        print(f"   ✅ Mapped: {total_mapped}")
        print(f"   ⏭️  Skipped: {total_skipped}")
        if total_errors > 0:
            print(f"   ❌ Errors: {total_errors}")
        
        if total_files > 0:
            coverage_pct = (total_mapped / total_files) * 100
            print(f"\n   Phase 2 Coverage: {coverage_pct:.1f}%")
        
        if args.dry_run:
            print("\n💡 This was a DRY RUN. Run without --dry-run to apply mappings.")
        else:
            print("\n✅ Phase 2 mapping complete!")
        
        print()
        
        return 0 if total_errors == 0 else 1
        
    finally:
        session.close()


if __name__ == '__main__':
    sys.exit(main())

