"""
REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Migrate existing JSON files to workspace database
DOMAIN: Cross-repo workspace management

Migration script to import existing JSON tracking files into database.
"""

from pathlib import Path
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .workspace_db import WorkspaceDB

logger = logging.getLogger(__name__)


def migrate_json_to_database(
    workspace_root: Path,
    db: Optional[WorkspaceDB] = None,
    json_files: Optional[Dict[str, str]] = None,
) -> Dict[str, int]:
    """
    Migrate existing JSON files to workspace database.
    
    Args:
        workspace_root: Workspace root directory
        db: WorkspaceDB instance (creates if None)
        json_files: Dict mapping file types to file paths
    
    Returns:
        Dictionary with migration counts
    """
    if db is None:
        db = WorkspaceDB(workspace_root=workspace_root)
    
    if json_files is None:
        json_files = {
            "tasks": "WORKSPACE-TASKS.json",
            "sessions": "SESSION-LOG.json",
            "issues": "CROSS-REPO-ISSUES.json",
            "decisions": "ARCHITECTURE-DECISIONS.json",
        }
    
    counts = {"tasks": 0, "sessions": 0, "issues": 0, "decisions": 0}
    
    # Migrate tasks
    tasks_file = workspace_root / json_files.get("tasks", "WORKSPACE-TASKS.json")
    if tasks_file.exists():
        try:
            with open(tasks_file) as f:
                data = json.load(f)
            
            if "active_tasks" in data:
                for task_data in data["active_tasks"]:
                    try:
                        db.add_task(
                            task_id=task_data.get("id", f"WS-TASK-{counts['tasks']}"),
                            title=task_data.get("title", ""),
                            status=task_data.get("status", "pending"),
                            priority=task_data.get("priority"),
                            repos_affected=task_data.get("repos_affected", []),
                            dependencies=task_data.get("dependencies", []),
                            description=task_data.get("description"),
                            session_created=task_data.get("session_created"),
                            assigned_to=task_data.get("assigned_to"),
                            notes=task_data.get("notes"),
                            related_files=task_data.get("related_files", []),
                        )
                        counts["tasks"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to migrate task {task_data.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Failed to read tasks file: {e}")
    
    # Migrate sessions
    sessions_file = workspace_root / json_files.get("sessions", "SESSION-LOG.json")
    if sessions_file.exists():
        try:
            with open(sessions_file) as f:
                data = json.load(f)
            
            if "sessions" in data:
                for session_data in data["sessions"]:
                    try:
                        # Add session
                        session = db.add_session(
                            session_id=session_data.get("session_id", ""),
                            user=session_data.get("user"),
                            ai_assistant=session_data.get("ai_assistant"),
                            handoff_notes=session_data.get("handoff_notes"),
                        )
                        
                        # Add activities
                        if "activities" in session_data:
                            for activity_data in session_data["activities"]:
                                db.add_session_activity(
                                    session_id=session.id,
                                    activity_type=activity_data.get("type", "unknown"),
                                    description=activity_data.get("description", ""),
                                    files_created=activity_data.get("files_created", []),
                                    outcome=activity_data.get("outcome"),
                                )
                        
                        # End session if completed
                        if session_data.get("status") == "completed":
                            db.end_session(session.id)
                        
                        counts["sessions"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to migrate session {session_data.get('session_id')}: {e}")
        except Exception as e:
            logger.error(f"Failed to read sessions file: {e}")
    
    # Migrate issues
    issues_file = workspace_root / json_files.get("issues", "CROSS-REPO-ISSUES.json")
    if issues_file.exists():
        try:
            with open(issues_file) as f:
                data = json.load(f)
            
            if "issues" in data:
                for issue_data in data["issues"]:
                    try:
                        db.add_issue(
                            issue_id=issue_data.get("id", ""),
                            issue_type=issue_data.get("type", "unknown"),
                            severity=issue_data.get("severity", "MEDIUM"),
                            title=issue_data.get("title", ""),
                            description=issue_data.get("description"),
                            repos_affected=issue_data.get("repos_affected", []),
                            detected_by=issue_data.get("detected_by", "manual"),
                            action_required=issue_data.get("action_required"),
                            related_task_id=issue_data.get("related_task"),
                        )
                        counts["issues"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to migrate issue {issue_data.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Failed to read issues file: {e}")
    
    # Migrate decisions
    decisions_file = workspace_root / json_files.get("decisions", "ARCHITECTURE-DECISIONS.json")
    if decisions_file.exists():
        try:
            with open(decisions_file) as f:
                data = json.load(f)
            
            if "decisions" in data:
                for decision_data in data["decisions"]:
                    try:
                        from datetime import datetime
                        date = datetime.fromisoformat(decision_data.get("date", datetime.utcnow().isoformat()))
                        
                        db.add_decision(
                            decision_id=decision_data.get("id", ""),
                            session=decision_data.get("session", ""),
                            decision=decision_data.get("decision", ""),
                            repos_affected=decision_data.get("repos_affected", []),
                            rationale=decision_data.get("rationale"),
                            status=decision_data.get("status", "implemented"),
                            impact=decision_data.get("impact"),
                            related_files=decision_data.get("related_files", []),
                            documentation=decision_data.get("documentation", []),
                        )
                        counts["decisions"] += 1
                    except Exception as e:
                        logger.warning(f"Failed to migrate decision {decision_data.get('id')}: {e}")
        except Exception as e:
            logger.error(f"Failed to read decisions file: {e}")
    
    logger.info(f"Migration complete: {counts}")
    return counts

