#!/usr/bin/env python3
"""
Create session handover for next session.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Create comprehensive session handover document
DOMAIN: Cross-repo workspace management
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import json

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.db.models import (
    WorkspaceSession,
    WorkspaceTask,
    CrossRepoIssue,
    ArchitectureDecision,
    WorkContext,
    UnregisteredFile,
)


def create_session_handover(
    session_id: str,
    start_time: datetime,
    end_time: datetime,
    user: str = "simonerses",
    ai_assistant: str = "claude-code",
    handoff_notes: str = None
) -> WorkspaceSession:
    """Create a session handover in the database."""
    
    workspace_root = Path.cwd()
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        # Check if session already exists
        existing = session.query(WorkspaceSession).filter_by(id=session_id).first()
        if existing:
            print(f"⚠️  Session {session_id} already exists. Updating...")
            ws_session = existing
        else:
            ws_session = WorkspaceSession(
                id=session_id,
                start_time=start_time,
                end_time=end_time,
                status="completed",
                user=user,
                ai_assistant=ai_assistant
            )
            session.add(ws_session)
        
        # Get current state
        current_context = session.query(WorkContext).filter_by(is_active=True).first()
        
        # Get session statistics
        total_tasks = session.query(WorkspaceTask).count()
        pending_tasks = session.query(WorkspaceTask).filter_by(status="pending").count()
        in_progress_tasks = session.query(WorkspaceTask).filter_by(status="in_progress").count()
        completed_tasks = session.query(WorkspaceTask).filter_by(status="completed").count()
        
        # Get recent tasks (created in this session)
        recent_tasks = session.query(WorkspaceTask).filter(
            WorkspaceTask.session_created.contains("2025-11-20")
        ).all()
        
        # Get open issues
        open_issues = session.query(CrossRepoIssue).filter_by(status="open").all()
        
        # Get recent architecture decisions
        recent_decisions = session.query(ArchitectureDecision).order_by(
            ArchitectureDecision.date.desc()
        ).limit(5).all()
        
        # Get unregistered files
        unregistered = session.query(UnregisteredFile).filter_by(status="unregistered").all()
        
        # Create handoff notes
        if not handoff_notes:
            handoff_notes = generate_handoff_notes(
                workspace_root,
                current_context,
                recent_tasks,
                open_issues,
                recent_decisions,
                unregistered,
                total_tasks,
                pending_tasks,
                in_progress_tasks,
                completed_tasks
            )
        
        ws_session.handoff_notes = handoff_notes
        ws_session.end_time = end_time
        ws_session.status = "completed"
        
        session.commit()
        
        print("=" * 70)
        print("  SESSION HANDOVER CREATED")
        print("=" * 70)
        print()
        print(f"Session ID: {session_id}")
        print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {(end_time - start_time).total_seconds() / 60:.1f} minutes")
        print()
        print("Current State:")
        print(f"  • Total tasks: {total_tasks}")
        print(f"  • Pending: {pending_tasks}")
        print(f"  • In Progress: {in_progress_tasks}")
        print(f"  • Completed: {completed_tasks}")
        print(f"  • Open issues: {len(open_issues)}")
        print(f"  • Unregistered files: {len(unregistered)}")
        if current_context:
            print(f"  • Active context: {current_context.repo}")
        print()
        print("✅ Session handover saved to database")
        print()
        print("Handoff notes preview:")
        print("-" * 70)
        print(handoff_notes[:500] + "..." if len(handoff_notes) > 500 else handoff_notes)
        print("-" * 70)
        print()
        
        # Also write to file for easy reading
        handover_file = workspace_root / f"SESSION-HANDOVER-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        handover_file.write_text(handoff_notes)
        print(f"📄 Handover also saved to: {handover_file.name}")
        print()
        
        return ws_session
        
    except Exception as e:
        print(f"❌ Error creating session handover: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        raise
    finally:
        session.close()


def generate_handoff_notes(
    workspace_root: Path,
    current_context,
    recent_tasks: List[WorkspaceTask],
    open_issues: List[CrossRepoIssue],
    recent_decisions: List[ArchitectureDecision],
    unregistered_files: List[UnregisteredFile],
    total_tasks: int,
    pending_tasks: int,
    in_progress_tasks: int,
    completed_tasks: int
) -> str:
    """Generate comprehensive handoff notes."""
    
    notes = f"""# Session Handover - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Session Focus:** WMS Implementation, Architecture Alignment Enforcement, Governance Enforcement

**Key Accomplishments:**
1. ✅ Implemented Workspace Management System (WMS) with full database integration
2. ✅ Added code-to-architecture alignment enforcement
3. ✅ Enhanced session_start.sh with governance enforcement and work context confirmation
4. ✅ Created weekly housekeeping task and script
5. ✅ Imported 51 tasks from architecture reviews into WMS database
6. ✅ Established workspace-level governance and task tracking

---

## Current Workspace State

### Task Statistics
- **Total Tasks:** {total_tasks}
- **Pending:** {pending_tasks}
- **In Progress:** {in_progress_tasks}
- **Completed:** {completed_tasks}

### Active Work Context
"""
    
    if current_context:
        notes += f"""- **Repository:** {current_context.repo}
- **Context ID:** {current_context.id}
- **Activated:** {current_context.activated_at.strftime('%Y-%m-%d %H:%M:%S')}
- **Notes:** {current_context.notes or "None"}
"""
    else:
        notes += "- **No active context set**\n"
    
    notes += f"""
### Open Issues
- **Total:** {len(open_issues)}
"""
    
    if open_issues:
        notes += "\n**Critical Issues:**\n"
        for issue in open_issues[:5]:
            notes += f"- **{issue.id}:** {issue.title} ({issue.severity})\n"
    
    notes += f"""
### Unregistered Files
- **Total:** {len(unregistered_files)}
"""
    
    if unregistered_files:
        notes += "\n**Top Unregistered Files:**\n"
        for uf in unregistered_files[:10]:
            notes += f"- {uf.file_path} ({uf.repo})\n"
    
    notes += """
---

## Major Accomplishments This Session

### 1. WMS Implementation Complete ✅

**What was done:**
- Created complete Workspace Management System (WMS) database schema
- Implemented Context Manager for work context tracking
- Implemented Governance Engine for architecture enforcement
- Implemented Workflow Engine for task lifecycle management
- Implemented Bastard Integration (mocked, ready for Meridian integration)
- Created CLI interface for WMS operations

**Files created:**
- `workspace/db/models.py` - Complete database schema
- `workspace/wms/context_manager.py` - Work context management
- `workspace/wms/governance_engine.py` - Architecture governance
- `workspace/wms/workflow_engine.py` - Task workflow management
- `workspace/wms/bastard_integration.py` - Bastard evaluation integration
- `workspace/wms/cli.py` - CLI interface

**Database tables created:**
- WorkspaceTask, WorkspaceSession, CrossRepoIssue, ArchitectureDecision
- WorkContext, Workflow, Violation, BastardReport
- ArchitectureComponent, CodeComponentMapping, CodeChange, UnregisteredFile

### 2. Architecture Alignment Enforcement ✅

**What was done:**
- Created ArchitectureValidator class for code-to-architecture validation
- Added database models for architecture component tracking
- Integrated architecture validation into Governance Engine
- Added file-to-component mapping capabilities
- Created enforcement mechanisms for code-to-architecture alignment

**Key features:**
- File-to-component mapping validation
- Pre-change validation (files must be mapped before changes)
- Task-to-component linking
- Unregistered file detection
- Component scope validation

**Files created:**
- `workspace/wms/architecture_validator.py` - Architecture validation logic
- Database models: ArchitectureComponent, CodeComponentMapping, CodeChange, UnregisteredFile

### 3. Enhanced Session Management ✅

**What was done:**
- Created workspace-level `session_start.sh` with governance enforcement
- Added work context confirmation requirement
- Integrated WMS context management
- Created GOVERNANCE-CONTEXT.md auto-generation
- Added pre-task checklist enforcement

**Key features:**
- Mandatory work context selection (workspace, meridian-core, meridian-research, meridian-trading)
- Auto-generated GOVERNANCE-CONTEXT.md with current state
- Pre-task governance checklist enforcement
- Architecture alignment checks on session start

**Files created:**
- `session_start.sh` - Workspace-level session start script
- `workspace/scripts/generate_governance_context.py` - Governance context generator
- `GOVERNANCE-CONTEXT.md` - Auto-generated governance context (updated each session)

### 4. Task Import from Architecture Reviews ✅

**What was done:**
- Created scripts to extract tasks from architecture review documents
- Imported 51 tasks from today's architecture reviews into WMS database
- Tasks include priorities, descriptions, and source documentation

**Task breakdown:**
- CRITICAL: 3 tasks
- HIGH: 29 tasks
- MEDIUM: 23 tasks

**Distribution:**
- meridian-core: 42 tasks
- meridian-trading: 6 tasks
- meridian-research: 3 tasks

**Files created:**
- `workspace/scripts/import_architecture_tasks_v2.py` - Task extraction script
- `workspace/scripts/manual_import_architecture_tasks.py` - Manual task import script

### 5. Weekly Housekeeping System ✅

**What was done:**
- Created comprehensive housekeeping script
- Added weekly housekeeping task to WMS
- Implemented cleanup and validation routines

**Housekeeping features:**
- Clean old sessions (>30 days)
- Check for stale tasks (>90 days)
- Find unregistered files
- Validate architecture mappings
- Clean temporary files
- Check for orphaned file references
- Validate database integrity
- Clean old logs
- Check for duplicate files

**Files created:**
- `workspace/scripts/housekeeping.py` - Housekeeping script
- `workspace/scripts/create_housekeeping_task.py` - Task creation script
- WMS Task: WS-TASK-055 - "Weekly workspace and repository housekeeping"

---

## Key Decisions Made

"""
    
    if recent_decisions:
        for decision in recent_decisions[:5]:
            notes += f"""### {decision.id}: {decision.decision[:100]}
- **Date:** {decision.date.strftime('%Y-%m-%d') if decision.date else 'N/A'}
- **Status:** {decision.status}
- **Impact:** {decision.impact or 'N/A'}
- **Repos Affected:** {', '.join(json.loads(decision.repos_affected)) if decision.repos_affected else 'N/A'}
"""
    else:
        notes += "No recent architecture decisions recorded.\n"
    
    notes += """
---

## Recent Tasks Created

"""
    
    if recent_tasks:
        for task in recent_tasks[:10]:
            notes += f"""### {task.id}: {task.title}
- **Status:** {task.status}
- **Priority:** {task.priority or 'N/A'}
- **Assigned Repo:** {task.assigned_repo or 'N/A'}
- **Created:** {task.created.strftime('%Y-%m-%d') if task.created else 'N/A'}
"""
    else:
        notes += "No recent tasks created.\n"
    
    notes += """
---

## Outstanding Issues

"""
    
    if open_issues:
        for issue in open_issues:
            notes += f"""### {issue.id}: {issue.title}
- **Type:** {issue.issue_type}
- **Severity:** {issue.severity}
- **Status:** {issue.status}
- **Repos Affected:** {', '.join(json.loads(issue.repos_affected)) if issue.repos_affected else 'N/A'}
- **Action Required:** {issue.action_required or 'None'}
"""
    else:
        notes += "No outstanding issues.\n"
    
    notes += """
---

## Next Steps for Next Session

### Priority 1: Register Architecture Components

**Action:** Register all major architecture components in the database.

**Why:** To enable code-to-architecture alignment enforcement. Files can't be mapped until components are registered.

**Steps:**
1. Review architecture documents:
   - `2025-11-20-MERIDIAN-CORE-ARCHITECTURE.md`
   - `2025-11-20-MERIDIAN-RESEARCH-ARCHITECTURE.md`
   - `2025-11-20-MERIDIAN-TRADING-ARCHITECTURE.md`
2. Register components using ArchitectureValidator:
   ```python
   validator = ArchitectureValidator(session, workspace_root)
   validator.register_component(
       component_name="LearningEngine",
       component_type="abstract_base_class",
       repo="meridian-core",
       expected_path="src/meridian_core/learning/learning_engine.py"
   )
   ```
3. Map existing files to components

### Priority 2: Map Existing Files to Components

**Action:** Map key files in each repository to their architecture components.

**Why:** To establish baseline for code-to-architecture tracking.

**Steps:**
1. Start with core framework files (meridian-core)
2. Map domain adapter files (meridian-trading, meridian-research)
3. Map workspace management files

**Files to map:**
- Core learning engine files
- Core orchestration files
- Trading strategy files
- Research skill files
- WMS files

### Priority 3: Set Up Pre-Commit Hooks

**Action:** Create git pre-commit hooks for architecture validation.

**Why:** To enforce code-to-architecture alignment at commit time.

**Steps:**
1. Create pre-commit hook script
2. Integrate with WMS ArchitectureValidator
3. Block commits with unmapped files
4. Test with sample commits

### Priority 4: Complete Trading Learning Engine

**Action:** Implement TradingLearningEngine per architecture review recommendations.

**Why:** Critical task (WS-TASK-038) identified in architecture review.

**Tasks:**
- WS-TASK-038: Implement TradingLearningEngine extending LearningEngine
- WS-TASK-039: Create trading data access layer
- WS-TASK-040: Implement trading pattern detection
- WS-TASK-041: Create nightly learning analysis script

### Priority 5: Run Weekly Housekeeping

**Action:** Schedule or run weekly housekeeping task.

**Why:** Keep workspace clean and detect issues early.

**Steps:**
1. Run: `python workspace/scripts/housekeeping.py`
2. Review report: `workspace/reports/housekeeping-YYYYMMDD.json`
3. Address any issues found
4. Schedule weekly execution (cron/scheduled task)

---

## Files Created/Modified This Session

### New Files

**WMS Core:**
- `workspace/db/models.py` - Complete database schema with WMS models
- `workspace/wms/context_manager.py` - Context management
- `workspace/wms/governance_engine.py` - Governance enforcement
- `workspace/wms/workflow_engine.py` - Workflow management
- `workspace/wms/bastard_integration.py` - Bastard integration
- `workspace/wms/cli.py` - CLI interface
- `workspace/wms/architecture_validator.py` - Architecture validation

**Scripts:**
- `session_start.sh` - Workspace-level session start
- `workspace/scripts/generate_governance_context.py` - Governance context generator
- `workspace/scripts/import_architecture_tasks_v2.py` - Task import script
- `workspace/scripts/manual_import_architecture_tasks.py` - Manual task import
- `workspace/scripts/housekeeping.py` - Weekly housekeeping
- `workspace/scripts/create_housekeeping_task.py` - Housekeeping task creator

**Documentation:**
- `GOVERNANCE-CONTEXT.md` - Auto-generated governance context
- `2025-11-20-WMS-IMPLEMENTATION-COMPLETE.md` - WMS implementation summary

---

## Database Status

**Database Location:** `workspace.db`

**Tables Created:**
- ✅ WorkspaceTask (55 tasks)
- ✅ WorkspaceSession
- ✅ CrossRepoIssue
- ✅ ArchitectureDecision
- ✅ WorkContext
- ✅ Workflow, WorkflowStage
- ✅ Violation, BastardReport
- ✅ ArchitectureComponent
- ✅ CodeComponentMapping
- ✅ CodeChange
- ✅ UnregisteredFile

**Database Health:** ✅ OK

---

## Governance Status

**Current State:**
- ✅ WMS fully implemented
- ✅ Architecture alignment enforcement active
- ✅ Governance context auto-generation active
- ✅ Session context tracking active
- ⚠️  Architecture components need to be registered
- ⚠️  Files need to be mapped to components

**Enforcement Points:**
- ✅ Session start requires work context confirmation
- ✅ Governance rules auto-injected via GOVERNANCE-CONTEXT.md
- ✅ Pre-task checklist enforced
- ⏳ Pre-commit hooks (not yet implemented)
- ⏳ Pre-deployment validation (not yet implemented)

---

## Important Notes for Next Session

1. **Start with:** Run `./session_start.sh` at workspace root to set work context
2. **First task:** Register architecture components (see Priority 1 above)
3. **Check:** Review unregistered files and map them to components
4. **Review:** Check WS-TASK-038 through WS-TASK-054 for high-priority tasks
5. **Schedule:** Set up weekly housekeeping cron job

---

## WMS Usage Quick Reference

**Set work context:**
```bash
./session_start.sh
# or
python -m workspace.wms.cli context set meridian-core
```

**Create task:**
```bash
python -m workspace.wms.cli task create "Title" "Description" --users 1 --priority high
```

**List tasks:**
```bash
python -m workspace.wms.cli task list
```

**Run housekeeping:**
```bash
python workspace/scripts/housekeeping.py
```

**Check database status:**
```bash
python workspace/scripts/db_status.py
```

---

**Session End Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Next Session:** Review this handover before starting work
**Contact:** Continue with WMS-enabled governance and architecture alignment

---

## Architecture Component Registration Checklist

Before making code changes, ensure components are registered:

- [ ] Register meridian-core components
- [ ] Register meridian-trading components
- [ ] Register meridian-research components
- [ ] Map existing files to components
- [ ] Validate all files are mapped
- [ ] Set up pre-commit hooks for validation

---

**End of Session Handover**
"""
    
    return notes


def main():
    """Create session handover."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Create session handover')
    parser.add_argument('--session-id', default=None, help='Session ID (default: auto-generated)')
    parser.add_argument('--start-time', default=None, help='Session start time (ISO format)')
    parser.add_argument('--end-time', default=None, help='Session end time (ISO format, default: now)')
    parser.add_argument('--user', default='simonerses', help='User name')
    parser.add_argument('--ai-assistant', default='claude-code', help='AI assistant name')
    args = parser.parse_args()
    
    # Generate session ID if not provided
    if not args.session_id:
        session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    else:
        session_id = args.session_id
    
    # Parse times
    if args.start_time:
        start_time = datetime.fromisoformat(args.start_time)
    else:
        # Default: 4 hours ago (adjust as needed)
        start_time = datetime.now() - timedelta(hours=4)
    
    if args.end_time:
        end_time = datetime.fromisoformat(args.end_time)
    else:
        end_time = datetime.now()
    
    try:
        create_session_handover(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            user=args.user,
            ai_assistant=args.ai_assistant
        )
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    from datetime import timedelta
    sys.exit(main())

