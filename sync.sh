#!/usr/bin/env bash
set -euo pipefail

DOTFILES="$(cd "$(dirname "$0")" && pwd)"
LOG="$HOME/.dotfiles-sync.log"

# Ensure gitleaks is findable in cron/launchd/scheduled task contexts
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"
}

cd "$DOTFILES"

# 1. Pull
if ! git pull --rebase origin master >>"$LOG" 2>&1; then
    log "PULL FAILED — merge conflict or network error"
    log "ABORT — manual resolution required"
    exit 1
fi
log "PULL OK"

# 2. Check for changes
if [ -z "$(git status --porcelain)" ]; then
    log "NOTHING TO SYNC"
    exit 0
fi

# 3. Stage
git add -A

# 4. Scan for secrets
if ! command -v gitleaks &>/dev/null; then
    log "WARNING: gitleaks not installed — skipping secret scan"
else
    SCAN_OUTPUT=$(gitleaks protect --staged 2>&1) || {
        log "SCAN FAILED — secrets detected:"
        echo "$SCAN_OUTPUT" | tee -a "$LOG"
        git reset HEAD --quiet
        log "ABORT — staged changes reverted, fix secrets before syncing"
        exit 1
    }
    log "SCAN OK — no secrets found"
fi

# 5. Commit
COMMIT_MSG="auto-sync: $(hostname) $(date '+%Y-%m-%d %H:%M')"
git commit -m "$COMMIT_MSG" --quiet
log "COMMIT $COMMIT_MSG"

# 6. Push
if ! git push origin master >>"$LOG" 2>&1; then
    log "PUSH FAILED — remote may have diverged"
    exit 1
fi
log "PUSH OK"
