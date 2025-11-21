#!/usr/bin/env python3
"""
Import tasks and actions from architecture review documents into WMS.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Extract tasks from all today's architecture reviews and add to WMS database
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


def extract_tasks_from_architecture_review(file_path: Path) -> List[Dict]:
    """Extract tasks from ARCHITECTURE-REVIEW-2025-11-20.md."""
    try:
        content = file_path.read_text()
        tasks = []
        
        # Extract Priority sections with actions
        priority_pattern = r'###\s+Priority\s+(\d+):\s+(.+?)\n\n\*\*Actions:\*\*\s*\n((?:-\s+.+\n?)+?)(?=\n---|\n###|$)'
        for match in re.finditer(priority_pattern, content, re.MULTILINE | re.DOTALL):
            priority_num = match.group(1)
            priority_title = match.group(2).strip()
            actions_text = match.group(3)
            
            priority_map = {'1': 'CRITICAL', '2': 'HIGH', '3': 'MEDIUM', '4': 'LOW'}
            priority = priority_map.get(priority_num, 'MEDIUM')
            
            # Split actions by bullet points
            for action in re.split(r'\n-\s+', actions_text):
                action = action.strip()
                if len(action) > 10 and not action.startswith('**'):
                    tasks.append({
                        'title': action.split('\n')[0][:200],
                        'description': f"Priority {priority_num}: {priority_title}\n\n{action[:800]}",
                        'source': str(file_path),
                        'priority': priority,
                        'type': 'priority_action'
                    })
        
        # Extract Critical Issues
        critical_pattern = r'\d+\.\s+\*\*(.+?)\*\*\s*\n(.+?)(?=\d+\.\s+\*\*|###|$)'
        critical_section = re.search(r'###\s+4\.1\s+Critical\s+Issues\s*\n((?:.+\n?)+?)(?=\n###|$)', content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if critical_section:
            for match in re.finditer(critical_pattern, critical_section.group(1), re.MULTILINE | re.DOTALL):
                title = match.group(1).strip()
                description = match.group(2).strip()
                
                # Extract recommendation if present
                recommendation = re.search(r'\*\*Recommendation:\*\*\s*(.+?)(?=\n\*\*|$)', description, re.IGNORECASE)
                if recommendation:
                    description = f"{description}\n\nRecommendation: {recommendation.group(1)}"
                
                tasks.append({
                    'title': title[:200],
                    'description': description[:1000],
                    'source': str(file_path),
                    'priority': 'HIGH',
                    'type': 'critical_issue'
                })
        
        # Extract Next Steps
        next_steps = re.search(r'###\s+🎯\s+Next\s+Steps\s*\n((?:.+\n?)+?)(?=\n---|$)', content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if next_steps:
            for line in next_steps.group(1).split('\n'):
                line = line.strip()
                if line and re.match(r'^\d+\.', line):
                    task_text = re.sub(r'^\d+\.\s+\*\*', '', line).strip()
                    if len(task_text) > 10:
                        tasks.append({
                            'title': task_text.split('**')[0][:200],
                            'description': task_text[:1000],
                            'source': str(file_path),
                            'priority': 'MEDIUM',
                            'type': 'next_step'
                        })
        
        return tasks
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return []


def extract_tasks_from_governance_recommendations(file_path: Path) -> List[Dict]:
    """Extract tasks from governance recommendations document."""
    try:
        content = file_path.read_text()
        tasks = []
        
        # Extract recommendation sections
        rec_pattern = r'###\s+(.+?)\s*\n((?:.+\n?)+?)(?=\n###|$)'
        for match in re.finditer(rec_pattern, content, re.MULTILINE | re.DOTALL):
            section_title = match.group(1).strip()
            section_content = match.group(2)
            
            # Skip certain sections
            if any(skip in section_title.lower() for skip in ['summary', 'conclusion', 'executive']):
                continue
            
            # Extract action items
            actions = re.finditer(r'(?:-|\d+\.)\s+\*\*(.+?)\*\*\s*\n(.+?)(?=\n[-*]|\n\d+\.|$)', section_content, re.MULTILINE | re.DOTALL)
            for action_match in actions:
                title = action_match.group(1).strip()
                description = action_match.group(2).strip()
                
                # Determine priority from section title
                priority = 'MEDIUM'
                if 'high' in section_title.lower() or 'critical' in section_title.lower():
                    priority = 'HIGH'
                elif 'low' in section_title.lower():
                    priority = 'LOW'
                
                tasks.append({
                    'title': title[:200],
                    'description': f"{section_title}\n\n{description[:800]}",
                    'source': str(file_path),
                    'priority': priority,
                    'type': 'governance_recommendation'
                })
        
        return tasks
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return []


def extract_tasks_from_core_review(file_path: Path) -> List[Dict]:
    """Extract tasks from meridian-core review."""
    try:
        content = file_path.read_text()
        tasks = []
        
        # Extract Critical recommendations
        critical_pattern = r'###\s+Critical\s+\(.+?\)\s*\n((?:.+\n?)+?)(?=\n###|$)'
        for match in re.finditer(critical_pattern, content, re.MULTILINE | re.DOTALL):
            critical_section = match.group(1)
            
            # Extract numbered items
            items = re.finditer(r'\d+\.\s+\*\*(.+?)\*\*\s*:?\s*(.+?)(?=\d+\.\s+\*\*|$)', critical_section, re.MULTILINE | re.DOTALL)
            for item_match in items:
                title = item_match.group(1).strip()
                description = item_match.group(2).strip()
                
                # Extract effort estimate if present
                effort = re.search(r'\*Effort:\s*(.+?)\*', description, re.IGNORECASE)
                if effort:
                    description = f"{description}\n\nEstimated effort: {effort.group(1)}"
                
                tasks.append({
                    'title': title[:200],
                    'description': description[:1000],
                    'source': str(file_path),
                    'priority': 'HIGH',
                    'type': 'critical_recommendation'
                })
        
        # Extract High Priority recommendations
        high_pattern = r'###\s+High\s+\(.+?\)\s*\n((?:.+\n?)+?)(?=\n###|$)'
        for match in re.finditer(high_pattern, content, re.MULTILINE | re.DOTALL):
            high_section = match.group(1)
            
            items = re.finditer(r'\d+\.\s+\*\*(.+?)\*\*\s*:?\s*(.+?)(?=\d+\.\s+\*\*|$)', high_section, re.MULTILINE | re.DOTALL)
            for item_match in items:
                title = item_match.group(1).strip()
                description = item_match.group(2).strip()
                
                tasks.append({
                    'title': title[:200],
                    'description': description[:1000],
                    'source': str(file_path),
                    'priority': 'HIGH',
                    'type': 'high_priority_recommendation'
                })
        
        # Extract Medium Priority recommendations
        medium_pattern = r'###\s+Medium\s+\(.+?\)\s*\n((?:.+\n?)+?)(?=\n###|$)'
        for match in re.finditer(medium_pattern, content, re.MULTILINE | re.DOTALL):
            medium_section = match.group(1)
            
            items = re.finditer(r'\d+\.\s+\*\*(.+?)\*\*\s*:?\s*(.+?)(?=\d+\.\s+\*\*|$)', medium_section, re.MULTILINE | re.DOTALL)
            for item_match in items:
                title = item_match.group(1).strip()
                description = item_match.group(2).strip()
                
                tasks.append({
                    'title': title[:200],
                    'description': description[:1000],
                    'source': str(file_path),
                    'priority': 'MEDIUM',
                    'type': 'medium_priority_recommendation'
                })
        
        return tasks
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return []


def extract_tasks_from_todo_review(file_path: Path) -> List[Dict]:
    """Extract tasks from TODO review."""
    try:
        content = file_path.read_text()
        tasks = []
        
        # Extract High Priority TODOs
        high_pattern = r'##\s+🔴\s+High\s+Priority\s+\(.+?\)\s*\n((?:.+\n?)+?)(?=\n##|$)'
        for match in re.finditer(high_pattern, content, re.MULTILINE | re.DOTALL):
            section = match.group(1)
            
            items = re.finditer(r'###\s+\d+\.\s+(.+?)\s*\n\*\*Location:\*\*\s*(.+?)\n\*\*Lines?:\*\*\s*(.+?)\n(.+?)(?=\n###|$)', section, re.MULTILINE | re.DOTALL)
            for item_match in items:
                title = item_match.group(1).strip()
                location = item_match.group(2).strip()
                lines = item_match.group(3).strip()
                description = item_match.group(4).strip()
                
                tasks.append({
                    'title': f"TODO: {title[:180]}",
                    'description': f"Location: {location}\nLines: {lines}\n\n{description[:800]}",
                    'source': str(file_path),
                    'priority': 'HIGH',
                    'type': 'todo'
                })
        
        return tasks
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return []


def extract_tasks_from_architecture_docs(file_path: Path) -> List[Dict]:
    """Extract tasks from architecture documentation."""
    try:
        content = file_path.read_text()
        tasks = []
        
        # Look for "MISSING", "NOT IMPLEMENTED", "TODO" sections
        missing_pattern = r'(?:❌|⚠️|MISSING|NOT\s+IMPLEMENTED|TODO):\s*(.+?)(?=\n|\.)'
        for match in re.finditer(missing_pattern, content, re.MULTILINE | re.IGNORECASE):
            task_text = match.group(1).strip()
            if len(task_text) > 10:
                tasks.append({
                    'title': f"Implement: {task_text[:180]}",
                    'description': f"Found in: {file_path.name}\n\n{task_text[:800]}",
                    'source': str(file_path),
                    'priority': 'MEDIUM',
                    'type': 'missing_implementation'
                })
        
        return tasks
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}")
        return []


def main():
    """Import tasks from architecture reviews into WMS."""
    print("=" * 70)
    print("  IMPORT ARCHITECTURE REVIEW TASKS TO WMS")
    print("  Extracting from all architecture review documents")
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
        
        # Today's documents to process
        files_to_process = [
            (workspace_root / "ARCHITECTURE-REVIEW-2025-11-20.md", extract_tasks_from_architecture_review),
            (workspace_root / "2025-11-20-PROJECT-GOVERNANCE-AND-TASK-TRACKING-RECOMMENDATIONS.md", extract_tasks_from_governance_recommendations),
            (workspace_root / "2025-11-20-MERIDIAN-CORE-ARCHITECTURE.md", extract_tasks_from_architecture_docs),
            (workspace_root / "2025-11-20-MERIDIAN-RESEARCH-ARCHITECTURE.md", extract_tasks_from_architecture_docs),
            (workspace_root / "2025-11-20-MERIDIAN-TRADING-ARCHITECTURE.md", extract_tasks_from_architecture_docs),
            (workspace_root / "2025-11-20-CREDENTIAL-MANAGEMENT-ARCHITECTURE.md", extract_tasks_from_architecture_docs),
            (workspace_root / "2025-11-20-CONFIGURATION-DRIFT-TRACKING-SYSTEM.md", extract_tasks_from_architecture_docs),
            (workspace_root / "2025-11-20-CODE-TO-ARCHITECTURE-TRACKING.md", extract_tasks_from_architecture_docs),
            (workspace_root / "meridian-core/docs/reviews/review_architecture_20251116_094525.md", extract_tasks_from_core_review),
            (workspace_root / "meridian-core/docs/TODO_REVIEW.md", extract_tasks_from_todo_review),
        ]
        
        print("1. Scanning architecture review documents...")
        print()
        
        for file_path, extract_func in files_to_process:
            if not file_path.exists():
                print(f"   ⚠️  File not found: {file_path.name}")
                continue
            
            print(f"   📄 Processing: {file_path.name}")
            
            try:
                tasks = extract_func(file_path)
                if tasks:
                    print(f"      ✅ Found {len(tasks)} task(s)")
                    all_tasks.extend(tasks)
                else:
                    print(f"      ℹ️  No tasks found")
            except Exception as e:
                print(f"      ❌ Error extracting: {e}")
            
            print()
        
        # Deduplicate tasks (same title)
        seen_titles = {}
        unique_tasks = []
        for task in all_tasks:
            title_key = task['title'].lower().strip()
            # Keep highest priority if duplicate
            if title_key in seen_titles:
                existing_idx = seen_titles[title_key]
                existing_priority = unique_tasks[existing_idx].get('priority', 'MEDIUM')
                new_priority = task.get('priority', 'MEDIUM')
                priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
                if priority_order.get(new_priority, 2) < priority_order.get(existing_priority, 2):
                    # Replace with higher priority
                    unique_tasks[existing_idx] = task
                continue
            
            seen_titles[title_key] = len(unique_tasks)
            unique_tasks.append(task)
        
        print(f"2. Found {len(unique_tasks)} unique tasks from reviews")
        print(f"   (Deduplicated from {len(all_tasks)} total tasks)")
        print()
        
        if not unique_tasks:
            print("⚠️  No tasks found in review documents")
            return 0
        
        # Show summary by priority
        by_priority = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'LOW': []}
        for task in unique_tasks:
            priority = task.get('priority', 'MEDIUM')
            by_priority[priority].append(task)
        
        print("   Priority breakdown:")
        for priority in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            count = len(by_priority[priority])
            if count > 0:
                print(f"      • {priority}: {count} task(s)")
        print()
        
        # Add tasks to WMS
        print("3. Adding tasks to WMS database...")
        print()
        
        created_tasks = []
        skipped_tasks = []
        errors = []
        
        for task_data in unique_tasks:
            try:
                # Check if task already exists (by title similarity)
                from workspace.db.models import WorkspaceTask
                existing = session.query(WorkspaceTask).filter_by(
                    title=task_data['title'][:500]
                ).first()
                
                if existing:
                    skipped_tasks.append(task_data['title'])
                    continue
                
                # Create task using WMS workflow engine
                priority_lower = task_data.get('priority', 'MEDIUM').lower()
                
                task = workflow.create_task(
                    title=task_data['title'],
                    description=f"{task_data.get('description', '')}\n\nSource: {Path(task_data.get('source', 'unknown')).name}",
                    actual_users=1,  # Default to 1 user
                    proposed_solution=None,  # No solution in reviews
                    priority=priority_lower
                )
                
                # Add metadata
                if task_data.get('source'):
                    source_file = Path(task_data['source']).name
                    task.notes = f"Imported from architecture review: {source_file}\nType: {task_data.get('type', 'review')}"
                    task.related_files = json.dumps([task_data['source']])
                    task.session_created = "2025-11-20-architecture-review-import"
                
                session.commit()
                created_tasks.append({
                    'id': task.id,
                    'title': task.title,
                    'status': task.status,
                    'priority': priority_lower
                })
                
                status_icon = '✅' if task.status == 'approved' else '⚠️' if task.status == 'blocked' else '📋'
                print(f"   {status_icon} {task.id}: {task.title[:60]}... ({task.status})")
                
            except Exception as e:
                errors.append((task_data['title'], str(e)))
                session.rollback()
                print(f"   ❌ Error creating '{task_data['title'][:60]}...': {e}")
        
        print()
        print("=" * 70)
        print("  IMPORT SUMMARY")
        print("=" * 70)
        print()
        print(f"✅ Tasks created: {len(created_tasks)}")
        print(f"⏭️  Tasks skipped (duplicates): {len(skipped_tasks)}")
        print(f"❌ Errors: {len(errors)}")
        print(f"📊 Total processed: {len(unique_tasks)}")
        print()
        
        if created_tasks:
            print("Created tasks (first 10):")
            for task_info in created_tasks[:10]:
                print(f"   • {task_info['id']}: {task_info['title'][:60]}... ({task_info['status']})")
            if len(created_tasks) > 10:
                print(f"   ... and {len(created_tasks) - 10} more")
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
        print("  1. Review tasks: python workspace/wms/cli.py task list")
        print("  2. Start working: python workspace/wms/cli.py task start <task_id>")
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

