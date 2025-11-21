#!/usr/bin/env bash
#
# Prepare the Meridian workspace on a new laptop so unit tests run without
# interactive credential prompts or path mismatches.
#
# This script:
#   1. Ensures the legacy /Users/$USER/Data-Projects symlink exists (for older
#      hard-coded paths inside tests and docs)
#   2. Copies the canonical TASK-QUEUE.json and ai_registry.json from
#      meridian-core into meridian-trading (tests expect them in that repo root)
#   3. Creates deterministic .env.testing files with dummy keys
#   4. Prints the environment variables you should export before running pytest
#
# Usage:
#   ./scripts/prepare_test_env.sh              # assumes ~/Data-Projects
#   WORKSPACE=/custom/path ./scripts/prepare_test_env.sh
#

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/Data-Projects}"
CORE_DIR="${CORE_DIR:-$WORKSPACE/meridian-core}"
TRADING_DIR="${TRADING_DIR:-$WORKSPACE/meridian-trading}"
RESEARCH_DIR="${RESEARCH_DIR:-$WORKSPACE/meridian-research}"
OPS_DIR="${OPS_DIR:-$WORKSPACE/Meridian-Core-Operations}"

info() {
  printf "\033[1;34m[INFO]\033[0m %s\n" "$*"
}

warn() {
  printf "\033[1;33m[WARN]\033[0m %s\n" "$*" >&2
}

die() {
  printf "\033[1;31m[ERROR]\033[0m %s\n" "$*" >&2
  exit 1
}

require_dir() {
  local path="$1"
  local label="$2"
  if [[ ! -d "$path" ]]; then
    die "$label directory not found at $path. Set WORKSPACE/CORE_DIR/etc. before running."
  fi
}

ensure_legacy_symlink() {
  local legacy="/Users/$USER/Data-Projects"
  if [[ -d "$legacy" ]]; then
    info "Legacy path $legacy already exists."
    return
  fi

  info "Creating legacy symlink $legacy -> $WORKSPACE (required by older scripts/tests)"
  sudo ln -s "$WORKSPACE" "$legacy"
}

copy_shared_assets() {
  info "Copying shared TASK-QUEUE.json and ai_registry.json into meridian-trading"

  local src_queue="$CORE_DIR/task-queue.json"
  local src_registry="$CORE_DIR/ai_registry.json"

  [[ -f "$src_queue" ]] || die "Cannot find $src_queue"
  [[ -f "$src_registry" ]] || die "Cannot find $src_registry"

  cp "$src_queue" "$TRADING_DIR/TASK-QUEUE.json"
  cp "$src_registry" "$TRADING_DIR/ai_registry.json"

  info "  ✓ Copied TASK-QUEUE.json"
  info "  ✓ Copied ai_registry.json"
}

write_testing_env() {
  local target="$1"
  local name="$2"

  cat <<'EOF' > "$target"
# Dummy credentials for local testing (do NOT use in production)
ANTHROPIC_API_KEY=dummy-anthropic
OPENAI_API_KEY=dummy-openai
GOOGLE_GEMINI_API_KEY=dummy-gemini
GROK_API_KEY=dummy-grok
IG_USERNAME=dummy-user
IG_PASSWORD=dummy-pass
IG_API_KEY=dummy-key
IG_ACC_TYPE=DEMO
ACCOUNT_BALANCE=50000
RISK_PER_TRADE=0.02
MAX_PORTFOLIO_RISK=0.06
EOF

  info "Wrote $name testing .env with dummy keys: $target"
}

write_env_files() {
  info "Creating .env.testing files with placeholder keys"
  write_testing_env "$TRADING_DIR/.env.testing" "meridian-trading"
  write_testing_env "$RESEARCH_DIR/.env.testing" "meridian-research"
}

print_env_exports() {
  local local_tmp="$1"
  cat <<EOF

================= NEXT STEPS =================
Before running pytest, export these variables so tests skip keychain/persistence:

export PROJECT_ROOT="$CORE_DIR"
export MERIDIAN_DISABLE_CREDENTIAL_MANAGER=1
export MERIDIAN_DISABLE_RISK_PERSISTENCE=1
export MERIDIAN_CREDENTIAL_DIR="$TRADING_DIR/.meridian"
export ALLOW_ENV_FALLBACK=1
export IG_USERNAME=dummy-user
export IG_PASSWORD=dummy-pass
export IG_API_KEY=dummy-key
export GROK_API_KEY=dummy-grok
export GOOGLE_GEMINI_API_KEY=dummy-gemini
export ANTHROPIC_API_KEY=dummy-anthropic
export OPENAI_API_KEY=dummy-openai
export MERIDIAN_TEST_TASK_QUEUE="$TRADING_DIR/TASK-QUEUE.json"
export MERIDIAN_TEST_AI_REGISTRY="$TRADING_DIR/ai_registry.json"
export TMPDIR="$local_tmp"

Then run tests, e.g.:

cd "$TRADING_DIR"
source .venv/bin/activate
set -a; source .env.testing; set +a
pytest -q
==============================================
EOF
}

main() {
  require_dir "$WORKSPACE" "Workspace"
  require_dir "$CORE_DIR" "meridian-core"
  require_dir "$TRADING_DIR" "meridian-trading"
  require_dir "$RESEARCH_DIR" "meridian-research"
  require_dir "$OPS_DIR" "Meridian-Core-Operations"

  ensure_legacy_symlink
  copy_shared_assets
  write_env_files
  local tmpdir="$WORKSPACE/.tmp"
  mkdir -p "$tmpdir"
  print_env_exports "$tmpdir"
}

main "$@"

