# ASSET_INDEX.md — Asset Activation Status

> 所有文明资产的激活状态索引。
> 状态机：Discovered → Indexed → Classified → Learned → Activated → Validated → Distilled

---

## Activation Status 状态机

```
Discovered
    ↓ 发现新知识源
Indexed
    ↓ 建立索引
Classified
    ↓ 分类标签
Learned
    ↓ 学习吸收
Activated
    ↓ 可被 Mission 引用
Validated
    ↓ 验证有效
Distilled
    ↓ 蒸馏沉淀
```

### 状态定义

| 状态 | 说明 | 是否可被引用 |
|------|------|-------------|
| **Discovered** | 发现新知识源，尚未处理 | ❌ |
| **Indexed** | 已建立索引，可被搜索 | ❌ |
| **Classified** | 已分类，有标签 | ❌ |
| **Learned** | 已学习，理解内容 | ❌ |
| **Activated** | 已激活，可被 Mission 引用 | ✅ |
| **Validated** | 已验证，确认有效 | ✅ |
| **Distilled** | 已蒸馏，沉淀为文明资产 | ✅ |

---

## Learning Queue Priority Score

资产进入 Learning Queue 后，按以下优先级排序：

| 因子 | 权重 | 说明 |
|------|------|------|
| **Novelty** | 30% | 新发现的知识，之前未接触过 |
| **Reuse** | 25% | 已有资产的复用价值 |
| **Mission Related** | 20% | 与当前 Mission 的相关性 |
| **Recency** | 15% | 时效性，越新越优先 |
| **Evidence Quality** | 10% | 证据质量，来源可信度 |

### 计算方式

```
Priority = Novelty × 0.3 + Reuse × 0.25 + MissionRelated × 0.2 + Recency × 0.15 + EvidenceQuality × 0.1
```

---

## Asset Schema

每个资产记录包含：

```json
{
    "asset_id": "string",
    "title": "string",
    "type": "principle|protocol|decision|observation|knowledge",
    "status": "discovered|indexed|classified|learned|activated|validated|distilled",
    "priority_score": 0.0,
    "tags": ["tag1", "tag2"],
    "source": "string",
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "activated_by": "mission_id|agent_id",
    "validated_by": "mission_id|agent_id",
    "distilled_to": "asset_id|null"
}
```

---

## Current Assets

> 此列表由 `knowledge_activation.py` 自动生成，手工修改无效。

<!-- ASSET_LIST_BEGIN -->

| # | ID | Title | Type | Status | Priority | Tags |
|---|---|---|---|---|---|---|
| 1 | ccebb0d6 | PUBLICATION_PRINCIPLE | protocol | discovered | 0.6 | - |
| 2 | 5de67e9c | README | protocol | discovered | 0.6 | - |
| 3 | 232a73f8 | recovery_protocol | protocol | discovered | 0.6 | - |
| 4 | 05dcb74b | gate_topology | knowledge | discovered | 0.6 | - |
| 5 | 7576fcf0 | daily_discovery_20260713 | knowledge | activated | 0.39 | - |
| 6 | bc0fc14d | daily_discovery_20260714 | knowledge | activated | 0.39 | - |
| 7 | ad1cd9a0 | discovery_20260714 | knowledge | activated | 0.39 | - |
| 8 | 6c4e4a1f | CONTRACT | protocol | activated | 0.39 | - |
| 9 | 4d0fc1f6 | first_day | protocol | activated | 0.39 | - |

<!-- ASSET_LIST_END -->