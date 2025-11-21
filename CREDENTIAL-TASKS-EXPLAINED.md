# Why You Need to Run These Tasks - Explained

**Date:** 2025-11-20  
**Purpose:** Clarify which tasks are REQUIRED vs RECOMMENDED

---

## TL;DR

1. **REQUIRED:** Install meridian-core in meridian-trading (code won't work without it)
2. **RECOMMENDED:** Run migration script (credentials will work via fallback, but consolidation is cleaner)

---

## Detailed Explanation

### 1. ⚠️ REQUIRED: Install meridian-core in meridian-trading

**What I changed:**
- Updated `meridian-trading/src/meridian_trading/config/credentials.py` to import from `meridian_core.utils.credential_store`
- Removed dependency on local `CredentialManager` class

**Why you need to install it:**
- Without `meridian-core` installed, the import fails
- The code has a try/except block that logs a warning, but then credential lookups return `None`
- Your credentials won't be accessible unless you use environment variables

**What happens if you skip this:**
```python
# In meridian-trading/config/credentials.py
from meridian_core.utils import credential_store  # ❌ ImportError!

# Credentials will be None
GROK_API_KEY = None  # Won't work!
```

**How to fix:**
```bash
cd meridian-trading
pip install -e ../meridian-core  # For development
```

---

### 2. 📋 RECOMMENDED: Run migration script

**Why it's recommended (not required):**

The shared `credential_store` has **backward compatibility** built in. It checks these keyring services in order:

1. `meridian-suite` (preferred - new unified service)
2. `meridian-research` (legacy fallback)
3. `meridian-core` (legacy fallback)
4. `meridian-trading-system` (legacy fallback)

So if your credentials are already in one of those services, they'll still work!

**When migration is needed:**
- If you have credentials in `meridian-trading-system` with **lowercase names** (e.g., `grok_api_key` instead of `GROK_API_KEY`)
  - The old system used lowercase service names
  - The new system uses canonical uppercase names (`GROK_API_KEY`)
  - Migration converts them to the canonical format

- If you want everything consolidated in one place (`meridian-suite`)
  - Easier to manage
  - No confusion about where credentials are stored
  - Future-proof (legacy services may be removed eventually)

**What happens if you skip this:**
- Credentials in `meridian-research` or `meridian-core` services will still work ✅
- Credentials in `meridian-trading-system` might not work if they use lowercase names ❌
- Multiple credential locations = harder to manage

**How to run:**
```bash
cd meridian-core
python scripts/migrate_existing_credentials.py
```

---

## Summary Table

| Task | Required? | Why |
|------|-----------|-----|
| Install meridian-core | ✅ **YES** | Code imports from it - won't work without it |
| Run migration script | ⚠️ **RECOMMENDED** | Credentials work via fallback, but migration consolidates everything |

---

## Quick Decision Tree

```
Do you have meridian-core installed in meridian-trading?
├─ YES → Skip to migration check
└─ NO → Install it first (REQUIRED)
    └─ pip install -e ../meridian-core

Are your credentials working now?
├─ YES → Migration is optional (but recommended for consolidation)
└─ NO → Run migration script (credentials might be in wrong format/location)
```

---

## Testing Checklist

After completing tasks, verify:

```bash
# 1. Test meridian-core is importable
cd meridian-trading
python -c "from meridian_core.utils import credential_store; print('✅ Import works')"

# 2. Test credential access
python -c "from meridian_trading.config.credentials import GROK_API_KEY; print('✅ Credential accessible' if GROK_API_KEY else '❌ Credential missing')"

# 3. Verify keyring service
python -c "from meridian_core.utils import credential_store; print('Service:', credential_store.PRIMARY_SERVICE)"
```

---

**Bottom line:** Install meridian-core (required), migrate credentials (recommended for cleanup).

