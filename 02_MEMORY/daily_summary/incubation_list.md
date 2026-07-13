# Incubation List — 未完成事项

> **Mission**: AUM-MISSION-ARCH-016 — 文明冻结
> **目的**: 记录暂停的事项，确保以后不会忘
> **更新原则**: 只增不删，已完成的事项标记 COMPLETED 但保留记录

---

## INC-001 — E2C 闭环完整实现

**名称**: E2C Closure（经验→约束闭环）

**暂停原因**:
今天在 [E2C_Closure_Principles_20260616.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/E2C_Closure_Principles_20260616.md) 中发现已有完整设计（P1/P2/P3 三原则），但当前 `experience_engine.compress()` 只做了 O→E（记录），没做 E→C（执行）。这是"废墟熔炼厂"的真正缺失环节，但不能在文明冻结期启动新开发。

**恢复条件**:
- ARCH-013 子任务1 的 `compress_audit_results()` 补丁需要基于 E2C 闭环重新评估
- 出现"审计输出无法落地为约束"的具体痛点

**预计优先级**: P1

**关联**: ARCH-013 子任务1 / ARCH-014 / 废墟熔炼厂考古

---

## INC-002 — Smelter Gate 系统级升级

**名称**: Smelter Gate System-Level Promotion

**暂停原因**:
[ARCH-015 拓扑审计](file:///c:/Users/User/ace_workspace/mine-seed/06_RUNTIME/ACE_RUNTIME_TOPOLOGY.md) 确认 Smelter Gate 当前是模块级局部节点（仅接入 Ollama 审计一条链路），不是系统级。是否升级为系统级需要独立 Mission 论证，不能在局部优化中悄悄升级。

**恢复条件**:
- 出现第二个 FA 模式产出路径需要接入 Gate
- 出现"FA 模式产出绕过 Gate"的安全事件

**预计优先级**: P2

**关联**: ARCH-014 / ARCH-015

---

## INC-003 — Mengpo Lite（孟婆遗忘层）

**名称**: Mengpo Lite（最小遗忘机制）

**暂停原因**:
目前没有证据证明需要。heartbeat 中有 `autophagy_engine.py` 的悬空引用，但该文件不存在。R1 考古报告中记载孟婆是"过滤/遗忘"层，但 ACE 当前还没有 Memory Overflow 的具体痛点。记忆无限增长问题目前由 `clean_old_data()` 部分缓解。

**恢复条件**:
- 出现 Memory Overflow（02_MEMORY/ 目录体积超过阈值）
- `clean_old_data()` 不够用，需要基于价值评分的遗忘机制

**预计优先级**: P2

**关联**: [governance_map_v1.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_assets/031_governance_map_v1.md) / R1 考古

---

## INC-004 — ASSET_INDEX 索引补全

**名称**: ASSET_INDEX 029-042 补全

**暂停原因**:
[ASSET_INDEX.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_assets/ASSET_INDEX.md) 当前只索引到 028，但 029-042 共14个资产文件存在但未被索引。这是维护缺口，不是内容缺失，不紧急。

**恢复条件**:
- 下次资产维护 Mission 启动时
- 或出现"找不到某个已知资产"的具体痛点

**预计优先级**: P3

**关联**: ARCH-015 扫描发现

---

## INC-005 — 4 个待确认节点层级论证

**名称**: Topology 待确认节点论证

**暂停原因**:
[ARCH-015 拓扑审计](file:///c:/Users/User/ace_workspace/mine-seed/06_RUNTIME/ACE_RUNTIME_TOPOLOGY.md) 识别出 4 个"疑似系统级但尚未被证据确认"的节点：Smelter Gate / Governor / Awareness Loop / Ops Cycle。每个节点都需要独立 Mission 论证其层级归属，不能在拓扑审计中顺手决定。

**恢复条件**:
- 某个节点的层级归属影响新 Mission 的设计
- 出现"模块级被误当系统级使用"的具体事故

**预计优先级**: P2

**关联**: ARCH-015

---

## INC-006 — 五大工厂其余部分（仿造/标记/回收/快递站）

**名称**: Five Factories Remaining Parts

**暂停原因**:
ARCH-014 Mission 中明确 Reject 了五大工厂其余部分的实现。当前没有证据表明系统存在"内容碎片化、需要自动分类整理"的具体问题。如果未来出现，再重新考虑。

**恢复条件**:
- 出现"内容碎片化、需要自动分类整理"的具体痛点
- 发现 R1 考古中有新的证据支持重新考虑

**预计优先级**: P3

**关联**: ARCH-014 / R1 五大加工厂考古

---

## INC-007 — DIV-001 外部合法性梯度差异

**名称**: DIV-001 External Legitimacy Gradient

**暂停原因**:
[divergence_log.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/civilization_audit/divergence_log.md) 记录了候选治理原则与 MANIFESTO #2 的梯度差异（"用于落地" vs "在系统内无效"），方向一致、强度不同。标注为 Incubate，不修改任何现有公理。

**恢复条件**:
- 出现需要对外部能力做合规判定的具体场景
- 候选治理原则正式进入 Admission 流程时

**预计优先级**: P3

**关联**: ARCH-013 子任务5

---

## 登记完成

- [x] E2C 闭环完整实现（INC-001, P1）
- [x] Smelter Gate 系统级升级（INC-002, P2）
- [x] Mengpo Lite 遗忘层（INC-003, P2）
- [x] ASSET_INDEX 索引补全（INC-004, P3）
- [x] 4 个待确认节点层级论证（INC-005, P2）
- [x] 五大工厂其余部分（INC-006, P3）
- [x] DIV-001 外部合法性梯度差异（INC-007, P3）

*登记时间: 2026-07-13*
