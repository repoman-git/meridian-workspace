# Meridian-Core Violations - Quick Reference

## 5 Critical Violations Found

### VIOLATION #1: IG Markets Connector (CRITICAL)
```
File: src/meridian_core/connectors/ig_connector.py
Type: 100% Trading-Specific Code
Severity: CRITICAL - MUST MOVE

Classes: IGConnector
Methods: open_position(), get_positions(), close_position()
Impact: Entire file is trading-broker integration - no generic use case
Fix: Move to meridian-trading/src/connectors/
Effort: 1-2 hours
Status: BLOCKER - prevents core from being domain-agnostic
```

---

### VIOLATION #2: CredentialManager Imports (CRITICAL)
```
Files: 4 connectors importing from meridian_trading
- anthropic_connector.py:35
- openai_connector.py:35
- gemini_connector.py:30
- grok_connector.py:35

Pattern:
try:
    from meridian_trading.security.credential_manager import CredentialManager
except ImportError:
    pass

Issue: Core should NEVER import from trading (even optionally)
Creates hidden dependency on meridian_trading existing
Impact: Core cannot be standalone/published to PyPI
Fix: Move CredentialManager to meridian-core as generic abstraction
Effort: 3-4 hours
Status: BLOCKER - violates core principle
```

---

### VIOLATION #3: Trading Validation Methods (HIGH)
```
Files: 3 AI connectors with domain-specific methods
- openai_connector.py:244-290 - validate_trade_idea()
- gemini_connector.py:~200-300 - validate_risk_rules()
- grok_connector.py:~200-250 - validate_trade_idea()

Examples:
def validate_trade_idea(self, market, direction, entry, stop, target):
    # Validates trading parameters - TRADING-SPECIFIC
    prompt = f"Evaluate this trade idea..."

def validate_risk_rules(self):
    # Uses "Larry Williams 2% rule", "6% portfolio max"
    # TRADING-SPECIFIC

Issue: Generic connectors should only call LLMs
Trading logic should be in trading repo
Customer support bot cannot reuse these
Fix: Extract methods to trading repo, keep generic callable interface
Effort: 2-3 hours
Status: HIGH - prevents code reuse for other domains
```

---

### VIOLATION #4: LM Studio Master Orchestrator (CRITICAL)
```
File: src/meridian_core/orchestrator/lmstudio_master.py
Type: Generic Pattern with Trading Context
Severity: CRITICAL - Must Abstract

Evidence of Trading Context:
- Line 13-20: "decides which expert AIs...to consult for trading decisions"
- Line 103: "You are a master trading orchestrator..."
- Line 256+: Example output shows LONG|SHORT|HOLD|NO_TRADE

The Problem:
Pattern (master LLM coordinates expert AIs) = GENERIC
Implementation (trading decisions, LONG/SHORT) = SPECIFIC
Example prompts/outputs = TRADING ONLY

Fix: 
1. Create generic LMStudioMasterOrchestrator in core
2. Keep expert selection logic in core
3. Move trading prompts/context to meridian-trading
4. Create TradingLMStudioOrchestrator(LMStudioMasterOrchestrator)

Effort: 4-5 hours
Status: CRITICAL - pattern locked into trading use case
```

---

### VIOLATION #5: Heavy ML Dependencies (MEDIUM)
```
File: src/meridian_core/orchestrator/convergence.py
Issue: Uses numpy + sklearn for simple similarity calculation

Imports:
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

Problems:
- numpy used only for np.mean() - can use statistics.mean()
- sklearn for cosine_similarity - simple linear algebra
- sentence_transformers is reasonable (semantic similarity)
- But numpy + sklearn add 500MB+ of dependencies for optional feature

Fix: 
Option 1: Replace numpy/sklearn with Python stdlib
  - Replace np.mean() → statistics.mean()
  - Implement cosine_similarity inline (3 lines of math)
  - Keep sentence_transformers (reasonable)
  
Option 2: Make optional/pluggable
  - Fallback implementation without ML
  - Use ML if available

Effort: 1-2 hours
Status: MEDIUM - reduces dependency footprint
```

---

## Violation Summary Table

| # | File | Issue | Severity | Fix | Effort | Impact |
|---|------|-------|----------|-----|--------|--------|
| 1 | `ig_connector.py` | 100% trading-specific | CRITICAL | Move to trading | 1-2h | Blocks PyPI |
| 2 | 4 connectors | Imports from trading | CRITICAL | Abstract to core | 3-4h | Blocks reuse |
| 3 | 3 connectors | Trade validation methods | HIGH | Extract to trading | 2-3h | Blocks reuse |
| 4 | `lmstudio_master.py` | Trading context embedded | CRITICAL | Abstract pattern | 4-5h | Blocks reuse |
| 5 | `convergence.py` | Heavy ML deps | MEDIUM | Use stdlib | 1-2h | Reduces deps |

**Total Effort to Fix All:** 11-16 hours (1-2 days)
**Result:** 72% → 95%+ ADR-001 compliance

---

## Compliance Before/After

### Current State (72% Compliant)
```
Rules Met: 8/11
- ✅ Generic interfaces (Learning Engine)
- ✅ Generic workflows (Orchestration)
- ✅ Reusable patterns (Voting, Allocation)
- ✅ Thread-safe database
- ✅ No pandas/numpy (except convergence)

Rules Failed:
- ❌ No domain imports (imports from meridian_trading)
- ❌ Works for ANY domain (IG connector + trade methods)
- ❌ Can publish to PyPI (trading code prevents this)
- ⚠️ ML dependencies (optional but heavy)
```

### After Fixes (95%+ Compliant)
```
All 11/11 rules met:
- ✅ No domain imports (CredentialManager moved to core)
- ✅ Works for ANY domain (IG removed, methods extracted)
- ✅ Generic interfaces everywhere
- ✅ Generic workflows everywhere
- ✅ Reusable patterns everywhere
- ✅ Thread-safe database
- ✅ Minimal dependencies
- ✅ Can publish to PyPI as open-source
```

---

## Customer Support Test Results

**Current:** 81% Pass (11/13 components work)
**Blockers:** IG Connector + Trade Validation Methods
**After Fix:** 100% Pass - can build support bot

---

## Implementation Roadmap

### Week 1 (P0 - Critical Path)
1. [ ] Move IG connector to meridian-trading/
2. [ ] Create CredentialManager abstraction in meridian-core/
3. [ ] Update all import statements

**Effort:** 3-4 hours  
**Result:** Removes obviously trading code

### Week 2-3 (P1 - Architectural Quality)
1. [ ] Extract trade validation methods from connectors
2. [ ] Abstract LM Studio master orchestrator pattern
3. [ ] Fix trading scope hardcoding in task_type_executor

**Effort:** 10-12 hours  
**Result:** Makes core truly generic

### Month 2 (P2-P3 - Long Term)
1. [ ] Simplify convergence detector (remove numpy/sklearn)
2. [ ] Refactor orchestration module (51 files → sub-packages)
3. [ ] Create plugin architecture for domains to extend

**Effort:** 20-30 hours  
**Result:** Enables extensibility

---

## Key Files to Address

### MUST FIX (Critical Path)
- `src/meridian_core/connectors/ig_connector.py` - MOVE ENTIRE FILE
- `src/meridian_core/connectors/anthropic_connector.py` - FIX IMPORT
- `src/meridian_core/connectors/openai_connector.py` - FIX IMPORT
- `src/meridian_core/connectors/gemini_connector.py` - FIX IMPORT
- `src/meridian_core/connectors/grok_connector.py` - FIX IMPORT
- `src/meridian_core/orchestrator/lmstudio_master.py` - REFACTOR

### SHOULD FIX (Quality)
- `src/meridian_core/orchestration/task_type_executor.py` - REMOVE TRADING SCOPES
- `src/meridian_core/orchestrator/convergence.py` - SIMPLIFY DEPS

---

## Architecture Principles Violated

**ADR-001 Principle:** Core should be "domain-agnostic" - works for ANY domain

**Test:** "Could someone build a customer support bot using this code?"
- Current Answer: ❌ NO (IG connector prevents it)
- After Fix: ✅ YES

**Impact of Violation:**
- Cannot publish to PyPI as generic framework
- Cannot be reused for research, healthcare, support, etc.
- Violates stated architectural principle
- Missed opportunity for open-source adoption

---

## References

- **ADR-001:** `/Users/simonerses/data-projects/meridian-core/ADR-001-COMPONENT-PLACEMENT.md`
- **Full Report:** `MERIDIAN-CORE-ARCHITECTURE-REVIEW.txt` (1047 lines)
- **Executive Summary:** `MERIDIAN-CORE-ARCHITECTURE-EXECUTIVE-SUMMARY.md`

