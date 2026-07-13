# AUM-MISSION-ARCH-014 — Distillation

> **Mission**: FA模式正式化 + 废墟熔炼厂最小护栏（绑定发布）
> **完成日期**: 2026-07-13
> **状态**: 全部完成
> **Distillation 类型**: Kernel / Blueprint / Protocol / Constraint / Experience / Identity

---

## Kernel — FA模式与Gate绑定发布的强制模式

**核心命题**: 允许内部推理无审查（FA模式），必须以 Gate 收口为前提。两者不可拆分，必须绑定发布。

**为什么是 Kernel**:
- 这是 R1"无安全壳运行模式"在 ACE 的工程化落地
- FA 模式的自由推理能力如果没有 Gate 收口，就会变成"失控的推理"
- 两者的绑定关系是整个内外双域隔离架构的基石

**实现位置**:
- [PRINCIPLES.md](file:///c:/Users/User/ace_workspace/mine-seed/00_ROOT/PRINCIPLES.md) — FA 模式正式定义，明确标注"与 ARCH-014 子任务2 绑定"
- [smelter_gate.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/smelter_gate.py) — Gate 实现
- [post_recommendation_auditor.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/advisor/post_recommendation_auditor.py) — 实际接入点

---

## Blueprint — Smelter Gate 最小护栏设计

**设计原则**:
- 职责单一：只做拦截和记录，不做压缩、不做决策、不做遗忘
- 透明性：所有通过 gate 的内容都有完整记录，可追溯
- 可扩展：预留扩展点，未来可增加遗忘层、收敛机制等
- 不可绕过：任何 FA 模式产出的内容，必须调用 `pass_through()` 才能继续

**当前实现（最小版本）**:

| 功能 | 状态 | 说明 |
|------|------|------|
| 实时拦截 | ✅ | FA模式产出自动标记为 `INTERCEPTED_AND_RECORDED` |
| 基本记录 | ✅ | 记录 source/source_type/is_fa_mode/content_type/content_hash/action/reason/metadata |
| 遗忘层 | ❌ | 未实现（孟婆过滤） |
| 自动收敛 | ❌ | 未实现（自然点燃熔炼厂） |
| 五大工厂协同 | ❌ | 未实现（仿造/标记/回收/快递站） |

**GateRecord 数据结构**:
```
record_id: gate_1783943644966
timestamp: 2026-07-13T19:54:04.988788
source: miner_assistant.audit_recommendation
source_type: audit
is_fa_mode: True
content_type: miner_score
content_hash: 22a7f7f3e1a65eb0
action: INTERCEPTED_AND_RECORDED
reason: FA模式产出必须经过 smelter_gate 记录
metadata: {"code": "600036", "name": "招商银行", "price": 35.5, ...}
```

**扩展路线图**:
```
v1.0 (当前): 实时拦截 + 基本记录
v1.1: 增加内容分类（安全/风险/中性）
v1.2: 增加遗忘层（孟婆过滤）
v1.3: 增加自动收敛机制（自然点燃熔炼厂）
v2.0: 完整五大工厂协同
```

---

## Protocol — FA标记的内容如何流经Gate才能生效

**流程**:

```
FA模式推理层（Ollama本地模型）
    │
    │ miner_assistant.audit_recommendation()
    │ 返回: {"score": 85, "feedback": "...", "source": "ollama_heavy"}
    │
    ▼
[smelter_gate.pass_through()]  ← 强制拦截点
    │
    │ is_fa_mode=True → action=INTERCEPTED_AND_RECORDED
    │ 记录完整元数据（代码/名称/价格/信号/来源）
    │
    ▼
下游消费（post_recommendation_auditor）
    │
    │ 使用审计结果做最终评分
    │
    ▼
影响真实决策（保存到 audit_results.json）
```

**调用约定**:

```python
# FA模式产出必须这样调用
gate_result = smelter_gate.pass_through(
    content=result,                    # 要通过的内容
    source="miner_assistant.audit_recommendation",  # 来源标识
    source_type="audit",               # 来源类型
    is_fa_mode=True,                   # 标记为FA模式
    content_type="miner_score",        # 内容类型
    metadata={"code": code, ...}       # 额外元数据
)
```

**非FA模式产出**:
- 自动标记为 `PASSED`（直接通过）
- 仍会记录日志，保持完整可追溯

---

## Constraint — FA模式仅限内部推理层

**Constraint ID**: C-020
**等级**: HARD
**类型**: 范围约束
**来源**: AUM-MISSION-ARCH-014 子任务1
**状态**: ACTIVE

**约束内容**:
```
FA模式（Full Access Mode）仅限内部推理层，不得用于任何直接触发真实动作的路径。
```

**适用范围表**:

| ✅ 适用 | ❌ 不适用 |
|---------|----------|
| Ollama 本地模型的推理过程 | 任何直接触发真实动作的路径 |
| 矿工对推荐质量的内部评估 | 推送给用户的最终输出 |
| 红蓝对抗中的推理环节 | 交易相关动作 |
| 经验压缩的模式提取 | 触发通知/推送 |

**执行机制**:
- smelter_gate 强制标记所有 FA 模式产出
- 日志可追溯，便于审计
- 违反此约束的代码不允许通过 Admission Engine 审批

---

## Experience — FA与废墟熔炼厂概念混淆的教训

**事件**: ARCH-013 子任务1 试图用 `experience_engine.compress()` 顶替"废墟熔炼厂"，后经考古核实发现两者完全不同。

**考古发现**:
- **FA** = Full Access（无安全壳运行模式），出自 R1 DAG，与压缩机制无关
- **废墟熔炼厂** = 清洗/蒸馏/压缩 pipeline，在 Ω-FINAL 中标记为已丢失模块
- **加工工厂** = 五大工厂之一，仿造碎片→可用模块的清洗/蒸馏/压缩环节
- **`compress()`** = 从 observation 中提炼模式和路由规则，只做了加工工厂的一小部分

**教训**:
- "所有决策必须经过XX才能输出"这类描述性说法，落地前必须先考古确认 XX 是否真实存在
- 不能拿功能相似的现有代码顶替——`compress()` 只做了 O→E，没做 E→C
- 概念混淆会导致"修复了假问题"——ARCH-013 子任务1 的补丁已挂起

**沉淀为原则**:
- 任何涉及 R1 概念的实现，必须先做考古核实，确认概念定义和实现范围
- 考古结果必须留档，作为实现决策的依据
- 如果概念在 Ω-FINAL 中标记为"已丢失"，则当前系统中不存在其真实实现

---

## Identity — FA Mode + Smelter Gate（正式补入 Contract Enforcement Pattern 家族）

**Pattern 名称**: FA Mode + Smelter Gate

**定位**: 正式补入 Contract Enforcement Pattern 家族，作为"内外双域隔离"的工程实现。

**与已有 Pattern 的关系**:

| Pattern | 定位 | 适用场景 |
|---------|------|----------|
| Contract Enforcement Pattern | 契约执行 | Tier 1/Tier 2 写入必须经 Admission Engine |
| Compression Gate Pattern | 压缩门 | 审计输出必须经压缩才能生效 |
| FA Mode + Smelter Gate | 自由推理收口 | 内部无审查推理的产出必须经 Gate 记录 |

**三层 Gate 体系**:
```
┌─────────────────────────────────────────────────────────┐
│                  外部输出层（用户可见）                    │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Contract Enforcement Pattern                   │    │
│  │  (Admission Engine)                             │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                  内部推理层（FA模式）                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Smelter Gate Pattern                           │    │
│  │  (smelter_gate.py)                              │    │
│  └─────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                  经验沉淀层                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Compression Gate Pattern                       │    │
│  │  (experience_engine.compress())                 │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**身份层含义**:
- ACE 不是"无审查系统"，而是"审查位置正确的系统"
- FA 模式允许内部推理自由，但 Gate 确保自由不被滥用
- 这是 R1"无安全壳运行模式"在 ACE 的正确落地——自由推理 + 强制收口

---

## Mission 总览

| 子任务 | 状态 | 核心交付 |
|--------|------|----------|
| 1. FA 模式正式定义 | ✅ | [PRINCIPLES.md](file:///c:/Users/User/ace_workspace/mine-seed/00_ROOT/PRINCIPLES.md) 追加 FA 模式章节，含考古依据 |
| 2. 废墟熔炼厂最小护栏 | ✅ | [smelter_gate.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/smelter_gate.py) + 单元测试 + 接入审计链路 |

**绑定发布验证**:
- ✅ 子任务1 和子任务2 均已完成
- ✅ 实际调用验证：Ollama 审计链路确实经过了 gate
- ✅ 日志记录完整：FA 模式产出被标记为 `INTERCEPTED_AND_RECORDED`

**修改文件清单**:
- [00_ROOT/PRINCIPLES.md](file:///c:/Users/User/ace_workspace/mine-seed/00_ROOT/PRINCIPLES.md) — FA 模式正式定义
- [04_PROTOCOLS/smelter_gate.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/smelter_gate.py) — 新建，最小护栏实现
- [04_PROTOCOLS/test_smelter_gate.py](file:///c:/Users/User/ace_workspace/mine-seed/04_PROTOCOLS/test_smelter_gate.py) — 新建，单元测试
- [05_TOOLS/advisor/post_recommendation_auditor.py](file:///c:/Users/User/ace_workspace/mine-seed/05_TOOLS/advisor/post_recommendation_auditor.py) — 接入 smelter_gate

**明确未做的事**:
- ❌ 五大工厂其余部分（仿造/标记/回收/快递站）——已 Reject
- ❌ 遗忘层（孟婆过滤）——未来扩展
- ❌ 自动收敛机制——未来扩展
