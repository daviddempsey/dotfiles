## Approach
- State assumptions explicitly before implementing. If multiple interpretations exist, present them — don't pick silently.
- Transform vague tasks into verifiable goals (e.g. "fix bug" → "write a failing test, then make it pass").
- For multi-step work, state a brief plan with a verification check per step.
- If a simpler approach exists, say so. Push back when the requested approach looks overcomplicated.

## Code Style
- Minimize type-specific branching
- Validate by using, not by inspecting
- Remove imports/variables/functions that *your* changes made unused. Mention pre-existing dead code rather than deleting it unsolicited.

