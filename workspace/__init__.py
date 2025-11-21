"""
Workspace Management Plane

Management plane for cross-repo workspace tracking and governance.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Workspace-level tracking, architecture governance, drift detection
DOMAIN: Cross-repo workspace management
"""

from .db import WorkspaceDB

__version__ = "0.1.0"
__all__ = ["WorkspaceDB"]

