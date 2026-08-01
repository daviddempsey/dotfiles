# Dotfile deployment

- This repository is the source of truth; home-directory files are deployment targets, mostly symlinked by `install.sh`. Edit the tracked source, not the linked target.
- Never add private keys, access tokens, `.env` files, or shell secrets. `keys/` contains public keys only; user secrets belong in the untracked locations named by `install.sh`.
- Do not run `install.sh` as verification. It may install/download gitleaks, replace existing files after moving them to `.bak`, rewrite the repository hook, and create or replace a daily launchd/cron/Task Scheduler job.
- Do not run `sync.sh` without explicit approval. It stages every repository change, scans, creates an automatic commit, pulls with rebase from `origin master`, and pushes to `origin master`.
- Preserve platform branches in `install.sh`: macOS, Linux/WSL, and Git Bash have different symlink and scheduler behavior. Keep new managed paths inside the `link` helper so existing files are backed up consistently.
- Treat `claude/settings.json`, SSH config, OpenClaw configuration, and scheduled jobs as security-sensitive. Do not print their values in logs or reports; validate structure without echoing content.

## Verification

```bash
bash -n install.sh sync.sh hooks/pre-commit
git diff --check
gitleaks detect --source .
```

- For JSON changes, parse the specific file locally. For link-map changes, inspect the source/destination pair statically; actual installation, scheduling, commit, pull, or push is a separate authorized operation.
