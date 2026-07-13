# AUM-MISSION-ARCH-013 — Distillation

> **Mission**: 已确认问题修复（Development Mission）
> **完成日期**: 2026-07-13
> **状态**: 全部5个子任务完成
> **Distillation 类型**: Kernel / Blueprint / Protocol / Constraint / Experience / Identity

---

## Kernel — 审计输出必须经压缩才能生效的强制模式

**核心命题**: 审计链路产出的评分/反馈，禁止直接用于影响真实推荐决策。必须先经过 `compress_audit_results()` 压缩流程，提炼为路由规则或策略建议后，才能进入下游决策链路。

**为什么是 Kernel**:
- 这不是某个模块的实现细节，而是整个文明审计闭环的根基
- 没有这道压缩门，审计输出就是"原始观察"而非"经验沉淀"
- 原始审计数据可能包含噪声、单次偏差、局部误判，必须经过模式提炼才能成为可复用知识

**实现位置**:
- [experience_engine.py](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/experience_engine.py) `compress_audit_results()` + `get_audit_compression_latest()`
- 策略调整必须引用 `get_audit_compression_latest()` 返回值，禁止直接读 `audit_results.json`

---

## Blueprint — ROOT_STATE 拆分后 00_ROOT/ 与 06_RUNTIME/state/ 的边界定义

**边界定义**:

| 内容性质 | 归属 Tier | 路径 | 判据 |
|---------|----------|------|------|
| 公理（Axiom_000-010） | Tier 1 | `00_ROOT/ROOT_STATE.md` | 不随运行状态变化，是文明的根本身份 |
| 原则库（P001-P018） | Tier 1 | `00_ROOT/ROOT_STATE.md` | 路由约束，演化缓慢，是文明沉淀的可执行规则 |
| 版本信息（Version/Last Verified/Repository） | Tier 3 | `06_RUNTIME/state/runtime_state.md` | 随每次唤醒更新 |
| 架构指纹（lab_01在线状态等） | Tier 3 | `06_RUNTIME/state/runtime_state.md` | 在线/离线状态会变化，是运行时快照 |
| 种子库版本记录 | Tier 3 | `06_RUNTIME/state/runtime_state.md` | 版本历史，但属于仓库演化轨迹而非文明身份 |
| Awakening 记录 | Tier 3 | `06_RUNTIME/state/runtime_state.md` | 由 awaken.py write_root_state() 追加写入 |
| 守护层目录索引 | Tier 3 | `07_GUARDIAN/README.md` | 是 07_GUARDIAN 目录的描述性索引，非原则条文 |

**写入路径契约**:
- `awaken.py write_root_state()` 优先写入 `06_RUNTIME/state/runtime_state.md`
- 若新位置不存在则回退到 `00_ROOT/ROOT_STATE.md`（向后兼容）
- 任何代码若需读取运行状态，应优先读 Tier 3 路径

**禁止行为**:
- ❌ 禁止将公理/原则迁到 Tier 3（会稀释文明身份层）
- ❌ 禁止将运行状态写入 Tier 1（会污染公理层）
- ❌ 禁止"整体迁移"——必须按内容性质逐条拆分

---

## Protocol — 经验数据清理规则

**清理命令**: `python experience_engine.py --clean N`（N 为保留天数，默认 7）

**可清理（中间态数据）**:
- `02_MEMORY/experience/learn_cycle_*.json` — 学习循环中间文件
- `02_MEMORY/experience/exp_debate_*.json` — 辩论中间产物
- `02_MEMORY/experience/exp_seeded_*.json` — 种子化中间产物
- `05_TOOLS/mine_output/observation_log.json` 中超过 N 天的 observation 条目

**不可清理（正式产出 / 原始数据源）**:
- ❌ `02_MEMORY/experience.json` — 压缩结果，是经验引擎的核心资产
- ❌ `05_TOOLS/mine_output/advisor/audit_results.json` — 原始审计数据，是 Evidence 源
- ❌ `02_MEMORY/civilization_audit/` — 已归档的文明审计报告
- ❌ `02_MEMORY/exploration/` — 已归档的探索报告
- ❌ 任何已沉淀为 Constraint/Blueprint 的正式产出

**清理规则**:
- 仅清理已被 `compress()` 或 `compress_audit_results()` 提炼过的中间态数据
- 清理操作不删除文件，而是将超过 N 天的条目移到 `archive/` 子目录（可回滚）
- 清理前自动备份一次 `experience.json` 到 `evolution/backup_YYYYMMDD_HHMMSS_clean.json`

---

## Constraint — 审计链路禁止绕过压缩机制直接生效

**Constraint ID**: C-019
**等级**: HARD
**类型**: 流程约束
**来源**: AUM-MISSION-ARCH-013 子任务1
**状态**: ACTIVE

**约束内容**:
```
任何模块若需使用 audit_results.json 中的评分/反馈来影响推荐决策、
路由调整、Policy 更新，必须通过 experience_engine.compress_audit_results()
压缩后的产物（get_audit_compression_latest() 返回值）获取，
禁止直接读取 audit_results.json 原始文件。
```

**判据**:
- ✅ 合规：调用 `ExperienceEngine.get_audit_compression_latest()` 获取审计摘要
- ❌ 违规：直接 `json.load(open(audit_results.json))` 用于决策

**例外**:
- 审计模块自身（post_recommendation_auditor.py）读写原始文件属于正常操作
- 压缩模块自身（experience_engine.compress_audit_results）读原始文件属于正常操作
- 仅"下游消费者"受此约束限制

**执行机制**:
- 代码审计可扫描 `audit_results.json` 在非 auditor/experience_engine 模块中的引用
- 违反此约束的代码不允许通过 Admission Engine 审批

---

## Experience — GPT 早期"整体迁移"判断被证伪的教训

**事件**: GPT 早期判断 ROOT_STATE.md 是"运行状态文件"，建议整体迁移到 06_RUNTIME/。

**证伪过程**:
- AUM-MISSION-ARCH-012 核实结果显示：约40%是纯运行状态，60%是公理/原则内容
- 如果当时直接按 GPT 的建议做了整体搬迁，现在就是一次真正的 Civilization 内容外泄事故——公理层会被掏空

**教训**:
- 分类操作必须先核实内容比例，不能凭文件名或功能猜测
- "ROOT_STATE" 这个名字暗示"状态文件"，但实际内容包含文明身份层
- AI 早期判断可能基于命名启发式而非内容核实，必须坚持"先核实再迁移"

**沉淀为原则**:
- 任何涉及 Tier 1/Tier 2 资产的内容操作（迁移/拆分/重命名），必须先做内容比例核实
- 核实结果必须留档，作为拆分决策的依据
- 边界项必须标注出来问，禁止自行判断硬拆

**关联**: 与 DFP-001（Drawer First Protocol）形成互补——DFP 要求"先翻抽屉再造轮子"，本教训要求"先看抽屉里到底是什么再决定怎么处理"。

---

## Identity — Compression Gate Pattern（补充 Contract Enforcement Pattern）

**Pattern 名称**: Compression Gate Pattern（压缩门模式）

**定位**: 是 Contract Enforcement Pattern（契约执行模式）的补充，专用于"原始数据 → 经验沉淀"这一过渡环节。

**Pattern 结构**:
```
Raw Data (观察/审计/反馈)
    │
    ▼
[Compression Gate]  ← 强制压缩流程
    │
    ▼
Compressed Knowledge (路由规则/模式/原则候选)
    │
    ▼
[Downstream Consumer]  ← 只能读压缩产物，不能读原始数据
```

**与 Contract Enforcement Pattern 的区别**:
- Contract Enforcement Pattern: 关注"契约是否被遵守"（如 Tier 1 写入必须经 Admission）
- Compression Gate Pattern: 关注"原始数据是否经过提炼才能生效"（如审计评分必须经压缩才能影响决策）

**适用场景**:
- 审计输出 → 策略调整
- 观察日志 → 路由规则
- 用户反馈 → 体验优化
- 任何"高噪声原始数据" → "低噪声可执行知识"的过渡

**反模式**:
- ❌ Raw Data Bypass: 下游消费者直接读原始数据，绕过压缩门
- ❌ Compression Skipped: 压缩门存在但从未被调用，原始数据无限堆积
- ❌ Compressed Overwritten: 压缩产物被原始数据直接覆盖

**身份层含义**:
- ACE 不是"会记笔记的系统"，而是"会把笔记提炼成规则的系统"
- Compression Gate 是这个身份的工程实现
- 没有 Compression Gate 的系统只是数据堆积，不是经验沉淀

---

## Mission 总览

| 子任务 | 优先级 | 状态 | 核心交付 |
|--------|--------|------|----------|
| 1. FA压缩覆盖缺口 | P0 | ✅ | compress_audit_results() + Compression Gate |
| 2. 跨平台路径修复 | P0 | ✅ | platform.system() 双路径支持 |
| 3. ROOT_STATE.md 拆分 | P1 | ✅ | 公理留Tier1,状态迁Tier3,边界项问后处理 |
| 4. 经验数据清理机制 | P2 | ✅ | clean_old_data(days) + 可清/不可清规则 |
| 5. MANIFESTO #2 归档 | P2 | ✅ | divergence_log.md DIV-001 (Incubate) |

**关键决策**:
- 子任务3的"守护层原则表"边界项经用户确认为"两边都不放"——归 07_GUARDIAN/README.md
- awaken.py 写入路径带向后兼容回退，避免破坏旧环境
- Compression Gate 通过 `get_audit_compression_latest()` 提供统一读取入口，便于约束执行
