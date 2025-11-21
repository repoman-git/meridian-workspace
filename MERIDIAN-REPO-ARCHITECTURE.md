# Meridian Repository Architecture & Roles

> **Purpose:** Clear definition of each Meridian repo's role, relationships, and when to use each one.

**Last Updated:** 2025-11-19  
**Status:** Active Documentation

---

## 🗺️ Repository Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MERIDIAN ECOSYSTEM                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  meridian-core   │  ← Generic AI orchestration framework
│                  │  ← Domain-agnostic (works for ANY domain)
│  (Foundation)    │  ← NO trading/research-specific code
│                  │  ← Includes MCP servers, GitHub publishing
└────────┬─────────┘
         │
         │ (used by)
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│meridian-│ │meridian-     │
│trading  │ │research      │
│         │ │              │
│Trading  │ │Research      │
│adapter  │ │adapter       │
│         │ │              │
│Uses     │ │Uses          │
│core     │ │core          │
└─────────┘ └──────────────┘

┌──────────────────┐
│Meridian-Core-    │  ← Shared ops utilities
│Operations        │  ← Session scripts, CA certs, bootstrap
│                  │  ← Governance docs, shared assets
└──────────────────┘

┌──────────────────┐
│meridian          │  ← ARCHIVED (2025-11-19)
│(legacy)          │  ← Features migrated to meridian-core
│                  │  ← See MERIDIAN-ARCHIVE-EVALUATION.md
└──────────────────┘
```

---

## 📦 Repository Roles

### 1. **meridian-core** 
**Role:** Generic AI orchestration framework (foundation layer)

**Purpose:**
- Domain-agnostic AI orchestration engine
- Multi-AI agent coordination (Claude, GPT-4, Gemini, Grok, Local LLM)
- Smart task allocation, voting, decision memory
- Abstract interfaces that ANY domain can implement
- NO domain-specific code (no trading, no research specifics)

**Key Features:**
- Autonomous orchestrator
- Multi-AI voting system
- Smart task allocation (cost/quality optimization)
- Decision memory graph
- Pre-flight resource checks
- Generic learning framework (abstract base classes)

**Dependencies:**
- None (foundation layer)
- Python 3.10+, AI SDKs (anthropic, openai, google-generativeai, etc.)

**Used By:**
- `meridian-trading` (trading domain adapter)
- `meridian-research` (research domain adapter)
- Any future domain adapters

**When to Use:**
- Building a new domain adapter (e.g., customer support, code review)
- Need generic AI orchestration without domain specifics
- Want reusable framework for multi-AI coordination

**Key Files:**
- `src/meridian_core/orchestration/` - Core orchestration logic
- `src/meridian_core/connectors/` - AI provider connectors
- `src/meridian_core/learning/` - Abstract learning framework

---

### 2. **meridian-trading**
**Role:** Trading domain adapter (uses meridian-core)

**Purpose:**
- Trading-specific implementations
- Larry Williams strategies (Williams %R, TDOM, COT)
- Risk management (2%/6% rules)
- Market indicators, backtesting
- Uses meridian-core for AI orchestration

**Key Features:**
- Trading strategies and indicators
- Risk management system
- Market scanners
- Backtesting engine
- Trading-specific learning engine (implements core interfaces)

**Dependencies:**
- `meridian-core` (required)
- Trading libraries (pandas, numpy, yfinance, openbb)

**Uses:**
- Imports from `meridian-core` for orchestration
- Implements `meridian-core` abstract interfaces
- Adds trading-specific logic on top

**When to Use:**
- Building trading strategies
- Need trading indicators/risk management
- Want AI-powered trading decisions using meridian-core

**Key Files:**
- `src/meridian_trading/indicators/` - Technical indicators
- `src/meridian_trading/strategies/` - Trading strategies
- `src/meridian_trading/risk/` - Risk management
- `src/meridian_trading/adapters/` - Core integration

---

### 3. **meridian-research**
**Role:** Research domain adapter (uses meridian-core)

**Purpose:**
- Research utilities with domain-specific skills
- Self-learning research system
- Multi-AI research coordination
- Knowledge base management
- Uses meridian-core for AI orchestration

**Key Features:**
- Research engine with skills system
- Self-learning capabilities (session analysis, pattern detection)
- Knowledge base (records research findings)
- CLI for research workflows
- Research-specific learning engine (implements core interfaces)

**Dependencies:**
- `meridian-core` (required)
- Research libraries (as needed)

**Uses:**
- Imports from `meridian-core` for orchestration
- Implements `meridian-core` abstract interfaces
- Adds research-specific logic on top

**When to Use:**
- Building research tools
- Need AI-powered research with skills
- Want self-learning research system

**Key Files:**
- `src/meridian_research/core/` - Research engine
- `src/meridian_research/skills/` - Domain skills
- `src/meridian_research/learning/` - Learning engine
- `src/meridian_research/knowledge/` - Knowledge base

---

### 4. **meridian** ⚠️ ARCHIVED
**Role:** ~~Original trading system with embedded orchestrator~~ **ARCHIVED (2025-11-19)**

**Status:** 🗄️ **ARCHIVED** - Features migrated to meridian-core

**Migration Summary:**
- ✅ **MCP Servers** → Migrated to `meridian-core/src/meridian_core/connectors/mcp/`
- ✅ **GitHub Issue Publishing** → Migrated to `meridian-core/scripts/publish_meta_review_to_github.py`
- ❌ **Trading System** → Already exists in `meridian-trading` (better architecture)
- ❌ **Orchestrator** → Superseded by `meridian-core` (better architecture)

**Original Purpose (Historical):**
- Complete trading system (indicators, strategies, risk)
- Had its own orchestrator framework (`ai_orchestrator_framework/`)
- Larry Williams strategies
- Self-contained (didn't use meridian-core)

**Why Archived:**
- Duplicate functionality with modern repos
- Monolithic architecture (superseded by modular approach)
- Unique features migrated to meridian-core
- No longer actively maintained

**When to Reference:**
- Historical reference only
- Understanding original implementation
- Migration documentation

**Migration Details:**
- See `MERIDIAN-ARCHIVE-EVALUATION.md` for full migration plan
- See `MERIDIAN-REPO-ANALYSIS.md` for feature comparison

---

### 5. **Meridian-Core-Operations**
**Role:** Shared operations utilities and assets

**Purpose:**
- Shared ops toolkit for all Meridian repos
- Session scripts (session_start.sh, session_end.sh)
- CA certificate migration tools
- Bootstrap scripts for new machines
- Governance documentation
- Shared assets (AI guidelines, ADRs)

**Key Features:**
- `bootstrap_meridian_env.sh` - Sets up all repos on new machine
- `ca_cert_transfer.sh` - Migrates SSL certificates
- Session script templates
- Shared documentation templates

**Dependencies:**
- None (standalone ops toolkit)

**Used By:**
- All Meridian repos (via `meridian-ops sync`)

**When to Use:**
- Setting up new development machine
- Migrating between machines
- Updating shared governance docs
- Syncing session scripts across repos

**Key Files:**
- `src/meridian_ops/assets/scripts/` - Session scripts
- `src/meridian_ops/assets/docs/` - Shared docs
- Bootstrap and migration tools

---

## 🔗 Dependency Graph

```
meridian-core (foundation)
    ↑
    │ (depends on)
    │
    ├── meridian-trading
    │   └── Uses core for orchestration
    │   └── Implements core interfaces
    │
    └── meridian-research
        └── Uses core for orchestration
        └── Implements core interfaces

Meridian-Core-Operations (standalone)
    └── Used by all repos
    └── No dependencies

meridian (ARCHIVED - 2025-11-19)
    └── Features migrated to meridian-core
    └── See MERIDIAN-ARCHIVE-EVALUATION.md
```

---

## ✅ Archive Status

### `meridian` Repo: ARCHIVED (2025-11-19)

**Decision:** Archive `meridian` after migrating valuable features

**Migrated Features:**
1. ✅ **MCP Server Suite** → `meridian-core/src/meridian_core/connectors/mcp/`
   - Multi-AI collaboration server
   - LM Studio integration server
   - Enhanced collaboration server (v2 with token tracking)

2. ✅ **GitHub Issue Publishing** → `meridian-core/scripts/publish_meta_review_to_github.py`
   - Automated issue creation from meta-reviews
   - Available to all repos

**Not Migrated (Superseded):**
- Trading system → Already in `meridian-trading` (better architecture)
- Orchestrator → Already in `meridian-core` (better architecture)
- LocalExec/Honesty → Already in `meridian-core`

**Archive Status:**
- ✅ Features evaluated and migrated
- ✅ Documentation updated
- ⏳ Archive branch created (pending)
- ⏳ README_ARCHIVED.md added (pending)

**See:**
- `MERIDIAN-ARCHIVE-EVALUATION.md` - Full evaluation and migration plan
- `MERIDIAN-REPO-ANALYSIS.md` - Feature comparison analysis

---

## 📋 Decision Matrix: Which Repo Should I Use?

| Task | Use This Repo | Why |
|------|---------------|-----|
| Build generic AI orchestration | `meridian-core` | Foundation layer, domain-agnostic |
| Build trading strategies | `meridian-trading` | Trading-specific, uses core |
| Build research tools | `meridian-research` | Research-specific, uses core |
| Work on original trading system | `meridian` ⚠️ | **ARCHIVED** - Use `meridian-trading` instead |
| Set up new machine | `Meridian-Core-Operations` | Bootstrap scripts |
| Add new AI connector | `meridian-core` | Generic, works for all domains |
| Add trading indicator | `meridian-trading` | Trading-specific |
| Add research skill | `meridian-research` | Research-specific |
| Add multi-AI voting | `meridian-core` | Generic orchestration feature |
| Add backtesting | `meridian-trading` | Trading-specific |
| Add self-learning | `meridian-core` (abstract) + domain adapter (implementation) | Split: interface in core, implementation in domain |

---

## 🎯 Clear Role Definitions

### **meridian-core**
> **"The HOW"** - Generic orchestration framework that works for ANY domain

### **meridian-trading**
> **"Trading WHAT"** - Trading-specific implementations using meridian-core

### **meridian-research**
> **"Research WHAT"** - Research-specific implementations using meridian-core

### **meridian** ⚠️
> **"ARCHIVED"** - Original trading system (archived 2025-11-19, features migrated to meridian-core)

### **Meridian-Core-Operations**
> **"The Ops"** - Shared utilities, scripts, and governance docs for all repos

---

## 📝 Next Steps

1. ✅ **`meridian` status clarified:**
   - [x] Determined it's legacy/archived
   - [x] Documented differences and migration plan
   - [x] Migrated valuable features to meridian-core

2. **Complete archive process:**
   - [ ] Finalize MCP server migration (test with AI tools)
   - [ ] Finalize GitHub publishing migration (test with repos)
   - [ ] Create archive branch in meridian repo
   - [ ] Add README_ARCHIVED.md to meridian repo
   - [ ] Mark repo as archived in GitHub

3. **Update documentation:**
   - [x] Architecture doc created
   - [ ] Add this architecture doc to all active repos
   - [ ] Update READMEs to reference this doc
   - [ ] Remove references to `meridian` from active repos

4. **Standardize:**
   - [ ] Ensure all repos have consistent AI-GUIDELINES.md
   - [ ] Ensure all repos have CROSS-REPO-GUIDE.md (or note why not)
   - [ ] Sync session scripts via meridian-ops

---

## 🔄 Cross-Repo Workflow

### When Working Across Repos:

1. **Generic feature** → Implement in `meridian-core`
2. **Domain-specific feature** → Implement in domain adapter (`meridian-trading` or `meridian-research`)
3. **Feature spans both** → Abstract interface in `meridian-core`, implementation in domain adapter
4. **Ops/scripts** → Update in `Meridian-Core-Operations`, sync to all repos

### Example: Adding Self-Learning

1. **Step 1 (meridian-core):** Create abstract `LearningEngine` base class
2. **Step 2 (meridian-trading):** Create `TradingLearningEngine` that implements it
3. **Step 3 (meridian-research):** Create `ResearchLearningEngine` that implements it

---

**This document should be:**
- Updated when repo roles change
- Referenced in all repo READMEs
- Used by AI assistants to understand architecture
- Kept in sync across all repos (via meridian-ops)

---

**Last Updated:** 2025-11-19  
**Maintained By:** Meridian Team  
**Questions?** See CROSS-REPO-GUIDE.md in each repo

