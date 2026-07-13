# Lineage Schema — 血缘记录标准格式

> **版本**: v1.0
> **日期**: 2026-07-13
> **目的**: 定义文明资产血缘记录的统一格式，确保 Continuity 约束可验证

---

## Schema 定义

每个文明资产的血缘记录包含以下字段：

```json
{
  "asset_id": "唯一标识符，格式：NNN_asset_name",
  "name": "资产名称",
  "category": "所属分类（公理层/原则层/治理层/能力层/角色层/协议层/认知层/架构层）",
  "origin_repository": "来源仓库",
  "origin_file": "来源文件路径",
  "origin_mission": "产生该资产的 Mission",
  "distillation_date": "蒸馏日期（YYYY-MM-DD）",
  "distilled_by": "蒸馏者（local_TRAE / cloud_GPT / etc）",
  "supporting_evidence": ["支撑证据列表"],
  "parent_asset": "父资产 ID（从哪个更早的资产演化来的，没有则 null）",
  "superseded_by": "被哪个新资产替代（没有则 null）",
  "status": "状态（active / superseded / deprecated / reference_only / partial）",
  "rebuild_hint": "重建提示（多少行可重建，或不可重建）",
  "confidence": "可信度（high / medium / low）",
  "gaps": ["已知缺口列表"]
}
```

---

## 字段详解

### 必填字段（100% 必须有）

| 字段 | 说明 | 缺失处理 |
|------|------|----------|
| asset_id | 唯一标识 | 禁止入库 |
| name | 资产名称 | 禁止入库 |
| category | 所属分类 | 禁止入库 |
| origin_repository | 来源仓库 | 标 unknown |
| origin_mission | 产生的 Mission | 标 unknown，但资产只能是 partial 状态 |
| distillation_date | 蒸馏日期 | 标 unknown |
| status | 状态 | 禁止入库 |
| rebuild_hint | 重建提示 | 禁止入库 |

### 可选字段（推荐有）

| 字段 | 说明 | 缺失处理 |
|------|------|----------|
| origin_file | 来源文件路径 | 可空 |
| distilled_by | 蒸馏者 | 可空 |
| supporting_evidence | 证据列表 | 可空数组 |
| parent_asset | 父资产 | null |
| superseded_by | 被替代 | null |
| confidence | 可信度 | 默认 medium |
| gaps | 缺口列表 | 空数组 |

---

## 状态定义

| 状态 | 含义 | 准入条件 |
|------|------|----------|
| **active** | 活跃使用中 | origin_mission 明确，evidence 充分，confidence ≥ medium |
| **reference_only** | 仅作参考，未实际使用 | 有参考价值但未落地，如 Recovery v2 |
| **superseded** | 已被替代 | superseded_by 指向新资产 |
| **deprecated** | 已废弃 | 不再使用，保留记录 |
| **partial** | 信息不完整 | origin_mission 或 evidence 缺失 |

---

## 分类定义

| 分类 | 含义 | 例子 |
|------|------|------|
| 公理层 | 不可修改的底层公理 | L∞ 本源层, R2 五元公理 |
| 原则层 | 指导原则 | 研究原则库, DFP-001 |
| 治理层 | 治理/审查/准入机制 | Governor, Admission, Mengpo |
| 能力层 | 能力抽象/路由/监控 | CSP, ModelRouter, ProviderWatchdog |
| 角色层 | 角色定义/分工 | 三角色系统 |
| 协议层 | 协议/流程规范 | Mission, Recovery, ExperienceEngine |
| 认知层 | 认知/判断/本体论 | JudgmentEngine, Ontology |
| 架构层 | 系统架构/蓝图 | 矿山体系, ContinuityEngine, ACE Civilization OS |

---

## 准入约束

### 孤儿资产禁止标 active

如果 origin_mission 是 unknown，资产状态只能是 **partial**，不能标 active。

### 断链必须修复

如果 parent_asset 指向不存在的资产，必须修复后才能标 active。

### 新资产必须同步登记 lineage

任何新资产进入 civilization_assets/ 时，必须同步更新 lineage_index.json。

---

## 血缘链结构

```
Origin Repository
    ↓
Origin Mission
    ↓
Supporting Evidence
    ↓
Distillation
    ↓
Asset (active)
    ↓
Superseded by (如果有)
    ↓
New Asset
```

---

## 查询接口

lineage_engine.py 提供以下查询：

| 接口 | 功能 |
|------|------|
| `get_asset(asset_id)` | 获取单个资产的血缘记录 |
| `get_lineage_chain(asset_id)` | 获取完整血缘链（向上追溯 parent） |
| `find_orphans()` | 检测孤儿资产（origin_mission 未知） |
| `find_broken_chains()` | 检测断链（parent_asset 不存在） |
| `get_stats()` | 获取统计信息 |
| `query_by_origin(repository)` | 按来源仓库查询资产 |

---

*版本：v1.0*
*日期：2026-07-13*
*Mission：Lineage 血缘系统建设*
