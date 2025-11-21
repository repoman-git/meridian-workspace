#!/usr/bin/env python3
"""
Backup workspace.db and JSON governance files into workspace/backups/.

Usage:
    python workspace/scripts/backup_workspace_state.py \
        --backup-dir workspace/backups
"""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List


JSON_FILES = [
    "WORKSPACE-TASKS.json",
    "CROSS-REPO-ISSUES.json",
    "ARCHITECTURE-DECISIONS.json",
    "SESSION-LOG.json",
]


def run_sqlite_backup(db_path: Path, dest_path: Path) -> None:
    subprocess.run(
        ["sqlite3", str(db_path), f".backup {dest_path}"],
        check=True,
    )


def create_tarball(workspace_root: Path, files: List[Path], tar_path: Path) -> None:
    cmd = ["tar", "-czf", str(tar_path)] + [str(file.relative_to(workspace_root)) for file in files if file.exists()]
    subprocess.run(cmd, cwd=workspace_root, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup workspace state")
    parser.add_argument("--workspace", default=".", help="Workspace root (default: current directory)")
    parser.add_argument("--backup-dir", default="workspace/backups", help="Backup directory")
    args = parser.parse_args()

    workspace_root = Path(args.workspace).resolve()
    backup_root = (workspace_root / args.backup_dir).resolve()
    backup_root.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d")

    db_path = workspace_root / "workspace.db"
    db_backup = backup_root / f"workspace-{timestamp}.db"
    run_sqlite_backup(db_path, db_backup)

    json_files = [workspace_root / name for name in JSON_FILES]
    tar_path = backup_root / f"workspace-state-{timestamp}.tar.gz"
    create_tarball(workspace_root, json_files, tar_path)

    print(f"SQLite backup: {db_backup}")
    print(f"JSON archive:  {tar_path}")


if __name__ == "__main__":
    main()


