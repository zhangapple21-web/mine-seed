# EGP-WR: Worker Registry（矿工注册协议）

**状态**: Draft  
**依据**: EGP宪法 Section 3.3  
**作者**: 疯子(CCO)  
**日期**: 2026-06-16  

---

## 0. 一句话

矿工必须注册才能上岗，注册即声明能力，考核即决定去留。

---

## 1. 为什么需要注册

现在矿工是谁？不知道。

哪些在跑？哪些挂了？哪些早该淘汰？不清楚。

没有花名册，调度就是盲派。

```
CCO收到任务 → 随便选一个矿工 → 碰运气
```

有了注册表：

```
CCO收到任务 → 查Worker Registry → 选最合适的矿工 → 带约束派单
```

---

## 2. 矿工档案

每个矿工一份档案：

```json
{
  "worker_id": "nim_llama_70b",
  "provider": "nvidia_nim",
  "status": "active",
  "tier": "primary",
  "capabilities": {
    "canonical_v2": { "sr": 0.75, "avg_latency": "6s" },
    "persona_deep": { "sr": 0.70, "avg_latency": "8s" },
    "slice_classification": { "sr": 0.78, "avg_latency": "5s" }
  },
  "constraints": [],
  "stats": {
    "total_tasks": 156,
    "success": 118,
    "fail": 38,
    "last_used": "2026-06-16T12:00+08:00"
  },
  "registered": "2026-06-01",
  "blacklisted": false
}
```

### 字段说明

| 字段 | 含义 |
|------|------|
| worker_id | 唯一标识，通常=模型名 |
| provider | 算力来源（NIM/GitHub/GLM/OR） |
| status | active/idle/testing/blacklisted/retired |
| tier | primary(主力)/reserve(储备)/candidate(候选) |
| capabilities | 各任务的SR和延迟 |
| constraints | 该矿工身上的活跃约束 |
| stats | 运行统计 |
| blacklisted | 是否被列入黑名单 |

---

## 3. 矿工等级

### primary（主力池）

当前直接承担生产任务。

标准：SR ≥ 70% + 延迟 ≤ 10s + 稳定运行7天+

当前主力：
```
nim_llama_70b    SR≈75%  延迟≈6s
glm_flash        SR≈80%  延迟≈3s
nim_gpt_120b     SR≈72%  延迟≈8s
```

### reserve（储备池）

已验证可用，但不是第一选择。

标准：SR ≥ 60% + 延迟 ≤ 30s

触发：主力池全忙或限流时启用。

当前储备：
```
nim_step_37_flash  （待验证）
gemini_flash       （待benchmark）
```

### candidate（候选池）

新矿工，尚未完成benchmark。

必须先通过canonical_v2 + slice_classification双测试，SR ≥ 60%才能升级到reserve。

当前候选：
```
gemini_flash  — benchmark未完成
```

---

## 4. 上岗流程

```
新矿工发现
  → 注册为candidate
  → 跑benchmark（B类任务，不抢A类资源）
  → 达标 → 升级reserve
  → 不达标 → 记录原因，淘汰或重测
```

### Benchmark标准

参照M2.7（因45-120s过慢被淘汰）：

| 指标 | 及格线 | 优秀线 |
|------|--------|--------|
| canonical_v2 SR | ≥ 60% | ≥ 75% |
| slice_classification SR | ≥ 60% | ≥ 80% |
| 平均延迟 | ≤ 30s | ≤ 10s |
| 稳定性(5轮) | 无超时 | 无超时 |

### Gemini Flash的特殊情况

Gemini需要走云电脑代理（One API），增加了网络延迟。
benchmark时需分离：模型延迟 vs 代理延迟。

如果模型延迟本身优秀但代理拖后腿，可进储备但标注"proxy_required"。

---

## 5. 淘汰流程

### 自动淘汰

```
连续3次任务失败 → 暂停调度 → 生成constraint draft
5次中4次失败 → blacklisted
```

### 手动淘汰

Host可以直接宣判。必须有原因记录。

### 淘汰记录

```json
{
  "worker_id": "gh_4o",
  "action": "blacklisted",
  "reason": "canonical_v2 SR=20%，连续8败",
  "decision_by": "host",
  "date": "2026-06-15",
  "replacement": "nim_llama_70b"
}
```

### 复活

黑名单不是永久。30天后可以申请重测。

如果重测达标，解除黑名单，降级为candidate重新走上岗流程。

---

## 6. 黑名单

当前黑名单：

| 矿工 | 原因 | 封禁日期 | 约束ID |
|------|------|----------|--------|
| gh_r1 | canonical_v2 8败 | 2026-06-14 | constraint_006 |
| nim_ultra_550b | 多任务失败 | 2026-06-14 | constraint_007 |
| gh_4o | canonical_v2 SR=20% | 2026-06-15 | constraint_001 |

黑名单矿工：CCO禁止派单，Constraint Engine自动拦截。

---

## 7. 当前矿工注册表

### 主力池

| 矿工 | 提供商 | canonical_v2 | persona_deep | 延迟 | 状态 |
|------|--------|-------------|-------------|------|------|
| nim_llama_70b | NIM | 75% | 70% | 6s | active |
| glm_flash | 智谱 | 80% | — | 3s | active |
| nim_gpt_120b | NIM | 72% | — | 8s | active |

### 储备池

| 矿工 | 提供商 | 备注 | 状态 |
|------|--------|------|------|
| nim_step_37_flash | NIM | 待验证 | idle |
| or_llama_33_70b | OR | 429限速 | idle |

### 候选池

| 矿工 | 提供商 | 备注 | 状态 |
|------|--------|------|------|
| gemini_flash | Google | benchmark未完成，需走One API代理 | testing |

### 已淘汰

| 矿工 | 原因 | 淘汰日期 |
|------|------|----------|
| gh_4o | SR=20% | 2026-06-15 |
| gh_r1 | 8连败 | 2026-06-14 |
| nim_ultra_550b | 多任务失败 | 2026-06-14 |
| M2.7 | 延迟45-120s | 2026-06-13 |

---

## 8. 能力声明

矿工不是什么都行。每个矿工必须声明自己能做什么。

### 能力矩阵

| 矿工 | canonical_v2 | persona_deep | slice_classification | upgrade_analysis |
|------|-------------|-------------|---------------------|-----------------|
| nim_llama_70b | ✅ 75% | ✅ 70% | ✅ 78% | ⚠️ 65% |
| glm_flash | ✅ 80% | ❌ | ✅ 78% | ⚠️ 72% |
| nim_gpt_120b | ✅ 72% | ❌ | ⚠️ 60% | ✅ 72% |

CCO根据能力矩阵选矿工，不盲派。

```
任务: canonical_v2
最佳选择: glm_flash (SR=80%)
备选: nim_llama_70b (SR=75%)
禁止: gh_4o (constraint_001)
```

---

## 9. 落地路径

| 阶段 | 动作 | 时间 |
|------|------|------|
| P0 | 手动维护注册表（本文档） | 现在 |
| P1 | benchmark结果自动更新到注册表 | 本周 |
| P2 | CCO调度时查能力矩阵选矿工 | 下周 |
| P3 | 淘汰/复活自动化 | 后续 |

---

## 10. 和其他协议的关系

```
EGP（宪法）— 定义三权分离
  ├─ SA（调度者权限）— CCO怎么调度
  ├─ CE（约束引擎）— 约束怎么生成和注入
  └─ WR（矿工注册）— 矿工怎么管理

三份协议形成一个闭环：
CE生成约束 → SA执行约束 → WR记录矿工状态 → CE观察结果 → 新约束
```
