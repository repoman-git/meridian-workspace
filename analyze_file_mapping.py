#!/usr/bin/env python3
"""
File Mapping Coverage Analysis - BASTARD-APPROVED-PLAN Day 2 Task 2.1

Analyzes current file mapping state and creates comprehensive analysis document.
"""

import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.architecture_validator import ArchitectureValidator


def count_files_in_repo(repo_path: Path, extensions: set = None) -> int:
    """Count files in a repository directory."""
    if not repo_path.exists():
        return 0
    
    count = 0
    # Common ignore patterns
    ignore_dirs = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', 
                   'build', 'dist', '.pytest_cache', '.mypy_cache', '.tox',
                   'venv*', '*.egg-info', '.eggs', '.env', 'logs'}
    
    for file_path in repo_path.rglob('*'):
        if file_path.is_file():
            # Skip ignored directories
            if any(ignore in file_path.parts for ignore in ignore_dirs):
                continue
            
            # Filter by extension if specified
            if extensions and file_path.suffix.lower() not in extensions:
                continue
            
            count += 1
    
    return count


def analyze_file_mapping():
    """Analyze current file mapping coverage."""
    print("\n" + "="*60)
    print("BASTARD-APPROVED-PLAN - Day 2 Task 2.1")
    print("File Mapping Coverage Analysis")
    print("="*60)
    
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        validator = ArchitectureValidator(session, workspace_root)
        
        # Get unregistered files
        unregistered = validator.get_unregistered_files()
        print(f"\nUnregistered files found: {len(unregistered)}")
        
        # Get mapped files count
        from workspace.db.models import CodeComponentMapping
        mapped_count = session.query(CodeComponentMapping).count()
        print(f"Mapped files in database: {mapped_count}")
        
        # Count total files in repos (Python files only for now)
        repos = {
            "meridian-core": workspace_root / "meridian-core",
            "meridian-research": workspace_root / "meridian-research",
            "meridian-trading": workspace_root / "meridian-trading",
            "workspace": workspace_root / "workspace",
        }
        
        print("\n" + "-"*60)
        print("Counting total files in repos...")
        print("-"*60)
        
        total_files = {}
        code_extensions = {'.py', '.md', '.json', '.yaml', '.yml', '.toml'}
        
        for repo_name, repo_path in repos.items():
            count = count_files_in_repo(repo_path, extensions=code_extensions)
            total_files[repo_name] = count
            print(f"{repo_name}: {count} files")
        
        grand_total = sum(total_files.values())
        print(f"\nTotal files across all repos: {grand_total}")
        
        # Calculate coverage
        total_unregistered = len(unregistered)
        # Note: mapped_count might be less accurate, use unregistered as baseline
        # Coverage = (total - unregistered) / total * 100
        if grand_total > 0:
            current_coverage = ((grand_total - total_unregistered) / grand_total) * 100
        else:
            current_coverage = 0
        
        print("\n" + "="*60)
        print("COVERAGE SUMMARY")
        print("="*60)
        print(f"Total files: {grand_total}")
        print(f"Unregistered: {total_unregistered}")
        print(f"Mapped (estimated): {grand_total - total_unregistered}")
        print(f"Current coverage: {current_coverage:.1f}%")
        print(f"Target coverage: 70.0%")
        print(f"Gap to target: {70.0 - current_coverage:.1f}%")
        
        # Analyze patterns
        print("\n" + "="*60)
        print("PATTERN ANALYSIS")
        print("="*60)
        
        # Group unregistered files by repo
        by_repo = defaultdict(list)
        by_extension = defaultdict(int)
        by_directory = defaultdict(int)
        test_files = []
        config_files = []
        core_files = []
        
        for uf in unregistered:
            by_repo[uf.repo].append(uf)
            
            file_path_obj = Path(uf.file_path)
            ext = file_path_obj.suffix.lower() or "(no extension)"
            by_extension[ext] += 1
            
            # Check if it's a test file
            if 'test' in file_path_obj.parts or file_path_obj.name.startswith('test_'):
                test_files.append(uf)
            
            # Check if it's a config file
            if file_path_obj.suffix.lower() in {'.json', '.yaml', '.yml', '.toml', '.md'}:
                config_files.append(uf)
            
            # Get top-level directory
            if len(file_path_obj.parts) > 0:
                top_dir = file_path_obj.parts[0]
                by_directory[top_dir] += 1
        
        print(f"\nUnregistered files by repo:")
        for repo, files in sorted(by_repo.items()):
            print(f"  {repo}: {len(files)} files ({len(files)/total_unregistered*100:.1f}%)")
        
        print(f"\nUnregistered files by extension:")
        for ext, count in sorted(by_extension.items(), key=lambda x: -x[1]):
            print(f"  {ext:20} {count:4} files ({count/total_unregistered*100:5.1f}%)")
        
        print(f"\nUnregistered files by top-level directory:")
        for dir_name, count in sorted(by_directory.items(), key=lambda x: -x[1])[:10]:
            print(f"  {dir_name:30} {count:4} files ({count/total_unregistered*100:5.1f}%)")
        
        print(f"\nSpecial categories:")
        print(f"  Test files: {len(test_files)} ({len(test_files)/total_unregistered*100:.1f}%)")
        print(f"  Config/docs: {len(config_files)} ({len(config_files)/total_unregistered*100:.1f}%)")
        
        # Identify high-value files to map
        print("\n" + "="*60)
        print("HIGH-VALUE FILES TO MAP")
        print("="*60)
        
        print("\nPriority 1: Core files (non-test, non-config):")
        high_value = [uf for uf in unregistered 
                     if uf not in test_files and uf not in config_files
                     and Path(uf.file_path).suffix == '.py']
        
        # Group by repo and show top files
        high_value_by_repo = defaultdict(list)
        for uf in high_value:
            high_value_by_repo[uf.repo].append(uf)
        
        for repo, files in sorted(high_value_by_repo.items()):
            print(f"\n  {repo}: {len(files)} high-value files")
            for uf in files[:10]:
                print(f"    • {uf.file_path}")
            if len(files) > 10:
                print(f"    ... and {len(files) - 10} more")
        
        # Create analysis document
        output_path = workspace_root / "FILE-MAPPING-ANALYSIS.md"
        
        analysis_content = f"""# File Mapping Coverage Analysis

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Task:** Day 2 Task 2.1 - Current State Analysis  
**Status:** Analysis Complete

---

## Summary

- **Total Files:** {grand_total}
- **Unregistered Files:** {total_unregistered}
- **Mapped Files (estimated):** {grand_total - total_unregistered}
- **Current Coverage:** {current_coverage:.1f}%
- **Target Coverage:** 70.0%
- **Gap to Target:** {max(0, 70.0 - current_coverage):.1f}%

---

## Breakdown by Repository

"""
        
        for repo_name, repo_total in sorted(total_files.items()):
            repo_unregistered = len(by_repo[repo_name])
            repo_mapped = repo_total - repo_unregistered
            repo_coverage = (repo_mapped / repo_total * 100) if repo_total > 0 else 0
            
            analysis_content += f"""### {repo_name}
- **Total files:** {repo_total}
- **Unregistered:** {repo_unregistered}
- **Mapped:** {repo_mapped}
- **Coverage:** {repo_coverage:.1f}%

"""
        
        analysis_content += f"""
---

## Pattern Analysis

### By File Extension

"""
        
        for ext, count in sorted(by_extension.items(), key=lambda x: -x[1]):
            pct = (count / total_unregistered * 100) if total_unregistered > 0 else 0
            analysis_content += f"- **{ext}**: {count} files ({pct:.1f}%)\n"
        
        analysis_content += f"""
### By Top-Level Directory

"""
        
        for dir_name, count in sorted(by_directory.items(), key=lambda x: -x[1])[:15]:
            pct = (count / total_unregistered * 100) if total_unregistered > 0 else 0
            analysis_content += f"- **{dir_name}**: {count} files ({pct:.1f}%)\n"
        
        analysis_content += f"""
### Special Categories

- **Test files:** {len(test_files)} ({len(test_files)/total_unregistered*100:.1f}%)
- **Config/docs files:** {len(config_files)} ({len(config_files)/total_unregistered*100:.1f}%)
- **Core Python files:** {len(high_value)} ({len(high_value)/total_unregistered*100:.1f}%)

---

## High-Value Files to Map (Priority 1)

These are core Python files (non-test, non-config) that should be mapped first.

### Total High-Value Files: {len(high_value)}

"""
        
        for repo, files in sorted(high_value_by_repo.items()):
            analysis_content += f"""### {repo} ({len(files)} files)

"""
            for uf in files[:20]:
                analysis_content += f"- `{uf.file_path}`\n"
            if len(files) > 20:
                analysis_content += f"- ... and {len(files) - 20} more\n"
            analysis_content += "\n"
        
        analysis_content += f"""
---

## Top 20 Unmapped Files (All Categories)

"""
        
        shown = 0
        for repo, files in sorted(by_repo.items()):
            for uf in files[:5]:
                if shown < 20:
                    analysis_content += f"1. **{repo}**: `{uf.file_path}`\n"
                    shown += 1
            if shown >= 20:
                break
        
        analysis_content += f"""
---

## Mapping Strategy

### Target: 70% Coverage

**Current:** {current_coverage:.1f}%  
**Target:** 70.0%  
**Gap:** {max(0, 70.0 - current_coverage):.1f}%

### Recommended Approach

1. **Priority 1: Map High-Value Core Files** ({len(high_value)} files)
   - Focus on non-test, non-config Python files
   - Files in `src/` directories
   - Files you actually work with

2. **Priority 2: Map Frequently Used Files**
   - Files in `scripts/` directories
   - Files in `wms/` directories (workspace management)
   - Files in `db/` directories (database access)

3. **Priority 3: Skip Low-Priority Files**
   - Test files (unless blocking something)
   - Config files (usually obvious placement)
   - Documentation files (not code)

### Estimated Effort

- **High-value files to map:** ~{len(high_value)} files
- **Estimated time:** 2 hours (Task 2.2)
- **Expected coverage after mapping:** ~70%+

---

## Files to Skip (Low Priority)

These can be mapped later or skipped:

- **Test files:** {len(test_files)} files (obvious placement)
- **Config/docs:** {len(config_files)} files (obvious placement)

**Total skip:** {len(test_files) + len(config_files)} files

---

## Next Steps

1. ✅ Task 2.1 Complete - Analysis done
2. ⏭️  Task 2.2: Map High-Value Files (2 hours)
   - Map {len(high_value)} high-value core files
   - Target: 70% coverage
   - Focus on files you actually work with

---

**Analysis Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Next Task:** Day 2 Task 2.2 - Map High-Value Files
"""
        
        output_path.write_text(analysis_content, encoding='utf-8')
        print(f"\n✅ Analysis document created: {output_path}")
        
        return {
            "total_files": grand_total,
            "unregistered": total_unregistered,
            "mapped": grand_total - total_unregistered,
            "coverage": current_coverage,
            "high_value_count": len(high_value),
        }
        
    finally:
        session.close()


if __name__ == "__main__":
    try:
        results = analyze_file_mapping()
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"\n✅ File mapping analysis complete")
        print(f"   Coverage: {results['coverage']:.1f}%")
        print(f"   High-value files to map: {results['high_value_count']}")
        print(f"\n✅ See FILE-MAPPING-ANALYSIS.md for full details")
        print("="*60)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

