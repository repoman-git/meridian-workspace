#!/usr/bin/env python3
"""
Manually import specific tasks from architecture reviews into WMS.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Import well-defined tasks from architecture reviews
DOMAIN: Cross-repo workspace management
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.governance_engine import GovernanceEngine
from workspace.wms.bastard_integration import BastardIntegration
from workspace.wms.workflow_engine import WorkflowEngine


# Define specific tasks from architecture reviews
ARCHITECTURE_TASKS = [
    # From ARCHITECTURE-REVIEW-2025-11-20.md - Priority 1
    {
        'title': 'Implement TradingLearningEngine extending LearningEngine',
        'description': '''Implement TradingLearningEngine for meridian-trading domain.

Priority 1: Complete meridian-trading Self-Learning

This is the missing self-learning implementation for the trading domain. The structure exists but no actual implementation.

Actions:
1. Implement `TradingLearningEngine` extending `LearningEngine` from meridian-core
2. Create trading data access layer
3. Implement trading pattern detection
4. Create nightly analysis script
5. Integrate with ProposalManager

Files to Create:
- src/meridian_trading/learning/trading_learning_engine.py
- src/meridian_trading/learning/trading_data.py
- src/meridian_trading/learning/pattern_detector.py
- src/meridian_trading/learning/trading_metrics.py
- scripts/nightly_learning_analysis.py

Impact: Trading domain can't learn from performance without this implementation.
Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-trading', 'meridian-core'],
        'source': 'ARCHITECTURE-REVIEW-2025-11-20.md',
        'type': 'implementation'
    },
    {
        'title': 'Create trading data access layer',
        'description': '''Create trading data access layer for TradingLearningEngine.

This will access trading data from data/positions.db and provide it to the learning engine for analysis.

Part of Priority 1: Complete meridian-trading Self-Learning

File: src/meridian_trading/learning/trading_data.py

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-trading'],
        'source': 'ARCHITECTURE-REVIEW-2025-11-20.md',
        'type': 'implementation'
    },
    {
        'title': 'Implement trading pattern detection',
        'description': '''Implement trading pattern detection for TradingLearningEngine.

Detect patterns in trading performance such as:
- TDOM patterns
- Losing streaks
- Strategy effectiveness
- Market conditions

Part of Priority 1: Complete meridian-trading Self-Learning

File: src/meridian_trading/learning/pattern_detector.py

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-trading'],
        'source': 'ARCHITECTURE-REVIEW-2025-11-20.md',
        'type': 'implementation'
    },
    {
        'title': 'Create nightly learning analysis script',
        'description': '''Create nightly analysis script for trading learning.

Script that runs automated learning cycles to analyze recent trades and generate proposals.

Part of Priority 1: Complete meridian-trading Self-Learning

File: scripts/nightly_learning_analysis.py

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-trading'],
        'source': 'ARCHITECTURE-REVIEW-2025-11-20.md',
        'type': 'automation'
    },
    {
        'title': 'Verify meridian-research learning bridge integration',
        'description': '''Verify learning bridge fully integrates with meridian-core.

Priority 2: Verify meridian-research Integration

Actions:
1. Verify learning bridge fully integrates with meridian-core
2. Ensure proposals flow to core's ProposalManager
3. Verify feedback bridge integration
4. Test learning cycles end-to-end

Files to Review:
- src/meridian_research/learning/bridge.py
- src/meridian_research/learning/session_store.py
- Verify integration with meridian_core.learning.ProposalManager

Priority: MEDIUM''',
        'priority': 'MEDIUM',
        'repos_affected': ['meridian-research', 'meridian-core'],
        'source': 'ARCHITECTURE-REVIEW-2025-11-20.md',
        'type': 'verification'
    },
    {
        'title': 'Consolidate Proposal vs LearningProposal database schemas',
        'description': '''Consolidate or document distinction between Proposal and LearningProposal schemas.

Critical Issue: Database Schema Duplication

The meridian-core database has both:
- Proposal table (used by ProposalManager)
- LearningProposal table (different schema)

Question: Why two proposal tables? Should they be merged?

Action: Consolidate schemas or document distinction clearly

Priority: MEDIUM''',
        'priority': 'MEDIUM',
        'repos_affected': ['meridian-core'],
        'source': 'ARCHITECTURE-REVIEW-2025-11-20.md',
        'type': 'refactoring'
    },
    {
        'title': 'Document database usage and standardize naming',
        'description': '''Document database usage clearly and standardize naming.

Priority 3: Database Consolidation

Actions:
1. Document database usage clearly
2. Consolidate proposal schemas (or document why two exist)
3. Standardize database naming
4. Ensure all databases use WAL mode
5. Create database migration guide

Current issues:
- Multiple databases (proposals.db, decisions.db, meridian.db)
- Some tables in main meridian.db, others in separate DBs
- Inconsistent - should standardize

Priority: MEDIUM''',
        'priority': 'MEDIUM',
        'repos_affected': ['meridian-core', 'meridian-research', 'meridian-trading'],
        'source': 'ARCHITECTURE-REVIEW-2025-11-20.md',
        'type': 'documentation'
    },
    
    # From meridian-core review - Critical
    {
        'title': 'Migrate task_queue/registry to SQLite for concurrency',
        'description': '''Migrate task_queue/registry to SQLite to fix concurrency/file I/O issues.

Critical (Blockers - Address Immediately)

Files: orchestrator.py, autonomous_orchestrator.py
Effort: 2 days

Current issue: File-based state management poses scalability and concurrency risks.
Solution: Move to SQLite with proper connection pooling and WAL mode.

Priority: CRITICAL''',
        'priority': 'CRITICAL',
        'repos_affected': ['meridian-core'],
        'source': 'review_architecture_20251116_094525.md',
        'type': 'refactoring'
    },
    {
        'title': 'Add comprehensive tests with >80% coverage',
        'description': '''Add comprehensive tests focusing on integration flows.

Critical (Blockers - Address Immediately)

New: tests/ directory
Effort: 3-5 days

Focus on integration flows. Current test coverage is insufficient for production readiness.

Priority: CRITICAL''',
        'priority': 'CRITICAL',
        'repos_affected': ['meridian-core'],
        'source': 'review_architecture_20251116_094525.md',
        'type': 'testing'
    },
    {
        'title': 'Refactor AutonomousOrchestrator to reduce god-class complexity',
        'description': '''Split AutonomousOrchestrator into composable classes.

High (Significant Impact - Address Next Sprint)

File: autonomous_orchestrator.py
Effort: 1-2 days

The class has grown into a 'God Object', tightly coupling many subsystems. Refactor to improve testability and maintainability.

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-core'],
        'source': 'review_architecture_20251116_094525.md',
        'type': 'refactoring'
    },
    {
        'title': 'Enhance pattern detection with statistical thresholds',
        'description': '''Add statistical thresholds and correlations in learning.

High (Significant Impact - Address Next Sprint)

File: orchestration_learning_engine.py
Effort: 1 day

Current pattern detection uses simple thresholds (e.g., failure_rate >=0.5). Enhance with more heuristics and correlations.

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-core'],
        'source': 'review_architecture_20251116_094525.md',
        'type': 'enhancement'
    },
    {
        'title': 'Improve error propagation with custom exceptions',
        'description': '''Implement custom exceptions and logging everywhere.

High (Significant Impact - Address Next Sprint)

Files: All
Effort: 1 day

No more swallowed errors. Improve error handling and propagation throughout the codebase.

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-core'],
        'source': 'review_architecture_20251116_094525.md',
        'type': 'improvement'
    },
    {
        'title': 'Security hardening: path validation, prompt escaping, DB encryption',
        'description': '''Implement security hardening measures.

High (Significant Impact - Address Next Sprint)

Files: autonomous_orchestrator.py, meta_review.py
Effort: 1 day

Security improvements:
- Path validation
- Prompt escaping
- DB encryption

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['meridian-core'],
        'source': 'review_architecture_20251116_094525.md',
        'type': 'security'
    },
    
    # From governance recommendations
    {
        'title': 'Create GOVERNANCE-CONTEXT.md for auto-injection into AI prompts',
        'description': '''Create governance context file that gets automatically included in AI context.

Recommendation 2: Governance Enforcement Mechanisms

This file should contain:
- Critical rules (ADR-001, import rules, etc.)
- Current context (session info, active issues)
- Governance checklist

File: GOVERNANCE-CONTEXT.md

This ensures governance docs are "active" not "passive".

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['workspace-root'],
        'source': '2025-11-20-PROJECT-GOVERNANCE-AND-TASK-TRACKING-RECOMMENDATIONS.md',
        'type': 'governance'
    },
    {
        'title': 'Create pre-task governance checklist enforcement',
        'description': '''Implement mandatory pre-task checklist for AI agents.

Recommendation 3: Governance Enforcement Mechanisms

Every AI agent should check before starting work:
- Read ADR-001-COMPONENT-PLACEMENT.md
- Read AI-GUIDELINES.md (relevant sections)
- Check WORKSPACE-TASKS.json for context
- Check CROSS-REPO-ISSUES.json for known issues
- Verify component placement
- Check for similar work in other repos
- Document decision rationale

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['workspace-root'],
        'source': '2025-11-20-PROJECT-GOVERNANCE-AND-TASK-TRACKING-RECOMMENDATIONS.md',
        'type': 'governance'
    },
    
    # From configuration drift tracking
    {
        'title': 'Implement code-to-architecture component tracking system',
        'description': '''Implement system to track all code/files back to architecture components.

From: 2025-11-20-CODE-TO-ARCHITECTURE-TRACKING.md

This system will:
1. Map files/modules to architecture components
2. Track git commits against components
3. Validate before deployment
4. Block deployment if files aren't traceable

This prevents scope creep by ensuring all code maps to agreed architecture.

Priority: CRITICAL''',
        'priority': 'CRITICAL',
        'repos_affected': ['workspace-root'],
        'source': '2025-11-20-CODE-TO-ARCHITECTURE-TRACKING.md',
        'type': 'implementation'
    },
    {
        'title': 'Create master architecture repository structure',
        'description': '''Create master architecture repository at workspace level.

From: 2025-11-20-CONFIGURATION-DRIFT-TRACKING-SYSTEM.md

Structure:
- architecture/master/ - Master specs per repo
- architecture/roadmaps/ - Future state
- architecture/diagrams/ - Architecture diagrams
- architecture/decisions/ - ADRs
- architecture/rules/ - Automated rules

This provides single source of truth for architecture.

Priority: HIGH''',
        'priority': 'HIGH',
        'repos_affected': ['workspace-root'],
        'source': '2025-11-20-CONFIGURATION-DRIFT-TRACKING-SYSTEM.md',
        'type': 'organization'
    },
]


def main():
    """Import specific tasks from architecture reviews into WMS."""
    print("=" * 70)
    print("  IMPORT ARCHITECTURE REVIEW TASKS TO WMS")
    print("  Manual import of specific, actionable tasks")
    print("=" * 70)
    print()
    
    workspace_root = Path.cwd()
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        # Initialize WMS components
        governance = GovernanceEngine(session, workspace_root=workspace_root)
        bastard = BastardIntegration(session, workspace_root / "workspace" / "skills")
        workflow = WorkflowEngine(session, governance, bastard, workspace_root=workspace_root)
        
        print(f"1. Found {len(ARCHITECTURE_TASKS)} tasks to import")
        print()
        
        # Check existing tasks
        from workspace.db.models import WorkspaceTask
        existing_titles = {task.title for task in session.query(WorkspaceTask).all()}
        
        print("2. Adding tasks to WMS database...")
        print()
        
        created_tasks = []
        skipped_tasks = []
        errors = []
        
        for task_data in ARCHITECTURE_TASKS:
            try:
                # Check if task already exists
                if task_data['title'] in existing_titles:
                    skipped_tasks.append(task_data['title'])
                    continue
                
                # Determine repos_affected
                repos_affected = task_data.get('repos_affected', ['workspace-root'])
                
                # Create task using WMS workflow engine
                priority_lower = task_data.get('priority', 'MEDIUM').lower()
                
                task = workflow.create_task(
                    title=task_data['title'],
                    description=task_data['description'],
                    actual_users=1,  # Default to 1 user
                    proposed_solution=None,  # No solution in reviews
                    priority=priority_lower
                )
                
                # Add metadata
                source_file = Path(task_data.get('source', 'unknown')).name
                task.notes = f"Imported from architecture review: {source_file}\nType: {task_data.get('type', 'review')}"
                task.related_files = json.dumps([task_data['source']])
                task.session_created = "2025-11-20-architecture-review-import"
                
                # Update repos_affected if it wasn't auto-determined
                if task.assigned_repo and task.assigned_repo not in repos_affected:
                    repos_affected = [task.assigned_repo] + [r for r in repos_affected if r != task.assigned_repo]
                task.repos_affected = json.dumps(repos_affected)
                
                session.commit()
                created_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'priority': priority_lower,
                    'repo': task.assigned_repo
                })
                
                status_icon = '✅' if task.status == 'approved' else '⚠️' if task.status == 'blocked' else '📋'
                print(f"   {status_icon} {task.id}: {task.title[:60]}...")
                print(f"      Repo: {task.assigned_repo or 'N/A'} | Status: {task.status} | Priority: {priority_lower.upper()}")
                print()
                
            except Exception as e:
                errors.append((task_data['title'], str(e)))
                session.rollback()
                print(f"   ❌ Error creating '{task_data['title'][:60]}...': {e}")
                import traceback
                traceback.print_exc()
                print()
        
        print("=" * 70)
        print("  IMPORT SUMMARY")
        print("=" * 70)
        print()
        print(f"✅ Tasks created: {len(created_tasks)}")
        print(f"⏭️  Tasks skipped (duplicates): {len(skipped_tasks)}")
        print(f"❌ Errors: {len(errors)}")
        print(f"📊 Total processed: {len(ARCHITECTURE_TASKS)}")
        print()
        
        if created_tasks:
            # Show by priority
            by_priority = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
            for task_info in created_tasks:
                priority = task_info['priority'].upper()
                by_priority[priority].append(task_info)
            
            print("Tasks created by priority:")
            for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                tasks = by_priority[priority]
                if tasks:
                    print(f"\n   {priority} ({len(tasks)} tasks):")
                    for task_info in tasks[:5]:
                        print(f"      • {task_info['id']}: {task_info['title'][:55]}... ({task_info['status']})")
                    if len(tasks) > 5:
                        print(f"      ... and {len(tasks) - 5} more")
            print()
        
        if skipped_tasks:
            print(f"Skipped tasks (already exist): {len(skipped_tasks)}")
            print()
        
        # Show status breakdown
        status_counts = {}
        for task_info in created_tasks:
            status = task_info['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            print("Task status breakdown:")
            for status, count in sorted(status_counts.items()):
                print(f"   • {status}: {count}")
            print()
        
        print("=" * 70)
        print("✅ Import complete!")
        print()
        print("Next steps:")
        print("  1. Review tasks: Check database for imported tasks")
        print("  2. Start working: Use WMS workflow engine to start tasks")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Import cancelled by user")
        sys.exit(1)

