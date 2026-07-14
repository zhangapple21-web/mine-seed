# RUNTIME_BOUNDARY.md — Runtime 与 Civilization 职责边界

> **四层架构中第 2 层（Runtime）的边界文档。**
> 任何 Runtime 写入前必须阅读。

---

## Runtime 唯一允许的内容

`06_RUNTIME/` 下**只允许**以下五类内容：

| 文件 | 含义 | 寿命 |
|------|------|------|
| `ROOT_STATE` | 当前运行指纹（版本、模型、能力） | 每次启动更新 |
| `ACTIVE_MISSION` | 当前进行中的 Mission | Mission 完成即归档 |
| `QUEUE` | 任务队列 | 任务取出即消失 |
| `SESSION` | 当前 Session 信息 | Session 结束即归档 |
| `TODAY` | 今日工作日志 | 明天冻结到 `02_MEMORY/history/` |

---

## Runtime 禁止内容（属于 Civilization）

以下内容**禁止**写入 `06_RUNTIME/`：

```
❌ Principles（原则）        → 02_MEMORY/principles/
❌ Assets（资产）            → 02_MEMORY/assets/
❌ Protocols（协议）         → 02_MEMORY/protocols/
❌ Evidence（证据）          → 02_MEMORY/evidence/
❌ Constraints（约束）       → 02_MEMORY/constraints/
❌ Distillation（蒸馏）      → 02_MEMORY/distillation/
❌ Blueprints（蓝图）        → 02_MEMORY/blueprints/
❌ History（历史）           → 02_MEMORY/history/
```

---

## 边界守卫（C-013/014/015/018）

| 约束 | 守护内容 | 工具 |
|------|----------|------|
| **C-013** | Single Canonical Path（防止嵌套考古） | `admission.py` 路径校验 |
| **C-014** | Time-Series Rotation（防止时间序列膨胀） | 每日轮转 |
| **C-015** | Protocol Wiring Contract（防止协议误分类） | 写入位置校验 |
| **C-018** | Asset Creation Gate（资产创建前门） | 三问审查 |

---

## Runtime 写入规则

```
Runtime 写入
   ↓
属于 Civilization？── 是 → 走 Admission Engine → 02_MEMORY/
   ↓ 否
属于 Runtime 状态？── 否 → 拒绝写入
   ↓ 是
写入 06_RUNTIME/ 允许的五个文件
```

---

## Mission 结束流程

```
Mission 完成
   ↓
ACTIVE_MISSION 归档
   ↓
产生的 Principles/Assets/Protocols 走 Admission Engine
   ↓
产生的 Evidence 写入 02_MEMORY/evidence/
   ↓
清理 06_RUNTIME/ 中残留的中间文件
```

---

## 边界违反示例（禁止行为）

```python
# ❌ 错误：Runtime 直接写入文明层
with open("02_MEMORY/principles/new_principle.md", "w") as f:
    f.write(...)

# ✅ 正确：Runtime 调用 Admission Engine
from admission import evolve, apply_constraint_patch
apply_constraint_patch(constraint_id="PR-006", content="...")

# ❌ 错误：Runtime 写 Principles 到 06_RUNTIME
with open("06_RUNTIME/principles.md", "w") as f:
    f.write(...)

# ✅ 正确：Principles 写入 02_MEMORY/principles/
with open("02_MEMORY/principles/PR-006-xxx.md", "w") as f:
    f.write(...)
```

---

*边界由 AUM-MISSION-ARCH-017 确立。变更需经 C-013/014/015 联合审核。*
