#!/usr/bin/env python3
"""
Sync critical workspace markdown specs into Meridian-Core-Operations.

Usage:
    python workspace/scripts/sync_workspace_docs.py \
        --dest /Users/simonerses/data-projects/Meridian-Core-Operations/workspace-management/docs
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


DOC_MAP: Dict[str, str] = {
    # Architecture specs
    "2025-11-20-MERIDIAN-CORE-ARCHITECTURE.md": "architecture",
    "2025-11-20-MERIDIAN-RESEARCH-ARCHITECTURE.md": "architecture",
    "2025-11-20-MERIDIAN-TRADING-ARCHITECTURE.md": "architecture",
    "MERIDIAN-REPO-ARCHITECTURE.md": "architecture",
    "MERIDIAN-REPO-ANALYSIS.md": "architecture",
    "MERIDIAN-ARCHIVE-EVALUATION.md": "architecture",
    "SELF-LEARNING-ARCHITECTURE-DIAGRAM.md": "architecture",

    # Governance / operations
    "2025-11-20-PROJECT-GOVERNANCE-AND-TASK-TRACKING-RECOMMENDATIONS.md": "governance",
    "2025-11-20-WMS-IMPLEMENTATION-COMPLETE.md": "governance",
    "2025-11-20-WMS-SPEC-INTEGRATION-ANALYSIS.md": "governance",
    "2025-11-20-WORKSPACE-CONTEXT-SYSTEM.md": "governance",
    "2025-11-20-WORKSPACE-DATABASE-ANALYSIS.md": "governance",
    "2025-11-20-WORKSPACE-DATABASE-IMPLEMENTATION-COMPLETE.md": "governance",
    "ARCHITECTURE-REVIEW-2025-11-20.md": "governance",
    "2025-11-20-BASTARD-INTEGRATION-WITH-WMS.md": "governance",
    "BASTARD-EXAMPLE-OVER-ENGINEERING.md": "governance",
    "BASTARD-V2-SUMMARY.md": "governance",
    "MERIDIAN-MIGRATION-SUMMARY.md": "governance",
    "MERIDIAN-TESTING-REPORT.md": "governance",
    "MERIDIAN-TESTING-COMPLETE.md": "governance",
    "MERIDIAN-TESTING-SUMMARY.md": "governance",
    "MERIDIAN-MCP-TESTING-COMPLETE.md": "governance",
    "2025-11-20-LEARNING-ENGINE-LOGGING-SCOPE.md": "governance",
    "2025-11-20-DATABASE-TECHNOLOGY-ANALYSIS.md": "governance",
    "2025-11-20-CREDENTIAL-MANAGEMENT-ARCHITECTURE.md": "governance",
    "CREDENTIAL-BRIDGE-STATUS.md": "governance",

    # Code-to-architecture / compliance
    "2025-11-20-CODE-TO-ARCHITECTURE-TRACKING.md": "code-alignment",
    "2025-11-20-CONFIGURATION-DRIFT-TRACKING-SYSTEM.md": "code-alignment",
    "CREDENTIAL-CONFIGURATION-ANALYSIS.md": "code-alignment",
    "CREDENTIAL-CONSOLIDATION-COMPLETE.md": "code-alignment",
    "CREDENTIAL-TASKS-EXPLAINED.md": "code-alignment",
}

EXCLUDES = {
    "GOVERNANCE-CONTEXT.md",
    "SESSION-HANDOVER-20251120-233809.md",
    "SESSION-HANDOVER-20251120-233832.md",
    "SESSION-HANDOVER-20251120-234300.md",
}


def sync_docs(workspace_root: Path, dest_root: Path) -> List[Tuple[Path, Path]]:
    copied: List[Tuple[Path, Path]] = []
    for filename, category in DOC_MAP.items():
        source = workspace_root / filename
        if not source.exists():
            continue
        if filename in EXCLUDES:
            continue
        dest_dir = dest_root / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename
        shutil.copy2(source, dest)
        copied.append((source, dest))
    return copied


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync workspace markdown docs into operations repo")
    parser.add_argument(
        "--workspace",
        default=str(Path(__file__).resolve().parents[2]),
        help="Workspace root (defaults to repo root)",
    )
    parser.add_argument(
        "--dest",
        required=False,
        default="/Users/simonerses/data-projects/Meridian-Core-Operations/workspace-management/docs",
        help="Destination docs directory inside Meridian-Core-Operations",
    )
    args = parser.parse_args()

    workspace_root = Path(args.workspace).resolve()
    dest_root = Path(args.dest).resolve()

    dest_root.mkdir(parents=True, exist_ok=True)
    copied = sync_docs(workspace_root, dest_root)

    if not copied:
        print("No documents copied (missing files or already synced).")
        return

    print("Copied documents:")
    for src, dst in copied:
        rel_dst = dst.relative_to(dest_root)
        print(f"  {src.name} -> {rel_dst}")


if __name__ == "__main__":
    main()


