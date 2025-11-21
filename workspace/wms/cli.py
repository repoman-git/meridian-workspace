#!/usr/bin/env python3
"""
WMS Command-Line Interface

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: CLI for Workspace Management System
DOMAIN: Cross-repo workspace management
"""

import click
from pathlib import Path
import sys

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.context_manager import ContextManager
from workspace.wms.governance_engine import GovernanceEngine
from workspace.wms.bastard_integration import BastardIntegration
from workspace.wms.workflow_engine import WorkflowEngine
from workspace.wms.architecture_validator import ArchitectureValidator


# Initialize database
WORKSPACE_ROOT = Path.cwd()
db = WorkspaceDB(workspace_root=WORKSPACE_ROOT)


@click.group()
def wms():
    """Workspace Management System - AI-governed workflow automation"""
    pass


# ============================================================================
# CONTEXT COMMANDS
# ============================================================================

@wms.group()
def context():
    """Manage work context (which repo you're in)"""
    pass


@context.command()
@click.argument('repo')
@click.option('--notes', help='Optional notes about what you\'re working on')
def set(repo: str, notes: str):
    """Set work context to a repo"""
    session = db._get_session()
    try:
        manager = ContextManager(WORKSPACE_ROOT, session)
        
        # Normalize repo name
        if not repo.startswith('meridian-'):
            repo = f'meridian-{repo}'
        
        manager.set_context(repo, notes)
    finally:
        session.close()


@context.command()
def show():
    """Show current work context"""
    session = db._get_session()
    try:
        manager = ContextManager(WORKSPACE_ROOT, session)
        
        ctx = manager.get_current_context()
        if not ctx:
            click.echo("No active context")
            return
        
        click.echo(f"\nCurrent Context:")
        click.echo(f"  Repo: {ctx.repo}")
        click.echo(f"  Path: {ctx.repo_path}")
        click.echo(f"  Since: {ctx.activated_at}")
        if ctx.notes:
            click.echo(f"  Notes: {ctx.notes}")
    finally:
        session.close()


@context.command()
def clear():
    """Clear current work context"""
    session = db._get_session()
    try:
        manager = ContextManager(WORKSPACE_ROOT, session)
        manager.clear_context()
    finally:
        session.close()


# ============================================================================
# TASK COMMANDS
# ============================================================================

@wms.group()
def task():
    """Manage tasks"""
    pass


@task.command()
@click.option('--title', prompt='Task title', help='Short task title')
@click.option('--description', prompt='Task description', help='Detailed description')
@click.option('--users', prompt='Actual users TODAY', type=int, help='Current user count')
@click.option('--solution', prompt='Proposed solution (optional)', default='', help='Implementation approach')
@click.option('--priority', default='medium', type=click.Choice(['low', 'medium', 'high', 'critical']))
def create(title: str, description: str, users: int, solution: str, priority: str):
    """Create a new task with validation"""
    session = db._get_session()
    try:
        # Initialize engines
        governance = GovernanceEngine(session, workspace_root=WORKSPACE_ROOT)
        bastard = BastardIntegration(session, WORKSPACE_ROOT / "workspace" / "skills")
        workflow = WorkflowEngine(session, governance, bastard, workspace_root=WORKSPACE_ROOT)
        
        # Create task
        task = workflow.create_task(
            title=title,
            description=description,
            actual_users=users,
            proposed_solution=solution if solution else None,
            priority=priority
        )
        
        click.echo(f"\n📋 Task created: {task.id}")
        click.echo(f"   Status: {task.status}")
        click.echo(f"   Assigned to: {task.assigned_repo}")
        
        if task.status == "blocked":
            click.echo(f"\n⚠️  Task is BLOCKED. Fix violations before proceeding.")
    finally:
        session.close()


@task.command()
@click.argument('task_id')
def start(task_id: str):
    """Start working on a task"""
    session = db._get_session()
    try:
        governance = GovernanceEngine(session, workspace_root=WORKSPACE_ROOT)
        bastard = BastardIntegration(session, WORKSPACE_ROOT / "workspace" / "skills")
        workflow = WorkflowEngine(session, governance, bastard, workspace_root=WORKSPACE_ROOT)
        
        success = workflow.start_task(task_id)
        
        if not success:
            click.echo("\n❌ Cannot start task. Fix issues first.")
    finally:
        session.close()


@task.command()
@click.argument('task_id')
def complete(task_id: str):
    """Complete a task (triggers final Bastard evaluation)"""
    session = db._get_session()
    try:
        governance = GovernanceEngine(session, workspace_root=WORKSPACE_ROOT)
        bastard = BastardIntegration(session, WORKSPACE_ROOT / "workspace" / "skills")
        workflow = WorkflowEngine(session, governance, bastard, workspace_root=WORKSPACE_ROOT)
        
        success = workflow.complete_task(task_id)
        
        if not success:
            click.echo("\n❌ Task completion REJECTED. Fix issues and try again.")
        else:
            click.echo("\n✅ Task completed and approved!")
    finally:
        session.close()


@task.command()
def list():
    """List all tasks"""
    session = db._get_session()
    try:
        from workspace.db.models import WorkspaceTask
        
        tasks = session.query(WorkspaceTask).order_by(WorkspaceTask.created.desc()).all()
        
        if not tasks:
            click.echo("No tasks found")
            return
        
        click.echo("\nTasks:")
        click.echo("-" * 80)
        
        for t in tasks:
            status_icon = {
                'planning': '📋',
                'approved': '✅',
                'in_progress': '🔄',
                'blocked': '⚠️',
                'completed': '✅',
                'cancelled': '❌'
            }.get(t.status, '?')
            
            click.echo(f"{status_icon} {t.id} - {t.title}")
            click.echo(f"   Status: {t.status} | Repo: {t.assigned_repo or 'N/A'}")
            if t.bastard_plan_grade:
                click.echo(f"   Plan grade: {t.bastard_plan_grade}")
            if t.bastard_completion_grade:
                click.echo(f"   Completion grade: {t.bastard_completion_grade}")
            click.echo()
    finally:
        session.close()


# ============================================================================
# ARCHITECTURE VALIDATION COMMANDS
# ============================================================================

@wms.group()
def arch():
    """Architecture validation and component management"""
    pass


@arch.command()
@click.option('--repo', help='Filter by repository')
@click.option('--status', default='active', help='Filter by status (active, deprecated, planned)')
def components(repo: str, status: str):
    """List registered architecture components"""
    session = db._get_session()
    try:
        from workspace.db.models import ArchitectureComponent
        
        query = session.query(ArchitectureComponent).filter_by(status=status)
        if repo:
            query = query.filter_by(repo=repo)
        
        components_list = query.order_by(ArchitectureComponent.repo, ArchitectureComponent.component_name).all()
        
        if not components_list:
            click.echo(f"No components found (repo={repo or 'all'}, status={status})")
            return
        
        click.echo(f"\n📦 Registered Components ({len(components_list)}):")
        click.echo("=" * 80)
        
        current_repo = None
        for comp in components_list:
            if comp.repo != current_repo:
                if current_repo is not None:
                    click.echo()
                click.echo(f"\n{comp.repo}:")
                current_repo = comp.repo
            
            mapping_count = len(comp.code_mappings)
            click.echo(f"   • {comp.component_name} ({comp.component_type})")
            click.echo(f"     ID: {comp.id}")
            if comp.expected_path:
                click.echo(f"     Path: {comp.expected_path}")
            if comp.description:
                click.echo(f"     Desc: {comp.description[:60]}...")
            click.echo(f"     Files mapped: {mapping_count}")
        
        click.echo()
    finally:
        session.close()


@arch.command()
@click.option('--repo', help='Filter by repository')
def unregistered(repo: str):
    """List unregistered files (not mapped to any component)"""
    session = db._get_session()
    try:
        validator = ArchitectureValidator(session, WORKSPACE_ROOT)
        
        unregistered_files = validator.get_unregistered_files(repo=repo)
        
        if not unregistered_files:
            click.echo(f"\n✅ No unregistered files found (repo={repo or 'all'})")
            return
        
        click.echo(f"\n⚠️  Unregistered Files ({len(unregistered_files)}):")
        click.echo("=" * 80)
        
        by_repo = {}
        for f in unregistered_files:
            if f.repo not in by_repo:
                by_repo[f.repo] = []
            by_repo[f.repo].append(f)
        
        for repo_name in sorted(by_repo.keys()):
            click.echo(f"\n{repo_name}: {len(by_repo[repo_name])} files")
            for f in by_repo[repo_name][:20]:  # Show first 20 per repo
                click.echo(f"   • {f.file_path}")
                if f.detection_count > 1:
                    click.echo(f"     (detected {f.detection_count} times)")
            if len(by_repo[repo_name]) > 20:
                click.echo(f"   ... and {len(by_repo[repo_name]) - 20} more")
        
        click.echo()
    finally:
        session.close()


@arch.command()
@click.option('--component-id', help='Filter by component ID')
@click.option('--repo', help='Filter by repository')
def mappings(component_id: str, repo: str):
    """List file-to-component mappings"""
    session = db._get_session()
    try:
        from workspace.db.models import CodeComponentMapping, ArchitectureComponent
        
        query = session.query(CodeComponentMapping)
        
        if component_id:
            query = query.filter_by(component_id=component_id)
        elif repo:
            # Join with ArchitectureComponent to filter by repo
            query = query.join(ArchitectureComponent).filter(ArchitectureComponent.repo == repo)
        
        mappings_list = query.order_by(CodeComponentMapping.file_path).all()
        
        if not mappings_list:
            click.echo("No mappings found")
            return
        
        click.echo(f"\n📁 File Mappings ({len(mappings_list)}):")
        click.echo("=" * 80)
        
        for mapping in mappings_list:
            comp = mapping.component
            click.echo(f"   • {mapping.file_path}")
            click.echo(f"     → {comp.component_name} ({comp.repo})")
            click.echo(f"     Type: {mapping.mapping_type or 'direct'}")
            if mapping.mapping_reason:
                click.echo(f"     Reason: {mapping.mapping_reason[:60]}...")
            click.echo()
        
        click.echo()
    finally:
        session.close()


@arch.command()
def status():
    """Show architecture validation status summary"""
    session = db._get_session()
    try:
        from workspace.db.models import ArchitectureComponent, CodeComponentMapping, UnregisteredFile
        from collections import defaultdict
        
        components = session.query(ArchitectureComponent).all()
        mappings = session.query(CodeComponentMapping).all()
        unregistered = session.query(UnregisteredFile).filter_by(status='unregistered').all()
        
        # Group by repo
        components_by_repo = defaultdict(int)
        mappings_by_repo = defaultdict(int)
        unregistered_by_repo = defaultdict(int)
        
        for comp in components:
            components_by_repo[comp.repo] += 1
        
        for mapping in mappings:
            comp = mapping.component
            mappings_by_repo[comp.repo] += 1
        
        for f in unregistered:
            unregistered_by_repo[f.repo] += 1
        
        click.echo("\n📊 ARCHITECTURE VALIDATION STATUS")
        click.echo("=" * 80)
        click.echo(f"\n✅ Registered Components: {len(components)}")
        click.echo(f"📁 File Mappings: {len(mappings)}")
        click.echo(f"⚠️  Unregistered Files: {len(unregistered)}")
        click.echo()
        click.echo("By Repository:")
        click.echo("-" * 80)
        
        all_repos = set(components_by_repo.keys()) | set(mappings_by_repo.keys()) | set(unregistered_by_repo.keys())
        
        for repo in sorted(all_repos):
            comp_count = components_by_repo.get(repo, 0)
            map_count = mappings_by_repo.get(repo, 0)
            unreg_count = unregistered_by_repo.get(repo, 0)
            
            coverage = "✅" if unreg_count == 0 else "⚠️"
            click.echo(f"{coverage} {repo}:")
            click.echo(f"   Components: {comp_count}")
            click.echo(f"   Mappings: {map_count}")
            click.echo(f"   Unregistered: {unreg_count}")
            click.echo()
        
        # Overall health
        total_files = len(mappings) + len(unregistered)
        if total_files > 0:
            coverage_pct = (len(mappings) / total_files) * 100
            click.echo("Overall Coverage:")
            click.echo(f"   {coverage_pct:.1f}% of files mapped to components")
            
            if coverage_pct >= 95:
                click.echo("   ✅ Excellent coverage!")
            elif coverage_pct >= 80:
                click.echo("   ⚠️  Good coverage, but some files unmapped")
            else:
                click.echo("   ❌ Low coverage - many files unmapped")
        
        click.echo()
    finally:
        session.close()


@arch.command()
@click.argument('component_name')
@click.argument('component_type')
@click.argument('repo')
@click.option('--path', help='Expected file path')
@click.option('--description', help='Component description')
def register(component_name: str, component_type: str, repo: str, path: str, description: str):
    """Register a new architecture component"""
    session = db._get_session()
    try:
        validator = ArchitectureValidator(session, WORKSPACE_ROOT)
        
        component = validator.register_component(
            component_name=component_name,
            component_type=component_type,
            repo=repo,
            expected_path=path,
            description=description,
            registered_by="cli"
        )
        
        click.echo(f"\n✅ Component registered:")
        click.echo(f"   ID: {component.id}")
        click.echo(f"   Name: {component.component_name}")
        click.echo(f"   Type: {component.component_type}")
        click.echo(f"   Repo: {component.repo}")
        if component.expected_path:
            click.echo(f"   Path: {component.expected_path}")
        click.echo()
    finally:
        session.close()


@arch.command()
@click.argument('file_path')
@click.argument('component_id')
@click.option('--reason', help='Reason for mapping')
@click.option('--type', 'mapping_type', default='direct', help='Mapping type (direct, indirect, dependency)')
def map_file(file_path: str, component_id: str, reason: str, mapping_type: str):
    """Map a file to an architecture component"""
    session = db._get_session()
    try:
        from workspace.db.models import ArchitectureComponent
        
        # Check component exists
        component = session.query(ArchitectureComponent).filter_by(id=component_id).first()
        if not component:
            click.echo(f"❌ Component not found: {component_id}")
            return
        
        validator = ArchitectureValidator(session, WORKSPACE_ROOT)
        
        mapping = validator.map_file_to_component(
            file_path=file_path,
            component_id=component_id,
            mapping_reason=reason or f"Mapped to {component.component_name}",
            mapping_type=mapping_type,
            created_by="cli"
        )
        
        click.echo(f"\n✅ File mapped:")
        click.echo(f"   File: {mapping.file_path}")
        click.echo(f"   Component: {component.component_name} ({component.repo})")
        click.echo(f"   Type: {mapping.mapping_type}")
        click.echo()
    finally:
        session.close()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    wms()

