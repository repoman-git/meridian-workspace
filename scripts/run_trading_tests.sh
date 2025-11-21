#!/usr/bin/env bash
#
# Convenience wrapper to run meridian-trading pytest suite with the same
# environment variables recommended by prepare_test_env.sh.
#
# Usage:
#   ./scripts/run_trading_tests.sh
#   WORKSPACE=/custom/path ./scripts/run_trading_tests.sh
#

set -euo pipefail

WORKSPACE="${WORKSPACE:-$HOME/Data-Projects}"
TRADING_DIR="${TRADING_DIR:-$WORKSPACE/meridian-trading}"
CORE_DIR="${CORE_DIR:-$WORKSPACE/meridian-core}"
TMP_DIR="${TMP_DIR:-$WORKSPACE/.tmp}"

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

[[ -d "$TRADING_DIR" ]] || die "Cannot find meridian-trading at $TRADING_DIR"
[[ -d "$CORE_DIR" ]] || die "Cannot find meridian-core at $CORE_DIR"
[[ -f "$TRADING_DIR/.env.testing" ]] || die "Missing $TRADING_DIR/.env.testing. Run scripts/prepare_test_env.sh first."
[[ -d "$TRADING_DIR/.venv" ]] || die "Missing virtualenv at $TRADING_DIR/.venv. Create it before running."

mkdir -p "$TMP_DIR"

info "Activating virtualenv"
pushd "$TRADING_DIR" >/dev/null

# shellcheck disable=SC1091
source .venv/bin/activate

info "Exporting testing environment variables"
set -a
source .env.testing
export PROJECT_ROOT="$CORE_DIR"
export MERIDIAN_DISABLE_CREDENTIAL_MANAGER=1
export MERIDIAN_DISABLE_RISK_PERSISTENCE=1
export MERIDIAN_CREDENTIAL_DIR="$TRADING_DIR/.meridian"
export ALLOW_ENV_FALLBACK=1
export MERIDIAN_TEST_TASK_QUEUE="$TRADING_DIR/TASK-QUEUE.json"
export MERIDIAN_TEST_AI_REGISTRY="$TRADING_DIR/ai_registry.json"
export TMPDIR="$TMP_DIR"
set +a

info "Running pytest (full suite)"
if ! pytest -q "$@"; then
  warn "pytest reported failures."
  deactivate || true
  popd >/dev/null
  exit 1
fi

info "pytest completed successfully"
deactivate || true
popd >/dev/null

