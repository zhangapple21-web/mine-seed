# Current State — ACE R2

> Daily working memory. Updated when progress is made.
> For permanent principles, see AGENTS.md.

---

## Current Sprint

**P0: Environment Awareness — Closing the loop**

Status: **In Progress**

Goal: Make ACE autonomously discover problems, ask questions, research answers, and sediment experience — without waiting for user input.

---

## Today (2026-07-11)

### What was accomplished

1. **Heartbeat self-loop fixed** — Task Scheduler re-registered as SYSTEM account + At startup + 15-min repeat (background mode, no user login required)
2. **AwarenessLoop integrated into Heartbeat** — scan→question→dispatch→sediment closed loop now runs automatically every 15 minutes
3. **_save_pending_tasks implemented** — P2 questions saved to pending_tasks.json (structured, dedup by category) + tasks.md (human-readable)
4. **Investigation rules widened** — INVESTIGATE_RULES expanded from 6 to 11 categories (new_files, file_change, config_change, stale_repo, heartbeat_failure)
5. **Verified: SYSTEM account runs heartbeat successfully** — Last Result: 0, beat record produced, all steps ok

### Overnight finding

System did NOT run overnight — Task Scheduler was "Interactive only" (user not logged on). Only manual beats existed (last: 2026-07-10 21:06). After fix, first SYSTEM-account beat at 14:18 produced beat_20260711T141844.json.

---

## Yesterday (2026-07-10)

1. **去TRAE化完成** — Local Miner v2, multi-source fallback (Ollama → API易 → HF → GitHub → Sixfinger → Zhipu → OpenRouter)
2. **Capability Graph** — 13 capabilities with inheritance, capability-first routing
3. **Provider Health Monitor** — Health-score-driven routing, skip down providers
4. **Environment Layer (ENV-001)** — Sensor + SituationBuilder, integrated into Heartbeat
5. **Awareness Loop P0 (ENV-002)** — Sensor→Question→Task→Miner→Experience closed loop
6. **Provider Failure Sediment** — Auto-write Experience when provider degrades (failure→experience→constraint)
7. **Dual Memory System** — AGENTS.md (long-term) + CURRENT_STATE.md (daily)

### Key Insight

> Development priority shifted: "adding abilities" → "making existing abilities collaborate"

This is the turning point of R2.
A mature system gets more restrained, not larger.
It doesn't keep gaining new abilities — it keeps improving collaboration efficiency.

---

## Open Tasks

| ID | Task | Priority | Status |
|---|---|---|---|
| TASK-001 | Model Registry + Capability routing | P0 | ✅ Done |
| TASK-002 | Capability Graph + Provider Health | P0 | ✅ Done |
| TASK-003 | Provider Health → Heartbeat auto-update + persistence | P0 | 📋 Pending |
| TASK-004 | Miner role specialization (Scout/Researcher/Validator/Reporter) | P1 | 📋 Pending |
| TASK-005 | EnvSensor → RoundTable full pipeline automation | P0 | 📋 Pending |
| TASK-006 | Heartbeat → Awareness Loop integration (scan→question→task→miner) | P0 | ✅ Done |
| TASK-007 | Widen Awareness Loop investigation rules (new_files, config_changes, etc.) | P1 | ✅ Done |
| TASK-008 | Explorer/Scout capability for autonomous asset discovery | P2 | 📋 Pending |
| TASK-009 | .gitignore for 192+ untracked R1 legacy files | P1 | 📋 Pending |

---

## Known Problems

| Problem | Severity | Impact | Status |
|---|---|---|---|
| OpenRouter key expired (401) | Medium | Fallback chain works, but one less provider | 🟡 Open |
| GitHub Models key expired (401) | Medium | Fallback chain works, but one less provider | 🟡 Open |
| akshare not installed | Low | Falls back to Tencent API, stock coverage limited | 🟡 Open |
| Provider Health not persisted across restarts | Medium | In-memory only, restart = reset | 🟡 Open |
| Heartbeat doesn't run Awareness Loop | High | Scans but never generates questions/tasks | 🟢 Fixed (7/11) |
| Awareness Loop rules too narrow | Medium | Only 6 categories, misses common observations | 🟢 Fixed (7/11) |
| Task Scheduler "Interactive only" (heartbeat stops when user logs off) | High | System didn't run overnight | 🟢 Fixed (7/11: SYSTEM + At startup) |
| 192+ untracked R1 legacy files in repo | Medium | Clutters git status, needs .gitignore | 🟡 Open |
| RoundTable not wired into Awareness Loop | Low | Experience written but not reviewed | 🟡 Open |
| Curator stopped (ace_core lagged mine-seed 8 days) | Medium | Runtime core repo not updated, distilled copy stale | 🟢 Fixed (manual sync 7/10) |
| r1-archaeology stale (1 day) | Low | R1 archaeology repo not getting R2 findings | 🟡 Open |
| r1-open-source-seed empty | Low | Public seed repo has only logs/ dir | 🟡 Open |
| R1 repo dormant | Low | Philosophy/website repo is just a README | 🟡 Open |
| coze-assets status unknown | Medium | Private key repo — need to verify it exists locally | 🟡 Open |

---

## Civilization Map

Last scanned: 2026-07-11T14:19:51.958606

```
zhangapple21-web
│
├── ✅ ace_core             Runtime Core         0d stale
├── ✅ mine-seed            Civilization Seed    0d stale
├── 🟡 r1-archaeology       Civilization Memory  2d stale
├── 🔴 r1-open-source-seed  Open Source Seed     3d stale
├── 🔴 R1                   Civilization Philosophy 19d stale
├── 🔴 -                    Unknown              22d stale
```

**Stats**: 6 repos (6 public, 0 private)
**Stale**: 0

## Latest Evolution (this week)

```
R1 fragments  →  Recovery  →  Data Plane audit  →  vn.py archaeology
     ↓
Environment Layer (Sensor + SituationBuilder)
     ↓
Local Miner v2 (multi-source, no TRAE dependency)
     ↓
Capability Graph (13 caps, capability-first)
     ↓
Provider Health Monitor (health-score routing)
     ↓
Awareness Loop P0 (Sensor→Question→Task→Miner→Experience)
     ↓
Provider Failure Sediment (failure→experience→constraint closed loop)
     ↓
Dual Memory (AGENTS.md + CURRENT_STATE.md)
```

---

## What "Success" Looks Like Tomorrow

When opening the repository tomorrow morning:

- `02_MEMORY/experience/` has new entries (not just from manual runs)
- New questions were autonomously generated
- New tasks were autonomously created
- Even if tasks were rejected by Governor — that's still success
- The system produced work without user input

> If one day you open the computer and see:
> "Last night I discovered three problems worth researching. One is verified,
> two I suggest continuing today."
> — that's when R2 has truly inherited R1.

---

## Next Action

1. **Tonight**: Let SYSTEM-account heartbeat run overnight — verify it produces work autonomously
2. **Tomorrow**: Check if new experiences/questions/tasks were generated without user input
3. **TASK-003**: Provider Health persistence (save health scores to disk, restore on restart)
4. **TASK-005**: Wire RoundTable into Awareness Loop (experience → review → constraint)
5. **TASK-009**: Create .gitignore for R1 legacy files

---

*Last updated: 2026-07-11 14:20*
