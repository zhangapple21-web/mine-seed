# R1 Civilization Atlas

这不是文件清单，而是把文件证据折叠为结构节点后的文明图谱初版。文件只是化石，结构才是生物。

- 生成时间：`2026-06-26T10:49:37`
- 结构节点：`12`
- 结构关系：`10`

## 当前节点

| 节点 | 类别 | 状态 | 重要度 | 证据数 | 首次/最近 |
| --- | --- | --- | ---: | ---: | --- |
| Experience Compression Layer | memory | alive | 5 | 5 | 2025-12-04T11:05:46 / 2026-06-25T10:31:16 |
| Lexicon System | structure | alive | 5 | 25 | 2025-12-04T11:05:45 / 2026-06-25T10:31:16 |
| Memory System | memory | alive | 5 | 21 | 2025-12-04T11:05:45 / 2026-06-25T10:31:16 |
| Permission Protocol | protocol | alive | 5 | 1 | 2025-12-04T11:05:45 / 2025-12-04T11:05:45 |
| Runtime Core | runtime | alive | 5 | 7 | 2025-12-04T11:05:49 / 2026-06-25T10:31:16 |
| Central Nervous System | ancestor-hypothesis | fossil | 4 | 86 | 2026-06-25T10:31:16 / 2026-06-25T10:31:16 |
| Dispatch / Routing System | routing | alive | 4 | 5 | 2025-12-04T11:05:49 / 2026-06-25T10:31:16 |
| Expanded Knowledge | ancestor-hypothesis | fossil | 4 | 1 | 2026-06-25T10:31:16 / 2026-06-25T10:31:16 |
| Integrated Vocabulary | ancestor-hypothesis | fossil | 4 | 1 | 2026-06-25T10:31:16 / 2026-06-25T10:31:16 |
| Persona / Chip System | persona | alive | 4 | 36 | 2025-12-04T11:05:49 / 2026-05-21T20:01:54 |
| Battleview | ancestor-hypothesis | fossil | 3 | 1 | 2026-06-25T10:31:16 / 2026-06-25T10:31:16 |
| Simulation System | simulation | alive | 3 | 11 | 2025-12-04T11:05:51 / 2026-06-25T10:31:16 |

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
  - `C:\Users\USER\Downloads\Telegram Desktop\Engineering\JSON\eco_layer.json` | 2026-06-01T15:35:40 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\eco_layer.json` | 2026-06-11T19:34:58 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\Engineering\JSON\eco_layer.zip` | 2026-06-11T13:56:04 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/ABC_┤╩┐Γ_macOS/┤╩┐Γ/expanded_knowledge.json` | 2026-06-25T10:31:16 | zip_entry

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
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764495281.json` | 2025-12-04T11:05:47 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\Engineering\JSON\lexicon_snapshot_v3.json` | 2026-05-25T21:34:24 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\Engineering\JSON\lexicon_snapshot_v2.json` | 2026-05-25T21:33:43 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\lexicon_snapshot_v3.json` | 2026-06-25T10:29:12 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\lexicon_routing_config.json` | 2025-12-04T11:05:48 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\lexicon_paths.json` | 2025-12-04T11:05:48 | scan_item

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
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\eco_layer.json` | 2025-12-04T11:05:46 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\v10_lexicon_slices_1764495281.json` | 2025-12-04T11:05:47 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\entries_map.json` | 2025-12-04T11:05:47 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\tags_index.json` | 2025-12-04T11:05:47 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\holo_memory\holo_memory_config.json` | 2025-12-04T11:05:47 | scan_item

### Permission Protocol

R1 的权限与边界协议，体现三层权限、门禁与可访问性控制。

- `status`: `alive`
- `category`: `protocol`
- `aliases`: `three_layer_permission_v7, permission`
- `connects`:
  - `governs` -> `runtime_core` (high)：权限协议直接约束运行核心
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\databases\three_layer_permission_v7.json` | 2025-12-04T11:05:45 | scan_item

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
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/main.py` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/run.py` | 2026-06-25T10:31:16 | zip_entry

### Central Nervous System

来自 ZIP 容器中的异常命名结构，像是一个更早的总控架构祖先，值得优先建立血缘关系。

- `status`: `fossil`
- `category`: `ancestor-hypothesis`
- `aliases`: `central_nervous_system`
- `possible_descendants`: `runtime_core, memory_system`
- `connects`:
  - `possible_ancestor_of` -> `runtime_core` (medium)：central_nervous_system 命名和其内部模块更像总控前身
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/COMPLETE_DOCUMENTATION.md` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/config/config_manager.py` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/config/default_config.yaml` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/core/autonomous_neural_adapter.py` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/core/__init__.py` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/file_structure.md` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/inference/model_inference.py` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/initialization_flow.md` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/input/input_processor.py` | 2026-06-25T10:31:16 | zip_entry
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/central_nervous_system/learning/learning_system.py` | 2026-06-25T10:31:16 | zip_entry

### Dispatch / Routing System

派单与路由体系，负责 AUM / offshore_dispatch / router_config 一类任务分发与流转。

- `status`: `alive`
- `category`: `routing`
- `aliases`: `offshore_dispatch, dispatch, router_config, aum`
- `connects`:
  - `routes` -> `runtime_core` (high)：派单/路由是运行调度层
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_System\Runtime\offshore_dispatch_config.json` | 2026-05-21T20:01:43 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\offshore_dispatch_config.json` | 2026-06-24T22:47:48 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\config\router_config.json` | 2025-12-04T11:05:49 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v2\auto_dispatch_runner.py` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/aum_system.py` | 2026-06-25T10:31:16 | zip_entry

### Expanded Knowledge

来自 ZIP 容器的异常命名知识结构，可能与 eco_layer / 经验压缩层存在继承关系。

- `status`: `fossil`
- `category`: `ancestor-hypothesis`
- `aliases`: `expanded_knowledge`
- `possible_descendants`: `experience_compression_layer`
- `connects`:
  - `possible_ancestor_of` -> `experience_compression_layer` (medium)：expanded_knowledge 与经验压缩/知识沉积命名接近
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/ABC_┤╩┐Γ_macOS/┤╩┐Γ/expanded_knowledge.json` | 2026-06-25T10:31:16 | zip_entry

### Integrated Vocabulary

来自 ZIP 容器的异常命名词汇结构，可能是 Lexicon System 的早期形态或旁系。

- `status`: `fossil`
- `category`: `ancestor-hypothesis`
- `aliases`: `integrated_vocabulary`
- `possible_descendants`: `lexicon_system`
- `connects`:
  - `possible_ancestor_of` -> `lexicon_system` (medium)：命名上更像 tri_world_lexicon 之前的词汇整合阶段
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/ABC_┤╩┐Γ_macOS/┤╩┐Γ/integrated_vocabulary.json` | 2026-06-25T10:31:16 | zip_entry | 已跳过重复（首次出现于 C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/ABC_┤╩┐Γ_macOS/┤╩┐Γ/expanded_knowledge.json）

### Persona / Chip System

人格与芯片体系，围绕 chip_v* / persona / reasoning_kernel 形成行为与执行人格层。

- `status`: `alive`
- `category`: `persona`
- `aliases`: `chip_v, chip_manifest, reasoning_kernel, persona, chip`
- `connects`:
  - `extends` -> `runtime_core` (medium)：人格/芯片为执行入口与推理行为提供可插拔层
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v3\chip_v3_core.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v2\core_v2_launcher.py` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v3\chip_v3_seeds.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v1\reasoning_kernel_v1.json` | 2025-12-04T11:05:52 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v1\chip_manifest.json` | 2025-12-04T11:05:52 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\core\personas\curator_freezone.json` | 2025-12-04T11:05:49 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v2\auto_dispatch_runner.py` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_v1\abstraction_log.txt` | 2025-12-04T11:05:52 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_core\chip_v1_metadata.json` | 2025-12-04T11:05:51 | scan_item
  - `C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY\core_copy\sandbox\chip_core\chip_v1_root.json` | 2025-12-04T11:05:51 | scan_item

### Battleview

ZIP 容器中出现的视角/对战命名，可能属于模拟或实验视图层。

- `status`: `fossil`
- `category`: `ancestor-hypothesis`
- `aliases`: `battleview`
- `possible_descendants`: `simulation_system`
- `connects`:
  - `possible_ancestor_of` -> `simulation_system` (low)：battleview 更接近模拟/实验视图层
- `evidence`:
  - `C:\Users\USER\Downloads\Telegram Desktop\新建文件夹.zip::╨┬╜¿╬─╝■╝╨/.vscode/battleview.json` | 2026-06-25T10:31:16 | zip_entry

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
