# Meridian Repos Meta-Review (2025-11-21)

Scope: meridian-core, meridian (root orchestrator), meridian-trading, meridian-research. Ground-up static review modeled after prior meta-reviews; emphasis on orchestrator correctness, cross-repo coupling, cost/ops safety. No runtime tests executed.

---

## Executive Summary
Concurrency safeguards in meridian-core’s autonomous executor are incomplete: the parallel runner can overshoot task limits and races shared counters, risking runaway task launch and unstable stop conditions. Root meridian ships a live-API validation script that hard-fails offline/CI and can incur cost. Core connectors carry a domain cross-dependency and set global logging at import, which conflicts with ADRs and host logging. Cost governance is configured conceptually (token budgets) but isn’t enforced for dollars. The codebase is well-documented and modular, but needs concurrency hardening, cost-safe testing, and cleaner repo boundaries.

---

## Method
- Readme/ADR/context: meridian-core, meridian, trading/research top-level docs.  
- Static code review of key modules: autonomous orchestrator/session runner, connectors, credential helpers, orchestration config, preflight manager, live test scripts.  
- No code execution; findings are static analysis.

---

## Strengths
- Clear separation of orchestrator components (session runner extracted from god object) and good doc headers.  
- Credential helper defaults to secure stores and disables env fallback unless explicitly enabled.  
- Preflight/voting/smart allocation hooks are present and configurable.  
- Architecture docs and ADRs exist across repos.

---

## Critical Issues
1) Parallel task cap can overshoot (in-flight tasks ignored)  
   - File: meridian-core/src/meridian_core/orchestration/autonomous_session_runner.py:277-354  
   - Issue: Submission loop checks only completed count; in-flight tasks aren’t counted, so up to max_workers extra tasks can launch even when max_tasks=1. Runaway work/spend risk.  
   - Fix: Gate submission on `tasks_completed + len(futures_to_task) < max_tasks` (or similar) before enqueueing.

2) Shared counters mutated without synchronization in parallel mode  
   - File: meridian-core/src/meridian_core/orchestration/autonomous_session_runner.py:295-360  
   - Issue: Multiple threads update continuous_failure_count, execution_stats, tasks_since_last_learning without locks; stop conditions and learning triggers can race and misfire.  
   - Fix: Protect shared counters with a lock or encapsulate updates in thread-safe helpers.

---

## Additional Findings
3) Live API test script fails offline and can incur cost  
   - File: meridian/test_all_api_keys.py:1-190  
   - Issue: Always calls Anthropic/OpenAI/Grok/Gemini/LM Studio and treats missing keys/network as failure; CI/offline runs hard-fail and may spend money.  
   - Fix: Gate behind env flag (e.g., REQUIRE_LIVE_KEYS=1), mark integration-only, and provide safe mock/no-network path.

4) Connector sets global logging at import  
   - File: meridian-core/src/meridian_core/connectors/openai_connector.py:56  
   - Issue: `logging.basicConfig` at import time overwrites host logging config.  
   - Fix: Remove/guard; configure logging in entry points, not libraries.

5) Cross-repo coupling in core connector (violates ADR intent)  
   - Files: meridian-core/src/meridian_core/connectors/openai_connector.py:32-38, grok_connector.py (same pattern)  
   - Issue: Core optionally imports CredentialManager from meridian-trading, creating a cross-repo dependency in “core” layer. Even with try/except, it couples core to domain repo and breaks clean placement rules.  
   - Fix: Inject credential manager via interface; document dependency or move shared credential manager to a neutral package.

6) Cost governance is token-only; no dollar budget enforcement  
   - File: meridian-core/src/meridian_core/orchestration/preflight_manager.py:47-96 (available_cost_budget=None TODO)  
   - Issue: Preflight/token budgets are tracked, but cost budgets are stubbed; high-volume unattended runs could exceed spend caps.  
   - Fix: Add provider cost config and enforce available_cost_budget in preflight checks; surface refusal when spend ceiling is reached.

---

## Recommendations (Prioritized)
1) Concurrency: Fix max_tasks guard and add locking for shared counters in parallel session runner; add regression tests for max_tasks=1 with max_workers>1 and concurrent failure increments.  
2) Cost safety: Implement cost budget tracking in preflight; fail fast when spend ceiling would be exceeded.  
3) Test hygiene: Gate `test_all_api_keys.py` behind explicit env, mock by default, and mark integration.  
4) Logging hygiene: Remove import-time `basicConfig` from openai_connector; rely on entry-point logging config.  
5) Architecture hygiene: Decouple core connectors from meridian-trading CredentialManager; use injected interface or shared neutral module.

---

## Score
- Stability/Resilience: 7.0/10 (concurrency races + task cap overshoot are material).  
- Architecture/Boundaries: 7.5/10 (mostly clean, but core ↔ trading coupling remains).  
- Operational Safety: 6.5/10 (live costful tests and missing dollar budgets).

---

## Notes
- Static review only; no runtime validation or live API calls.  
- No code changes beyond this report.  
- Use this as an entry point; deeper domain-specific testing (trading/research pipelines) not covered here.
