# Reject List

> Items explicitly rejected from Civilization Repository.

| Item | Rejection Reason | Date |
|------|-----------------|------|
| Memory MCP as Repository | Violates AX-002 (Repository Supremacy): MCP is LLM-specific, no Git versioning, not LLM-agnostic | 2026-07-14 |
| Direct Shadow → local_miner bypass | Violates PR-001 (Find Before Build): bypasses established governance chain (TaskRouter) | 2026-07-14 |
| Static worker_registry.json | Violates CP-002 design: Registry must be Capability Snapshot, not dead list | 2026-07-14 |
| New Red Team personalities | Violates GV-003: fixed 5 personalities, no expansion allowed | 2026-07-14 |
| New attack methods per personality | Violates GV-003: fixed 3 methods per personality, weapon library does not grow | 2026-07-14 |
| AGENTS.md as long Prompt | Violates AGENTS.md Never Rules: must remain identity entry, not encyclopedia | 2026-07-14 |
| Runtime writing to 02_MEMORY/assets/ | Violates C-018 + RUNTIME_BOUNDARY.md: must go through Admission Engine | 2026-07-14 |
| Chat logs as civilization assets | Violates PR-003 (Distill Before Archive): raw logs are noise, not assets | 2026-07-14 |
| Uncompressed files to GitHub | Violates user preference: files must be distilled, compressed, reviewed first | 2026-07-14 |
| GitHub Actions (immediate) | User deprioritized: focus on foundational feedback loop first | 2026-07-14 |
| Miner Judge A/B (immediate) | User deprioritized: focus on ARCH-014 and core issues first | 2026-07-14 |
