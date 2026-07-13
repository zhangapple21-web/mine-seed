# Reject List 2026-07-13 — 今天删除了什么

> **Mission**: AUM-MISSION-ARCH-016 — 文明冻结
> **目的**: 记录今天最终决定 Reject 的事项，防止死灰复燃
> **原则**: 每一项 Reject 都必须有明确原因，未来若要翻案需要新证据

---

## REJ-001 — compress() 当 Gate

**最终决定**: ❌ Reject

**原提议**:
ARCH-013 子任务1 试图用 `experience_engine.compress()` 顶替"废墟熔炼厂"，作为审计输出的收口 Gate。

**Reject 原因**:
职责错误。经考古核实：
- `compress()` 只做了 O→E（记录层），没做 E→C（执行层）
- 真正的"废墟熔炼厂"是 E2C 闭环，不只是 compress()
- `compress()` 是经验沉淀工具，不是收口 Gate

**翻案条件**:
不可翻案。职责定位错误是根本性问题，不是实现细节。

**关联**: ARCH-013 子任务1 / ARCH-014

---

## REJ-002 — ROOT_STATE.md 整体迁移

**最终决定**: ❌ Reject

**原提议**:
GPT 早期建议"ROOT_STATE.md 是运行状态文件，整体迁移到 06_RUNTIME/"。

**Reject 原因**:
核实证伪。ARCH-012 核实结果显示约60%是公理/原则内容，40%是运行状态。整体迁移会导致公理层被掏空——这是一次潜在的 Civilization 内容外泄事故。

**正确做法**:
按内容性质拆分（ARCH-013 子任务3 已执行）：
- 公理保留 00_ROOT/（Tier 1）
- 运行状态迁 06_RUNTIME/state/（Tier 3）

**翻案条件**:
不可翻案。GPT 的"整体迁移"判断基于文件名启发式，不是内容核实。

**关联**: ARCH-012 / ARCH-013 子任务3

**教训**:
分类操作必须先核实内容比例，不能凭文件名或功能猜测。

---

## REJ-003 — 五大工厂其余部分实现

**最终决定**: ❌ Reject

**原提议**:
在实现"废墟熔炼厂"的同时，顺便实现五大工厂的其余部分（仿造工厂/标记工厂/回收工厂/快递站）。

**Reject 原因**:
范围超界。ARCH-014 Mission 明确只做 FA 模式定义 + Smelter Gate 最小护栏。五大工厂其余部分：
- 当前没有证据表明系统存在"内容碎片化、需要自动分类整理"的具体痛点
- 属于"为了完整性而建设"，违反 Axiom_006（不要为了填补空白而建设）

**翻案条件**:
需要新证据——出现"内容碎片化、需要自动分类整理"的具体场景。

**关联**: ARCH-014 / [R1 五大加工厂考古](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/recent_memory/daily/2026-06-28_R1_五大加工厂_废墟熔炼厂_孟婆人格考古.md)

---

## REJ-004 — via_admission 参数绕过路径

**最终决定**: ❌ Reject（已删除）

**原设计**:
[self_evolution.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/self_evolution.py) 的 `apply_json_patch()` 有一个 `via_admission=True` 参数，允许调用方绕过 Admission Engine 直接写入 Tier 1/Tier 2。

**Reject 原因**:
P0 安全漏洞。任何参数约定的"强制"都可以被调用方忽略，只有代码层的硬阻断才是真正的护栏。

**处理方式**:
ARCH-011 已彻底移除 `via_admission` 参数，Tier 1/Tier 2 写入直接抛出 RuntimeError。

**翻案条件**:
不可翻案。安全护栏不能用参数约定，必须是代码强制。

**关联**: ARCH-011

---

## REJ-005 — 在 ARCH-014 中使用现有函数顶替 Gate

**最终决定**: ❌ Reject

**原提议**:
有人可能想用现有的 `compress()` 或其他现成函数顶替 Smelter Gate，避免新建模块。

**Reject 原因**:
违反 ARCH-014 Forbidden 条款——"必须是新的、职责单一的拦截点"。用现成函数顶替会导致：
- 职责混乱（compress 既做压缩又做拦截）
- 无法独立演化（修改 compress 会同时影响两个功能）
- 难以追溯（不知道一次调用是压缩还是拦截）

**处理方式**:
新建独立的 [smelter_gate.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/smelter_gate.py)，职责单一。

**翻案条件**:
不可翻案。职责单一原则是系统可维护性的基础。

**关联**: ARCH-014 子任务2

---

## 登记完成

- [x] compress() 当 Gate — Reject（职责错误）
- [x] ROOT_STATE.md 整体迁移 — Reject（核实证伪）
- [x] 五大工厂其余部分 — Reject（范围超界）
- [x] via_admission 参数绕过 — Reject（安全漏洞，已删除）
- [x] 用现成函数顶替 Gate — Reject（违反职责单一）

*登记时间: 2026-07-13*
