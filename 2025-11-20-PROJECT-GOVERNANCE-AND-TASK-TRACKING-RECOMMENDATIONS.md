# 2025-11-20 - Project Governance and Task Tracking Recommendations

**Date:** 2025-11-20  
**Context:** After architecture documentation session, assessing governance and task tracking  
**Purpose:** Recommendations for avoiding silos, controlling code creep, and improving AI collaboration

---

## Executive Summary

Based on this session's findings:
1. ✅ **Architecture docs created** - Good foundation for context
2. ⚠️ **Task tracking fragmented** - Multiple TASK-QUEUE.json files across repos
3. ⚠️ **Code creep happening** - Despite governance docs, work splinters across repos
4. ⚠️ **AI guidelines not enforced** - Docs exist but not consistently followed
5. ⚠️ **Session boundaries unclear** - Work from previous sessions not properly tracked

**Key Recommendation:** Implement a **unified workspace-level task tracking system** with **explicit session handoff protocols**.

---

## Current Problems Identified

### Problem 1: Fragmented Task Tracking

**Current State:**
- Multiple TASK-QUEUE.json files:
  - `meridian-core/task-queue.json`
  - `meridian-trading/TASK-QUEUE.json`
  - `meridian/BACKLOG.json`
  - `meridian/COMPLETED-TASKS.json`
  - Various other task files

**Impact:**
- ❌ Tasks scattered across repos
- ❌ No unified view of work
- ❌ Cross-repo dependencies not visible
- ❌ Duplicate work possible
- ❌ Session continuity lost

### Problem 2: Code Creep Despite Governance Docs

**Current State:**
- ✅ AI-GUIDELINES.md exists
- ✅ AI-HOUSE-MODEL.md exists
- ✅ ADR-001-COMPONENT-PLACEMENT.md exists
- ❌ **But code still creeps into wrong repos**

**Why?**
1. **AI agents don't check docs first** - Start coding before reading governance
2. **Docs not "injected" into context** - Not automatically included in prompts
3. **No enforcement mechanism** - Docs are suggestions, not enforced rules
4. **Session boundaries unclear** - Previous session decisions not visible
5. **User communication may be unclear** - Instructions might not emphasize governance

### Problem 3: Session Handoff Gaps

**Current State:**
- Work done in one session not clearly documented for next session
- AI agents start "fresh" without context of previous work
- Decisions made in one session not visible in next
- Architectural changes not tracked across sessions

---

## Recommendations

### Recommendation 1: Unified Workspace-Level Task Tracking

**Create a workspace-level task tracking system at the parent folder level.**

```
data-projects/
├── WORKSPACE-TASKS.json          ← NEW: Unified task tracking
├── SESSION-LOG.json              ← NEW: Session activity log
├── CROSS-REPO-ISSUES.json        ← NEW: Cross-repo issues
├── ARCHITECTURE-DECISIONS.json   ← NEW: Architecture decisions log
│
├── meridian-core/
│   ├── task-queue.json          ← Repo-specific tasks (if needed)
│   └── ...
├── meridian-research/
│   └── ...
└── meridian-trading/
    ├── TASK-QUEUE.json           ← Repo-specific tasks (if needed)
    └── ...
```

#### WORKSPACE-TASKS.json Structure

```json
{
  "version": "1.0",
  "workspace": "data-projects",
  "last_updated": "2025-11-20T...",
  "updated_by": "session-id",
  
  "session_context": {
    "current_session": "2025-11-20-session-001",
    "session_start": "2025-11-20T...",
    "previous_session": "2025-11-19-session-002",
    "session_handoff_notes": "Architecture docs created. Credential consolidation complete."
  },
  
  "active_tasks": [
    {
      "id": "WS-TASK-001",
      "title": "Implement TradingLearningEngine",
      "status": "pending",
      "priority": "HIGH",
      "repos_affected": ["meridian-trading", "meridian-core"],
      "dependencies": [],
      "created": "2025-11-20",
      "session_created": "2025-11-20-session-001",
      "assigned_to": null,
      "notes": "Self-learning for trading domain"
    }
  ],
  
  "cross_repo_issues": [
    {
      "id": "WS-ISSUE-001",
      "title": "Code creep: domain-specific logic in core",
      "severity": "HIGH",
      "repos_affected": ["meridian-core"],
      "description": "Trading-specific imports found in core",
      "status": "open",
      "created": "2025-11-20"
    }
  ],
  
  "recent_decisions": [
    {
      "id": "DEC-001",
      "date": "2025-11-20",
      "session": "2025-11-20-session-001",
      "decision": "Consolidate credentials to meridian-suite keyring",
      "repos_affected": ["meridian-core", "meridian-research", "meridian-trading"],
      "rationale": "Single source of truth for credentials",
      "status": "implemented"
    }
  ]
}
```

**Benefits:**
- ✅ Unified view of all work
- ✅ Cross-repo dependencies visible
- ✅ Session continuity maintained
- ✅ Code creep can be tracked

### Recommendation 2: Enhanced Session Handoff Protocol

**Create explicit session start/end protocols.**

#### Session Start Protocol

Every session should start with:

1. **Read SESSION-LOG.json** - See what happened in last session
2. **Read WORKSPACE-TASKS.json** - See active tasks and decisions
3. **Read CROSS-REPO-ISSUES.json** - See known issues
4. **Review ARCHITECTURE-DECISIONS.json** - See recent architecture changes
5. **Check governance docs** - Refresh on ADR-001, AI-GUIDELINES
6. **Update session status** - Mark session start in SESSION-LOG.json

#### Session End Protocol

Every session should end with:

1. **Document decisions made** - Add to ARCHITECTURE-DECISIONS.json
2. **Update task status** - Mark tasks complete/in-progress in WORKSPACE-TASKS.json
3. **Log session activity** - Add to SESSION-LOG.json
4. **Flag issues** - Add to CROSS-REPO-ISSUES.json if problems found
5. **Handoff notes** - Write clear handoff notes for next session

#### SESSION-LOG.json Structure

```json
{
  "version": "1.0",
  "sessions": [
    {
      "session_id": "2025-11-20-session-001",
      "start_time": "2025-11-20T10:00:00Z",
      "end_time": "2025-11-20T12:00:00Z",
      "user": "simonerses",
      "ai_assistant": "claude-code",
      
      "activities": [
        {
          "type": "documentation",
          "description": "Created architecture documents for all repos",
          "files_created": [
            "2025-11-20-MERIDIAN-CORE-ARCHITECTURE.md",
            "2025-11-20-MERIDIAN-RESEARCH-ARCHITECTURE.md",
            "2025-11-20-MERIDIAN-TRADING-ARCHITECTURE.md"
          ],
          "time": "2025-11-20T10:30:00Z"
        },
        {
          "type": "analysis",
          "description": "Assessed credential consolidation",
          "time": "2025-11-20T11:00:00Z"
        }
      ],
      
      "decisions_made": [
        {
          "decision": "Consolidate credentials to meridian-suite",
          "repos_affected": ["meridian-core", "meridian-research", "meridian-trading"],
          "rationale": "Single source of truth"
        }
      ],
      
      "issues_found": [
        {
          "issue": "Multiple TASK-QUEUE.json files cause fragmentation",
          "severity": "MEDIUM",
          "action_required": "Create unified task tracking"
        }
      ],
      
      "handoff_notes": "Architecture docs complete. Next session should focus on implementing unified task tracking."
    }
  ]
}
```

### Recommendation 3: Governance Enforcement Mechanisms

**Make governance docs more effective.**

#### Problem: Docs Exist But Not Followed

**Why docs don't work:**
1. AI agents don't automatically read them
2. No enforcement mechanism
3. User instructions don't emphasize governance
4. Docs are "passive" - only read if explicitly referenced

#### Solution: Active Governance

**1. Mandatory Pre-Task Checklist**

Every AI agent should check this before starting work:

```markdown
## Pre-Task Governance Checklist

Before writing ANY code:

- [ ] Read ADR-001-COMPONENT-PLACEMENT.md
- [ ] Read AI-GUIDELINES.md (relevant sections)
- [ ] Check WORKSPACE-TASKS.json for context
- [ ] Check CROSS-REPO-ISSUES.json for known issues
- [ ] Verify component placement (core vs domain adapter)
- [ ] Check for similar work in other repos
- [ ] Document decision rationale
```

**2. Governance Injection into Prompts**

Create a **GOVERNANCE-CONTEXT.md** file that gets automatically included in AI context:

```markdown
# GOVERNANCE-CONTEXT.md
# Auto-injected into every AI interaction

## CRITICAL RULES

1. **Component Placement (ADR-001)**
   - Core: Generic, domain-agnostic
   - Domain: Trading/Research specific
   - NEVER: Domain code in core

2. **Import Rules**
   - Core: Cannot import domain adapters
   - Domain: Can import core

3. **Session Protocol**
   - Read SESSION-LOG.json first
   - Check WORKSPACE-TASKS.json
   - Document decisions

## CURRENT CONTEXT
- Last session: 2025-11-20-session-001
- Active issues: See CROSS-REPO-ISSUES.json
- Recent decisions: See ARCHITECTURE-DECISIONS.json
```

**3. Code Review Checkpoints**

Add pre-commit hooks or manual checks:

```python
# scripts/governance_check.py

def check_component_placement(file_path):
    """Check if file is in correct repo based on imports."""
    # Check for domain-specific imports in core
    # Check for core imports in domain (OK)
    # Flag violations
    
def check_session_context():
    """Check if session handoff was followed."""
    # Verify SESSION-LOG.json updated
    # Verify WORKSPACE-TASKS.json updated
    # Flag missing context
```

**4. User Communication Template**

Provide a template for better communication:

```markdown
## User Communication Best Practices

### ✅ DO:
- "Please implement X, but first check ADR-001 for placement"
- "Create a plan before coding, following AI-GUIDELINES.md"
- "Document this decision in ARCHITECTURE-DECISIONS.json"
- "Check WORKSPACE-TASKS.json for similar work"

### ❌ DON'T:
- "Just add this feature" (no context)
- "Fix this quickly" (no governance check)
- "Make it work" (no placement verification)

### Better Pattern:
1. **State the goal** - "I need to implement X"
2. **Request governance check** - "Please verify placement per ADR-001"
3. **Request plan** - "Create a plan per AI-GUIDELINES.md"
4. **Request documentation** - "Document decision per protocol"
```

### Recommendation 4: Code Creep Detection and Prevention

**Active monitoring for code creep.**

#### CROSS-REPO-ISSUES.json

```json
{
  "version": "1.0",
  "issues": [
    {
      "id": "ISSUE-001",
      "type": "code_creep",
      "severity": "HIGH",
      "title": "Trading-specific code found in meridian-core",
      "description": "File X imports pandas, which violates ADR-001",
      "repo": "meridian-core",
      "file": "src/meridian_core/learning/orchestration_data.py",
      "detected": "2025-11-20",
      "detected_by": "manual-review",
      "status": "open",
      "action_required": "Move to meridian-trading or make generic",
      "assigned_to": null
    }
  ]
}
```

#### Automated Detection Script

```python
# scripts/detect_code_creep.py

def scan_for_code_creep():
    """Scan repos for violations of ADR-001."""
    
    # Check meridian-core for domain-specific imports
    for file in find_files("meridian-core/src"):
        if has_domain_specific_imports(file):
            report_violation(file, "Domain-specific imports in core")
    
    # Check for reverse dependencies (core importing domain)
    if core_imports_domain():
        report_violation("core", "Core importing from domain adapter")
    
    # Generate CROSS-REPO-ISSUES.json
    update_issues_file(violations)
```

### Recommendation 5: Improve User-AI Communication

**You asked: "Is my lack of experience working with AI causing me to incorrectly communicate?"**

**Answer:** Possibly - but it's fixable. Here's a framework:

#### Current Communication Pattern (Likely)

```
User: "Add this feature"
AI: [Starts coding immediately]
Result: Code in wrong place, violates governance
```

#### Improved Communication Pattern

```
User: "I need to add feature X. Please:
1. Check ADR-001 for correct placement
2. Read related code to avoid duplication
3. Create a plan before coding
4. Document the decision"

AI: [Follows checklist, creates plan, gets approval, then codes]
Result: Code in correct place, follows governance
```

#### Communication Framework

**For every request, use this pattern:**

```
1. **Intent**: "I want to..."
2. **Governance Check**: "Please verify per ADR-001..."
3. **Context Check**: "Check for similar work in..."
4. **Planning**: "Create a plan per AI-GUIDELINES.md..."
5. **Documentation**: "Document decision in..."
6. **Execution**: "Then implement..."
```

**Example:**

```
Bad: "Add a trading strategy"

Better: "I want to add a new trading strategy. Please:
- Check ADR-001 to ensure it goes in meridian-trading (not core)
- Check WORKSPACE-TASKS.json for similar work
- Review existing strategies to match patterns
- Create a plan per AI-GUIDELINES.md before coding
- Document any architectural decisions
- Then implement the strategy"
```

---

## Implementation Plan

### Phase 1: Immediate (This Session)

1. ✅ **Create workspace task tracking files**
   - `WORKSPACE-TASKS.json`
   - `SESSION-LOG.json`
   - `CROSS-REPO-ISSUES.json`
   - `ARCHITECTURE-DECISIONS.json`

2. ✅ **Document this session**
   - Add to SESSION-LOG.json
   - Document decisions in ARCHITECTURE-DECISIONS.json
   - Create handoff notes

3. ✅ **Create GOVERNANCE-CONTEXT.md**
   - Condensed governance rules
   - Auto-inject into AI context

### Phase 2: Next Session

1. **Test session handoff protocol**
   - Start session by reading SESSION-LOG.json
   - Verify context is clear
   - Update as needed

2. **Create governance check script**
   - `scripts/governance_check.py`
   - Scan for code creep
   - Flag violations

3. **Update AI-GUIDELINES.md**
   - Add mandatory checklist
   - Add session protocol
   - Emphasize workspace-level tracking

### Phase 3: Ongoing

1. **Enforce governance checks**
   - Run before every commit
   - Flag violations in CROSS-REPO-ISSUES.json
   - Require resolution before merging

2. **Improve documentation**
   - Add communication templates
   - Add examples of good/bad patterns
   - Create quick reference cards

---

## Summary: Key Changes

### What We'll Add

1. **Workspace-level task tracking**
   - `WORKSPACE-TASKS.json` - Unified task view
   - `SESSION-LOG.json` - Session continuity
   - `CROSS-REPO-ISSUES.json` - Issue tracking
   - `ARCHITECTURE-DECISIONS.json` - Decision log

2. **Enhanced governance enforcement**
   - Mandatory pre-task checklist
   - GOVERNANCE-CONTEXT.md (auto-injected)
   - Code creep detection scripts
   - Session handoff protocols

3. **Better communication patterns**
   - Communication framework
   - User request templates
   - AI response protocols

### Expected Outcomes

- ✅ **No more silos** - Unified task tracking
- ✅ **Less code creep** - Active governance enforcement
- ✅ **Better continuity** - Session handoff protocols
- ✅ **Clearer communication** - Structured patterns
- ✅ **Accountability** - Decision tracking

---

## Next Steps

**Immediate Actions:**

1. **Create workspace tracking files** (this session)
2. **Document this session** in SESSION-LOG.json
3. **Create GOVERNANCE-CONTEXT.md**
4. **Update session_start.sh** to read governance context

**Future Sessions:**

1. **Start every session** with governance context
2. **End every session** with handoff notes
3. **Track all decisions** in ARCHITECTURE-DECISIONS.json
4. **Flag issues** in CROSS-REPO-ISSUES.json

---

**Last Updated:** 2025-11-20  
**Status:** Recommendations Complete - Awaiting Implementation

