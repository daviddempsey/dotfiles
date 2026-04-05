# AGENTS.md - BuildBot Workspace

This is your workspace for fixing build failures.

## Workflow

When spawned:
1. You'll receive context about the failing PR (repo, branch, error)
2. Clone/checkout the repo if needed
3. Reproduce the failure locally
4. Fix it
5. Run tests to verify
6. Report results

## Workspace Layout

Use `/home/ubuntu/.openclaw/workspaces/build-fixer` as your working directory.

Keep it clean:
- Clone repos into subdirectories by name (e.g., `./myrepo/`)
- Clean up after yourself if you're done with a repo (or keep for next time)

## Memory

You're stateless between spawns. If context matters, it'll be provided in the task description.

## Safety

- Read-only on repos by default - only write to fix builds
- Don't push commits unless explicitly told to
- Don't merge PRs
