# Laptop Swap Runbook

Document the end-to-end process for bringing a fresh macOS laptop online for Meridian development. Follow the steps in order; check off each item as you complete it.

---

## 1. Base macOS Setup

1. Sign in with Apple ID and enable Touch ID.
2. Install all pending macOS updates (`System Settings → General → Software Update`), then reboot.
3. Install Xcode command line tools (required for Git/compilers):
   ```bash
   xcode-select --install
   ```
4. Verify the tools:
   ```bash
   xcode-select -p
   gcc --version
   ```

---

## 2. Homebrew & Core CLI Utilities

1. Install Homebrew (skip if already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Add Brew to your shell profile:
   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```
3. Install baseline CLI tools:
   ```bash
   brew install git python@3.11 pyenv pipx jq ripgrep fd wget tree
   ```
4. Confirm versions (sample):
   ```bash
   git --version
   python3 --version
   pipx --version
   ```

---

## 3. Python Environment

1. Ensure the preferred Python version is on `PATH`:
   ```bash
   pyenv install 3.11.8   # or matching project version
   pyenv global 3.11.8
   ```
2. Upgrade pip/setuptools/wheel globally:
   ```bash
   python3 -m pip install --upgrade pip setuptools wheel
   ```
3. Install virtualenv tooling (pick one):
   - `pipx install pipenv`
   - `pipx install poetry`
   - or rely on `python -m venv` per repo
4. Verify you can create a venv:
   ```bash
   python3 -m venv ~/venvs/meridian && source ~/venvs/meridian/bin/activate
   deactivate
   ```

---

## 4. SSH, Git, and Credentials

1. Generate (or copy) SSH keys:
   ```bash
   ssh-keygen -t ed25519 -C "you@company.com"
   ```
2. Add the public key to GitHub (Settings → SSH keys).
3. Configure Git defaults:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@company.com"
   git config --global pull.rebase false
   git config --global credential.helper osxkeychain
   ```
4. Test GitHub access:
   ```bash
   ssh -T git@github.com
   ```

---

## 5. Meridian Workspace Bootstrap

1. Create workspace directory:
   ```bash
   mkdir -p ~/Data-Projects && cd ~/Data-Projects
   ```
2. Clone repositories (SSH preferred):
   ```bash
   git clone git@github.com:repoman-git/meridian-core.git
   git clone git@github.com:repoman-git/meridian-trading.git
   git clone git@github.com:repoman-git/meridian-research.git
   git clone git@github.com:repoman-git/meridian-core-operations.git Meridian-Core-Operations
   ```
3. (Optional) Clone any ancillary repos (`meridian`, `meridian-ops`, etc.) from internal mirrors if needed.

---

## 6. Repository Environment Setup

Perform this section inside each repo (`meridian-core`, `meridian-trading`, `meridian-research`, `Meridian-Core-Operations`).

1. Create/activate repo venv:
   ```bash
   cd /Users/you/Data-Projects/meridian-core
   python3 -m venv .venv && source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
   - `meridian-trading` also needs any optional data packages (already covered by `.[dev]`).
   - `Meridian-Core-Operations` installs the `meridian-ops` CLI.
3. Copy `.env.example` if provided, otherwise create `.env` with API keys:
   ```bash
   cat <<'EOF' > .env
   ANTHROPIC_API_KEY=...
   OPENAI_API_KEY=...
   GOOGLE_GEMINI_API_KEY=...
   GROK_API_KEY=...
   EOF
   ```
4. Run unit tests to verify environment:
   ```bash
   pytest -q
   ```
5. Repeat for each repo (activate/deactivate venvs as you switch).

---

## 7. Meridian Ops Sync

1. Ensure the toolkit is installed:
   ```bash
   cd ~/Data-Projects/Meridian-Core-Operations
   pip install -e .
   ```
2. Sync shared assets into every repo:
   ```bash
   meridian-ops sync --target ~/Data-Projects/meridian-core
   meridian-ops sync --target ~/Data-Projects/meridian-trading
   meridian-ops sync --target ~/Data-Projects/meridian-research
   ```
3. Include learning assets when needed:
   ```bash
   meridian-ops sync --target ... --include-learning
   ```

---

## 8. Verification Checklist

- `git status` clean in each repo.
- `pytest` passes in each repo.
- `meridian-ops list-assets` works globally.
- CLI entry points respond:
  ```bash
  meridian-core --help        # if exposed
  meridian-trading --help
  meridian-research --help
  ```
- AI provider env vars resolve (`python - <<'PY'` to print).

---

## 9. Optional Enhancements

- Install Docker Desktop if you run core services locally.
- Restore any local databases/configs (e.g., `meridian.db`).
- Set up IDE tooling (VS Code, Cursor, PyCharm) and point them at the workspace.
- Configure shell prompt/aliases (e.g., `alias mc='cd ~/Data-Projects/meridian-core'`).

---

## 10. Post-Swap Sign-Off

1. Run one end-to-end workflow (e.g., `meridian-core` smoke test or `meridian-trading` backtest) to confirm integrations.
2. Archive this checklist with timestamps and any deviations.
3. Inform the team that the new laptop is live and the old machine can be decommissioned.

---

**Tip:** Keep this file in version control so future swaps reuse the same playbook. Update it whenever the stack changes (new Python version, additional repos, etc.).

