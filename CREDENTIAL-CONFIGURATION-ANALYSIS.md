# Credential Configuration Analysis

**Date:** 2025-11-20  
**Purpose:** Comprehensive analysis of all credential/API key management systems across Meridian repos

---

## Executive Summary

After migrating to a new laptop and following a refactoring, there are **multiple conflicting credential management systems** scattered across 4 active repos. This document identifies all systems, their conflicts, and provides a consolidation plan.

---

## Current State: Multiple Conflicting Systems

### 1. **meridian** (ARCHIVED - but still used)
**Location:** `meridian/src/config/credentials.py` + `meridian/src/security/credential_manager.py`

**Keyring Service:** `meridian-trading-system`

**Approach:**
- Full `CredentialManager` class with Fernet encryption
- Master key stored in `~/.meridian/master.key`
- Credentials encrypted in keyring
- Fallback to `.env` if `ALLOW_ENV_FALLBACK=1`

**Status:** ❌ **CONFLICTING** - Uses different keyring service than others

---

### 2. **meridian-core** (Foundation Layer)
**Location:** `meridian-core/src/meridian_core/utils/credential_store.py` + `meridian-core/src/meridian_core/connectors/credential_helper.py`

**Keyring Services:** 
- **Preferred:** `meridian-suite` (from env: `MERIDIAN_KEYRING_SERVICE`)
- **Legacy fallbacks:** `meridian-core`, `meridian-research`

**Approach:**
- Simple keyring wrapper (no encryption layer)
- Uses Python `keyring` library directly
- Service mapping: `service_name` → `ANTHROPIC_API_KEY` etc.
- **No .env fallback by default** (disabled unless `ALLOW_ENV_FALLBACK=1`)

**Status:** ✅ **DESIGNED AS SHARED** - But migration script uses wrong service name

**Migration Script:** `meridian-core/scripts/migrate_credentials.py`
- **Problem:** Uses `meridian-core` service instead of `meridian-suite`
- **Impact:** Creates separate keyring entries, not accessible to other repos

---

### 3. **meridian-trading** (Trading Domain)
**Location:** `meridian-trading/src/meridian_trading/config/credentials.py` + `meridian-trading/src/meridian_trading/security/credential_manager.py`

**Keyring Service:** `meridian-trading-system`

**Approach:**
- Full `CredentialManager` class (same as archived `meridian`)
- Fernet encryption + master key
- Trading-specific credentials (IG_USERNAME, IG_PASSWORD, IG_API_KEY)
- Falls back to `.env` if `ALLOW_ENV_FALLBACK=1`

**Status:** ❌ **CONFLICTING** - Uses different keyring service, duplicates CredentialManager

---

### 4. **meridian-research** (Research Domain)
**Location:** `meridian-research/src/meridian_research/utils/credential_store.py`

**Keyring Services:**
- **Preferred:** Shared store from `meridian-core` (`meridian-suite`)
- **Fallback:** Legacy `meridian-research` service
- **Additional:** Encrypted file storage (`.meridian/credentials.enc`)

**Approach:**
- **Tries to import** `meridian_core.utils.credential_store` (shared)
- Falls back to local secret_manager if core not installed
- Encrypted file for cross-machine sync (password-protected)
- Priority: Encrypted file → keyring → env vars

**Status:** ⚠️ **MIXED** - Attempts to use shared store but has complex fallback chain

---

## Key Conflicts Identified

### Conflict #1: Multiple Keyring Services
| Repo | Service Name | Status |
|------|-------------|--------|
| `meridian` (archived) | `meridian-trading-system` | ❌ Legacy |
| `meridian-core` (migration script) | `meridian-core` | ❌ Wrong service |
| `meridian-core` (code) | `meridian-suite` | ✅ Preferred |
| `meridian-trading` | `meridian-trading-system` | ❌ Conflicts with core |
| `meridian-research` | `meridian-suite` (via core) | ✅ Correct |

**Problem:** Credentials stored in one service are invisible to repos using another service.

---

### Conflict #2: Duplicate CredentialManager Classes
- `meridian/src/security/credential_manager.py` (archived)
- `meridian-trading/src/meridian_trading/security/credential_manager.py` (active)

**Problem:** Code duplication, maintenance burden, different encryption keys.

---

### Conflict #3: Inconsistent Fallback Behavior
- **meridian-core:** No `.env` fallback by default (strict)
- **meridian-trading:** `.env` fallback if `ALLOW_ENV_FALLBACK=1`
- **meridian-research:** Encrypted file + keyring + env (complex)

**Problem:** Different behavior across repos, confusing for developers.

---

### Conflict #4: Migration Scripts Use Wrong Service
- `meridian-core/scripts/migrate_credentials.py` stores in `meridian-core` service
- But code expects `meridian-suite` service
- Result: Migration doesn't work correctly

---

## Working vs Broken Configurations

### ✅ **Working Configurations**

1. **meridian-core credential_store.py**
   - ✅ Clean API
   - ✅ Shared keyring service (`meridian-suite`)
   - ✅ Simple, maintainable
   - ⚠️ Migration script uses wrong service

2. **meridian-research credential_store.py**
   - ✅ Attempts to use shared store
   - ✅ Has encrypted file fallback for cross-machine sync
   - ⚠️ Complex fallback chain

### ❌ **Broken Configurations**

1. **meridian-core migrate_credentials.py**
   - ❌ Uses `meridian-core` service instead of `meridian-suite`
   - ❌ Migrated credentials won't be found by code

2. **meridian-trading CredentialManager**
   - ❌ Uses `meridian-trading-system` service (isolated)
   - ❌ Can't share credentials with core/research
   - ❌ Duplicates code from archived meridian

3. **meridian (archived) CredentialManager**
   - ❌ Repo is archived but code still referenced
   - ❌ Uses old service name

---

## Consolidation Plan

### Phase 1: Standardize on Shared Keyring Service

**Goal:** All repos use `meridian-suite` as the single keyring service.

**Actions:**
1. ✅ **meridian-core** already uses `meridian-suite` (correct)
2. ❌ Fix `meridian-core/scripts/migrate_credentials.py` to use `meridian-suite`
3. ❌ Update `meridian-trading` to use shared `meridian-core.utils.credential_store` instead of local CredentialManager
4. ✅ **meridian-research** already uses shared store (correct, but complex)

---

### Phase 2: Remove Duplicate CredentialManager

**Goal:** Single credential management system across all repos.

**Actions:**
1. **Keep:** `meridian-core/src/meridian_core/utils/credential_store.py` (shared, simple)
2. **Remove:** `meridian-trading/src/meridian_trading/security/credential_manager.py` (duplicate)
3. **Update:** `meridian-trading` to import from `meridian-core`

**Trade-off:** Trading-specific encryption (Fernet) would be removed. Evaluate if this is needed.

---

### Phase 3: Simplify Fallback Behavior

**Goal:** Consistent fallback priority across all repos.

**Proposed Priority:**
1. **Environment variables** (for CI/CD, explicit overrides)
2. **Shared keyring** (`meridian-suite` service)
3. **Legacy keyrings** (temporary, for migration period)
4. **Encrypted file** (meridian-research only, for cross-machine sync)

**Note:** `.env` file loading should be explicit, not automatic (security risk).

---

### Phase 4: Migration & Cleanup

**Actions:**
1. Migrate all credentials to `meridian-suite` keyring service
2. Update all code to use `meridian-core.utils.credential_store`
3. Remove duplicate CredentialManager classes
4. Update documentation
5. Test all repos can access shared credentials

---

## Recommendation: Single Source of Truth

### Use `meridian-core` as the Credential Authority

**Why:**
- ✅ Already designed as shared/foundation layer
- ✅ Simple, maintainable API
- ✅ Used by research repo (proven to work)
- ✅ No domain-specific code (works for all repos)

**Implementation:**
```python
# All repos use this:
from meridian_core.utils import credential_store

# Get credential:
api_key = credential_store.get_secret("GROK_API_KEY")

# Store credential:
credential_store.set_secret("GROK_API_KEY", "xai-...")
```

**Benefits:**
- Single keyring service (`meridian-suite`)
- No code duplication
- Consistent behavior across repos
- Easier to maintain and debug

---

## Architecture Question: Master Repo vs Separate Repos?

**Current:** Three parallel repos (meridian-core, meridian-trading, meridian-research)

**Question:** Should there be one master repo with three sub-repos?

### Analysis

**Arguments FOR Separate Repos:**
1. ✅ **Clear separation of concerns** - Core is domain-agnostic, trading/research are domain-specific
2. ✅ **Independent versioning** - Each repo can evolve at its own pace
3. ✅ **Reduced coupling** - Changes in trading don't affect research
4. ✅ **Easier to open-source core** - Can share core without trading/research code
5. ✅ **Different access control** - Trading vs research may have different stakeholders
6. ✅ **Smaller git history** - Each repo has focused history
7. ✅ **Current architecture matches best practices** - Monorepo vs multi-repo is a common pattern

**Arguments FOR Master Repo (Monorepo):**
1. ✅ **Easier credential sharing** - Single `.env`, single keyring setup
2. ✅ **Unified dependencies** - Single `requirements.txt`, `pyproject.toml`
3. ✅ **Atomic commits** - Can change core + trading + research in one commit
4. ✅ **Simpler CI/CD** - One pipeline
5. ✅ **Better IDE support** - Cross-repo refactoring easier

**Recommendation: Keep Separate Repos**

**Why:**
- Architecture aligns with clean separation (core is foundation, trading/research are applications)
- Credential sharing can be solved with the consolidation plan above
- The refactoring that created separate repos was done for good reasons (see MERIDIAN-REPO-ARCHITECTURE.md)

**Credential Consolidation Solves the Sharing Problem:**
- Use shared keyring service (`meridian-suite`)
- Use shared credential_store from `meridian-core`
- All repos read from same OS keyring (no need for shared `.env`)

---

## Next Steps

### Immediate Actions
1. ✅ Document all credential systems (this document)
2. ❌ Fix `meridian-core/scripts/migrate_credentials.py` to use `meridian-suite`
3. ❌ Test credential access across all repos
4. ❌ Update `meridian-trading` to use shared credential_store

### Short-term (This Week)
1. Migrate all credentials to `meridian-suite` keyring
2. Update all code to use shared credential_store
3. Remove duplicate CredentialManager classes
4. Update documentation

### Long-term
1. Evaluate if encryption layer needed (currently only trading has it)
2. Consider encrypted file sync for cross-machine scenarios
3. Create unified credential management documentation

---

## References

- `MERIDIAN-REPO-ARCHITECTURE.md` - Repository structure documentation
- `meridian-core/src/meridian_core/utils/credential_store.py` - Recommended shared store
- `meridian-core/scripts/migrate_credentials.py` - Migration script (needs fix)
- `meridian-trading/docs/AI-CREDENTIALS.md` - Trading credential docs
- `meridian-research/docs/KEYRING_SECRET_MANAGEMENT.md` - Research credential docs

---

**Last Updated:** 2025-11-20  
**Status:** Analysis Complete - Ready for Consolidation

