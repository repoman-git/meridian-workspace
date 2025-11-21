# Multi-AI Review Execution Plan

## Current Blockers

1. **No network access in this Cursor environment**  
   - `curl https://example.com` fails with “Could not resolve host,” so outbound API calls to Claude/Gemini/Grok cannot be made from here.

2. **WMS CLI dependencies originally blocked by PEP 668**  
   - System Python disallows global `pip install`. We now have a dedicated venv (`workspace/.venv`) where `sqlalchemy` and `click` are installed, so the CLI works, but only inside that venv.

3. **Meta-review scripts expect API keys + network**  
   - `meridian-core/scripts/*meta_review*.py` require keys in `.env` and need to reach cloud AI services. Without network, they fail even if we trigger them via the local MCP server.

## Proposed Solution

### A. Run Meta Reviews on a Networked Host
1. On a machine with outbound Internet:
   - Clone/pull `meridian-core` and `workspace`.
   - `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`.
   - Configure `.env` with Claude/Gemini/Grok API keys.
2. Copy the prompts from `workspace/meta-review/`:
   - `WORKSPACE.md`, `MERIDIAN-CORE.md`, `MERIDIAN-RESEARCH.md`, `MERIDIAN-TRADING.md`.
3. Run the relevant scripts (e.g., `python scripts/run_meta_review.py --files workspace/meta-review/MERIDIAN-CORE.md ...`).
4. Collect JSON reports from `logs/*.json` for traceability.

### B. Feed Results Back into WMS
1. Use the workspace CLI via the new venv:
   ```bash
   cd /Users/simonerses/data-projects
   workspace/.venv/bin/python workspace/wms/cli.py task start WS-TASK-XXX
   ```
   (start tasks once meta review says “proceed”).  
2. After implementation, complete tasks so Bastard records the completion grade:
   ```bash
   workspace/.venv/bin/python workspace/wms/cli.py task complete WS-TASK-XXX
   ```
3. Attach meta-review report references in `WORKSPACE-TASKS.json` / task notes for audit.

### C. Update Documentation
1. `meridian-core/MULTI-AI-REVIEW-GUIDE.md` – add a note that reviews must run where API access is available.
2. `workspace/README.md` – document the `workspace/.venv` pattern and point to `META-REVIEW-EXECUTION-PLAN.md`.

## Status
| Item | Status |
| --- | --- |
| WMS CLI virtualenv | ✅ (`workspace/.venv`) with `sqlalchemy` + `click`, CLI verified |
| WS-TASK-057 (CLI dependencies) | ✅ Started + completed, Bastard grade B |
| Meta-review prompts | ✅ Stored under `workspace/meta-review/*.md` |
| Network access in Cursor | ❌ (blocked; meta review must run elsewhere) |

## Next Steps
1. On a networked machine, execute the four meta-review prompts and save the JSON outputs.
2. Apply the recommendations: close obsolete tasks, rewrite where needed, and start critical ones via the workspace CLI so Bastard can issue plan grades.
3. When implementations finish, use the same CLI to complete tasks and capture Bastard completion grades.
4. (Optional) Build a simple runner that iterates through `workspace/meta-review/*.md`, invokes `run_meta_review.py`, and updates tasks automatically once a networked runtime is available.

This keeps the architecture process intact: meta reviews produce guidance, WMS/Bastard enforce execution quality, and all decisions remain auditable.***


