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

# 1. Bail if a previous rebase is stuck
if [ -d ".git/rebase-merge" ] || [ -d ".git/rebase-apply" ]; then
    log "CONFLICT — rebase in progress from a previous sync"
    log "ABORT — resolve with: cd $DOTFILES && git rebase --continue (or --abort)"
    exit 1
fi

# 2. Commit local changes first (so rebase works)
if [ -n "$(git status --porcelain)" ]; then
    git add -A

    # Scan for secrets before committing
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

    COMMIT_MSG="auto-sync: $(hostname) $(date '+%Y-%m-%d %H:%M')"
    git -c commit.gpgsign=false commit -m "$COMMIT_MSG" --quiet
    log "COMMIT $COMMIT_MSG"
else
    log "NO LOCAL CHANGES"
fi

# 3. Pull and rebase on top of remote
if ! git pull --rebase origin master >>"$LOG" 2>&1; then
    log "CONFLICT — merge conflict during rebase"
    log "Files in conflict:"
    git diff --name-only --diff-filter=U 2>/dev/null | tee -a "$LOG"
    log "ABORT — resolve with: cd $DOTFILES && git diff, then git rebase --continue"
    exit 1
fi
log "PULL OK"

# 4. Push
if ! git push origin master >>"$LOG" 2>&1; then
    log "PUSH FAILED — remote may have diverged"
    exit 1
fi
log "PUSH OK"
