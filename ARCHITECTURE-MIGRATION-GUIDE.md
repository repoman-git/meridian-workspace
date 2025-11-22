# Architecture Migration Guide

**Date:** 2025-11-22  
**Status:** Post-Architecture Fix Migration

---

## Overview

This guide helps you migrate code to the new architecture after the ADR-001 compliance fixes.

---

## Key Changes

### 1. Trading Code Moved

**Before:**
```python
from meridian_core.trading.ig_connector import IGConnector
from meridian_core.trading.validation import validate_trading_logic
```

**After:**
```python
from meridian_trading.connectors.ig_connector import IGConnector
from meridian_trading.validation import validate_trading_logic
```

### 2. Validation Functions

Validation functions are now in `meridian_trading.validation`:
- `validate_trading_logic()`
- All trading-specific validation

### 3. Research Integration

Research tasks can now be executed via orchestrator:
```python
from meridian_core.orchestration.research_bridge import ResearchBridge

bridge = ResearchBridge()
result = bridge.execute_research_task({
    'description': 'Research query',
    'metadata': {'skill_name': 'investment-research'}
})
```

---

## Migration Steps

1. **Update Imports**
   - Change `meridian_core.trading.*` → `meridian_trading.*`
   - Update validation function imports

2. **Clear Caches**
   - Remove `__pycache__` directories
   - Regenerate imports

3. **Update API Keys**
   - Add missing keys to keyring or .env
   - Verify all providers work

4. **Test Changes**
   - Run test suites
   - Verify imports work

---

## Common Issues

### Import Errors
**Problem:** `ModuleNotFoundError: No module named 'meridian_core.trading'`

**Solution:** Update import to `meridian_trading`

### API Key Errors
**Problem:** `401 Authentication Error`

**Solution:** Add API keys to keyring or .env file

### Cache Issues
**Problem:** Old imports still work (stale cache)

**Solution:** Remove `__pycache__` directories

---

## Support

For issues, check:
- Architecture decisions: `ADR-001-COMPONENT-PLACEMENT.md`
- Validation report: `2025-11-22-Cursor-PHASE-1-VALIDATION-REPORT.md`
- Cleanup report: `2025-11-22-Cursor-POST-ARCHITECTURE-CLEANUP-REPORT.md`
