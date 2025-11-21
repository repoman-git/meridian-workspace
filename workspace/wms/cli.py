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
# MAIN
# ============================================================================

if __name__ == '__main__':
    wms()

