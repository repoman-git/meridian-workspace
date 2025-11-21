#!/usr/bin/env python3
"""
Commit and push changes across all repositories.

REPO: workspace (management plane)
LAYER: Management Plane
PURPOSE: Commit and push changes across all repos with clean working trees
DOMAIN: Cross-repo workspace management
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import json

# Add workspace to path
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))


def run_command(cmd: List[str], cwd: Path, check: bool = True) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout, e.stderr


def get_git_status(repo_path: Path) -> Dict:
    """Get git status for a repository."""
    status = {
        'is_repo': (repo_path / '.git').exists(),
        'has_changes': False,
        'has_untracked': False,
        'has_uncommitted': False,
        'current_branch': None,
        'has_remote': False,
        'changes': []
    }
    
    if not status['is_repo']:
        return status
    
    # Check current branch
    exit_code, stdout, _ = run_command(['git', 'branch', '--show-current'], repo_path, check=False)
    if exit_code == 0:
        status['current_branch'] = stdout.strip()
    
    # Check for changes
    exit_code, stdout, _ = run_command(['git', 'status', '--porcelain'], repo_path, check=False)
    if exit_code == 0:
        lines = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
        if lines:
            status['has_changes'] = True
            status['changes'] = lines
            status['has_untracked'] = any(line.startswith('??') for line in lines)
            status['has_uncommitted'] = any(not line.startswith('??') for line in lines)
    
    # Check for remote
    exit_code, stdout, _ = run_command(['git', 'remote', '-v'], repo_path, check=False)
    if exit_code == 0 and stdout.strip():
        status['has_remote'] = True
    
    return status


def commit_repo(repo_path: Path, repo_name: str, message: str = None) -> Tuple[bool, str]:
    """Commit changes in a repository."""
    if not message:
        message = f"WMS: Update workspace management and governance enforcement\n\n- Enhanced session management\n- Added architecture alignment enforcement\n- Created weekly housekeeping task\n- Imported tasks from architecture reviews\n\nDate: {datetime.now().strftime('%Y-%m-%d')}"
    
    # Check status
    status = get_git_status(repo_path)
    
    if not status['is_repo']:
        return False, "Not a git repository"
    
    if not status['has_changes']:
        return True, "No changes to commit"
    
    # Stage all changes
    print(f"   Staging changes...")
    exit_code, stdout, stderr = run_command(['git', 'add', '-A'], repo_path, check=False)
    if exit_code != 0:
        return False, f"Failed to stage: {stderr}"
    
    # Commit
    print(f"   Committing changes...")
    exit_code, stdout, stderr = run_command(
        ['git', 'commit', '-m', message],
        repo_path,
        check=False
    )
    if exit_code != 0:
        return False, f"Failed to commit: {stderr}"
    
    return True, stdout.strip()


def push_repo(repo_path: Path, repo_name: str) -> Tuple[bool, str]:
    """Push changes to remote."""
    status = get_git_status(repo_path)
    
    if not status['has_remote']:
        return True, "No remote configured (skipped)"
    
    if not status['current_branch']:
        return False, "No current branch"
    
    # Push
    print(f"   Pushing to remote...")
    exit_code, stdout, stderr = run_command(
        ['git', 'push', 'origin', status['current_branch']],
        repo_path,
        check=False
    )
    if exit_code != 0:
        return False, f"Failed to push: {stderr}"
    
    return True, stdout.strip()


def commit_all_repos(workspace_root: Path, commit_message: str = None, push: bool = True):
    """Commit and push changes across all repositories."""
    print("=" * 70)
    print("  COMMIT AND PUSH ALL REPOSITORIES")
    print("=" * 70)
    print()
    print(f"Workspace: {workspace_root}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    repos = ['meridian-core', 'meridian-trading', 'meridian-research']
    
    # Check workspace root
    workspace_is_repo = (workspace_root / '.git').exists()
    if workspace_is_repo:
        repos.insert(0, '.')
    
    results = []
    
    for repo_name in repos:
        repo_path = workspace_root / repo_name if repo_name != '.' else workspace_root
        
        print(f"──────────────────────────────────────────────────────────────────────")
        print(f"Repository: {repo_name}")
        print(f"──────────────────────────────────────────────────────────────────────")
        print()
        
        if not repo_path.exists():
            print(f"   ⚠️  Repository not found: {repo_path}")
            results.append({
                'repo': repo_name,
                'status': 'skipped',
                'reason': 'not found'
            })
            print()
            continue
        
        # Get status
        status = get_git_status(repo_path)
        
        if not status['is_repo']:
            print(f"   ⚠️  Not a git repository: {repo_path}")
            results.append({
                'repo': repo_name,
                'status': 'skipped',
                'reason': 'not a git repo'
            })
            print()
            continue
        
        print(f"   Branch: {status['current_branch']}")
        print(f"   Remote: {'✅ Yes' if status['has_remote'] else '❌ No'}")
        print()
        
        if not status['has_changes']:
            print(f"   ✅ No changes to commit (clean tree)")
            results.append({
                'repo': repo_name,
                'status': 'clean',
                'branch': status['current_branch']
            })
            print()
            continue
        
        # Show changes summary
        if status['changes']:
            print(f"   Changes:")
            for line in status['changes'][:10]:
                if line.startswith('??'):
                    print(f"      + {line[3:]} (untracked)")
                elif line.startswith(' M') or line.startswith('M '):
                    print(f"      ~ {line[3:]} (modified)")
                elif line.startswith(' A') or line.startswith('A '):
                    print(f"      + {line[3:]} (added)")
                elif line.startswith(' D') or line.startswith('D '):
                    print(f"      - {line[3:]} (deleted)")
                else:
                    print(f"      ? {line} (unknown)")
            if len(status['changes']) > 10:
                print(f"      ... and {len(status['changes']) - 10} more")
            print()
        
        # Commit
        success, message = commit_repo(repo_path, repo_name, commit_message)
        
        if not success:
            print(f"   ❌ Commit failed: {message}")
            results.append({
                'repo': repo_name,
                'status': 'failed',
                'reason': message
            })
            print()
            continue
        
        print(f"   ✅ Committed: {message[:60]}...")
        results.append({
            'repo': repo_name,
            'status': 'committed',
            'branch': status['current_branch']
        })
        
        # Push if requested
        if push:
            push_success, push_message = push_repo(repo_path, repo_name)
            if push_success:
                if "No remote" in push_message:
                    print(f"   ℹ️  {push_message}")
                else:
                    print(f"   ✅ Pushed to remote")
                results[-1]['pushed'] = push_success
            else:
                print(f"   ⚠️  Push failed: {push_message}")
                results[-1]['pushed'] = False
                results[-1]['push_error'] = push_message
        
        print()
    
    # Summary
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print()
    
    committed = [r for r in results if r['status'] == 'committed']
    clean = [r for r in results if r['status'] == 'clean']
    skipped = [r for r in results if r['status'] == 'skipped']
    failed = [r for r in results if r['status'] == 'failed']
    
    print(f"✅ Committed: {len(committed)}")
    for r in committed:
        print(f"   • {r['repo']}: {r['branch']}")
    
    print(f"\n✅ Clean (no changes): {len(clean)}")
    for r in clean:
        print(f"   • {r['repo']}")
    
    if skipped:
        print(f"\n⏭️  Skipped: {len(skipped)}")
        for r in skipped:
            print(f"   • {r['repo']}: {r['reason']}")
    
    if failed:
        print(f"\n❌ Failed: {len(failed)}")
        for r in failed:
            print(f"   • {r['repo']}: {r['reason']}")
    
    print()
    
    # Verify all trees are clean
    print("Verifying all trees are clean...")
    print()
    
    all_clean = True
    for repo_name in repos:
        repo_path = workspace_root / repo_name if repo_name != '.' else workspace_root
        
        if not repo_path.exists():
            continue
        
        status = get_git_status(repo_path)
        if status['is_repo']:
            if status['has_changes']:
                print(f"   ⚠️  {repo_name}: Still has uncommitted changes")
                all_clean = False
            else:
                print(f"   ✅ {repo_name}: Clean")
    
    print()
    
    if all_clean and not failed:
        print("✅ All repositories have clean working trees!")
    elif failed:
        print("⚠️  Some repositories failed to commit")
    else:
        print("⚠️  Some repositories still have uncommitted changes")
    
    print()
    
    return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Commit and push changes across all repositories')
    parser.add_argument('--message', '-m', help='Commit message (default: auto-generated)')
    parser.add_argument('--no-push', action='store_true', help='Don\'t push to remote')
    parser.add_argument('--workspace-root', default=None, help='Workspace root directory')
    args = parser.parse_args()
    
    workspace_root = Path(args.workspace_root) if args.workspace_root else Path.cwd()
    
    try:
        results = commit_all_repos(
            workspace_root,
            commit_message=args.message,
            push=not args.no_push
        )
        
        # Exit with error code if any failed
        failed = [r for r in results if r.get('status') == 'failed']
        if failed:
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Commit cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())



