# The Bastard Integration with WMS

**Date:** November 20, 2025  
**Purpose:** Documentation of The Bastard evaluation system and its integration with the Workspace Management System (WMS)

---

## Executive Summary

**The Bastard** is an adversarial evaluation skill designed to catch over-engineering, validate deployment claims, and enforce scale appropriateness. It's a core component of the WMS workflow engine, providing validation at two critical points:

1. **Plan Evaluation** - Before starting work on a task
2. **Completion Evaluation** - Before marking a task as complete

The Bastard v2.0 adds **Scale Appropriateness** validation, specifically designed to catch over-engineering and ensure solutions match actual user scale.

---

## Files Imported

### 1. Skill Definition
- **Location:** `workspace/skills/evaluation-bastard-skill.yaml`
- **Purpose:** Complete YAML specification for The Bastard skill
- **Use:** Loaded by WMS Bastard Integration component

### 2. Documentation
- **Location:** `workspace/architecture/bastard/`
- **Files:**
  - `BASTARD-V2-SUMMARY.md` - Summary of v2.0 upgrade (scale appropriateness)
  - `BASTARD-EXAMPLE-OVER-ENGINEERING.md` - Example verdict catching over-engineering

---

## Key Features of The Bastard v2.0

### New in v2.0: Scale Appropriateness Validation

**The Problem:**
> "The Bastard needs to challenge: WTF is this for? Big or small? Why are you showing me big when we need small and scalable?"

**The Solution:**
The Bastard now starts EVERY evaluation with a **Scale Reality Check**:

```
STEP 0: SCALE REALITY CHECK

WHO'S USING THIS TODAY?
└─ Not "someday" or "eventually" - RIGHT NOW

WHAT'S THE ACTUAL USER COUNT?
└─ 1 person? 10? 100? 1000?

WHY ARE YOU BUILDING FOR 1000 USERS WHEN YOU HAVE 1?
└─ Justify the complexity or simplify the solution
```

### Evaluation Categories

The Bastard evaluates tasks across six categories:

1. **Scale Appropriateness** ⭐ NEW in v2.0
   - Detects over-engineering
   - Validates solution matches actual user count
   - Recommends appropriate tier (1, 2, or 3)

2. **Deployment Maturity**
   - Can it install on a fresh machine?
   - What breaks if credentials are missing?
   - Is it portable?

3. **Portability**
   - OS-specific dependencies?
   - Hardcoded paths?
   - Can it run in a container?

4. **State Management**
   - Where is ALL state stored?
   - Can state be exported/imported?
   - What gets lost during migration?

5. **Credential Management**
   - Multiple credential sources?
   - Clear error messages?
   - Works in degraded mode?

6. **Documentation**
   - Does README match reality?
   - Are claims substantiated?
   - Examples actually work?

### New Grade: OVER-ENGINEERED

Issued when:
- Recommending enterprise tools for personal use
- Kubernetes for single laptop deployment
- HashiCorp Vault for 1 user
- No Tier 1 (simple) solution provided

**Example Verdict:**
```
This is over-engineered garbage.

You're building a nuclear reactor to boil water.

ACTUAL SCALE: 1 user
DESIGNED FOR: 1000 users

COMPLEXITY GAP: 1000x over-engineered

Recommendation: Start with Tier 1 solution.
Scale when you ACTUALLY NEED IT.
```

---

## Integration with WMS

### WMS Workflow Engine Integration

The Bastard is integrated into the WMS workflow at two points:

#### 1. Task Creation (Plan Evaluation)

```python
# workspace/wms/workflow_engine.py

def create_task(...):
    # ... governance validation ...
    
    # Evaluate plan with The Bastard
    if proposed_solution:
        report = self.bastard.evaluate_plan(
            task, actual_users, proposed_solution
        )
        
        if report.overall_grade in ['F', 'D', 'OVER_ENGINEERED']:
            task.status = TaskStatus.BLOCKED
            print(f"❌ The Bastard REJECTED the plan")
        else:
            task.status = TaskStatus.APPROVED
            print(f"✅ The Bastard APPROVED the plan")
```

**Evaluation Questions:**
- Who's using this? (actual user count TODAY)
- Is solution appropriately sized?
- Are there Tier 1/2/3 options?
- Is this over-engineered?

#### 2. Task Completion (Completion Evaluation)

```python
def complete_task(...):
    # ... task must be IN_PROGRESS ...
    
    # Final Bastard evaluation
    report = self.bastard.evaluate_completion(task)
    
    if report.overall_grade in ['F', 'D']:
        task.status = TaskStatus.BLOCKED
        print(f"❌ The Bastard REJECTED completion")
        return False
    else:
        task.status = TaskStatus.COMPLETED
        print(f"✅ The Bastard APPROVED completion")
        return True
```

**Evaluation Questions:**
- Was it implemented in correct repo?
- Does it match architecture decisions?
- Is it portable/deployable?
- Any over-engineering detected?

### Database Integration

The Bastard reports are stored in the workspace database:

```python
# workspace/db/models.py

class BastardReport(Base):
    """Reports from The Bastard evaluations."""
    
    task_id = Column(Integer, ForeignKey("tasks.id"))
    evaluation_type = Column(String(50))  # plan, completion
    
    # Grades
    overall_grade = Column(String(1))  # F, D, C, B, A, OVER_ENGINEERED
    scale_appropriateness = Column(String(1))
    deployment_maturity = Column(String(1))
    portability = Column(String(1))
    state_management = Column(String(1))
    credential_management = Column(String(1))
    
    # Scale assessment
    actual_users = Column(Integer)
    designed_for_users = Column(Integer)
    over_engineering_score = Column(Integer)  # 1-10
    
    # Recommendations
    tier_recommendation = Column(Integer)  # 1, 2, or 3
    critical_blockers = Column(JSON)
    required_fixes = Column(JSON)
    
    full_report = Column(Text)  # Complete verdict
```

---

## Example: Catching Over-Engineering

### Scenario
User creates task: "Add credential management"

**Proposed Solution:** "Deploy HashiCorp Vault cluster with Consul"

**Actual Users:** 1 (your wife)

### The Bastard's Verdict

```
🔴 SCALE REALITY CHECK

WHO'S USING THIS?
└─ Your wife (1 person, non-technical)

WHAT'S THE COMPLEXITY?
└─ Proposed: HashiCorp Vault, Kubernetes
└─ Actual need: pip install, .env file

OVER-ENGINEERING DETECTED: 1000x

VERDICT: Grade F (Scale Appropriateness)

You're building a spaceship to go to the grocery store.

Recommendation:
- Tier 1: Use .env file, SQLite, pip install
- Tier 2: Upgrade when you hit 5-10 users
- Tier 3: Vault/k8s when you hit 50+ users

Current grade: F
Fix scale mismatch to proceed.
```

**Result:** Task is BLOCKED until user provides Tier 1 solution.

---

## Scale Tiers

The Bastard recommends solutions based on three tiers:

### Tier 1: Personal Use (1-5 users)
- **Credentials:** .env file
- **Database:** SQLite
- **Deployment:** Local (pip install)
- **Setup time:** 2 minutes
- **Cost:** $0/month

### Tier 2: Team Use (5-20 users)
- **Credentials:** Config file (git-crypt encrypted)
- **Database:** PostgreSQL (single instance)
- **Deployment:** Docker Compose
- **Migration effort:** 4 hours
- **Cost:** <$50/month

### Tier 3: Enterprise (50+ users)
- **Credentials:** AWS Secrets Manager / Vault
- **Database:** PostgreSQL RDS with replicas
- **Deployment:** Kubernetes
- **Migration effort:** 1-2 weeks
- **Cost:** $500+/month

**Upgrade Triggers:**
- Tier 1 → Tier 2: 5-10 users need shared access
- Tier 2 → Tier 3: 50+ users OR compliance requirements

---

## Integration Points

### 1. WMS CLI Commands

```bash
# View Bastard report for a task
wms bastard report WS-TASK-001

# Output shows:
# - Overall grade
# - Category grades
# - Scale assessment
# - Tier recommendations
# - Critical blockers
# - Required fixes
```

### 2. Task Workflow

```
1. CREATE TASK
   ├─ wms task create
   ├─ Governance validates placement
   ├─ Governance validates scale
   ├─ The Bastard evaluates plan ← NEW
   └─ Status: APPROVED or BLOCKED

2. START TASK
   ├─ wms task start WS-TASK-001
   └─ Status: IN_PROGRESS

3. DO THE WORK
   └─ Implement in assigned repo

4. COMPLETE TASK
   ├─ wms task complete WS-TASK-001
   ├─ The Bastard evaluates completion ← NEW
   └─ Status: COMPLETED or BLOCKED
```

### 3. Meridian Core Orchestration

The Bastard is called via Meridian Core's AI Orchestrator:

```python
# workspace/wms/bastard_integration.py

def _call_bastard(self, prompt: str) -> str:
    """Call The Bastard via Meridian orchestration."""
    from meridian_core import AIOrchestrator
    
    orchestrator = AIOrchestrator()
    verdict = orchestrator.execute_with_skill(
        ai_provider="claude",
        skill_name="evaluation-bastard",
        task=prompt,
        require_brutal_honesty=True
    )
    return verdict
```

---

## Benefits

### For Development
1. ✅ **Catch over-engineering early** - Before writing code
2. ✅ **Match solutions to actual scale** - Not imaginary scale
3. ✅ **Ship faster** - Start simple, scale later
4. ✅ **Enforce architecture decisions** - Through validation

### For Users
1. ✅ **Simple installation** - Tier 1 solutions work immediately
2. ✅ **No ops knowledge required** - For personal use
3. ✅ **Clear upgrade path** - When scale increases
4. ✅ **Portable solutions** - Survive migration

### For Future Scale
1. ✅ **Clear upgrade triggers** - Know when to scale
2. ✅ **Estimated migration effort** - Plan accordingly
3. ✅ **No rewrites** - Abstraction layers preserve code
4. ✅ **Scale tiers documented** - Future-proof architecture

---

## Philosophy: Start Small, Scale Smart

### The Principle

```
✅ DO:
- Design with scale HOOKS (abstractions)
- Document scale TIERS (1, 2, 3)
- Implement for TODAY (actual users)
- Provide upgrade PATH (when needed)

❌ DON'T:
- Build for 1000 users on day 1
- Add complexity "just in case"
- Recommend Vault for personal use
- Skip the simple solution
```

### The Questions

Every architecture must answer:

1. **What's Tier 1?** (Simple, for TODAY)
2. **When to upgrade to Tier 2?** (Trigger defined)
3. **When to upgrade to Tier 3?** (Trigger defined)
4. **What's the migration effort?** (Hours estimated)
5. **Does code need changes?** (Hopefully no)

---

## Next Steps

1. ✅ **Files imported** - The Bastard spec and examples in workspace
2. ⏳ **Extend database schema** - Add `BastardReport` model
3. ⏳ **Build Bastard Integration** - `workspace/wms/bastard_integration.py`
4. ⏳ **Integrate with Workflow Engine** - Plan and completion evaluation
5. ⏳ **Test integration** - Mock Bastard initially, real calls later
6. ⏳ **CLI commands** - `wms bastard report` command

---

## Related Files

- **WMS Spec:** `workspace/WMS-IMPLEMENTATION-SPEC-FOR-CURSOR.md`
- **WMS Integration Analysis:** `2025-11-20-WMS-SPEC-INTEGRATION-ANALYSIS.md`
- **Bastard Skill:** `workspace/skills/evaluation-bastard-skill.yaml`
- **Bastard v2.0 Summary:** `workspace/architecture/bastard/BASTARD-V2-SUMMARY.md`
- **Example Verdict:** `workspace/architecture/bastard/BASTARD-EXAMPLE-OVER-ENGINEERING.md`

---

## Summary

The Bastard v2.0 provides brutal, honest evaluation of tasks before and after implementation. Its new scale appropriateness validation catches over-engineering and ensures solutions match actual user scale.

**Integration Status:** Specifications imported, ready for implementation  
**Priority:** High (core WMS component)  
**Dependencies:** WMS database schema, Meridian Core orchestration

---

**Status:** Documentation Complete - Ready for Implementation  
**Created:** 2025-11-20  
**Related:** WS-TASK-005

