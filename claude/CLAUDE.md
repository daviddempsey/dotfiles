## Code Style
- Minimize type-specific branching
- Validate by using, not by inspecting
- If you see unused or unnecessary code, either remove it or suggest removing it

## Workflow
- Never run `rm -rf .next` or `next build` while a Next.js dev server is running -- kill the dev server first
- When making changes to Docker-based projects, rebuild containers when necessary
