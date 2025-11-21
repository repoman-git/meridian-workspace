#!/bin/bash
# Workspace Management System - Session End Script
# Run this at the end of every coding session to finalize and document work

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get workspace root
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

echo ""
echo "======================================================================"
echo "  WORKSPACE MANAGEMENT SYSTEM - SESSION END"
echo "======================================================================"
echo ""
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. GET CURRENT SESSION
echo "──────────────────────────────────────────────────────────────────────"
echo "1. GETTING CURRENT SESSION"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

CURRENT_SESSION_ID=""
CURRENT_CONTEXT=""

if [ -f ".workspace-context" ]; then
    CURRENT_CONTEXT=$(head -n 1 .workspace-context 2>/dev/null || echo "")
    echo -e "${CYAN}Current context: ${BOLD}$CURRENT_CONTEXT${NC}"
else
    echo -e "${YELLOW}⚠️  No active context found${NC}"
fi

echo ""

# Get or create session ID
SESSION_ID=$(run_python -c "
import sys
from pathlib import Path
from datetime import datetime, timedelta
sys.path.insert(0, '$WORKSPACE_ROOT')

try:
    from workspace.db import WorkspaceDB
    from workspace.db.models import WorkspaceSession
    from sqlalchemy import desc
    
    workspace_root = Path('$WORKSPACE_ROOT')
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        # Get in-progress session or most recent
        current = session.query(WorkspaceSession).filter_by(status='in_progress').first()
        if not current:
            current = session.query(WorkspaceSession).order_by(desc(WorkspaceSession.start_time)).first()
        
        if current:
            print(current.id)
        else:
            # Create new session
            session_id = f'session-{datetime.now().strftime(\"%Y%m%d-%H%M%S\")}'
            ws_session = WorkspaceSession(
                id=session_id,
                start_time=datetime.now() - timedelta(hours=4),
                status='in_progress',
                user='simonerses',
                ai_assistant='claude-code'
            )
            session.add(ws_session)
            session.commit()
            print(session_id)
    finally:
        session.close()
except:
    print('session-$(date +%Y%m%d-%H%M%S)', end='')
" 2>/dev/null | head -1)

if [ -z "$SESSION_ID" ]; then
    SESSION_ID="session-$(date '+%Y%m%d-%H%M%S')"
    echo -e "${YELLOW}⚠️  Could not get session from database, using: $SESSION_ID${NC}"
else
    echo -e "${GREEN}✅ Session ID: $SESSION_ID${NC}"
fi

echo ""

# 2. SESSION SUMMARY
echo "──────────────────────────────────────────────────────────────────────"
echo "2. SESSION SUMMARY"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

# Get session statistics
run_python -c "
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, '$WORKSPACE_ROOT')

try:
    from workspace.db import WorkspaceDB
    from workspace.db.models import WorkspaceTask, CrossRepoIssue, WorkContext
    
    workspace_root = Path('$WORKSPACE_ROOT')
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        # Get current context
        current_context = session.query(WorkContext).filter_by(is_active=True).first()
        
        # Get task statistics
        total_tasks = session.query(WorkspaceTask).count()
        pending_tasks = session.query(WorkspaceTask).filter_by(status='pending').count()
        in_progress_tasks = session.query(WorkspaceTask).filter_by(status='in_progress').count()
        completed_tasks = session.query(WorkspaceTask).filter_by(status='completed').count()
        
        # Get recent tasks (created today)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_tasks = session.query(WorkspaceTask).filter(
            WorkspaceTask.created >= today_start
        ).all()
        
        # Get open issues
        open_issues = session.query(CrossRepoIssue).filter_by(status='open').count()
        
        print(f'📊 Current State:')
        print(f'   • Total tasks: {total_tasks}')
        print(f'   • Pending: {pending_tasks}')
        print(f'   • In Progress: {in_progress_tasks}')
        print(f'   • Completed: {completed_tasks}')
        print(f'   • Open issues: {open_issues}')
        print()
        
        if current_context:
            print(f'🎯 Active Context: {current_context.repo}')
            if current_context.notes:
                print(f'   Notes: {current_context.notes}')
            print()
        
        if recent_tasks:
            print(f'📋 Recent tasks created today: {len(recent_tasks)}')
            for task in recent_tasks[:5]:
                print(f'   • {task.id}: {task.title[:60]}... ({task.status})')
            if len(recent_tasks) > 5:
                print(f'   ... and {len(recent_tasks) - 5} more')
            print()
    finally:
        session.close()
except Exception as e:
    print(f'Error: {e}')
" 2>&1 | head -30

# 3. CREATE SESSION HANDOVER
echo "──────────────────────────────────────────────────────────────────────"
echo "3. CREATING SESSION HANDOVER"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

echo "Creating comprehensive session handover..."

if run_python workspace/scripts/create_session_handover.py --session-id "$SESSION_ID" --user "simonerses" --ai-assistant "claude-code" 2>&1 | tail -20; then
    echo -e "${GREEN}✅ Session handover created${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Failed to create session handover${NC}"
fi

echo ""

# 4. VERIFY CLEAN WORKING TREES
echo "──────────────────────────────────────────────────────────────────────"
echo "4. VERIFYING CLEAN WORKING TREES"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

ALL_CLEAN=true
for repo in meridian-core meridian-trading meridian-research; do
    if [ -d "$repo" ] && [ -d "$repo/.git" ]; then
        cd "$repo"
        if [ -z "$(git status --porcelain)" ]; then
            echo -e "${GREEN}✅ $repo: Clean${NC}"
        else
            echo -e "${YELLOW}⚠️  $repo: Has uncommitted changes${NC}"
            git status --short | head -5
            ALL_CLEAN=false
        fi
        cd ..
    fi
done

echo ""

if [ "$ALL_CLEAN" = true ]; then
    echo -e "${GREEN}✅ All repositories have clean working trees${NC}"
else
    echo -e "${YELLOW}⚠️  Some repositories have uncommitted changes${NC}"
    echo "   Consider running: python workspace/scripts/commit_all_repos.py"
fi

echo ""

# 5. SESSION END SUMMARY
echo "──────────────────────────────────────────────────────────────────────"
echo "5. SESSION END SUMMARY"
echo "──────────────────────────────────────────────────────────────────────"
echo ""

echo -e "${GREEN}✅ Session ended successfully${NC}"
echo ""
echo -e "${BOLD}Session ID:${NC} $SESSION_ID"
echo -e "${BOLD}End Time:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

if [ -n "$CURRENT_CONTEXT" ]; then
    echo -e "${BOLD}Active Context:${NC} $CURRENT_CONTEXT"
    echo ""
fi

echo -e "${BOLD}Next Steps:${NC}"
echo "  1. Review session handover: Check SESSION-HANDOVER-*.md"
echo "  2. Review tasks: Check database for pending tasks"
echo "  3. Next session: Run ./session_start.sh to begin"
echo ""

echo "======================================================================"
echo ""
echo -e "${GREEN}✅ Session complete!${NC}"
echo ""

