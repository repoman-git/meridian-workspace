#!/usr/bin/env bash
#
# Laptop swap automation script for Meridian development environments.
# This script bootstraps macOS tooling, clones repositories, prepares Python
# environments, and syncs shared Meridian Ops assets.
#
# Usage:
#   chmod +x laptopswap.sh
#   ./laptopswap.sh
#
# Environment overrides:
#   PYTHON_VERSION=3.11.8 ./laptopswap.sh
#   WORKSPACE="$HOME/Data-Projects" ./laptopswap.sh
#

set -euo pipefail

PYTHON_VERSION="${PYTHON_VERSION:-3.11.8}"
WORKSPACE="${WORKSPACE:-$HOME/Data-Projects}"
BREW_PACKAGES=(git python@3.11 pyenv pipx jq ripgrep fd wget tree)
REPOS=(
  "git@github.com:repoman-git/meridian-core.git|meridian-core"
  "git@github.com:repoman-git/meridian-trading.git|meridian-trading"
  "git@github.com:repoman-git/meridian-research.git|meridian-research"
  "git@github.com:repoman-git/meridian-core-operations.git|Meridian-Core-Operations"
)

info() {
  printf "\033[1;34m[INFO]\033[0m %s\n" "$*"
}

warn() {
  printf "\033[1;33m[WARN]\033[0m %s\n" "$*" >&2
}

step() {
  printf "\n\033[1;32m==> %s\033[0m\n" "$*"
}

ensure_xcode_tools() {
  step "Verifying Xcode Command Line Tools"
  if xcode-select -p &>/dev/null; then
    info "Xcode CLTs already installed."
  else
    info "Installing Xcode CLTs (GUI prompt will appear)..."
    xcode-select --install || warn "Run xcode-select --install manually if prompt failed."
    until xcode-select -p &>/dev/null; do
      sleep 5
      info "Waiting for Xcode CLT installation to finish..."
    done
  fi
}

ensure_homebrew() {
  step "Ensuring Homebrew is installed"
  if ! command -v brew &>/dev/null; then
    info "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [[ -d /opt/homebrew/bin ]]; then
      echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> "$HOME/.zprofile"
      eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
  else
    info "Homebrew already installed; running brew update."
    brew update
  fi
}

install_brew_packages() {
  step "Installing baseline Brew packages"
  for pkg in "${BREW_PACKAGES[@]}"; do
    if brew list "$pkg" &>/dev/null; then
      info "Package $pkg already installed."
    else
      brew install "$pkg"
    fi
  done
}

setup_python_toolchain() {
  step "Configuring Python toolchain"
  if command -v pyenv &>/dev/null; then
    if ! pyenv versions --bare | grep -qx "$PYTHON_VERSION"; then
      info "Installing Python $PYTHON_VERSION via pyenv"
      pyenv install "$PYTHON_VERSION"
    fi
    pyenv global "$PYTHON_VERSION"
  else
    warn "pyenv missing; relying on system python3."
  fi
  if command -v pipx &>/dev/null; then
    pipx ensurepath
  fi
}

setup_git_defaults() {
  step "Configuring Git defaults"
  git config --global credential.helper osxkeychain || true
  git config --global pull.rebase false
  git config --global init.defaultBranch main
  info "Git user.name currently: $(git config --global user.name || echo 'unset')"
  info "Git user.email currently: $(git config --global user.email || echo 'unset')"
}

ensure_workspace() {
  step "Preparing workspace directory at $WORKSPACE"
  mkdir -p "$WORKSPACE"
}

clone_repositories() {
  step "Cloning Meridian repositories"
  for entry in "${REPOS[@]}"; do
    IFS="|" read -r repo target <<<"$entry"
    dest="$WORKSPACE/$target"
    if [[ -d "$dest/.git" ]]; then
      info "Repo $target already exists; pulling latest."
      if ! env GIT_TERMINAL_PROMPT=0 git -C "$dest" pull --ff-only; then
        warn "Could not fast-forward $target (likely due to missing credentials). Skipping pull."
      fi
    else
      if ! env GIT_TERMINAL_PROMPT=0 git clone "$repo" "$dest"; then
        warn "Failed to clone $repo (credential or network issue). Resolve manually and rerun."
      fi
    fi
  done
}

bootstrap_repo() {
  local path="$1"
  local repo_name
  repo_name="$(basename "$path")"
  step "Bootstrapping Python environment for $repo_name"
  cd "$path"

  if [[ ! -d .venv ]]; then
    python3 -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip setuptools wheel
  if [[ "$repo_name" != "meridian-core" ]]; then
    if [[ -d "$WORKSPACE/meridian-core" ]]; then
      info "Installing local meridian-core dependency into $repo_name environment"
      pip install -e "$WORKSPACE/meridian-core"
    else
      warn "meridian-core repository not found at $WORKSPACE/meridian-core; skipping local core install for $repo_name"
    fi
  fi
  if ! pip install -e ".[dev]"; then
    warn "Falling back to pip install -e . for $repo_name"
    pip install -e .
  fi
  deactivate
}

bootstrap_all_repos() {
  step "Installing repo-specific dependencies"
  for entry in "${REPOS[@]}"; do
    IFS="|" read -r _ target <<<"$entry"
    bootstrap_repo "$WORKSPACE/$target"
  done
}

ensure_env_file() {
  local repo="$1"
  local env_path="$repo/.env"
  if [[ -f "$env_path" ]]; then
    info ".env already exists in $(basename "$repo")."
  else
    warn "Creating placeholder .env in $(basename "$repo"). Fill in API keys manually."
    cat <<'EOF' > "$env_path"
# Meridian API keys - replace with real values
ANTHROPIC_API_KEY=replace_me
OPENAI_API_KEY=replace_me
GOOGLE_GEMINI_API_KEY=replace_me
GROK_API_KEY=replace_me
EOF
  fi
}

create_env_files() {
  step "Ensuring .env files exist"
  for repo in meridian-core meridian-trading meridian-research; do
    ensure_env_file "$WORKSPACE/$repo"
  done
}

install_meridian_ops_cli() {
  step "Installing meridian-ops CLI"
  cd "$WORKSPACE/Meridian-Core-Operations"
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -e .
  deactivate
}

sync_ops_assets() {
  step "Syncing Meridian Ops assets into repos"
  local cli="$WORKSPACE/Meridian-Core-Operations/.venv/bin/meridian-ops"
  if [[ ! -x "$cli" ]]; then
    warn "meridian-ops CLI not found; reinstalling."
    install_meridian_ops_cli
  fi
  for repo in meridian-core meridian-trading meridian-research; do
    "$cli" sync --target "$WORKSPACE/$repo" --include-learning || warn "Ops sync failed for $repo"
  done
}

run_repo_tests() {
  step "Running pytest smoke checks"
  for entry in "${REPOS[@]}"; do
    IFS="|" read -r _ target <<<"$entry"
    cd "$WORKSPACE/$target"
    if [[ -d .venv ]]; then
      # shellcheck disable=SC1091
      source .venv/bin/activate
      test_env=()
      if [[ "$target" == "meridian-trading" ]]; then
        cred_dir="$WORKSPACE/$target/.meridian"
        test_env+=("MERIDIAN_DISABLE_CREDENTIAL_MANAGER=1")
        test_env+=("MERIDIAN_CREDENTIAL_DIR=$cred_dir")
        test_env+=("ALLOW_ENV_FALLBACK=1")
        test_env+=("IG_USERNAME=dummy_user")
        test_env+=("IG_PASSWORD=dummy_pass")
        test_env+=("IG_API_KEY=dummy_key")
        test_env+=("GROK_API_KEY=dummy_key")
        test_env+=("GOOGLE_GEMINI_API_KEY=dummy_key")
        test_env+=("ANTHROPIC_API_KEY=dummy_key")
        test_env+=("OPENAI_API_KEY=dummy_key")
      fi
      if [[ ${#test_env[@]} -gt 0 ]]; then
        if ! env "${test_env[@]}" pytest -q; then
          warn "Tests failed in $target. Investigate manually."
        fi
      else
        if ! pytest -q; then
        warn "Tests failed in $target. Investigate manually."
      fi
      fi
      deactivate
    else
      warn "Missing .venv in $target; skipping tests."
    fi
  done
}

main() {
  ensure_xcode_tools
  ensure_homebrew
  install_brew_packages
  setup_python_toolchain
  setup_git_defaults
  ensure_workspace
  clone_repositories
  bootstrap_all_repos
  create_env_files
  install_meridian_ops_cli
  sync_ops_assets
  run_repo_tests

  step "Setup complete!"
  info "Review repo-specific README files for any manual steps."
}

main "$@"

