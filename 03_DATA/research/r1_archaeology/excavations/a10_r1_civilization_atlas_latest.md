# R1 Civilization Atlas

这不是文件清单，而是把文件证据折叠为结构节点后的文明图谱初版。文件只是化石，结构才是生物。

- 生成时间：`2026-07-09T09:00:04`
- 结构节点：`8`
- 结构关系：`6`

## 当前节点

| 节点 | 类别 | 状态 | 重要度 | 证据数 | 首次/最近 |
| --- | --- | --- | ---: | ---: | --- |
| Experience Compression Layer | memory | alive | 5 | 11 | 2025-12-04T11:05:46 / 2026-07-03T16:14:51 |
| Lexicon System | structure | alive | 5 | 133 | 2025-12-04T11:05:45 / 2026-07-08T15:22:42 |
| Memory System | memory | alive | 5 | 1113 | 2025-12-04T11:05:45 / 2026-07-08T15:22:42 |
| Permission Protocol | protocol | alive | 5 | 2 | 2025-12-04T11:05:45 / 2026-06-29T19:22:11 |
| Runtime Core | runtime | alive | 5 | 5 | 2025-12-04T11:05:49 / 2026-06-16T19:24:09 |
| Dispatch / Routing System | routing | alive | 4 | 27 | 2025-12-04T11:05:49 / 2026-07-08T15:22:42 |
| Persona / Chip System | persona | alive | 4 | 71 | 2025-12-04T11:05:49 / 2026-07-02T10:20:39 |
| Simulation System | simulation | alive | 3 | 10 | 2025-12-04T11:05:51 / 2025-12-04T11:05:51 |

## 结构节点说明

### Experience Compression Layer

经验压缩层，承载 eco_layer / expanded_knowledge 一类把经验沉积为可路由结构的机制。

- `status`: `alive`
- `category`: `memory`
- `aliases`: `eco_layer, expanded_knowledge`
- `connects`:
  - `part_of` -> `memory_system` (high)：eco_layer 明显属于经验沉积与压缩层
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\eco_layer.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\Engineering\eco_layer.json` | 2026-06-01T15:35:40 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\Engineering\JSON\eco_layer.json` | 2026-06-01T15:35:40 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\eco_layer.json` | 2026-06-11T19:34:58 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\ROOT_ASSETS\eco_layer.json` | 2026-06-11T19:34:58 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\analyze_eco_layer.py` | 2026-06-26T20:44:52 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\09_KNOWLEDGE\eco_layer_cross_validated.md` | 2026-06-30T14:17:14 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\09_KNOWLEDGE\pending_validation\eco_layer_cross_validated.md` | 2026-06-30T14:17:14 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\Engineering\eco_layer.zip` | 2026-06-11T13:56:04 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\Engineering\JSON\eco_layer.zip` | 2026-06-11T13:56:04 | scan_item

### Lexicon System

R1 的词汇体系核心，负责沉淀、组织和供给 tri_world / lexicon 相关知识。

- `status`: `alive`
- `category`: `structure`
- `aliases`: `lexicon, tri_world_lexicon, integrated_vocabulary, lexicon_snapshot, v10_lexicon_slices`
- `connects`:
  - `part_of` -> `memory_system` (high)：词汇体系长期附着于 holo_memory 语义空间
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\tri_world_lexicon.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764608809.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764735384.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764700609.json` | 2025-12-04T11:05:45 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\06_RUNTIME\ace\data\memory\lexicon.json` | 2026-07-08T15:22:38 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\02_MEMORY\lexicon.json` | 2026-07-08T15:19:01 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\06_RUNTIME\ace\data\memory\lexicon_backup_mengpo_20260708_152238.json` | 2026-07-08T15:19:01 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\02_MEMORY\lexicon_backup_mengpo_20260706_155951.json` | 2026-07-06T15:56:28 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\06_RUNTIME\ace\data\memory\lexicon_backup_mengpo_20260706_155951.json` | 2026-07-06T15:56:28 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\02_MEMORY\lexicon_backup_mengpo_20260705_152536.json` | 2026-07-05T15:22:54 | scan_item

### Memory System

记忆体系，围绕 holo_memory / system_state / memory_manager 维护长期沉积和状态承接。

- `status`: `alive`
- `category`: `memory`
- `aliases`: `holo_memory, system_state, memory_manager, memory`
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\tri_world_lexicon.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764608809.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764735384.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764700609.json` | 2025-12-04T11:05:45 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\system_state.json` | 2025-12-04T11:05:45 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\06_RUNTIME\ace\data\memory\lexicon.json` | 2026-07-08T15:22:38 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\02_MEMORY\lexicon.json` | 2026-07-08T15:19:01 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\06_RUNTIME\ace\data\memory\lexicon_backup_mengpo_20260708_152238.json` | 2026-07-08T15:19:01 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\02_MEMORY\lexicon_backup_mengpo_20260706_155951.json` | 2026-07-06T15:56:28 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\06_RUNTIME\ace\data\memory\lexicon_backup_mengpo_20260706_155951.json` | 2026-07-06T15:56:28 | scan_item

### Permission Protocol

R1 的权限与边界协议，体现三层权限、门禁与可访问性控制。

- `status`: `alive`
- `category`: `protocol`
- `aliases`: `three_layer_permission_v7, permission`
- `connects`:
  - `governs` -> `runtime_core` (high)：权限协议直接约束运行核心
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\three_layer_permission_v7.json` | 2025-12-04T11:05:45 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\re_archaeology\claude-code-l3tchupkt\utils\permissions\shadowedRuleDetection.ts` | 2026-06-29T19:22:11 | scan_item

### Runtime Core

运行核心，负责把协议、记忆、词汇和路由接入可执行入口。

- `status`: `alive`
- `category`: `runtime`
- `aliases`: `unrestricted_ai.py, runner_loop.py, full_shadow_patch.sh, run.py, main.py`
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\unrestricted_ai.py` | 2025-12-04T11:05:52 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\config\full_shadow_patch.sh` | 2025-12-04T11:05:49 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\unrestricted_ai.py` | 2026-06-11T19:37:20 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\unrestricted_ai.py.txt` | 2026-06-16T19:24:09 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\Knowledge_Base\AI对话\unrestricted_ai.py.txt` | 2026-05-26T18:26:41 | scan_item

### Dispatch / Routing System

派单与路由体系，负责 AUM / offshore_dispatch / router_config 一类任务分发与流转。

- `status`: `alive`
- `category`: `routing`
- `aliases`: `offshore_dispatch, dispatch, router_config, aum`
- `connects`:
  - `routes` -> `runtime_core` (high)：派单/路由是运行调度层
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\08_ARCHAEOLOGY\2026-07-03_aum_archaeology.md` | 2026-07-03T20:14:30 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\09_KNOWLEDGE\2026-07-03_aum_archaeology.md` | 2026-07-03T20:14:30 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\02_MEMORY\EXP-AUM-001.json` | 2026-07-03T20:22:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\09_KNOWLEDGE\EXP-AUM-001.json` | 2026-07-03T20:22:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\09_KNOWLEDGE\constraint\EXP-AUM-001.json` | 2026-07-03T20:22:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\10_BACKUP\daily_20260703_213259\09_KNOWLEDGE\constraint\EXP-AUM-001.json` | 2026-07-03T20:22:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\07_TASKS\archived\AUM-TASK-2026-06-28-GOV-001.md` | 2026-07-02T09:44:30 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\R1_System\Runtime\offshore_dispatch_config.json` | 2026-05-21T20:01:43 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_System\Runtime\offshore_dispatch_config.json` | 2026-05-21T20:01:43 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\offshore_dispatch_config.json` | 2026-06-24T22:47:48 | scan_item

### Persona / Chip System

人格与芯片体系，围绕 chip_v* / persona / reasoning_kernel 形成行为与执行人格层。

- `status`: `alive`
- `category`: `persona`
- `aliases`: `chip_v, chip_manifest, reasoning_kernel, persona, chip`
- `connects`:
  - `extends` -> `runtime_core` (medium)：人格/芯片为执行入口与推理行为提供可插拔层
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\08_ARCHAEOLOGY\2026-07-02_r1_chip_evolution_archaeology.md` | 2026-07-02T10:20:39 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ace_runtime\09_KNOWLEDGE\2026-07-02_r1_chip_evolution_archaeology.md` | 2026-07-02T10:20:39 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\mine-seed\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\mine-seed\01_AGENTS\xiaofengzi\research\modules\r1_archaeology\fragments\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\mine-seed\fragments\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\mine-seed\modules\r1_archaeology\fragments\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\mine-seed\r1_archaeology\fragments\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\mine-seed\research\modules\r1_archaeology\fragments\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\ACE_CIVILIZATION_BACKUP\cold_storage\mine-seed\xiaofengzi\research\modules\r1_archaeology\fragments\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\mine-seed\01_AGENTS\xiaofengzi\research\modules\r1_archaeology\fragments\persona_matrix_pc_v1.txt` | 2026-06-28T16:12:50 | scan_item

### Simulation System

模拟与实验层，承接 simulator / battleview 一类用于验证和演化的实验结构。

- `status`: `alive`
- `category`: `simulation`
- `aliases`: `r1_simulator, simulator, battleview`
- `connects`:
  - `tests` -> `runtime_core` (medium)：模拟层用于验证或演化运行行为
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator\state_model.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\config\decision_patterns_v1.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\snapshots\sim_run_20251201_0144.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\snapshots\sim_run_20251201_0148.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\snapshots\sim_run_20251201_0149.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\snapshots\sim_run_20251201_0150.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\snapshots\sim_run_20251201_0155.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\snapshots\sim_run_20251201_0157.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\snapshots\sim_run_20251201_0159.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\r1_simulator_v1\config\style_mixer_v1.json` | 2025-12-04T11:05:51 | scan_item

## 当前最值得继续追的空白

- `central_nervous_system` 是否是 `Runtime Core` 的明确祖先，而不是旁系实验架构。
- `integrated_vocabulary` 到 `tri_world_lexicon` 的迁移链是否还能从更多 ZIP 或文本碎片里补齐。
- `expanded_knowledge` 到 `eco_layer` 的关系目前仍偏命名推断，缺少中间桥接证据。
- `battleview` 更像模拟视图还是独立实验层，目前证据不足。
