# 2025-11-20 - Credential Management Architecture (Current State)

**Date:** 2025-11-20  
**Status:** ✅ **CONSOLIDATED & UNIFIED**  
**Purpose:** Visual representation of the unified credential management architecture after consolidation

---

## Executive Summary

All Meridian repos now use a **unified credential management system**:
- **Single keyring service:** `meridian-suite` (shared across all repos)
- **Shared credential store:** `meridian_core.utils.credential_store`
- **Consistent API:** All repos use the same functions to get/set credentials
- **Backward compatible:** Still reads from legacy services during migration

---

## 1. Unified Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    MERIDIAN CREDENTIAL MANAGEMENT                             │
│                         (Unified Architecture)                                 │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                           meridian-core                                       │
│                    (Credential Authority)                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │              credential_store.py                                    │     │
│  │         (Shared Credential Management)                              │     │
│  │                                                                     │     │
│  │  PRIMARY_SERVICE = "meridian-suite"                                │     │
│  │                                                                     │     │
│  │  Functions:                                                         │     │
│  │    • get_secret(key_name) → Optional[str]                          │     │
│  │    • set_secret(key_name, value) → bool                            │     │
│  │    • get_secret_by_service(service) → Optional[str]                │     │
│  │                                                                     │     │
│  │  Keyring Service:                                                   │     │
│  │    ┌─────────────────────────────────────────────┐                 │     │
│  │    │  meridian-suite (PRIMARY)                    │                 │     │
│  │    │  • GROK_API_KEY                              │                 │     │
│  │    │  • GOOGLE_GEMINI_API_KEY                     │                 │     │
│  │    │  • ANTHROPIC_API_KEY                         │                 │     │
│  │    │  • OPENAI_API_KEY                            │                 │     │
│  │    │  • LOCAL_LLM_URL                             │                 │     │
│  │    │  • IG_USERNAME (trading)                     │                 │     │
│  │    │  • IG_PASSWORD (trading)                     │                 │     │
│  │    │  • IG_API_KEY (trading)                      │                 │     │
│  │    └─────────────────────────────────────────────┘                 │     │
│  │                                                                     │     │
│  │  Legacy Fallback (backward compatibility):                         │     │
│  │    ┌─────────────────────────────────────────────┐                 │     │
│  │    │  LEGACY_SERVICES (checked in order):         │                 │     │
│  │    │  1. meridian-suite (preferred)               │                 │     │
│  │    │  2. meridian-research                        │                 │     │
│  │    │  3. meridian-core                            │                 │     │
│  │    │  4. meridian-trading-system                  │                 │     │
│  │    └─────────────────────────────────────────────┘                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │              Migration Scripts                                      │     │
│  │  • migrate_credentials.py         → Migrate from .env to keyring   │     │
│  │  • migrate_existing_credentials.py → Consolidate legacy services   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                              ↑ imports from
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌───────────────────┐   ┌───────────────────┐
        │ meridian-research │   │ meridian-trading  │
        │  (Uses Shared)    │   │  (Uses Shared)    │
        └───────────────────┘   └───────────────────┘
```

---

## 2. Current Implementation by Repo

### meridian-core (Authority)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           meridian-core                                       │
│                    src/meridian_core/utils/credential_store.py                │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  PRIMARY_SERVICE = "meridian-suite"                                          │
│                                                                               │
│  LEGACY_SERVICES = [                                                          │
│      "meridian-suite",      # Primary (checked first)                        │
│      "meridian-research",   # Legacy fallback                                │
│      "meridian-core",       # Legacy fallback                                │
│      "meridian-trading-system"  # Legacy fallback                            │
│  ]                                                                            │
│                                                                               │
│  Functions:                                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  def get_secret(key_name: str) -> Optional[str]:                │        │
│  │      """Retrieve credential from shared keyring services."""    │        │
│  │      # Checks LEGACY_SERVICES in order                           │        │
│  │      # Returns first match                                       │        │
│  │                                                                  │        │
│  │  def set_secret(key_name: str, value: str) -> bool:             │        │
│  │      """Store credential into shared keyring service."""         │        │
│  │      # Always stores in PRIMARY_SERVICE (meridian-suite)         │        │
│  │                                                                  │        │
│  │  def get_secret_by_service(service_name: str) -> Optional[str]: │        │
│  │      """Get credential by connector service (e.g., 'grok')."""   │        │
│  │      # Maps service → canonical name                              │        │
│  │      # grok → GROK_API_KEY                                        │        │
│  │      # gemini → GOOGLE_GEMINI_API_KEY                             │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                               │
│  Migration Scripts:                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  scripts/migrate_credentials.py                                 │        │
│  │  • Reads from .env file                                         │        │
│  │  • Stores in meridian-suite keyring                              │        │
│  │  • Uses canonical credential names (GROK_API_KEY, etc.)          │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│  ┌─────────────────────────────────────────────────────────────────┐        │
│  │  scripts/migrate_existing_credentials.py                         │        │
│  │  • Scans legacy keyring services                                 │        │
│  │  • Copies to meridian-suite                                      │        │
│  │  • Skips duplicates (won't overwrite)                            │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### meridian-research (Domain Adapter)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        meridian-research                                      │
│         src/meridian_research/utils/credential_store.py                       │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │           Import Shared Store                                        │     │
│  │                                                                     │     │
│  │  try:                                                               │     │
│  │      from meridian_core.utils import credential_store               │     │
│  │          as shared_credential_store                                 │     │
│  │  except ImportError:                                                │     │
│  │      shared_credential_store = None                                 │     │
│  │                                                                     │     │
│  │  if shared_credential_store:                                        │     │
│  │      def _get_keyring_secret(key_name: str) -> Optional[str]:      │     │
│  │          return shared_credential_store.get_secret(key_name)        │     │
│  │                                                                     │     │
│  │      def _set_keyring_secret(key_name: str, value: str) -> bool:   │     │
│  │          return shared_credential_store.set_secret(key_name, value) │     │
│  │                                                                     │     │
│  │  else:                                                              │     │
│  │      # Fallback to legacy secret_manager                            │     │
│  │      ...                                                            │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ✅ Uses shared credential_store from meridian-core                          │
│  ✅ All credentials accessed via meridian-suite keyring                       │
│  ✅ Additional: Encrypted file storage for cross-machine sync                 │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

### meridian-trading (Domain Adapter - UPDATED)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        meridian-trading                                       │
│       src/meridian_trading/config/credentials.py (UPDATED)                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │           Import Shared Store (NEW)                                 │     │
│  │                                                                     │     │
│  │  try:                                                               │     │
│  │      from meridian_core.utils import credential_store               │     │
│  │          as shared_credential_store                                 │     │
│  │      SHARED_STORE_AVAILABLE = True                                  │     │
│  │  except ImportError:                                                │     │
│  │      shared_credential_store = None                                 │     │
│  │      SHARED_STORE_AVAILABLE = False                                 │     │
│  │                                                                     │     │
│  │  def _get_from_shared_keyring(credential_name: str) -> Optional[str]: │   │
│  │      """Get credential from shared meridian-suite keyring service.""" │   │
│  │      if not SHARED_STORE_AVAILABLE:                                 │     │
│  │          return None                                                │     │
│  │      return shared_credential_store.get_secret(credential_name)     │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  Credentials (all use shared store):                                         │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  # AI API Keys (shared across repos)                               │     │
│  │  GROK_API_KEY = _get_from_shared_keyring("GROK_API_KEY")          │     │
│  │      or _get_from_env("GROK_API_KEY")                              │     │
│  │                                                                     │     │
│  │  GOOGLE_GEMINI_API_KEY = _get_from_shared_keyring(                │     │
│  │      "GOOGLE_GEMINI_API_KEY") or _get_from_env(...)               │     │
│  │                                                                     │     │
│  │  ANTHROPIC_API_KEY = _get_from_shared_keyring("ANTHROPIC_API_KEY")│     │
│  │      or _get_from_env("ANTHROPIC_API_KEY")                         │     │
│  │                                                                     │     │
│  │  # Trading-specific (also in shared keyring)                       │     │
│  │  IG_USERNAME = _get_from_shared_keyring("IG_USERNAME")            │     │
│  │      or _get_from_env("IG_USERNAME")                               │     │
│  │                                                                     │     │
│  │  IG_PASSWORD = _get_from_shared_keyring("IG_PASSWORD")            │     │
│  │      or _get_from_env("IG_PASSWORD")                               │     │
│  │                                                                     │     │
│  │  IG_API_KEY = _get_from_shared_keyring("IG_API_KEY")              │     │
│  │      or _get_from_env("IG_API_KEY")                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ✅ REMOVED: Local CredentialManager class (was duplicate)                   │
│  ✅ NOW USES: Shared credential_store from meridian-core                     │
│  ✅ All credentials in meridian-suite keyring                                 │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Credential Access Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      CREDENTIAL ACCESS FLOW (Current)                         │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  Application Code (Any Repo)                                                  │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Example: meridian-trading needs GROK_API_KEY                                │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  from meridian_trading.config.credentials import GROK_API_KEY      │     │
│  │                                                                     │     │
│  │  # Or directly:                                                     │     │
│  │  from meridian_core.utils import credential_store                   │     │
│  │  api_key = credential_store.get_secret("GROK_API_KEY")             │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                              │                                               │
│                              │ calls                                          │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  meridian_core.utils.credential_store.get_secret()                 │     │
│  │                                                                     │     │
│  │  Checks keyring services in order:                                  │     │
│  │  1. meridian-suite (PRIMARY) ← Returns here if found               │     │
│  │  2. meridian-research (legacy) ← Fallback                           │     │
│  │  3. meridian-core (legacy) ← Fallback                               │     │
│  │  4. meridian-trading-system (legacy) ← Fallback                     │     │
│  │                                                                     │     │
│  │  Returns: credential value or None                                  │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                              │                                               │
│                              │ accesses                                       │
│                              ▼                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                    OS Keyring (macOS Keychain)                      │     │
│  │                                                                     │     │
│  │  Service: meridian-suite                                           │     │
│  │  ┌─────────────────────────────────────────────────────────────┐   │     │
│  │  │  Credential: GROK_API_KEY                                    │   │     │
│  │  │  Value: xai-...                                              │   │     │
│  │  │                                                               │   │     │
│  │  │  Credential: GOOGLE_GEMINI_API_KEY                           │   │     │
│  │  │  Value: AIzaSy...                                            │   │     │
│  │  │                                                               │   │     │
│  │  │  Credential: ANTHROPIC_API_KEY                               │   │     │
│  │  │  Value: sk-ant-...                                           │   │     │
│  │  │                                                               │   │     │
│  │  │  ... (all credentials)                                       │   │     │
│  │  └─────────────────────────────────────────────────────────────┘   │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Credential Storage Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    CREDENTIAL STORAGE LAYERS                                  │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  Layer 1: OS Keyring (Primary Storage)                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                    macOS Keychain / Windows Credential Manager      │     │
│  │                                                                     │     │
│  │  Service: meridian-suite (PRIMARY - all repos use this)            │     │
│  │  ┌───────────────────────────────────────────────────────────────┐ │     │
│  │  │  GROK_API_KEY                    → xai-...                    │ │     │
│  │  │  GOOGLE_GEMINI_API_KEY           → AIzaSy...                  │ │     │
│  │  │  ANTHROPIC_API_KEY               → sk-ant-...                 │ │     │
│  │  │  OPENAI_API_KEY                  → sk-...                     │ │     │
│  │  │  LOCAL_LLM_URL                   → http://...                 │ │     │
│  │  │  IG_USERNAME (trading)           → user@...                   │ │     │
│  │  │  IG_PASSWORD (trading)           → pass...                    │ │     │
│  │  │  IG_API_KEY (trading)            → key...                     │ │     │
│  │  └───────────────────────────────────────────────────────────────┘ │     │
│  │                                                                     │     │
│  │  Legacy Services (backward compatibility - migration period):       │     │
│  │  ┌───────────────────────────────────────────────────────────────┐ │     │
│  │  │  meridian-research        → (legacy, being migrated)          │ │     │
│  │  │  meridian-core            → (legacy, being migrated)          │ │     │
│  │  │  meridian-trading-system  → (legacy, being migrated)          │ │     │
│  │  └───────────────────────────────────────────────────────────────┘ │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↑ accessed via
                                    │
┌──────────────────────────────────────────────────────────────────────────────┐
│  Layer 2: Shared Credential Store API                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  meridian_core.utils.credential_store                              │     │
│  │                                                                     │     │
│  │  • get_secret(key_name)                                            │     │
│  │    → Checks meridian-suite first                                    │     │
│  │    → Falls back to legacy services if not found                    │     │
│  │                                                                     │     │
│  │  • set_secret(key_name, value)                                     │     │
│  │    → Always stores in meridian-suite                                │     │
│  │                                                                     │     │
│  │  • get_secret_by_service(service)                                  │     │
│  │    → Maps service name to credential name                          │     │
│  │    → grok → GROK_API_KEY                                           │     │
│  │    → gemini → GOOGLE_GEMINI_API_KEY                                │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    ↑ used by
                                    │
┌──────────────────────────────────────────────────────────────────────────────┐
│  Layer 3: Domain Adapter Credentials                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  meridian-research:                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  from meridian_core.utils import credential_store                   │     │
│  │  api_key = credential_store.get_secret("GROK_API_KEY")             │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  meridian-trading:                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  from meridian_core.utils import credential_store                   │     │
│  │      as shared_credential_store                                     │     │
│  │  GROK_API_KEY = shared_credential_store.get_secret("GROK_API_KEY")│     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Migration Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      CREDENTIAL MIGRATION FLOW                                │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  OLD STATE (Before Consolidation)                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ meridian-    │  │ meridian-    │  │ meridian-    │                      │
│  │ research     │  │ core         │  │ trading-     │                      │
│  │ keyring      │  │ keyring      │  │ system       │                      │
│  │              │  │              │  │ keyring      │                      │
│  │ ❌ Isolated  │  │ ❌ Isolated  │  │ ❌ Isolated  │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Migration Scripts Run
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  MIGRATION PROCESS                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  migrate_existing_credentials.py                                    │     │
│  │                                                                     │     │
│  │  1. Scan legacy keyring services:                                  │     │
│  │     • meridian-research                                             │     │
│  │     • meridian-core                                                 │     │
│  │     • meridian-trading-system                                       │     │
│  │                                                                     │     │
│  │  2. For each credential found:                                      │     │
│  │     • Check if already exists in meridian-suite                     │     │
│  │     • If not, copy to meridian-suite                                │     │
│  │     • If exists and same value, skip                                │     │
│  │     • If exists but different, skip (won't overwrite)               │     │
│  │                                                                     │     │
│  │  3. Verify migration:                                               │     │
│  │     • Count migrated credentials                                    │     │
│  │     • Report status                                                 │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Credentials copied
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  NEW STATE (After Consolidation)                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                    meridian-suite (UNIFIED)                         │     │
│  │                                                                     │     │
│  │  ✅ All credentials in single keyring service                       │     │
│  │  ✅ Accessible to all repos                                         │     │
│  │  ✅ Consistent naming (GROK_API_KEY, etc.)                          │     │
│  │                                                                     │     │
│  │  Legacy services still checked for backward compatibility           │     │
│  │  (will be deprecated after migration period)                        │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │ meridian-research│  │ meridian-core    │  │ meridian-trading │         │
│  │                  │  │                  │  │                  │         │
│  │ ✅ Uses shared   │  │ ✅ Uses shared   │  │ ✅ Uses shared   │         │
│  │    store         │  │    store         │  │    store         │         │
│  │                  │  │                  │  │                  │         │
│  │ ✅ All creds in  │  │ ✅ All creds in  │  │ ✅ All creds in  │         │
│  │    meridian-suite│  │    meridian-suite│  │    meridian-suite│         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Service-to-Credential Mapping

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                  SERVICE NAME → CREDENTIAL NAME MAPPING                       │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  meridian_core.utils.credential_store.SERVICE_KEY_MAP                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Service Identifier          →  Canonical Credential Name                    │
│  ─────────────────────────────────────────────────────────────              │
│  "anthropic"  or "claude"    →  ANTHROPIC_API_KEY                            │
│  "openai"     or "chatgpt"   →  OPENAI_API_KEY                               │
│  "gemini"                     →  GOOGLE_GEMINI_API_KEY                        │
│  "grok"       or "xai"       →  GROK_API_KEY                                 │
│  "local_llm"                 →  LOCAL_LLM_URL                                │
│                                                                               │
│  Usage:                                                                       │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  # Get by service name:                                            │     │
│  │  api_key = credential_store.get_secret_by_service("grok")         │     │
│  │  # Internally maps to: GROK_API_KEY                                │     │
│  │                                                                     │     │
│  │  # Get directly by credential name:                                │     │
│  │  api_key = credential_store.get_secret("GROK_API_KEY")             │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Credential Access Priority

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    CREDENTIAL ACCESS PRIORITY                                 │
└──────────────────────────────────────────────────────────────────────────────┘

When an application requests a credential, here's the lookup order:

Priority 1: Shared Keyring (meridian-suite) ✅ PRIMARY
┌──────────────────────────────────────────────────────────────────────────┐
│  Service: meridian-suite                                                 │
│  Credential: GROK_API_KEY (canonical name)                               │
│  ✅ All repos check here first                                            │
└──────────────────────────────────────────────────────────────────────────┘
                    │
                    │ Not found? Check legacy services
                    ▼
Priority 2: Legacy Keyring Services (backward compatibility)
┌──────────────────────────────────────────────────────────────────────────┐
│  Checked in order:                                                        │
│  1. meridian-research                                                     │
│  2. meridian-core                                                         │
│  3. meridian-trading-system                                               │
│  ⚠️  Only during migration period                                          │
│  ⚠️  Will be deprecated once all creds migrated                            │
└──────────────────────────────────────────────────────────────────────────┘
                    │
                    │ Not found? Check environment variables (if enabled)
                    ▼
Priority 3: Environment Variables (optional, for development/CI)
┌──────────────────────────────────────────────────────────────────────────┐
│  Only if ALLOW_ENV_FALLBACK=1                                             │
│  • .env file (via python-dotenv)                                          │
│  • System environment variables                                           │
│  ⚠️  Not enabled by default (security)                                    │
│  ⚠️  Intended for local development only                                  │
└──────────────────────────────────────────────────────────────────────────┘
                    │
                    │ Not found?
                    ▼
Priority 4: Return None
┌──────────────────────────────────────────────────────────────────────────┐
│  Credential not available                                                 │
│  • Application should handle gracefully                                   │
│  • User should run migration script                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 8. What Was Fixed (Current vs Old)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        BEFORE (Old State) ❌                                  │
└──────────────────────────────────────────────────────────────────────────────┘

meridian-core:
  ❌ Migration script used "meridian-core" service (wrong)
  ❌ Migrated credentials not accessible to other repos
  ❌ Used service names (grok) instead of canonical names (GROK_API_KEY)

meridian-trading:
  ❌ Used local CredentialManager class (isolated)
  ❌ Used "meridian-trading-system" keyring service (isolated)
  ❌ Couldn't share credentials with other repos
  ❌ Duplicate code from archived meridian repo

meridian-research:
  ✅ Already used shared store (was correct)

Result:
  ❌ 3 different keyring services
  ❌ Credentials stored in one service invisible to others
  ❌ Code duplication
  ❌ Inconsistent behavior

┌──────────────────────────────────────────────────────────────────────────────┐
│                        AFTER (Current State) ✅                               │
└──────────────────────────────────────────────────────────────────────────────┘

meridian-core:
  ✅ Migration script uses "meridian-suite" service (correct)
  ✅ Uses canonical credential names (GROK_API_KEY, etc.)
  ✅ All migrated credentials accessible to all repos
  ✅ Migration script uses shared credential_store for consistency

meridian-trading:
  ✅ Uses shared credential_store from meridian-core
  ✅ Uses "meridian-suite" keyring service (unified)
  ✅ Can share credentials with other repos
  ✅ Removed duplicate CredentialManager code

meridian-research:
  ✅ Already used shared store (still correct)
  ✅ Uses "meridian-suite" keyring service

Result:
  ✅ Single keyring service (meridian-suite)
  ✅ All repos can access all credentials
  ✅ No code duplication
  ✅ Consistent behavior across repos
  ✅ Backward compatible (reads from legacy services during migration)
```

---

## 9. File Structure (Current)

```
meridian-core/
├── src/meridian_core/utils/
│   └── credential_store.py              ✅ Shared credential store
│       • PRIMARY_SERVICE = "meridian-suite"
│       • LEGACY_SERVICES = [...]
│       • get_secret(key_name)
│       • set_secret(key_name, value)
│       • get_secret_by_service(service)
│
└── scripts/
    ├── migrate_credentials.py           ✅ Fixed: uses meridian-suite
    │   • Reads from .env
    │   • Stores in meridian-suite
    │   • Uses canonical names
    │
    └── migrate_existing_credentials.py  ✅ New: consolidates legacy creds
        • Scans legacy services
        • Copies to meridian-suite
        • Skips duplicates

meridian-research/
└── src/meridian_research/utils/
    └── credential_store.py              ✅ Uses shared store from core
        • Imports from meridian_core.utils.credential_store
        • Wraps shared functions
        • Additional: encrypted file storage

meridian-trading/
└── src/meridian_trading/config/
    └── credentials.py                   ✅ UPDATED: uses shared store
        • Imports from meridian_core.utils.credential_store
        • All credentials use shared store
        • Removed local CredentialManager dependency
```

---

## 10. Usage Examples (Current State)

### Getting Credentials

```python
# Option 1: Use domain adapter's credentials module
from meridian_trading.config.credentials import GROK_API_KEY
# Uses shared store internally

# Option 2: Use shared store directly
from meridian_core.utils import credential_store
api_key = credential_store.get_secret("GROK_API_KEY")

# Option 3: Get by service name
api_key = credential_store.get_secret_by_service("grok")
# Internally maps "grok" → "GROK_API_KEY"
```

### Storing Credentials

```python
# Use shared store directly
from meridian_core.utils import credential_store
credential_store.set_secret("GROK_API_KEY", "xai-...")
# Always stores in meridian-suite service
```

### Migration Example

```bash
# Migrate credentials from .env file
cd meridian-core
python scripts/migrate_credentials.py
# Stores all credentials in meridian-suite keyring

# Consolidate existing credentials from legacy services
python scripts/migrate_existing_credentials.py
# Copies from legacy services to meridian-suite
```

---

## 11. Summary

### ✅ Current Architecture Benefits

1. **Single Source of Truth** - All credentials in `meridian-suite` keyring
2. **Universal Access** - All repos can access all credentials
3. **No Code Duplication** - Single credential_store used everywhere
4. **Consistent API** - Same functions across all repos
5. **Backward Compatible** - Still reads from legacy services during migration
6. **Security** - OS keyring storage (macOS Keychain/Windows Credential Manager)
7. **Easy Migration** - Scripts to consolidate existing credentials

### 🎯 Key Points

- **Primary Service:** `meridian-suite` (all repos use this)
- **Shared Module:** `meridian_core.utils.credential_store`
- **Canonical Names:** `GROK_API_KEY`, `GOOGLE_GEMINI_API_KEY`, etc. (not `grok`, `gemini`)
- **Backward Compatible:** Legacy services still checked during migration period
- **Migration Tools:** Scripts available to consolidate credentials

### 📋 Next Steps

1. ✅ Run `migrate_existing_credentials.py` to consolidate legacy credentials
2. ✅ Verify credentials accessible across all repos
3. ✅ Test API connections with unified credentials
4. ⏳ (Future) Deprecate legacy services after migration period

---

**Last Updated:** 2025-11-20  
**Status:** ✅ Unified & Consolidated  
**Version:** Current State (Post-Consolidation)

