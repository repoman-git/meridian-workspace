#!/usr/bin/env python3
"""
Import tasks and actions from architecture review documents into WMS.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Extract tasks from architecture reviews and add to WMS database
DOMAIN: Cross-repo workspace management
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import json

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.governance_engine import GovernanceEngine
from workspace.wms.bastard_integration import BastardIntegration
from workspace.wms.workflow_engine import WorkflowEngine


def extract_tasks_from_review(content: str, source_file: str) -> List[Dict]:
    """Extract tasks and actions from review document content."""
    tasks = []
    
    # Pattern 1: Priority sections (Priority 1, Critical, High Priority, etc.)
    priority_patterns = [
        r'(?:Priority\s+)?(?:1|CRITICAL|HIGH):\s+(.+?)(?=\n##|\n###|$)',
        r'###\s+(?:Priority|Critical|High|Medium|Low)\s+Priority:?\s*\n(.+?)(?=\n##|\n###|$)',
        r'###\s+\d+\.\s+(.+?)(?=\n##|\n###|$)',
        r'**Priority:**\s*(CRITICAL|HIGH|MEDIUM|LOW)\s*\n(.+?)(?=\n##|\n###|$)',
    ]
    
    # Pattern 2: Action items or recommendations
    action_patterns = [
        r'\*\*Actions?:\*\*\s*\n((?:-\s+.+\n?)+)',
        r'**Actions:**\s*\n((?:\d+\.\s+.+\n?)+)',
        r'**Recommendation:**\s*(.+?)(?=\n\n|\n\*\*|$)',
        r'**Actions to Take:**\s*\n((?:-\s+.+\n?)+)',
        r'TASK[-\s]([A-Z]+[-\s]\d+):\s*(.+?)(?=\n|$)',
    ]
    
    # Pattern 3: TODO/FIXME items
    todo_patterns = [
        r'TODO[:\s]+(.+?)(?=\n|$)',
        r'FIXME[:\s]+(.+?)(?=\n|$)',
        r'⚠️\s+(.+?)(?=\n|$)',
        r'❌\s+(.+?)(?=\n|$)',
    ]
    
    # Pattern 4: Issues/Findings sections
    issue_patterns = [
        r'###\s+(?:Issues|Findings|Problems)\s+Found:\s*\n((?:.+\n?)+?)(?=\n##|\n###|$)',
        r'\*\*Issues?:\*\*\s*\n((?:-\s+.+\n?)+)',
    ]
    
    # Extract priority tasks
    for pattern in priority_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        for match in matches:
            task_text = match.group(1).strip()
            if len(task_text) > 20:  # Ignore very short matches
                tasks.append({
                    'title': task_text.split('\n')[0][:200],
                    'description': task_text[:1000],
                    'source': source_file,
                    'priority': 'HIGH',
                    'type': 'priority_item'
                })
    
    # Extract action items
    for pattern in action_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        for match in matches:
            actions_text = match.group(1) if match.lastindex >= 1 else match.group(0)
            # Split into individual actions
            for action in re.split(r'\n[-*]\s+|\n\d+\.\s+', actions_text):
                action = action.strip()
                if len(action) > 20:
                    tasks.append({
                        'title': action.split('\n')[0][:200],
                        'description': action[:1000],
                        'source': source_file,
                        'priority': 'MEDIUM',
                        'type': 'action_item'
                    })
    
    # Extract TODO/FIXME
    for pattern in todo_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            task_text = match.group(1).strip()
            if len(task_text) > 10:
                tasks.append({
                    'title': f"TODO: {task_text[:180]}",
                    'description': task_text[:1000],
                    'source': source_file,
                    'priority': 'MEDIUM',
                    'type': 'todo'
                })
    
    return tasks


def extract_tasks_from_architecture_review(file_path: Path) -> List[Dict]:
    """Extract tasks from ARCHITECTURE-REVIEW-2025-11-20.md."""
    try:
        content = file_path.read_text()
        tasks = []
        
        # Extract "Priority 1", "Priority 2", etc. sections
        priority_sections = re.finditer(
            r'###\s+Priority\s+(\d+):\s+(.+?)\n\n\*\*Actions:\*\*\s*\n((?:-\s+.+\n?)+)',
            content,
            re.MULTILINE | re.DOTALL
        )
        
        for match in priority_sections:
            priority_num = match.group(1)
            priority_title = match.group(2).strip()
            actions = match.group(3)
            
            priority_map = {'1': 'CRITICAL', '2': 'HIGH', '3': 'MEDIUM', '4': 'LOW'}
            priority = priority_map.get(priority_num, 'MEDIUM')
            
            # Split actions
            for action in re.split(r'\n-\s+', actions):
                action = action.strip()
                if len(action) > 10:
                    tasks.append({
                        'title': action.split('\n')[0][:200],
                        'description': f"{priority_title}\n\n{action[:800]}",
                        'source': str(file_path),
                        'priority': priority,
                        'type': 'architecture_review'
                    })
        
        # Extract Critical Issues section
        critical_section = re.search(
            r'###\s+4\.1\s+Critical\s+Issues\s*\n((?:.+\n?)+?)(?=\n###|$)',
            content,
            re.MULTILINE | re.DOTALL | re.IGNORECASE
        )
        
        if critical_section:
            issues_text = critical_section.group(1)
            # Extract numbered items
            for issue_match in re.finditer(
                r'\d+\.\s+\*\*(.+?)\*\*\s*\n(.+?)(?=\d+\.\s+\*\*|$)',
                issues_text,
                re.MULTILINE | re.DOTALL
            ):
                title = issue_match.group(1).strip()
                description = issue_match.group(2).strip()
                
                tasks.append({
                    'title': title[:200],
                    'description': description[:1000],
                    'source': str(file_path),
                    'priority': 'HIGH',
                    'type': 'critical_issue'
                })
        
        # Extract Recommendations section
        recommendations = extract_tasks_from_review(content, str(file_path))
        tasks.extend(recommendations)
        
        return tasks
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return []


def extract_tasks_from_review_file(file_path: Path) -> List[Dict]:
    """Extract tasks from a review file."""
    try:
        content = file_path.read_text()
        tasks = extract_tasks_from_review(content, str(file_path))
        return tasks
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return []


def main():
    """Import tasks from architecture reviews into WMS."""
    print("=" * 70)
    print("  IMPORT ARCHITECTURE REVIEW TASKS TO WMS")
    print("=" * 70)
    print()
    
    workspace_root = Path.cwd()
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        # Initialize WMS components
        governance = GovernanceEngine(session)
        bastard = BastardIntegration(session, workspace_root / "workspace" / "skills")
        workflow = WorkflowEngine(session, governance, bastard)
        
        all_tasks = []
        
        # Files to process (today's documents)
        files_to_process = [
            workspace_root / "ARCHITECTURE-REVIEW-2025-11-20.md",
            workspace_root / "2025-11-20-MERIDIAN-CORE-ARCHITECTURE.md",
            workspace_root / "2025-11-20-MERIDIAN-RESEARCH-ARCHITECTURE.md",
            workspace_root / "2025-11-20-MERIDIAN-TRADING-ARCHITECTURE.md",
            workspace_root / "2025-11-20-CREDENTIAL-MANAGEMENT-ARCHITECTURE.md",
            workspace_root / "2025-11-20-PROJECT-GOVERNANCE-AND-TASK-TRACKING-RECOMMENDATIONS.md",
            workspace_root / "2025-11-20-CONFIGURATION-DRIFT-TRACKING-SYSTEM.md",
            workspace_root / "2025-11-20-CODE-TO-ARCHITECTURE-TRACKING.md",
            workspace_root / "meridian-core/docs/reviews/review_architecture_20251116_094525.md",
            workspace_root / "meridian-core/docs/TODO_REVIEW.md",
        ]
        
        print("1. Scanning architecture review documents...")
        print()
        
        for file_path in files_to_process:
            if not file_path.exists():
                print(f"   ⚠️  File not found: {file_path.name}")
                continue
            
            print(f"   📄 Processing: {file_path.name}")
            
            if file_path.name == "ARCHITECTURE-REVIEW-2025-11-20.md":
                tasks = extract_tasks_from_architecture_review(file_path)
            else:
                tasks = extract_tasks_from_review_file(file_path)
            
            if tasks:
                print(f"      ✅ Found {len(tasks)} task(s)")
                all_tasks.extend(tasks)
            else:
                print(f"      ℹ️  No tasks found")
            print()
        
        # Deduplicate tasks (same title)
        seen_titles = set()
        unique_tasks = []
        for task in all_tasks:
            title_key = task['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_tasks.append(task)
        
        print(f"2. Found {len(unique_tasks)} unique tasks from reviews")
        print()
        
        if not unique_tasks:
            print("⚠️  No tasks found in review documents")
            return 0
        
        # Add tasks to WMS
        print("3. Adding tasks to WMS database...")
        print()
        
        created_tasks = []
        skipped_tasks = []
        
        for task_data in unique_tasks:
            try:
                # Check if task already exists (by title similarity)
                existing = session.query(db.WorkspaceTask).filter_by(
                    title=task_data['title'][:500]
                ).first()
                
                if existing:
                    skipped_tasks.append(task_data['title'])
                    continue
                
                # Create task using WMS workflow engine
                task = workflow.create_task(
                    title=task_data['title'],
                    description=f"{task_data.get('description', '')}\n\nSource: {task_data.get('source', 'unknown')}",
                    actual_users=1,  # Default to 1 user for now
                    proposed_solution=None,  # No solution provided in review
                    priority=task_data.get('priority', 'medium').lower()
                )
                
                # Add metadata
                if task_data.get('source'):
                    task.notes = f"Imported from: {Path(task_data['source']).name}"
                    task.related_files = json.dumps([task_data['source']])
                    task.session_created = "2025-11-20-architecture-review-import"
                
                session.commit()
                created_tasks.append(task.id)
                
                print(f"   ✅ Created: {task.id} - {task.title[:60]}...")
                
            except Exception as e:
                print(f"   ❌ Error creating task '{task_data['title'][:60]}...': {e}")
                session.rollback()
        
        print()
        print("=" * 70)
        print("  IMPORT SUMMARY")
        print("=" * 70)
        print()
        print(f"✅ Tasks created: {len(created_tasks)}")
        print(f"⏭️  Tasks skipped (duplicates): {len(skipped_tasks)}")
        print(f"📊 Total processed: {len(unique_tasks)}")
        print()
        
        if created_tasks:
            print("Created tasks:")
            for task_id in created_tasks[:10]:  # Show first 10
                task = session.query(db.WorkspaceTask).filter_by(id=task_id).first()
                if task:
                    print(f"   • {task_id}: {task.title[:60]}...")
            if len(created_tasks) > 10:
                print(f"   ... and {len(created_tasks) - 10} more")
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

