# Decision Record: Evolution 作为 System Property 而非 Capability

> **Decision ID**: DR-2026-07-15-001
> **Status**: DECIDED
> **Decider**: ARCH-024 裁定2
> **Created**: 2026-07-15

---

## 决策内容

**Evolution（演化）被归类为 System Property（系统涌现属性），而非 Capability（能力）。**

---

## 依据

### 1. 定义区分

**Capability（能力）**：系统**能做什么**——可以被主动调用、测试、度量。

- 例如：Observe（观察）、Transform（变换）、Act（执行）
- 特点：有明确的输入输出，可以被显式触发

**System Property（系统涌现属性）**：系统**做了什么之后发生了什么**——是运行过程的涌现结果，不是可以被主动调用的功能。

- 例如：稳定性、可靠性、演化
- 特点：无法被显式触发，只能通过持续运行来观察

### 2. Evolution 的本质

Evolution 描述的是系统在持续运行过程中，通过经验积累、约束调整、架构迭代而发生的改变。它不是某个可以被调用的函数或模块，而是整个闭环运行的结果。

用公式表达：

```
Evolution = f(Observe → Transform → Act → Observe, 时间)
```

没有独立的"演化"操作，只有持续的观察-变换-执行闭环在时间维度上的累积效应。

### 3. 验证方式

- **Capability**：可以构造单元测试，验证输入→输出
- **System Property**：只能通过长期观察，验证系统是否发生了变化

Evolution 无法通过单元测试验证——你无法在测试中"调用演化"。你只能运行系统一段时间，然后观察它是否变得更智能/更稳定/更高效。

---

## ARCH-020 的原始发现

Red Team 在 ARCH-020 中指出：

> "Evolution 是缺失的 Capability"——这个表述可能引起误解。更准确的表述应该是："系统缺少对演化的显式支持"。

但"支持演化"不等于"演化本身是 Capability"。支持演化的方式包括：
- E→C 闭环（经验→约束）
- 记忆沉淀
- 架构迭代机制

这些是 Capability，但 Evolution 本身是结果。

---

## 决策结论

| 项目 | 归类 | 理由 |
|------|------|------|
| Evolution | **System Property** | 不是"能做什么"，而是"做了之后发生了什么" |
| E→C Closure | **Capability**（Transform 子类） | 可以被显式触发：监听失败→生成约束 |
| Memory Distillation | **Capability**（Transform 子类） | 可以被显式触发：读取经验→压缩→存储 |

---

## 遗留问题

如果 Evolution 是 System Property，那么"系统是否在演化"如何度量？

**建议指标**：
- 约束库增长率（每周新增多少约束）
- 经验沉淀速率（每周压缩多少经验）
- 失败重复率（相同错误是否在减少）

这些指标需要单独的设计文档。

---

## 变更记录

| 日期 | 变更内容 |
|------|---------|
| 2026-07-15 | 创建决策记录，确认 Evolution 为 System Property |

---

*此文档为 ARCH-024 板块一交付物，响应裁定2。*