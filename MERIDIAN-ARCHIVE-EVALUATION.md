# Meridian Repo Archive Evaluation

**Date:** 2025-11-19  
**Purpose:** Evaluate unique features in `meridian` repo before archiving to determine if they should be migrated to other repos

---

## 🎯 Executive Summary

**Recommendation:** Archive `meridian` after migrating **2 valuable features** to `meridian-core`:
1. ✅ **MCP Server implementations** (high value - enables AI tool integration)
2. ✅ **GitHub Issue Publishing from Meta-Review** (medium value - useful for all repos)

**Features to Archive (not needed):**
- Embedded trading system (already in `meridian-trading`)
- Embedded orchestrator (superseded by `meridian-core`)

---

## 📋 Feature Analysis

### 1. MCP Server Implementations ⭐⭐⭐ HIGH VALUE

**Location:** `meridian/ai_orchestrator_framework/mcp-server/`

**What it is:**
- Model Context Protocol (MCP) server implementations
- Enables AI tools (Claude Code, Continue.dev, Grok) to interact with the system
- Provides secure local code execution via MCP protocol

**Unique Files:**
- `server.py` - Multi-AI collaboration MCP server
- `server_localexec.py` - Secure LocalExec MCP server
- `server_lmstudio.py` - LM Studio integration MCP server
- `server_v2.py` - Enhanced version
- Configuration files and documentation

**Current State in meridian-core:**
- Has `server_localexec.py` but appears to be a basic version
- Does NOT have the full MCP server suite
- Missing multi-AI collaboration server
- Missing LM Studio integration server

**Value Assessment:**
- ✅ **HIGH VALUE** - MCP is becoming standard for AI tool integration
- ✅ **Would benefit:** All repos (meridian-core, meridian-trading, meridian-research)
- ✅ **Use case:** Allows AI assistants to interact with orchestrator via MCP protocol
- ✅ **Future-proof:** MCP is the emerging standard for AI tool integration

**Migration Recommendation:**
- ✅ **MIGRATE** to `meridian-core/src/meridian_core/connectors/mcp/`
- Makes MCP servers available to all repos
- Consolidates MCP functionality in one place
- Enables AI tools to work with any Meridian repo

**Migration Effort:** Medium (2-3 days)
- Copy MCP server files
- Update imports to use meridian-core connectors
- Test with each AI tool (Claude Code, Continue.dev, Grok)
- Update documentation

---

### 2. GitHub Issue Publishing from Meta-Review ⭐⭐ MEDIUM VALUE

**Location:** `meridian/scripts/publish_meta_review_to_github.py`

**What it is:**
- Script that publishes meta-review findings to GitHub Issues
- Automatically creates issues for HIGH/CRITICAL findings
- Supports dry-run mode, severity filtering, label management

**Key Features:**
- Runs meta-review via orchestrator
- Filters by severity (CRITICAL, HIGH, MEDIUM, LOW, ENHANCEMENT)
- Creates GitHub issues with proper formatting
- Supports multiple token sources (GH_TOKEN, GITHUB_TOKEN_GA, GITHUB_TOKEN)
- Preflight checks for token validity and repo access

**Current State in meridian-core:**
- Has meta-review functionality
- Does NOT have GitHub issue publishing
- Review findings are only logged, not published

**Value Assessment:**
- ✅ **MEDIUM VALUE** - Useful for automated issue tracking
- ✅ **Would benefit:** All repos (meridian-core, meridian-trading, meridian-research)
- ✅ **Use case:** Automatically create GitHub issues from code reviews
- ⚠️ **Note:** Could be optional/plugin rather than core feature

**Migration Recommendation:**
- ✅ **MIGRATE** to `meridian-core/scripts/` or `meridian-core/src/meridian_core/utils/`
- Makes it available to all repos
- Can be used by CI/CD pipelines
- Optional feature (doesn't break if GitHub token not set)

**Migration Effort:** Low (1 day)
- Copy script
- Update imports to use meridian-core orchestrator
- Test with different repos
- Add to meridian-core documentation

---

### 3. Embedded Trading System ⭐ NOT NEEDED

**Location:** `meridian/src/`

**What it is:**
- Complete trading system (indicators, strategies, risk management)
- Larry Williams strategies implementation

**Current State:**
- Already exists in `meridian-trading` repo (separate, uses meridian-core)
- More modern, modular architecture

**Value Assessment:**
- ❌ **NOT NEEDED** - Superseded by `meridian-trading`
- ❌ **Duplicate** - Same functionality exists in better form
- ❌ **Legacy** - Old monolithic architecture

**Migration Recommendation:**
- ❌ **DO NOT MIGRATE** - Archive with meridian repo
- `meridian-trading` is the modern replacement

---

### 4. Embedded Orchestrator ⭐ NOT NEEDED

**Location:** `meridian/ai_orchestrator_framework/`

**What it is:**
- Embedded AI orchestrator framework
- Similar functionality to meridian-core

**Current State:**
- Superseded by `meridian-core` (standalone, better architecture)
- Other repos already use meridian-core

**Value Assessment:**
- ❌ **NOT NEEDED** - Superseded by `meridian-core`
- ❌ **Duplicate** - Same functionality exists in better form
- ❌ **Legacy** - Old embedded architecture

**Migration Recommendation:**
- ❌ **DO NOT MIGRATE** - Archive with meridian repo
- `meridian-core` is the modern replacement
- Any unique features should be evaluated individually (see MCP servers above)

---

## 📊 Feature Comparison Matrix

| Feature | meridian | meridian-core | Value | Migrate? |
|---------|----------|---------------|-------|----------|
| **MCP Server (full suite)** | ✅ Has | ⚠️ Partial | HIGH | ✅ YES |
| **GitHub Issue Publishing** | ✅ Has | ❌ Missing | MEDIUM | ✅ YES |
| **Trading System** | ✅ Has | ❌ (in trading repo) | N/A | ❌ NO |
| **Orchestrator** | ✅ Has | ✅ Better version | N/A | ❌ NO |
| **LocalExec** | ✅ Has | ✅ Has | N/A | ❌ NO (already exists) |
| **Honesty Framework** | ✅ Has | ✅ Has | N/A | ❌ NO (already exists) |

---

## 🚀 Migration Plan

### Phase 1: Migrate MCP Servers (Priority: HIGH)

**Target:** `meridian-core/src/meridian_core/connectors/mcp/`

**Files to Migrate:**
```
meridian/ai_orchestrator_framework/mcp-server/
├── server.py                    → mcp/collaboration_server.py
├── server_localexec.py          → mcp/localexec_server.py (enhance existing)
├── server_lmstudio.py           → mcp/lmstudio_server.py
├── server_v2.py                 → mcp/enhanced_server.py
├── config.json                  → mcp/config.json
├── README.md                    → mcp/README.md
└── requirements.txt             → (merge into meridian-core requirements)
```

**Steps:**
1. Create `meridian-core/src/meridian_core/connectors/mcp/` directory
2. Copy MCP server files
3. Update imports to use meridian-core connectors
4. Update configuration to work with meridian-core structure
5. Test with Claude Code, Continue.dev, Grok
6. Update documentation
7. Add to meridian-core README

**Testing:**
- Test each MCP server with appropriate AI tool
- Verify secure execution works
- Verify collaboration features work
- Test with meridian-core orchestrator

---

### Phase 2: Migrate GitHub Publishing (Priority: MEDIUM)

**Target:** `meridian-core/scripts/publish_meta_review_to_github.py`

**Files to Migrate:**
```
meridian/scripts/publish_meta_review_to_github.py
→ meridian-core/scripts/publish_meta_review_to_github.py
```

**Steps:**
1. Copy script to meridian-core
2. Update imports to use meridian-core orchestrator
3. Update repo defaults (make configurable)
4. Test with meridian-core meta-review
5. Test with different repos (meridian-trading, meridian-research)
6. Add to meridian-core documentation
7. Add to CI/CD examples

**Testing:**
- Test dry-run mode
- Test issue creation
- Test with different severities
- Test token validation
- Test with different repos

---

### Phase 3: Archive meridian (After Migration)

**Steps:**
1. ✅ Verify MCP servers migrated and working
2. ✅ Verify GitHub publishing migrated and working
3. ✅ Update all documentation to reference meridian-core
4. ✅ Create archive branch in meridian repo
5. ✅ Add README_ARCHIVED.md explaining migration
6. ✅ Update MERIDIAN-REPO-ARCHITECTURE.md
7. ✅ Mark repo as archived in GitHub

**Archive Message:**
```
This repo has been archived. Key features have been migrated:

- MCP Servers → meridian-core/src/meridian_core/connectors/mcp/
- GitHub Issue Publishing → meridian-core/scripts/publish_meta_review_to_github.py
- Trading System → meridian-trading (separate repo)
- Orchestrator → meridian-core (separate repo)

For active development, use:
- meridian-core (orchestration framework)
- meridian-trading (trading system)
- meridian-research (research system)
```

---

## 📝 Detailed Feature Descriptions

### MCP Server: Multi-AI Collaboration

**File:** `server.py`

**Capabilities:**
- `write_analysis()` - Write analysis to shared workspace
- `read_analysis()` - Read analysis from workspace
- `list_analyses()` - List all analyses with metadata
- `ask_grok()` - Query Grok AI directly
- `create_task()` - Create tasks for AIs to work on
- `update_shared_context()` - Update shared knowledge base

**Use Cases:**
- Claude Code can write analysis that Continue.dev can read
- Grok can query other AIs
- Shared context between different AI tools
- Task handoff between AI assistants

**Why Valuable:**
- Enables true multi-AI collaboration
- Standard protocol (MCP) for AI tool integration
- Works with Claude Code, Continue.dev, Grok
- Future-proof (MCP is emerging standard)

---

### MCP Server: Secure LocalExec

**File:** `server_localexec.py`

**Capabilities:**
- `run_code()` - Execute code in secure sandbox
- `get_execution_status()` - Check execution status
- `list_recent_executions()` - Audit log access

**Security Features:**
- RestrictedPython sandbox for Python
- Resource limits (CPU, memory, time)
- Input validation
- API key authentication
- Audit logging

**Why Valuable:**
- Secure local code execution via MCP
- Can be used by any AI tool that supports MCP
- Better than direct subprocess calls
- Audit trail for security

**Note:** meridian-core has `server_localexec.py` but this version may be more complete.

---

### MCP Server: LM Studio Integration

**File:** `server_lmstudio.py`

**Capabilities:**
- Integration with LM Studio local LLM server
- MCP protocol for local LLM access

**Why Valuable:**
- Enables local LLM access via MCP
- Works with AI tools that support MCP
- Standard interface for local LLMs

---

### GitHub Issue Publishing

**File:** `publish_meta_review_to_github.py`

**Capabilities:**
- Runs meta-review via orchestrator
- Filters findings by severity
- Creates GitHub issues automatically
- Supports dry-run mode
- Token validation and repo access checks
- Configurable labels and scopes

**Use Cases:**
- Automated issue creation from code reviews
- CI/CD integration
- Quality assurance automation
- Track review findings as issues

**Why Valuable:**
- Automates issue tracking
- Integrates review findings with GitHub workflow
- Can be used by all repos
- Supports CI/CD pipelines

---

## ✅ Final Recommendations

### Migrate (High Priority):
1. ✅ **MCP Server Suite** → `meridian-core/src/meridian_core/connectors/mcp/`
   - Value: HIGH
   - Effort: Medium (2-3 days)
   - Benefit: Enables AI tool integration for all repos

2. ✅ **GitHub Issue Publishing** → `meridian-core/scripts/`
   - Value: MEDIUM
   - Effort: Low (1 day)
   - Benefit: Automated issue tracking for all repos

### Archive (Don't Migrate):
1. ❌ **Embedded Trading System** → Already in meridian-trading
2. ❌ **Embedded Orchestrator** → Already in meridian-core
3. ❌ **LocalExec Connector** → Already in meridian-core (may need enhancement)
4. ❌ **Honesty Framework** → Already in meridian-core

---

## 📅 Timeline

**Week 1:**
- Day 1-2: Migrate MCP servers
- Day 3: Test MCP servers with AI tools
- Day 4: Migrate GitHub publishing script
- Day 5: Test GitHub publishing, update docs

**Week 2:**
- Day 1: Final testing and verification
- Day 2: Update all documentation
- Day 3: Archive meridian repo
- Day 4-5: Buffer for issues

---

## 🔍 Verification Checklist

Before archiving, verify:

- [ ] MCP servers work with Claude Code
- [ ] MCP servers work with Continue.dev
- [ ] MCP servers work with Grok
- [ ] GitHub publishing works with meridian-core
- [ ] GitHub publishing works with meridian-trading
- [ ] GitHub publishing works with meridian-research
- [ ] All documentation updated
- [ ] MERIDIAN-REPO-ARCHITECTURE.md updated
- [ ] All repos reference meridian-core (not meridian)
- [ ] Archive message added to meridian repo

---

**Last Updated:** 2025-11-19  
**Status:** Ready for Migration  
**Next Step:** Begin Phase 1 (MCP Server Migration)



