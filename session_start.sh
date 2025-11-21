#!/bin/bash
# Workspace Management System - Session Start Script
# Run this before every coding session to enforce governance and set work context

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Args and flags
AUTO_ACK=${SESSION_ACKNOWLEDGE:-0}
SKIP_CONTEXT=${SESSION_SKIP_CONTEXT:-0}

for arg in "$@"; do
    case "$arg" in
        --auto-ack|--non-interactive-ack)
            AUTO_ACK=1
            shift
            ;;
        --skip-context)
            SKIP_CONTEXT=1
            shift
            ;;
    esac
done

echo ""
echo "======================================================================"
echo "  WORKSPACE MANAGEMENT SYSTEM - SESSION START"
echo "======================================================================"
echo ""
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Session ID: $(date '+%Y%m%d_%H%M%S')"
echo ""

# Get workspace root (parent of this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$SCRIPT_DIR"
cd "$WORKSPACE_ROOT"

run_python() {
    if command -v python3 >/dev/null 2>&1; then
        python3 "$@"
    else
        echo -e "${RED}❌ python3 not available${NC}" >&2
        return 1
    fi
}

# Check if WMS is available
check_wms() {
    if [ ! -f "workspace/db/workspace_db.py" ]; then
        echo -e "${RED}❌ WMS not found. Make sure you're in the workspace root directory.${NC}"
        echo "   Expected: workspace/db/workspace_db.py"
        return 1
    fi
    return 0
}

# 1. WMS CHECK
echo "──────────────────────────────────────────────────────────────────────"
echo "1. WMS AVAILABILITY CHECK"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

if ! check_wms; then
    exit 1
fi

echo -e "${GREEN}✅ WMS found${NC}"
echo ""

# 2. WORK CONTEXT CONFIRMATION
echo "──────────────────────────────────────────────────────────────────────"
echo "2. WORK CONTEXT CONFIRMATION"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

VALID_REPOS=("workspace" "meridian-core" "meridian-research" "meridian-trading")
SELECTED_REPO=""

if [ "$SKIP_CONTEXT" -eq 1 ]; then
    echo -e "${YELLOW}⚠️  Context confirmation skipped (--skip-context)${NC}"
    echo ""
else
    # Get current context if any
    CURRENT_CONTEXT=""
    if [ -f ".workspace-context" ]; then
        CURRENT_REPO=$(head -n 1 .workspace-context 2>/dev/null || echo "")
        if [ -n "$CURRENT_REPO" ]; then
            CURRENT_CONTEXT="$CURRENT_REPO"
            echo -e "${CYAN}Current context: ${BOLD}$CURRENT_CONTEXT${NC}"
            echo ""
        fi
    fi
    
    echo -e "${BOLD}Which repository will you be working in for this session?${NC}"
    echo ""
    echo "  ${GREEN}1)${NC} workspace (WMS - management plane)"
    echo "  ${GREEN}2)${NC} meridian-core (framework - generic)"
    echo "  ${GREEN}3)${NC} meridian-research (domain adapter - research)"
    echo "  ${GREEN}4)${NC} meridian-trading (domain adapter - trading)"
    echo ""
    
    if [ "$AUTO_ACK" -eq 1 ]; then
        # Auto mode: use current context or default to workspace
        if [ -n "$CURRENT_CONTEXT" ]; then
            SELECTED_REPO="$CURRENT_CONTEXT"
            echo -e "${YELLOW}Auto-mode: Using current context: $SELECTED_REPO${NC}"
        else
            SELECTED_REPO="workspace"
            echo -e "${YELLOW}Auto-mode: Defaulting to workspace${NC}"
        fi
    else
        # Interactive mode
        read -p "Enter choice (1-4) or repository name: " choice
        
        case "$choice" in
            1)
                SELECTED_REPO="workspace"
                ;;
            2)
                SELECTED_REPO="meridian-core"
                ;;
            3)
                SELECTED_REPO="meridian-research"
                ;;
            4)
                SELECTED_REPO="meridian-trading"
                ;;
            *)
                # Check if it's a valid repo name
                if [[ " ${VALID_REPOS[@]} " =~ " ${choice} " ]]; then
                    SELECTED_REPO="$choice"
                else
                    echo -e "${RED}❌ Invalid repository: $choice${NC}"
                    echo "   Valid repositories: ${VALID_REPOS[*]}"
                    exit 1
                fi
                ;;
        esac
    fi
    
    # Verify repository exists
    if [ ! -d "$SELECTED_REPO" ]; then
        echo -e "${RED}❌ Repository directory not found: $SELECTED_REPO${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${CYAN}Selected repository: ${BOLD}$SELECTED_REPO${NC}"
    echo ""
    
    # Optional notes
    NOTES=""
    if [ "$AUTO_ACK" -eq 0 ]; then
        read -p "Optional: What are you working on? (press Enter to skip): " NOTES
    fi
    
    # Set context via WMS
    echo "Setting work context via WMS..."
    NOTES_ESCAPED=$(printf '%s\n' "$NOTES" | sed "s/'/'\"'\"'/g")
    if run_python - <<PY
import sys
from pathlib import Path
sys.path.insert(0, str(Path("$WORKSPACE_ROOT").resolve()))

from workspace.db import WorkspaceDB
from workspace.wms.context_manager import ContextManager

workspace_root = Path("$WORKSPACE_ROOT").resolve()
db = WorkspaceDB(workspace_root=workspace_root)
session = db._get_session()

try:
    context_manager = ContextManager(workspace_root, session)
    notes = "$NOTES_ESCAPED" if "$NOTES_ESCAPED" else None
    context = context_manager.set_context("$SELECTED_REPO", notes)
    print(f"Context ID: {context.id}")
finally:
    session.close()
PY
    then
        echo -e "${GREEN}✅ Work context set: $SELECTED_REPO${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Failed to set context in database (continuing anyway)${NC}"
    fi
    echo ""
fi

# 3. GOVERNANCE ENFORCEMENT
echo "──────────────────────────────────────────────────────────────────────"
echo "3. GOVERNANCE ENFORCEMENT"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

echo "Generating GOVERNANCE-CONTEXT.md..."

if run_python workspace/scripts/generate_governance_context.py --repo "${SELECTED_REPO:-workspace}" --notes "${NOTES:-}" --output "GOVERNANCE-CONTEXT.md" 2>&1; then
    echo -e "${GREEN}✅ GOVERNANCE-CONTEXT.md generated${NC}"
    echo ""
    echo -e "${CYAN}⚠️  CRITICAL: This file is auto-injected into every AI interaction${NC}"
    echo -e "${CYAN}⚠️  AI agents MUST follow these rules without exception${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠️  Warning: Failed to generate GOVERNANCE-CONTEXT.md${NC}"
    echo "   You may need to create it manually or check WMS setup"
    echo ""
fi

# 4. PRE-TASK CHECKLIST ENFORCEMENT
echo "──────────────────────────────────────────────────────────────────────"
echo "4. PRE-TASK CHECKLIST ENFORCEMENT"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

CHECKLIST_ITEMS=(
    "Read ADR-001-COMPONENT-PLACEMENT.md"
    "Read AI-GUIDELINES.md (relevant sections)"
    "Consult ARCHITECTURE-DOCS-INDEX.md for doc locations"
    "Check WORKSPACE-TASKS.json for context"
    "Check CROSS-REPO-ISSUES.json for known issues"
    "Verify component placement (core vs domain adapter)"
    "Check for similar work in other repos"
    "Create a plan before writing code"
    "Document decision rationale"
)

echo -e "${BOLD}Pre-Task Governance Checklist:${NC}"
echo ""
echo -e "${YELLOW}BEFORE WRITING ANY CODE, AI AGENTS MUST:${NC}"
echo ""

for item in "${CHECKLIST_ITEMS[@]}"; do
    echo -e "  ${GREEN}☐${NC} $item"
done

echo ""
echo -e "${CYAN}⚠️  This checklist is MANDATORY and ENFORCED${NC}"
echo -e "${CYAN}⚠️  Violations will be logged and may block commits${NC}"
echo ""

if [ "$AUTO_ACK" -eq 0 ]; then
    read -p "Press Enter to acknowledge and continue..."
    echo ""
fi

# 5. ARCHITECTURE ALIGNMENT ENFORCEMENT
echo "──────────────────────────────────────────────────────────────────────"
echo "5. ARCHITECTURE ALIGNMENT ENFORCEMENT"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

echo -e "${CYAN}⚠️  CODE-TO-ARCHITECTURE ALIGNMENT REQUIRED${NC}"
echo ""
echo "Before making ANY code changes:"
echo "  1. ✅ Files must be mapped to architecture components"
echo "  2. ✅ Changes must be within component scope"
echo "  3. ✅ Tasks must link files to components"
echo "  4. ✅ No unregistered files allowed"
echo ""
echo -e "${YELLOW}Violations will block commits and deployments.${NC}"
echo ""

# Check for unregistered files in current context
if [ -n "$SELECTED_REPO" ] && [ -d "$SELECTED_REPO" ]; then
    echo "Checking for unregistered files in $SELECTED_REPO..."
    if run_python - <<PY 2>&1 | head -20
import sys
from pathlib import Path
sys.path.insert(0, str(Path("$WORKSPACE_ROOT").resolve()))

from workspace.db import WorkspaceDB
from workspace.wms.architecture_validator import ArchitectureValidator

workspace_root = Path("$WORKSPACE_ROOT").resolve()
db = WorkspaceDB(workspace_root=workspace_root)
session = db._get_session()

try:
    validator = ArchitectureValidator(session, workspace_root)
    unregistered = validator.get_unregistered_files(repo="$SELECTED_REPO")
    
    if unregistered:
        print(f"⚠️  Found {len(unregistered)} unregistered file(s) in $SELECTED_REPO:")
        for uf in unregistered[:10]:
            print(f"  • {uf.file_path}")
        if len(unregistered) > 10:
            print(f"  ... and {len(unregistered) - 10} more")
        print("")
        print("Map files to components with:")
        print("  python workspace/wms/cli.py map-file <file> <component_id>")
    else:
        print("✅ No unregistered files found")
finally:
    session.close()
PY
    then
        echo ""
    fi
fi

echo ""

# 6. GOVERNANCE DOCUMENTS CHECK
echo "──────────────────────────────────────────────────────────────────────"
echo "6. GOVERNANCE DOCUMENTS CHECK"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

GOV_DOCS=(
    "GOVERNANCE-CONTEXT.md"
    "AI-GUIDELINES.md"
    "CROSS-REPO-ISSUES.json"
    "WORKSPACE-TASKS.json"
    "ARCHITECTURE-DECISIONS.json"
)

ALL_DOCS_OK=true
for doc in "${GOV_DOCS[@]}"; do
    # Check in workspace root
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅${NC} $doc (workspace root)"
    # Check in selected repo
    elif [ -n "$SELECTED_REPO" ] && [ -f "$SELECTED_REPO/$doc" ]; then
        echo -e "${GREEN}✅${NC} $doc ($SELECTED_REPO)"
    # Check in meridian-core (source of truth for some docs)
    elif [ -f "meridian-core/$doc" ]; then
        echo -e "${GREEN}✅${NC} $doc (meridian-core)"
    else
        echo -e "${YELLOW}⚠️${NC}  $doc (not found)"
        ALL_DOCS_OK=false
    fi
done

echo ""

if [ "$ALL_DOCS_OK" = false ]; then
    echo -e "${YELLOW}⚠️  Some governance documents are missing${NC}"
    echo "   This may affect governance enforcement"
    echo ""
fi

# 7. SESSION SUMMARY
echo "──────────────────────────────────────────────────────────────────────"
echo "7. SESSION START COMPLETE"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

echo -e "${GREEN}✅ Session started successfully${NC}"
echo ""
echo -e "${BOLD}Work Context:${NC} ${SELECTED_REPO:-not set}"
if [ -n "$NOTES" ]; then
    echo -e "${BOLD}Notes:${NC} $NOTES"
fi
echo ""
echo -e "${BOLD}Governance Status:${NC}"
echo "  • GOVERNANCE-CONTEXT.md: $(if [ -f 'GOVERNANCE-CONTEXT.md' ]; then echo -e "${GREEN}READY${NC}"; else echo -e "${YELLOW}MISSING${NC}"; fi)"
echo "  • Pre-task checklist: ${GREEN}ENFORCED${NC}"
echo "  • Component placement rules: ${GREEN}ENFORCED${NC}"
echo "  • Planning requirements: ${GREEN}ENFORCED${NC}"
echo "  • Code-to-architecture alignment: ${GREEN}ENFORCED${NC}"
echo ""
echo -e "${CYAN}📋 Remember:${NC}"
echo "  • GOVERNANCE-CONTEXT.md is auto-injected into AI prompts"
echo "  • Pre-task checklist is MANDATORY before any code changes"
echo "  • Component placement violations will be flagged"
echo "  • Files must be mapped to architecture components"
echo "  • Code changes must align with architecture design"
echo "  • Run ./session_end.sh when done"
echo ""
echo "======================================================================"
echo ""

# Export context for use in session
export WORKSPACE_CONTEXT_REPO="$SELECTED_REPO"
export WORKSPACE_CONTEXT_NOTES="$NOTES"

echo -e "${GREEN}✅ Ready to begin work!${NC}"
echo ""

