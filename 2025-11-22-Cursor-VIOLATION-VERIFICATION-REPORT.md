# Violation Verification Report

**Date:** 2025-11-21 23:59:51  
**Session:** 20251121_235951  
**Repository:** meridian-core  
**Goal:** Verify ADR-001 violations before fixing

---

## Summary

- **Violations Found:** 4/5
- **False Positives:** 1/5
- **Total Fix Time Estimate:** 10-14 hours
- **Severity Breakdown:**
  - CRITICAL: 1
  - HIGH: 3
  - MEDIUM: 0
  - LOW: 0

---

## Verified Violations

### 1. IG Connector in Core ✓ EXISTS

**Severity:** CRITICAL  
**Status:** CONFIRMED  
**Location:** `src/meridian_core/connectors/ig_connector.py`

**Evidence:**
- Full IG Markets API connector implementation
- Contains trading-specific methods:
  - `place_order()`
  - `get_positions()`
  - `close_position()`
  - `get_market_data()`
- This is clearly trading-domain specific and violates ADR-001

**Impact:**
- Core framework contains trading-specific code
- Should be in meridian-trading repository
- Blocks proper separation of concerns

**Fix Time:** 4-6 hours  
**Fix Priority:** 1 (Highest)

**Recommended Action:**
- Move `ig_connector.py` to `meridian-trading/src/meridian_trading/connectors/`
- Update all imports across codebase
- Move related tests
- Verify no core code depends on it

---

### 2. CredentialManager Trading Imports ✓ EXISTS

**Severity:** HIGH  
**Status:** CONFIRMED  
**Locations:**
- `src/meridian_core/connectors/gemini_connector.py` (line 30)
- `src/meridian_core/connectors/grok_connector.py` (line 30)
- `src/meridian_core/connectors/openai_connector.py` (line 35)
- `src/meridian_core/connectors/anthropic_connector.py` (line 29)

**Evidence:**
```python
from meridian_trading.security.credential_manager import CredentialManager  # type: ignore
```

**Impact:**
- Core framework depends on trading repository
- Creates circular dependency risk
- Violates ADR-001 component placement rules

**Fix Time:** 2-3 hours  
**Fix Priority:** 2

**Recommended Action:**
- Option A: Move CredentialManager to meridian-core (if generic enough)
- Option B: Create generic credential helper in core, keep trading-specific in trading
- Option C: Use dependency injection to remove direct import
- Update all 4 connector files

---

### 3. Trading-Specific Validation Methods ✓ EXISTS

**Severity:** HIGH  
**Status:** CONFIRMED  
**Locations:**
- `src/meridian_core/connectors/gemini_connector.py` - `validate_trading_logic()` (line 377)
- `src/meridian_core/connectors/grok_connector.py` - `validate_trade_idea()` (line 307)
- `src/meridian_core/connectors/openai_connector.py` - `validate_trade_idea()` (line 244)

**Evidence:**
- `validate_trading_logic()`: Validates trading strategy code, position sizing, risk management
- `validate_trade_idea()`: Validates trade setups, risk/reward, stop losses, targets
- Both methods are explicitly trading-domain specific

**Impact:**
- Core connectors contain trading-domain logic
- Should be in meridian-trading or removed from core
- Methods reference trading concepts (positions, orders, risk management)

**Fix Time:** 2-3 hours  
**Fix Priority:** 3

**Recommended Action:**
- Move validation methods to meridian-trading
- Create generic validation if needed
- Update callers to use trading-specific validators

---

### 4. LM Studio Trading Context ✗ NOT EXISTS (False Positive)

**Severity:** N/A  
**Status:** FALSE POSITIVE  
**Location:** `src/meridian_core/connectors/mcp/lmstudio_server.py`

**Evidence:**
- File contains no trading-specific code
- Generic MCP server for LM Studio integration
- No references to trading, positions, orders, or trading concepts
- Properly generic and domain-agnostic

**Impact:** None - No violation  
**Fix Time:** 0 hours  
**Fix Priority:** N/A

**Recommended Action:** None - File is compliant

---

### 5. Numpy/Sklearn in Convergence ✓ EXISTS

**Severity:** HIGH  
**Status:** CONFIRMED  
**Location:** `src/meridian_core/orchestrator/convergence.py`

**Evidence:**
```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
```

**Impact:**
- Heavy ML dependencies in core framework
- May not be acceptable if core should be lightweight
- However, convergence detection is generic (not trading-specific)
- This might be acceptable if convergence is a core framework feature

**Fix Time:** 1-2 hours (if needed)  
**Fix Priority:** 4 (Lower - may be acceptable)

**Recommended Action:**
- **Decision needed:** Is convergence detection a core framework feature?
- If yes: Keep as-is (acceptable dependency)
- If no: Move to domain adapter or make optional dependency
- Consider making sentence_transformers optional with fallback

---

## Recommended Fix Order

1. **Phase 1: IG Connector Migration** (4-6h) - CRITICAL
   - Highest impact violation
   - Clear trading-domain code
   - Straightforward migration

2. **Phase 2: CredentialManager Fix** (2-3h) - HIGH
   - Affects 4 files
   - Need to decide on solution approach
   - Important for dependency management

3. **Phase 3: Validation Methods** (2-3h) - HIGH
   - Affects 3 connector files
   - Clear trading-domain logic
   - Straightforward extraction

4. **Phase 4: Convergence Dependencies** (1-2h) - HIGH (conditional)
   - Requires architectural decision
   - May be acceptable as-is
   - Lower priority if acceptable

---

## Files Requiring Changes

### Core Files to Modify:
- `src/meridian_core/connectors/ig_connector.py` (DELETE - move to trading)
- `src/meridian_core/connectors/gemini_connector.py` (UPDATE imports, remove validation)
- `src/meridian_core/connectors/grok_connector.py` (UPDATE imports, remove validation)
- `src/meridian_core/connectors/openai_connector.py` (UPDATE imports, remove validation)
- `src/meridian_core/connectors/anthropic_connector.py` (UPDATE imports)
- `src/meridian_core/orchestrator/convergence.py` (REVIEW - may be acceptable)

### Trading Files to Create/Update:
- `meridian-trading/src/meridian_trading/connectors/ig_connector.py` (NEW)
- `meridian-trading/src/meridian_trading/validation/` (NEW - validation methods)
- Update imports in trading repo

### Test Files:
- Move IG connector tests to trading
- Update connector tests in core
- Verify all tests pass

---

## Validation Checklist

After fixes, verify:

- [ ] No `meridian_trading` imports in `meridian-core/src/meridian_core/`
- [ ] No IG connector files in `meridian-core/src/meridian_core/connectors/`
- [ ] No trading validation methods in core connectors
- [ ] All tests pass in both repos
- [ ] No circular dependencies
- [ ] ADR-001 compliance >= 95%

---

## Next Steps

1. **Start with Phase 0 verification** ✅ (COMPLETE)
2. **Proceed to Phase 1** - IG Connector Migration
3. **Continue through phases** in priority order
4. **Run Phase 5** - Final validation after all fixes

---

**Report Generated:** 2025-11-21 23:59:51  
**Ready to proceed with fixes**

