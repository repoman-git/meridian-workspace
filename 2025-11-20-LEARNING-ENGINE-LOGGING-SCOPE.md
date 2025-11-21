# 2025-11-20 - Learning Engine Logging Scope

**Question:** Is work done in this folder logged in the learning engine?

**Answer:** **Partially** - Only work that goes through the Meridian orchestrator system is logged.

---

## What Gets Logged

### ✅ Logged Activities

**Only orchestration decisions are logged.** These happen when:

1. **Tasks executed through orchestrator** (meridian-core)
   - When `AIOrchestrator` or `AutonomousOrchestrator` executes a task
   - When tasks are run via CLI: `meridian-core orchestrator`
   - When tasks are processed from `TASK-QUEUE.json`
   - When orchestrator runs in autonomous session mode

2. **What gets logged:**
   ```
   • Task ID
   • Agent ID (which AI was chosen: claude, gpt-4, gemini, grok, etc.)
   • Task type (code_generation, documentation, etc.)
   • Success/failure status
   • Failure reason (if failed)
   • Tokens used
   • Duration (seconds)
   • Decision process (which agents were considered, scores, etc.)
   • Timestamp
   ```

3. **Where it's logged:**
   - **Primary:** `meridian-core/logs/orchestration_decisions.db` (SQLite)
   - **Fallback:** `meridian-core/logs/orchestration_log.jsonl` (JSONL)

4. **Who reads it:**
   - `OrchestrationLearningEngine` reads from the database
   - Analyzes patterns (agent success rates, task type failures, etc.)
   - Generates improvement proposals
   - Stores proposals in `logs/proposals.db`

---

## What Does NOT Get Logged

### ❌ Not Logged Activities

**General workspace activities are NOT logged:**

1. **File operations** (creating/editing files)
   - Creating architecture documents (like this one)
   - Editing code files directly
   - Creating configuration files
   - Git operations

2. **Direct code execution**
   - Running Python scripts directly (not through orchestrator)
   - Manual testing
   - Direct CLI commands (not via orchestrator)

3. **Domain-specific activities** (unless they go through orchestrator)
   - Research queries in `meridian-research` (unless using orchestrator)
   - Trading operations in `meridian-trading` (unless using orchestrator)
   - Manual API calls
   - Direct connector usage (without orchestrator)

4. **Meta-work**
   - Documentation writing
   - Architecture planning
   - Database design
   - Meeting notes
   - Task planning

---

## How to Get Work Logged

### Option 1: Use the Orchestrator

If you want your work to be logged and learned from:

1. **Create a task** in `TASK-QUEUE.json` or via API
2. **Run orchestrator:**
   ```bash
   cd meridian-core
   meridian-core orchestrator run
   ```
3. **Work will be logged** when orchestrator processes the task

### Option 2: Use Orchestrator Programmatically

```python
from meridian_core.orchestration import AutonomousOrchestrator

orchestrator = AutonomousOrchestrator()

# Create and execute task
task = {
    "title": "Review architecture document",
    "description": "Review the new architecture document",
    "task_type": "code_review"
}

result = orchestrator.execute_task(task)
# This will be logged automatically
```

### Option 3: Use Domain Adapters with Orchestrator

**meridian-research:**
- Uses orchestrator internally via `MeridianCoreAdapter`
- Research sessions are logged in `data/learning/sessions/*.json.enc`
- Learning engine analyzes these sessions

**meridian-trading:**
- Would use orchestrator via `OrchestratorBridge`
- Trading decisions would be logged (when implemented)
- Learning engine would analyze trading performance

---

## Current Logging Status

### What's Currently Being Logged

```
Found databases:
✅ /Users/simonerses/data-projects/meridian-core/benchmarks/challenging_test/orchestration_decisions.db
✅ /Users/simonerses/data-projects/meridian-core/benchmarks/orchestrator_results/orchestration_decisions.db
✅ /Users/simonerses/data-projects/meridian-trading/logs/orchestration_decisions.db
```

These databases contain:
- **Benchmark runs** (test orchestrator tasks)
- **Orchestrator results** (actual orchestrator executions)
- **Trading decisions** (if trading system used orchestrator)

### What's NOT Currently Being Logged

- ❌ Architecture document creation (this work)
- ❌ Code review activities (unless via orchestrator)
- ❌ Manual file edits
- ❌ Direct script execution
- ❌ Git operations
- ❌ General development work

---

## Learning Engine Analysis

### What the Learning Engine Reads

The `OrchestrationLearningEngine` reads from:

1. **Source:** `logs/orchestration_decisions.db` (SQLite)
   - All orchestration decisions stored there

2. **Analysis performed:**
   - Agent success rates (which agents work best for which tasks)
   - Task type performance (which task types succeed/fail)
   - Failure patterns (common failure reasons)
   - Token usage patterns
   - Performance optimization opportunities

3. **Output:**
   - Proposals stored in `logs/proposals.db`
   - Improvement suggestions
   - Pattern detection results

### What the Learning Engine Does NOT Analyze

- ❌ File changes (Git history)
- ❌ Direct code edits
- ❌ Manual testing
- ❌ Documentation work
- ❌ General workspace activity

---

## Summary

| Activity Type | Logged? | Notes |
|--------------|---------|-------|
| Orchestrator tasks | ✅ Yes | All orchestrator decisions logged |
| Benchmark runs | ✅ Yes | Test orchestrator tasks logged |
| Research via orchestrator | ✅ Yes | Via meridian-research adapter |
| Trading via orchestrator | ✅ Yes | Via meridian-trading adapter |
| Direct file edits | ❌ No | Only if files changed via orchestrator task |
| Manual script execution | ❌ No | Only if script executed via orchestrator |
| Architecture docs (like this) | ❌ No | General workspace activity |
| Git operations | ❌ No | Not tracked by learning engine |
| Code review (manual) | ❌ No | Only if done via orchestrator |

---

## Recommendation

If you want your development work to be learned from by the system:

1. **Create tasks** in orchestrator task queue
2. **Use orchestrator** to execute development tasks
3. **Use domain adapters** (meridian-research, meridian-trading) which use orchestrator internally
4. **Run autonomous sessions** which process tasks and log decisions

**Current work (architecture documents, credential consolidation, etc.)** is NOT logged because it's:
- General workspace activity
- Not executed through orchestrator
- Not part of the task execution workflow

---

**Last Updated:** 2025-11-20  
**Status:** Current State Analysis

