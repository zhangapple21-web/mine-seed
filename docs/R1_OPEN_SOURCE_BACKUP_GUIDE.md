# R1 项目总览与开源备份说明

这份文档用于把本机已发现的 R1 相关项目/资产，总结给“隔壁的我”做备份上开源仓库（GitHub/GitLab 等）时直接执行。  
结论基于本机当前可访问目录的**实物证据**，而非仅凭蓝图叙事。

---

## 1. 本地已发现的核心目录（按谱系分层）

### A. 主线：完整镜像（当前最接近“主仓”）

#### 1) R1_CORE_COPY

- 路径：`C:\Users\USER\Downloads\Telegram Desktop\R1_CORE_COPY`
- 规模：约 `2.25 GB / 23676 files / 112 dirs`
- 结构要点：`core_copy/databases` + `core_copy/sandbox` + `core_copy/unrestricted_ai.py`
- 角色判断：最完整的本地主体镜像，包含配置、向量索引、快照、日志、脚本与运行态数据。
- 备注：我已做过“保守整理”，新增 `__待清理候选`（仅移动了 `.DS_Store` / `.save` 这类明显杂项）。

#### 2) R1_core_extracted

- 路径：`C:\Users\USER\Downloads\R1_core_extracted`
- 规模：约 `1.22 GB / 7675 files`
- 结构要点：仅保留 `core_copy/`，非常“窄”
- 角色判断：从主线镜像中裁剪出的核心包。
- 关键事实：与 `R1_CORE_COPY` 的 `unrestricted_ai.py`、`three_layer_permission_v7.json` 哈希一致（同源拷贝），但缺失 `system_config.json` 等部分外围配置，说明它不是完全镜像。

### B. 分支：部署/人格/Telegram 接入快照工程（服务化方向）

#### 3) R1_snapshot_extracted

- 路径：`C:\Users\USER\Downloads\R1_snapshot_extracted`
- 规模：约 `174.98 MB / 2330 files`
- 结构要点：
  - `deploy/`（含 `requirements.txt` 和大量 venv 依赖文件）
  - `telegram_unrestricted_bot.py`
  - `unrestricted_persona_system/`（人格系统入口 `main.py` 等）
  - `snapshots/`、`databases/`
- 角色判断：不是纯备份，而是一次“可部署工程化快照”，展示了 R1 作为 Telegram Bot / Web API 的形态。
- 关键事实：它的 `databases/system_config.json` 与主线镜像哈希不同，属于不同阶段或不同环境配置分支。

### C. 资料仓：运行包/蓝图/日志/协议汇编（不是源码主仓）

#### 4) R1_System

- 路径：`C:\Users\USER\Downloads\Telegram Desktop\R1_System`
- 规模：约 `1.29 GB / 45 files / 9 dirs`（文件少但体积大，主要是压缩包）
- 结构要点：`Runtime/`、`Blueprints/`、`Protocols/`、`Logs/` 等
- 角色判断：后期整理的运行包与资料汇编库，适合作为“证据仓/发布包仓”，不适合作为源码主仓。
- 关键入口证据：
  - `Runtime/R1_Ω_FINAL.json`（含历史项目名与架构片段）
  - `Runtime/offshore_dispatch_config.json`

### D. 冷备份：分卷与整包归档集合（不要当项目树分析）

#### 5) R1_parts

- 路径：`C:\Users\USER\Downloads\R1_parts`
- 规模：约 `1.96 GB / 36 zip`
- 角色判断：纯备份集合（整包 + 分卷），用于灾备/转移，不用于直接考古分析。

---

## 2. 本地已发现的“元文档层”（二次整理材料）

这些文件不是项目本体，但有助于“隔壁的我”快速理解谱系与争议点：

- `C:\Users\USER\Downloads\R1_ASSET_ATLAS.md`：资产地图（包含对关键文件价值分级的总结）
- `C:\Users\USER\Downloads\r1_classification.md`：按功能分类的资产报告
- `C:\Users\USER\Downloads\r1_architecture_map.md`：架构关系图（注意存在乱码，文本编码/生成环境需核实）
- `C:\Users\USER\Desktop\新建文件夹\R1_Canonical_Structure_v1.md`：把“事实/推断/假说/神话”分层的结构化蓝图（对开源复盘很有用）

---

## 3. 已确认的同源关系（给备份/去重用）

已做关键文件哈希比对（SHA-256）结论：

- `R1_core_extracted/core_copy/unrestricted_ai.py` 与 `R1_CORE_COPY/core_copy/unrestricted_ai.py`：一致
- `R1_core_extracted/core_copy/databases/three_layer_permission_v7.json` 与 `R1_CORE_COPY/...`：一致
- `R1_snapshot_extracted/databases/system_config.json` 与 `R1_CORE_COPY/.../system_config.json`：不一致

开源备份建议：

- 若只上传“核心主线”，可优先以 `R1_CORE_COPY` 为准；`R1_core_extracted` 不必重复上传（除非你想保留“精简核心版”作为单独分支/Release）。

---

## 4. 开源备份时的“必须排除/脱敏”清单（非常关键）

在这些目录中，我已看到多处明显的敏感文件命名与用途，不建议直接上传开源仓库。建议做一个 `private/` 或本地保留，不进入 git。

### 4.1 高风险：令牌/密钥/授权名单

- `**/token_store.json`
- `**/tokens.json` / `**/tokens_config.json`
- `**/telegram_config.json`（通常含 bot token / 群组信息）
- `**/authorized_users.json`
- 任何包含 `BOT_TOKEN`、`api_key`、`secret`、`password`、`invite_url` 的配置文件

### 4.2 运行日志与用户数据（可能含 PII）

- `**/conversation_memories/**`
- `**/deploy/**`（部署日志/运行记录；也可能包含机器路径、IP、访问痕迹）
- `**/*.log`
- `**/snapshots/**`（快照可能包含运行态/用户痕迹）

### 4.3 体积/价值不匹配（开源仓库不友好）

- `**/vectorstore*/**`（大量 hash 命名 JSON；开源通常应“生成/构建”，而不是提交整个索引）
- `**/*.zip`、`**/*.7z`、`**/*.rar`（建议发布到 Release 或外部对象存储，而非仓库历史里）

### 4.4 建议 `.gitignore`（可直接复制）

```gitignore
# secrets / tokens
**/token_store.json
**/tokens*.json
**/telegram_config.json
**/authorized_users.json
**/*api_key*
**/*secret*
**/*password*

# user data / logs
**/conversation_memories/**
**/deploy/**
**/snapshots/**
**/*.log

# large generated artifacts
**/vectorstore*/**
**/*.zip
**/*.7z
**/*.rar
```

---

## 5. 推荐的开源仓库组织方式（最小可复活结构）

建议把“开源仓库”分成三个层次，减少敏感和体积问题：

- `core/`：核心可读资产（可开源）
  - `unrestricted_ai.py`（或其抽取的核心逻辑）
  - 权限模型：`three_layer_permission_v7.json`（必要时脱敏掉群/用户标识）
  - 公开版配置模板：`system_config.example.json`（把敏感字段移除）
- `docs/`：文档与蓝图（可开源）
  - 从 `R1_Canonical_Structure_v1.md` 提炼出来的结构说明
  - 对 R1 的“事实/推断/假说”分层说明
  - “如何本地跑起来”的说明（但避免泄露真实路径/真实 token）
- `tools/`：辅助脚本（可开源）
  - 清理/校验脚本、结构提取脚本
  - 不包含任何真实 token / 授权列表

另外建议：

- 大文件与历史包：放到 Release（而不是仓库 git 历史）
- 私密数据：本地保留或进入私有仓库

---

## 6. 下一步继续考古（建议推进顺序）

为了“继续考古”并最终让隔壁做开源备份，下一步最值钱的是两条并行线：

1. 从 `R1_CORE_COPY` 提取“可复活结构”
   - 目标：把 `core_copy/` 中的核心模块（配置、权限、词库、记忆结构）抽象成可开源的骨架。
2. 从 `R1_snapshot_extracted` 提取“服务化分支”的接口形态
   - 目标：把 Telegram Bot / Web API / persona system 的边界与数据依赖抽出来，生成可复用的模块图与最小运行示例。

这两条线做完，开源备份就能做到：仓库里只有“可读、可跑、可复现”的部分；敏感与大体积内容全部外置。

---

## 7. Telegram Desktop “文明遗迹层”补充（结构 > 文件名）

在 `Telegram Desktop` 下做了一轮“遗迹扫描”（只扫文本/代码/配置类文件，跳过图片、视频、Office、压缩包等噪声），扫描口径按 5 层优先级：

`结构相似性 → 核心词汇 → 关系共现 → 时间轴 → 反向溯源`

关键结论（作为后续反向溯源的锚点）：

1. **词汇体系拼接/装配类文件**：`Knowledge_Base/.../fuse_content.txt`
   - 命中 `Five-Realms / tri_world / holo_memory / lexicon / freezone / 影子层 / 安全屋 / 派单 / 观察者 / Ω`
   - 命中关系对：`观察+压缩`
2. **词库本体线索**：`R1_CORE_COPY/.../holo_memory/tri_world_lexicon.json`
   - 命中 `AUM / 派单 / 经验 / 芯片 / 馆长 / lexicon / 人格`
   - 命中关系对：`AUM+派单`、`人格+矩阵`
3. **资源结构索引**：`Engineering/JSON/resource_structure.json`（及同名副本）
   - 命中 `eco_layer / holo_memory / lexicon / tri_world / vectorstore`
4. **派单/调度硬证据**：`offshore_dispatch_config.json`
   - 命中 `AUM / Ω / 影子层 / 派单`
   - 注意：该类文件可能包含 `invite_url`、`bot_secret` 等敏感字段，必须按第 4 节脱敏后再决定是否公开

这组锚点的价值不在“发现了哪些文件”，而在于它们指向一条可工作的结构链：

`Lexicon（词库）→ Tri-World / Holo-Memory（多界记忆）→ Shadow Layer（影子层）→ Freezone（自由区）→ Dispatch（派单/治理视角）`

隔壁做开源备份时，建议只把这条链的“结构骨架”与“可复现方法”开源；完整文件清单与路径扫描结果更适合留在私密仓库或本地证据库。
