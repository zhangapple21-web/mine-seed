# Experiment Zone（自由区）— 边界约束

> **来源**: R1 四界体系考古（2026-06-28）
> **状态**: ACTIVE
> **原则**: 允许任何实验，但禁止直接修改生产资产

---

## 定义

```
自由区 = 允许任何实验、允许失败、允许胡思乱想、允许长怪东西
```

这里**没有 Admission**，**没有 Governor**，**没有 Constraint**。
只有：**Experiment**。

---

## 边界

### 允许

| 活动 | 输出位置 |
|------|----------|
| 推演 | `logs/` |
| 失败 | `snapshots/` |
| 路由实验 | `reports/` |
| 约束实验 | `reports/` |
| 词汇实验 | `reports/` |
| 图谱实验 | `reports/` |
| 论文熔炼 | `reports/` |

### 禁止

- ❌ 直接修改 `world_models/*`
- ❌ 直接修改 `active_manifest.json`
- ❌ 直接修改 `02_MEMORY/civilization_assets/*`
- ❌ 直接修改 `04_CONSTRAINT/*`
- ❌ 跳过 Admission 将实验结果写入 Repository

---

## 与其他工厂的协同

```
自由区（产生实验）
    ↓
失败
    ↓
孟婆（过滤污染）
    ↓
废墟熔炼厂（拆解/提炼）
    ↓
新 Seed
    ↓
实验室（验证）
    ↓
Admission（准入）
    ↓
Repository（文明资产）
```

---

## 输出规范

所有自由区实验输出必须包含：

```json
{
  "experiment_id": "EXP-YYYYMMDD-NNN",
  "hypothesis": "实验假设",
  "method": "实验方法",
  "result": "PASS|FAIL|INCONCLUSIVE",
  "evidence": {},
  "timestamp": "ISO8601"
}
```

---

*自由区是创新的土壤。馆长诞生于自由区，因为没有约束，它才特别会长东西。但自由不等于无序——输出位置有限定，生产资产有保护。*