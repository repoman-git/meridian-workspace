#!/usr/bin/env python3
"""
Generate GOVERNANCE-CONTEXT.md file for auto-injection into AI prompts.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Auto-generate governance context from existing docs
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
from workspace.wms.context_manager import ContextManager, get_quick_context


def find_governance_docs(workspace_root: Path) -> dict:
    """Find all governance documentation files."""
    docs = {
        'ai_guidelines': [],
        'adr': [],
        'house_model': [],
        'cross_repo_guide': []
    }
    
    # Search for AI-GUIDELINES.md
    for path in workspace_root.rglob('AI-GUIDELINES.md'):
        if 'venv' not in str(path) and '.git' not in str(path):
            docs['ai_guidelines'].append(path)
    
    # Search for ADR-001 files
    for path in workspace_root.rglob('ADR-001*.md'):
        if 'venv' not in str(path) and '.git' not in str(path):
            docs['adr'].append(path)
    
    # Search for AI-HOUSE-MODEL files
    for path in workspace_root.rglob('*AI-HOUSE-MODEL*.md'):
        if 'venv' not in str(path) and '.git' not in str(path):
            docs['house_model'].append(path)
    
    # Search for CROSS-REPO-GUIDE files
    for path in workspace_root.rglob('*CROSS-REPO*.md'):
        if 'venv' not in str(path) and '.git' not in str(path):
            docs['cross_repo_guide'].append(path)
    
    return docs


def extract_critical_rules(workspace_root: Path, context_repo: str = None) -> str:
    """Extract critical governance rules from documentation."""
    rules = []
    
    # Find primary AI-GUIDELINES.md (prefer repo-specific if context is set)
    ai_guidelines = None
    if context_repo:
        repo_path = workspace_root / context_repo
        if repo_path.exists():
            candidate = repo_path / "AI-GUIDELINES.md"
            if candidate.exists():
                ai_guidelines = candidate
    
    # Fallback to workspace root or first found
    if not ai_guidelines:
        candidates = list(workspace_root.rglob('AI-GUIDELINES.md'))
        if candidates:
            # Prefer meridian-core as source of truth
            for candidate in candidates:
                if 'meridian-core' in str(candidate) and 'venv' not in str(candidate):
                    ai_guidelines = candidate
                    break
            if not ai_guidelines:
                ai_guidelines = candidates[0]
    
    if ai_guidelines and ai_guidelines.exists():
        content = ai_guidelines.read_text()
        # Extract CRITICAL RULE section
        if "CRITICAL RULE" in content or "⚠️" in content:
            lines = content.split('\n')
            in_critical = False
            critical_section = []
            for line in lines:
                if "CRITICAL RULE" in line or "⚠️" in line:
                    in_critical = True
                    critical_section.append(line)
                elif in_critical and line.startswith('#'):
                    break
                elif in_critical:
                    critical_section.append(line)
            
            if critical_section:
                rules.append("## CRITICAL RULE\n\n" + '\n'.join(critical_section[:20]))
    
    return '\n\n'.join(rules) if rules else "## CRITICAL RULE\n\n⚠️ **NO CODE SHALL BE WRITTEN OR MODIFIED UNTIL A CLEAR PLAN HAS BEEN FORMULATED AND AGREED UPON.**"


def generate_governance_context(workspace_root: Path, context_repo: str = None, context_notes: str = None) -> str:
    """Generate GOVERNANCE-CONTEXT.md content."""
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        # Get current context
        context_manager = ContextManager(workspace_root, session)
        current_context = context_manager.get_current_context()
        
        if context_repo and not current_context:
            # Set context if provided
            current_context = context_manager.set_context(context_repo, context_notes)
        
        # Get session info
        session_id = datetime.now().strftime('%Y-%m-%d-%H%M%S')
        
        # Load workspace state
        workspace_tasks = []
        cross_repo_issues = []
        architecture_decisions = []
        
        workspace_tasks_file = workspace_root / "WORKSPACE-TASKS.json"
        if workspace_tasks_file.exists():
            try:
                with open(workspace_tasks_file) as f:
                    data = json.load(f)
                    workspace_tasks = data.get('active_tasks', [])[:5]  # Top 5
            except:
                pass
        
        cross_repo_issues_file = workspace_root / "CROSS-REPO-ISSUES.json"
        if cross_repo_issues_file.exists():
            try:
                with open(cross_repo_issues_file) as f:
                    data = json.load(f)
                    cross_repo_issues = data.get('issues', [])[:5]  # Top 5
            except:
                pass
        
        architecture_decisions_file = workspace_root / "ARCHITECTURE-DECISIONS.json"
        if architecture_decisions_file.exists():
            try:
                with open(architecture_decisions_file) as f:
                    data = json.load(f)
                    architecture_decisions = data.get('decisions', [])[-5:]  # Last 5
            except:
                pass
        
        # Extract critical rules
        critical_rules = extract_critical_rules(workspace_root, context_repo or (current_context.repo if current_context else None))
        
        # Generate content
        content = f"""# GOVERNANCE-CONTEXT.md
# Auto-generated for AI context injection
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Session: {session_id}

⚠️ **THIS FILE IS AUTO-INJECTED INTO EVERY AI INTERACTION**
⚠️ **AI AGENTS MUST FOLLOW THESE RULES WITHOUT EXCEPTION**

---

{critical_rules}

---

## PRE-TASK GOVERNANCE CHECKLIST

**BEFORE WRITING ANY CODE, AI AGENTS MUST:**

1. ✅ **Read ADR-001-COMPONENT-PLACEMENT.md** - Understand component placement rules
2. ✅ **Read AI-GUIDELINES.md** - Review planning and execution guidelines
3. ✅ **Check WORKSPACE-TASKS.json** - See active tasks and avoid duplication
4. ✅ **Check CROSS-REPO-ISSUES.json** - Be aware of known issues
5. ✅ **Verify component placement** - Ensure code belongs in correct repo
6. ✅ **Check for similar work** - Avoid duplicate effort across repos
7. ✅ **Create a plan first** - NO CODE without approved plan
8. ✅ **Document decisions** - Update ARCHITECTURE-DECISIONS.json

---

## CURRENT WORK CONTEXT

"""
        
        if current_context:
            content += f"""**Active Repository:** `{current_context.repo}`
**Context ID:** `{current_context.id}`
**Activated:** {current_context.activated_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
            if current_context.notes:
                content += f"**Notes:** {current_context.notes}\n"
        else:
            content += "**No active context set.**\n"
        
        content += f"""
**Session ID:** `{session_id}`
**Workspace Root:** `{workspace_root}`

---

## COMPONENT PLACEMENT RULES (ADR-001)

### ✅ Place in meridian-core IF:
- Works for ANY domain (generic, reusable)
- No domain-specific imports
- Abstract interface or workflow
- Reusable orchestration logic
- Generic utilities

### ❌ Do NOT place in meridian-core IF:
- Domain-specific logic (trading, research, customer support)
- Domain-specific imports (pandas for trading, etc.)
- Domain-specific business rules

### ✅ Import Rules:
- **meridian-core:** Cannot import domain adapters (meridian-trading, meridian-research)
- **Domain repos:** Can import meridian-core
- **Domain repos:** Cannot import other domain repos

### ✅ Repository Structure:
- **meridian-core:** Generic framework (orchestration, learning, connectors)
- **meridian-trading:** Trading domain adapter (strategies, indicators, risk)
- **meridian-research:** Research domain adapter (skills, knowledge, workflows)
- **workspace:** Management plane (WMS, cross-repo governance)

---

## ACTIVE WORKSPACE STATE

### Recent Tasks (from WORKSPACE-TASKS.json)
"""
        
        if workspace_tasks:
            for task in workspace_tasks[:5]:
                content += f"- **{task.get('id', 'N/A')}:** {task.get('title', 'N/A')} ({task.get('status', 'N/A')})\n"
        else:
            content += "- No active tasks found\n"
        
        content += "\n### Recent Cross-Repo Issues (from CROSS-REPO-ISSUES.json)\n"
        
        if cross_repo_issues:
            for issue in cross_repo_issues[:5]:
                content += f"- **{issue.get('id', 'N/A')}:** {issue.get('title', 'N/A')} ({issue.get('severity', 'N/A')})\n"
        else:
            content += "- No active issues found\n"
        
        content += "\n### Recent Architecture Decisions (from ARCHITECTURE-DECISIONS.json)\n"
        
        if architecture_decisions:
            for decision in architecture_decisions[-5:]:
                content += f"- **{decision.get('decision', 'N/A')}** ({decision.get('date', 'N/A')})\n"
        else:
            content += "- No recent decisions found\n"
        
        content += """
---

## ENFORCEMENT

**These rules are ENFORCED, not suggested:**
- Pre-task checklist is MANDATORY
- Component placement violations will be flagged
- Plan-before-code rule is STRICT
- Session context MUST be set before work begins

**Violations will be logged and may block commits.**

---

## SESSION PROTOCOL

1. **Session Start:**
   - Run `./session_start.sh` at workspace root
   - Confirm work context (which repo you're working in)
   - Governance context is auto-injected

2. **Before Any Work:**
   - Read this file (GOVERNANCE-CONTEXT.md)
   - Complete pre-task checklist
   - Verify component placement

3. **During Work:**
   - Follow planning guidelines
   - Document decisions
   - Check for cross-repo conflicts

4. **Session End:**
   - Run `./session_end.sh` at workspace root
   - Document session activities
   - Update task status

---

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Auto-generated by:** workspace/scripts/generate_governance_context.py
"""
        
        return content
        
    finally:
        session.close()


def main():
    """Generate GOVERNANCE-CONTEXT.md file."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate GOVERNANCE-CONTEXT.md')
    parser.add_argument('--repo', help='Work context repository (meridian-core, meridian-trading, etc.)')
    parser.add_argument('--notes', help='Context notes')
    parser.add_argument('--output', default='GOVERNANCE-CONTEXT.md', help='Output file path')
    args = parser.parse_args()
    
    workspace_root = Path.cwd()
    output_path = workspace_root / args.output
    
    print("Generating GOVERNANCE-CONTEXT.md...")
    print(f"Workspace root: {workspace_root}")
    if args.repo:
        print(f"Work context: {args.repo}")
    print()
    
    try:
        content = generate_governance_context(workspace_root, args.repo, args.notes)
        output_path.write_text(content)
        print(f"✅ Generated: {output_path}")
        print()
        print("GOVERNANCE-CONTEXT.md is ready for AI context injection.")
        return 0
    except Exception as e:
        print(f"❌ Error generating GOVERNANCE-CONTEXT.md: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

