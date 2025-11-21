"""
Workspace Database Module

Management plane database for workspace tracking.
Uses SQLAlchemy + SQLite, following meridian-core patterns.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Workspace-level task tracking, architecture tracking, drift detection
DOMAIN: Cross-repo workspace management
"""

from .workspace_db import WorkspaceDB
from .models import (
    Base,
    WorkspaceTask,
    WorkspaceSession,
    CrossRepoIssue,
    ArchitectureDecision,
    ArchitectureState,
    ComponentPlacement,
    DriftDetection,
    ContextSwitch,
)

__all__ = [
    "WorkspaceDB",
    "Base",
    "WorkspaceTask",
    "WorkspaceSession",
    "CrossRepoIssue",
    "ArchitectureDecision",
    "ArchitectureState",
    "ComponentPlacement",
    "DriftDetection",
    "ContextSwitch",
]

