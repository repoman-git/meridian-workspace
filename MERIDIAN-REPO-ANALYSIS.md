# Meridian Repo Analysis: Services & Unique Features

**Date:** 2025-11-19  
**Purpose:** Determine if `meridian` repo provides services to other repos and what unique features it has

---

## 🔍 Analysis Results

### Question 1: Does `meridian` provide services to other repos?

**Answer: NO**

**Evidence:**
- `meridian-trading` imports from `meridian_core` (not `meridian`)
- `meridian-research` imports from `meridian_core` (not `meridian`)
- `meridian-core` only imports from itself
- **Zero imports from `meridian` repo found in other repos**

**Conclusion:** `meridian` is **standalone** and does NOT provide services to other repos.

---

### Question 2: Does `meridian` have unique features not in other repos?

**Answer: PARTIALLY - Some features exist in both, some are unique**

#### Features That Exist in BOTH Repos:

1. **LocalExec Connector** ✅
   - `meridian`: `ai_orchestrator_framework/src/connectors/localexec_connector.py`
   - `meridian-core`: `src/meridian_core/connectors/localexec_connector.py`
   - **Status:** Different implementations (files differ)
   - **Note:** Both have LocalExec, but implementations may vary

2. **Honesty Framework** ✅
   - `meridian`: `ai_orchestrator_framework/src/orchestration/honesty_policy.py`
   - `meridian-core`: `src/meridian_core/orchestration/honesty_policy.py`
   - **Status:** Both have it

3. **MCP Server Support** ⚠️
   - `meridian`: Has `mcp-server/` directory with implementations
   - `meridian-core`: Has `server_localexec.py` but unclear if full MCP server
   - **Status:** `meridian` appears to have more complete MCP server implementation

#### Features UNIQUE to `meridian`:

1. **MCP Server Directory** 🆕
   - `meridian/ai_orchestrator_framework/mcp-server/`
   - Contains: `server_localexec.py`, `server.py`, `server_v2.py`, `server_lmstudio.py`
   - **Status:** Full MCP server implementations
   - **Not found in:** `meridian-core` (only has `server_localexec.py`)

2. **GitHub Issue Publishing from Meta-Review** 🆕
   - `meridian` has scripts to publish meta-review findings to GitHub Issues
   - Mentioned in `ai_orchestrator_framework/README.md`
   - **Status:** Unique to `meridian`
   - **Not found in:** `meridian-core`

3. **Trading System Integration** 🆕
   - `meridian` has complete trading system (`src/`) integrated with orchestrator
   - `meridian-trading` is separate repo that uses `meridian-core`
   - **Status:** `meridian` has embedded trading system

4. **Different Orchestrator Architecture** 🆕
   - `meridian`: Uses `ai_orchestrator_framework/` (embedded)
   - `meridian-core`: Standalone framework
   - **Status:** Different architectures, potentially different features

---

## 📊 Feature Comparison Matrix

| Feature | meridian | meridian-core | meridian-trading | meridian-research |
|---------|----------|---------------|------------------|-------------------|
| **Orchestrator** | ✅ Embedded (`ai_orchestrator_framework/`) | ✅ Standalone framework | ❌ Uses meridian-core | ❌ Uses meridian-core |
| **LocalExec** | ✅ Has | ✅ Has | ❌ (via core) | ❌ (via core) |
| **Honesty Framework** | ✅ Has | ✅ Has | ❌ (via core) | ❌ (via core) |
| **MCP Server** | ✅ Full implementation | ⚠️ Partial (`server_localexec.py`) | ❌ | ❌ |
| **GitHub Issue Publishing** | ✅ Has | ❌ | ❌ | ❌ |
| **Trading System** | ✅ Embedded | ❌ | ✅ Separate repo | ❌ |
| **Research System** | ❌ | ❌ | ❌ | ✅ Separate repo |
| **Provides Services** | ❌ No | ✅ Yes (to trading/research) | ❌ No | ❌ No |

---

## 🎯 Key Findings

### 1. `meridian` is NOT a Service Provider
- **No other repos import from `meridian`**
- It's a standalone system with embedded orchestrator
- Other repos use `meridian-core` instead

### 2. `meridian` Has Some Unique Features
- **MCP Server implementations** (more complete than meridian-core)
- **GitHub Issue publishing** from meta-review
- **Embedded trading system** (vs. separate `meridian-trading` repo)

### 3. Feature Duplication
- Both `meridian` and `meridian-core` have:
  - LocalExec connector (different implementations)
  - Honesty Framework
  - Orchestration capabilities
- **This creates maintenance burden** - changes need to be made in both places

### 4. Architecture Difference
- **`meridian`**: Monolithic (trading + orchestrator together)
- **`meridian-core` + `meridian-trading`**: Modular (framework + domain adapter)
- **Modern approach:** Modular (meridian-core + domain adapters)

---

## 💡 Recommendations

### Option 1: Migrate Unique Features to meridian-core
**If MCP server and GitHub publishing are valuable:**

1. **Migrate MCP server** from `meridian` to `meridian-core`
   - Makes it available to all repos
   - Consolidates maintenance

2. **Migrate GitHub publishing** to `meridian-core` (or create separate tool)
   - Generic feature that could benefit all repos

3. **Refactor `meridian`** to use `meridian-core` + `meridian-trading`
   - Remove embedded orchestrator
   - Use modular architecture

**Benefits:**
- Single source of truth
- Less duplication
- Features available to all repos

### Option 2: Keep `meridian` as Legacy/Reference
**If migration is too costly:**

1. **Mark `meridian` as legacy/reference**
   - Document it's the original implementation
   - Keep for historical reference

2. **Focus development on `meridian-core` + domain adapters**
   - Modern, modular architecture
   - Better separation of concerns

3. **Extract unique features** if needed:
   - Copy MCP server to meridian-core if valuable
   - Copy GitHub publishing if valuable

**Benefits:**
- Clear separation (legacy vs. modern)
- No breaking changes
- Can reference old implementation

### Option 3: Archive `meridian`
**If it's truly no longer needed:**

1. **Archive the repo** (read-only)
2. **Document migration path** for anyone still using it
3. **Focus entirely on `meridian-core` + domain adapters**

**Benefits:**
- Simplest architecture
- No confusion about which to use
- Clear direction forward

---

## 📝 Decision Needed

**Questions to answer:**

1. **Is `meridian` still actively used?**
   - If yes → Keep it, but clarify its role
   - If no → Archive or migrate

2. **Are MCP server features valuable?**
   - If yes → Migrate to `meridian-core`
   - If no → Leave in `meridian` or remove

3. **Is GitHub issue publishing needed?**
   - If yes → Migrate to `meridian-core` or separate tool
   - If no → Leave in `meridian` or remove

4. **Should `meridian` be refactored to use `meridian-core`?**
   - If yes → Migration project
   - If no → Keep as-is, document as legacy

---

## 🔄 Next Steps

1. **Decide on `meridian`'s future** (migrate, archive, or keep)
2. **Document decision** in MERIDIAN-REPO-ARCHITECTURE.md
3. **Update all repo READMEs** to clarify relationships
4. **Create migration plan** if consolidating

---

**Last Updated:** 2025-11-19  
**Status:** Analysis Complete - Awaiting Decision



