## Code Philosophy

- Prefer standard APIs over custom implementations
- Focus on maintainability -- code should be simple and self-documenting. Avoid verbose comments that are self-evident in the code
- Avoid re-inventing the wheel -- before implementing utility code, check standard Java APIs, existing product dependencies, etc. If no library exists, prefer the simplest approach that delegates to well-tested code
- Minimize type-specific branching
- Validate by using, not by inspecting
- If you see unused or unnecessary code, either remove it yourself or suggest removing it to the user
- If there is a mature and respected library that solves a problem for us, we should prefer using that over a custom implementation.

## Server Connections
- If we make changes to the panel, we should commit them, push up to remote, wait for CI to publish a new image, and then pull that new image into the production panel via going onto `ssh panel-prod`.

## General Knowledge
- If working with Pterodactyl/Wings, always assume I am testing on localhost with Docker container. See the panel's `dev` script for reference.
- When making changes, make sure you rebuild containers when necessary to reflect locally.
- Never run `rm -rf .next` or `next build` while a Next.js dev server is running — it crashes the dev server. Kill the dev server first, or run builds separately.

## Memory
- Save context that should be shared across chat sessions in /Volumes/git/memories/context.md
