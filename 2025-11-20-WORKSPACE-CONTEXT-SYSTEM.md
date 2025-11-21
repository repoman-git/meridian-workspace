# 2025-11-20 - Workspace Context System Architecture

**Date:** 2025-11-20  
**Purpose:** Workspace context management system - Management plane vs Execution plane  
**Architectural Pattern:** Context-based workspace orchestration

---

## Executive Summary

**Problem:** Working directly in repos causes:
- Context switching overhead (cd between repos)
- Loss of workspace-level visibility
- Difficulty coordinating cross-repo work
- Fragmented task tracking
- No single "command center"

**Solution:** **Workspace Context System**
- Work from workspace root (`data-projects/`)
- Set "work context" to identify active repo
- All operations scoped to context
- Workspace = Management plane
- Repos = Execution plane

**Pattern:** Similar to Kubernetes contexts, Docker contexts, or multi-workspace IDEs.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          MANAGEMENT PLANE                                     │
│                        (data-projects/ - Workspace Root)                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              Workspace Context Manager                               │      │
│  │  • Context switching (set-repo, set-context)                        │      │
│  │  • Context-aware operations                                         │      │
│  │  • Cross-repo coordination                                          │      │
│  │  • Management plane operations                                      │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              Workspace Database (workspace.db)                      │      │
│  │  • Task tracking (all repos)                                       │      │
│  │  • Architecture tracking                                           │      │
│  │  • Drift detection                                                 │      │
│  │  • Session management                                              │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              Master Architecture Repository                          │      │
│  │  • Architecture diagrams (all repos)                               │      │
│  │  • Roadmaps                                                        │      │
│  │  • ADRs                                                            │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐      │
│  │              Governance & Policies                                   │      │
│  │  • AI-GUIDELINES.md                                                 │      │
│  │  • Governance checks                                                │      │
│  │  • Drift prevention                                                 │      │
│  └────────────────────────────────────────────────────────────────────┘      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↓ context-aware operations
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐   ┌───────────────────┐
        │  EXECUTION PLANE  │   │  EXECUTION PLANE  │
        │                   │   │                   │
        │ meridian-core     │   │ meridian-research │
        │ (Active Context)  │   │ (Inactive)        │
        │                   │   │                   │
        │ • Source code     │   │ • Source code     │
        │ • Repo tasks      │   │ • Repo tasks      │
        │ • Local config    │   │ • Local config    │
        └───────────────────┘   └───────────────────┘
```

---

## Context System Design

### Concept: Management Plane vs Execution Plane

**Management Plane (Workspace):**
- **Purpose:** Orchestration, governance, cross-repo coordination
- **Operations:** Task management, architecture tracking, drift detection
- **Scope:** All repos
- **Tools:** Workspace context manager, workspace.db, governance

**Execution Plane (Repos):**
- **Purpose:** Domain-specific implementation
- **Operations:** Code changes, testing, repo-specific tasks
- **Scope:** Single repo
- **Tools:** Git, repo-specific tooling

### Context States

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         CONTEXT STATE MACHINE                                 │
└──────────────────────────────────────────────────────────────────────────────┘

No Context
    │
    ├─> workspace init <repo>    → Active Context
    │
Active Context (meridian-core)
    │
    ├─> workspace context set meridian-research  → Active Context (meridian-research)
    │
    ├─> workspace context set none                → No Context
    │
    └─> workspace context show                   → Display current context
```

---

## Implementation

### 1. Workspace Context Manager

#### `workspace/context/context_manager.py`

```python
"""
Workspace Context Manager

Manages work context - which repo you're working in today.
All operations are scoped to the active context.

Usage:
    workspace init meridian-core          # Set initial context
    workspace context set meridian-research  # Switch context
    workspace context show                 # Show current context
    workspace context reset                # Clear context
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from ..db.workspace_db import WorkspaceDB


class ContextState(Enum):
    """Context state."""
    NO_CONTEXT = "no_context"
    ACTIVE = "active"
    SUSPENDED = "suspended"


@dataclass
class WorkContext:
    """Work context - which repo you're working in."""
    repo: str  # meridian-core, meridian-research, meridian-trading
    repo_path: Path  # Full path to repo
    workspace_path: Path  # Workspace root
    activated_at: datetime
    activated_by: str  # user/session
    context_id: str  # Unique context ID
    
    # Context metadata
    previous_context: Optional[str] = None
    context_notes: Optional[str] = None
    
    # Active operations
    active_task_id: Optional[str] = None
    active_session_id: Optional[str] = None


class ContextManager:
    """Manages workspace context."""
    
    def __init__(self, workspace_root: Path, db: Optional[WorkspaceDB] = None):
        """
        Initialize context manager.
        
        Args:
            workspace_root: Workspace root directory
            db: Workspace database (optional)
        """
        self.workspace_root = Path(workspace_root)
        self.context_file = self.workspace_root / ".workspace-context.json"
        self.db = db
        
        # Available repos
        self.available_repos = {
            "meridian-core": self.workspace_root / "meridian-core",
            "meridian-research": self.workspace_root / "meridian-research",
            "meridian-trading": self.workspace_root / "meridian-trading",
        }
    
    def get_current_context(self) -> Optional[WorkContext]:
        """Get current work context."""
        if not self.context_file.exists():
            return None
        
        try:
            import json
            with open(self.context_file) as f:
                data = json.load(f)
            
            return WorkContext(
                repo=data["repo"],
                repo_path=Path(data["repo_path"]),
                workspace_path=Path(data["workspace_path"]),
                activated_at=datetime.fromisoformat(data["activated_at"]),
                activated_by=data["activated_by"],
                context_id=data["context_id"],
                previous_context=data.get("previous_context"),
                context_notes=data.get("context_notes"),
                active_task_id=data.get("active_task_id"),
                active_session_id=data.get("active_session_id"),
            )
        except Exception as e:
            print(f"⚠️  Error reading context: {e}")
            return None
    
    def set_context(self, repo: str, notes: Optional[str] = None) -> WorkContext:
        """
        Set work context to a repo.
        
        Args:
            repo: Repo name (meridian-core, meridian-research, meridian-trading)
            notes: Optional context notes
        
        Returns:
            WorkContext instance
        """
        if repo not in self.available_repos:
            raise ValueError(f"Unknown repo: {repo}. Available: {list(self.available_repos.keys())}")
        
        repo_path = self.available_repos[repo]
        
        if not repo_path.exists():
            raise ValueError(f"Repo path does not exist: {repo_path}")
        
        # Get previous context
        previous_context = None
        current = self.get_current_context()
        if current:
            previous_context = current.repo
        
        # Create new context
        context = WorkContext(
            repo=repo,
            repo_path=repo_path,
            workspace_path=self.workspace_root,
            activated_at=datetime.now(),
            activated_by=self._get_user(),
            context_id=self._generate_context_id(),
            previous_context=previous_context,
            context_notes=notes,
        )
        
        # Save context
        self._save_context(context)
        
        # Log context switch
        if self.db:
            self.db.log_context_switch(context)
        
        return context
    
    def clear_context(self):
        """Clear current context."""
        if self.context_file.exists():
            self.context_file.unlink()
    
    def _save_context(self, context: WorkContext):
        """Save context to file."""
        import json
        
        data = {
            "repo": context.repo,
            "repo_path": str(context.repo_path),
            "workspace_path": str(context.workspace_path),
            "activated_at": context.activated_at.isoformat(),
            "activated_by": context.activated_by,
            "context_id": context.context_id,
            "previous_context": context.previous_context,
            "context_notes": context.context_notes,
            "active_task_id": context.active_task_id,
            "active_session_id": context.active_session_id,
        }
        
        with open(self.context_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _get_user(self) -> str:
        """Get current user."""
        import os
        return os.getenv("USER", "unknown")
    
    def _generate_context_id(self) -> str:
        """Generate unique context ID."""
        import uuid
        return str(uuid.uuid4())[:8]
```

### 2. Context-Aware Operations

#### `workspace/context/context_aware.py`

```python
"""
Context-aware operations.

All operations automatically use the active context.
"""

from pathlib import Path
from typing import Optional

from .context_manager import ContextManager, WorkContext


class ContextAware:
    """Context-aware operation wrapper."""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
    
    def get_repo_path(self) -> Path:
        """Get current repo path."""
        context = self.context_manager.get_current_context()
        if not context:
            raise RuntimeError("No active context. Run: workspace context set <repo>")
        return context.repo_path
    
    def get_repo_name(self) -> str:
        """Get current repo name."""
        context = self.context_manager.get_current_context()
        if not context:
            raise RuntimeError("No active context. Run: workspace context set <repo>")
        return context.repo
    
    def ensure_context(self):
        """Ensure context is set, raise error if not."""
        context = self.context_manager.get_current_context()
        if not context:
            raise RuntimeError("No active context. Run: workspace context set <repo>")
    
    def execute_in_context(self, func, *args, **kwargs):
        """
        Execute function in context.
        
        Changes working directory to repo, executes function, returns to workspace.
        """
        import os
        from contextlib import contextmanager
        
        @contextmanager
        def context_switch():
            original_cwd = os.getcwd()
            try:
                repo_path = self.get_repo_path()
                os.chdir(repo_path)
                yield repo_path
            finally:
                os.chdir(original_cwd)
        
        with context_switch():
            return func(*args, **kwargs)
```

### 3. CLI Interface

#### `workspace/cli/workspace_cli.py`

```python
"""
Workspace CLI - Context management commands.

Usage:
    workspace init <repo>              # Initialize workspace and set context
    workspace context set <repo>       # Set work context
    workspace context show             # Show current context
    workspace context reset            # Clear context
    workspace context list             # List available repos
    workspace task add <title>         # Add task (scoped to context)
    workspace task list                # List tasks (filtered by context)
"""

import click
from pathlib import Path

from ..context.context_manager import ContextManager
from ..context.context_aware import ContextAware
from ..db.workspace_db import WorkspaceDB


@click.group()
@click.pass_context
def workspace(ctx):
    """Workspace context management."""
    workspace_root = Path.cwd()
    ctx.ensure_object(dict)
    ctx.obj['workspace_root'] = workspace_root
    ctx.obj['context_manager'] = ContextManager(workspace_root)
    ctx.obj['db'] = WorkspaceDB(workspace_root / "workspace.db")


@workspace.command()
@click.argument('repo')
@click.option('--notes', help='Context notes')
@click.pass_context
def init(ctx, repo, notes):
    """Initialize workspace and set context to repo."""
    context_manager = ctx.obj['context_manager']
    
    try:
        context = context_manager.set_context(repo, notes)
        click.echo(f"✅ Workspace initialized")
        click.echo(f"   Active context: {context.repo}")
        click.echo(f"   Repo path: {context.repo_path}")
        click.echo(f"   Context ID: {context.context_id}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@workspace.group()
def context():
    """Context management commands."""
    pass


@context.command('set')
@click.argument('repo')
@click.option('--notes', help='Context notes')
@click.pass_context
def set_context(ctx, repo, notes):
    """Set work context to repo."""
    context_manager = ctx.obj['context_manager']
    
    try:
        context = context_manager.set_context(repo, notes)
        click.echo(f"✅ Context set to: {context.repo}")
        click.echo(f"   Repo path: {context.repo_path}")
        
        if context.previous_context:
            click.echo(f"   Previous: {context.previous_context}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@context.command('show')
@click.pass_context
def show_context(ctx):
    """Show current context."""
    context_manager = ctx.obj['context_manager']
    
    context = context_manager.get_current_context()
    if not context:
        click.echo("⚠️  No active context")
        click.echo("   Run: workspace context set <repo>")
    else:
        click.echo(f"Active context: {context.repo}")
        click.echo(f"Repo path: {context.repo_path}")
        click.echo(f"Activated: {context.activated_at}")
        click.echo(f"Context ID: {context.context_id}")
        
        if context.active_task_id:
            click.echo(f"Active task: {context.active_task_id}")
        
        if context.context_notes:
            click.echo(f"Notes: {context.context_notes}")


@context.command('reset')
@click.pass_context
def reset_context(ctx):
    """Clear current context."""
    context_manager = ctx.obj['context_manager']
    context_manager.clear_context()
    click.echo("✅ Context cleared")


@context.command('list')
@click.pass_context
def list_repos(ctx):
    """List available repos."""
    context_manager = ctx.obj['context_manager']
    
    click.echo("Available repos:")
    for repo_name, repo_path in context_manager.available_repos.items():
        exists = "✅" if repo_path.exists() else "❌"
        click.echo(f"  {exists} {repo_name}: {repo_path}")
```

### 4. Context File Format

#### `.workspace-context.json`

```json
{
  "repo": "meridian-core",
  "repo_path": "/Users/simonerses/data-projects/meridian-core",
  "workspace_path": "/Users/simonerses/data-projects",
  "activated_at": "2025-11-20T14:00:00",
  "activated_by": "simonerses",
  "context_id": "a1b2c3d4",
  "previous_context": "meridian-research",
  "context_notes": "Working on learning integration",
  "active_task_id": "WS-TASK-002",
  "active_session_id": "2025-11-20-session-001"
}
```

---

## Usage Patterns

### Pattern 1: Daily Workflow

```bash
# Start of day - set context
cd /Users/simonerses/data-projects
workspace context set meridian-core

# All operations are now scoped to meridian-core
workspace task add "Implement learning integration"
workspace task list  # Shows tasks for meridian-core

# Switch context if needed
workspace context set meridian-research

# End of day - can clear context or leave it
workspace context show
```

### Pattern 2: Context-Aware Operations

```python
from workspace.context.context_manager import ContextManager
from workspace.context.context_aware import ContextAware

# Initialize
context_manager = ContextManager(Path.cwd())
context_aware = ContextAware(context_manager)

# Operations automatically use context
repo_path = context_aware.get_repo_path()  # Returns current repo path
repo_name = context_aware.get_repo_name()  # Returns current repo name

# Execute in context
def run_tests():
    import subprocess
    subprocess.run(["pytest", "tests/"])

context_aware.execute_in_context(run_tests)  # Runs in repo directory
```

### Pattern 3: Cross-Repo Operations

```python
# From workspace, work across repos
context_manager = ContextManager(workspace_root)

# Set context to core
context_manager.set_context("meridian-core")
# ... work on core ...

# Switch to research
context_manager.set_context("meridian-research")
# ... work on research ...

# Back to workspace management
context_manager.clear_context()
# ... workspace-level operations ...
```

---

## Database Integration

### Track Context Switches

```sql
-- Add to workspace.db

CREATE TABLE context_switches (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    repo_path TEXT NOT NULL,
    activated_at TIMESTAMP NOT NULL,
    activated_by TEXT,
    context_id TEXT,
    previous_context TEXT,
    context_notes TEXT,
    duration_seconds REAL,  -- How long context was active
    operations_count INTEGER,  -- Number of operations in context
    created_at TIMESTAMP NOT NULL
);
```

### Context-Aware Task Filtering

```python
# When listing tasks, filter by context
def get_tasks_for_context(context: WorkContext) -> List[Task]:
    """Get tasks relevant to current context."""
    # Get tasks for this repo
    repo_tasks = db.get_tasks_for_repo(context.repo)
    
    # Get cross-repo tasks that affect this repo
    cross_repo_tasks = db.get_tasks_affecting_repo(context.repo)
    
    return repo_tasks + cross_repo_tasks
```

---

## Benefits

### 1. Single Command Center

✅ **Work from workspace root always**
- No need to `cd` between repos
- All operations from one location
- Better visibility across repos

### 2. Context-Aware Operations

✅ **All operations automatically scoped**
- Tasks filtered by context
- Commands run in correct repo
- Less context switching overhead

### 3. Management Plane Separation

✅ **Clear separation of concerns**
- Workspace = Management/Orchestration
- Repos = Execution/Implementation
- Governance at workspace level

### 4. Better Coordination

✅ **Cross-repo work easier**
- See all repos from workspace
- Coordinate across repos
- Track dependencies

### 5. Session Continuity

✅ **Context persists across sessions**
- Context file tracks active repo
- Resume work where you left off
- Better session handoff

---

## Architecture Decision

### Recommended Approach: **Hybrid Context System**

**Management Plane Operations** (Always in workspace):
- Task management
- Architecture tracking
- Drift detection
- Cross-repo coordination
- Governance

**Execution Plane Operations** (Context-scoped):
- Code changes
- Testing
- Repo-specific operations
- Git operations

**Context-Aware Filtering:**
- Tasks filtered by context
- Commands scoped to context
- Operations execute in repo path

---

## Implementation Plan

### Phase 1: Core Context System

1. **Create context manager**
   - `workspace/context/context_manager.py`
   - Context file (`.workspace-context.json`)
   - Context switching logic

2. **Create CLI commands**
   - `workspace context set <repo>`
   - `workspace context show`
   - `workspace context reset`

### Phase 2: Context-Aware Operations

1. **Context-aware wrapper**
   - Operations automatically use context
   - Path resolution scoped to context
   - Command execution in context

2. **Task filtering**
   - Tasks filtered by active context
   - Cross-repo tasks visible when relevant

### Phase 3: Database Integration

1. **Track context switches**
   - Log context changes
   - Track context duration
   - Analytics on context usage

2. **Context-aware queries**
   - Tasks by context
   - Issues by context
   - Decisions by context

---

## Summary

### What You Asked For

✅ **Work in workspace folder** - Yes, always work from workspace root

✅ **Context session** - Set context to identify active repo

✅ **Requests scoped to context** - Operations automatically use context

✅ **Management plane** - Workspace handles orchestration/governance

✅ **Architecture awareness** - Requests checked against repo architecture

### Architecture Recommendation

**Pattern:** **Management Plane / Execution Plane Separation**

- **Management Plane (Workspace):**
  - Governance
  - Task tracking
  - Architecture tracking
  - Cross-repo coordination

- **Execution Plane (Repos):**
  - Code implementation
  - Testing
  - Repo-specific operations

- **Context Bridge:**
  - Context-aware operations
  - Automatic scoping
  - Seamless switching

**This is a strong architectural pattern** - similar to Kubernetes, Docker, or modern IDEs with multi-workspace support.

---

**Last Updated:** 2025-11-20  
**Status:** Architecture Design Complete - Ready for Implementation

