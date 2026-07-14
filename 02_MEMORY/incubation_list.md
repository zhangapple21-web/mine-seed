# Incubation List

> Assets or missions paused, awaiting conditions.

| Name | Reason for Pause | Recovery Conditions | Priority |
|------|------------------|---------------------|----------|
| R1 "Processing Plant" (5 factories + ruin smelter + Mengpo) | ARCH-013 marked as incomplete; compress() is temporary patch | Full pipeline implementation (randomization, metadata labeling, decomposition, sync) | High |
| Memory MCP Integration | Evaluated as Retrieval Layer only; Repository API missing | Repository API (search/get/list/commit/snapshot/diff) implemented | Medium |
| Admission Engine (admission.py) | Referenced in RUNTIME_BOUNDARY.md but not implemented | C-013~024 constraints distilled + evolve()/apply_constraint_patch() coded | High |
| Experience Engine v2 | Current compress() lacks auto-trigger mechanism | Full pipeline from ARCH-013 completed | Medium |
| GitHub Actions CI/CD | User explicitly deprioritized in favor of ARCH-014 | ARCH-018 completed + recovery score > 95% | Low |
| Miner Judge A/B Testing | User explicitly deprioritized | Shadow Observer 7-day period completed with evidence | Low |
| FA Mode + Smelter Gate binding | Must be released together; currently Smelter Gate done but FA mode only named | Full FA mode implementation with real护栏 | High |
| Stock Advisor T+5 tracking | T+1 working but T+5 needs longer history | 5 trading days of T+5 data accumulated | Medium |
