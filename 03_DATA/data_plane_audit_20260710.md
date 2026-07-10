# ACE Data Plane 审计报告 - 2026-07-10

## 审计范围
全量数据源调用追踪 + Runtime 调度能力审计

---

## 一、数据源调用点（12处活跃调用）

### AkShare
| 文件 | 行号 | 功能 |
|------|------|------|
| stock_advisor.py | 144 | `ak.stock_zh_a_spot_em()` — 全市场实时行情 |
| stock_advisor.py | 227 | `ak.stock_zh_a_hist()` — 历史K线 |
| stock_advisor.py | 247 | `ak.stock_individual_fund_flow()` — 资金流向 |
| dragon_leader_v2.py | 211 | `ak.stock_board_concept_name_em()` — 板块概念（降级） |
| dragon_leader_v2.py | 285 | `ak.stock_zh_a_spot()` — 全市场快照 |

### 腾讯API
| 文件 | 行号 | 功能 |
|------|------|------|
| stock_query.py | 65 | `qt.gtimg.cn/q=` — 实时行情 |
| stock_query.py | 185 | `ifzq.gtimg.cn/fqkline/get` — 历史K线 |
| stock_query.py | 236 | `qt.gtimg.cn/q=ff_` — 资金流向 |

### 东财直连
| 文件 | 行号 | 功能 |
|------|------|------|
| dragon_leader_v2.py | 255 | `push2.eastmoney.com/clist/get` — 板块排行 |

### Baostock（条件触发）
| 文件 | 行号 | 功能 |
|------|------|------|
| dragon_leader_v2.py | 355 | `bs.query_stock_industry()` — 行业分类（降级） |

### YFinance（手动触发）
| 文件 | 行号 | 功能 |
|------|------|------|
| signal_discovery.py | 590 | `yf.download()` — S&P500 数据 |

---

## 二、Capability × Provider 矩阵

| Capability | AkShare | Tencent | Mootdx | EastMoney | Baostock | YFinance |
|------------|---------|---------|--------|-----------|----------|----------|
| realtime_quote | ✓ | ✓ | ✗(死代码) | — | — | — |
| history_kline | ✓ | ✓ | ✗(死代码) | — | — | — |
| fund_flow | ✓ | ✓ | — | — | — | — |
| board_sector | ✓ | — | — | ✓ | — | — |
| industry_cls | — | — | — | — | ✓ | — |
| us_stock_history | — | — | — | — | — | ✓ |

---

## 三、重复实现（5对）

| 重复 | 模块A | 模块B | 状态 |
|------|-------|-------|------|
| 全市场行情 | stock_advisor (akshare spot_em) | dragon_leader (akshare spot) | 活跃 |
| 腾讯行情解析 | stock_query (活跃) | dragon_leader (死代码) | 清理完成 |
| 历史K线 | stock_advisor + stock_query | dragon_leader (死代码) | 清理完成 |
| 资金流向 | stock_advisor + stock_query | — | 活跃 |
| 板块数据 | dragon_leader 内部双源 | — | 活跃 |

---

## 四、问题修复记录

| 问题 | 修复 | 状态 |
|------|------|------|
| 资金流降级返回随机数 | 改为调用 `StockQuery.get_fund_flow()` | ✅ 已修复 |
| mootdx 死代码 | 移除 `get_tdx_client()`/`get_mootdx_kline()`/`get_mootdx_quotes()` | ✅ 已修复 |
| 腾讯批量行情死代码 | 移除 `get_tencent_batch()` | ✅ 已修复 |
| 随机因子模拟 | 第1层因子筛选已改为真实指标 | ✅ 已修复 |
| 异常吞掉 | stock_query.py 已加 logger.warning | ✅ 已修复 |

---

## 五、Runtime 调度能力复用分析

### 可直接复用（已验证）

| Miner 能力 | 映射到 Data Plane | 代码证据 |
|-----------|------------------|---------|
| WorkerRegistry | ProviderRegistry | task_router_v2.py L76-L140 |
| get_fallback_chain | 数据源 fallback 链 | task_router_v2.py L351-L358 |
| ObservationLog | DataQualityLog | task_router_v2.py L143-L228 |
| ModelRouter.score | 四维评分（延迟/完整率/可用率/成本） | model_router.py L69-L100 |
| routing_constraints | AVOID/PREFER 约束 | routing_constraints.json |
| auto_retire/auto_promote | Provider tier 升降 | model_router.py L143-L191 |
| JudgeLayer | 数据交叉验证 | task_router_v2.py L361-L494 |
| O→E→C→R 闭环 | 观察→经验→约束→路由 | constraint_proposer.py |

### 缺失（需适配层）

| 缺失点 | 说明 |
|--------|------|
| Capability Registry | 显式声明实时行情/历史K线等能力 |
| Provider 基类 | 统一 `fetch(capability, params)` 接口 |
| Cache 层 | 同一只股票一天内不重复请求 |
| 数据质量验证 | schema 校验、字段完整性、交叉验证 |

---

## 六、结论

**不需要独立的 Data Router。** Miner 体系已经具备 Provider 调度所需的全部核心能力（Registry/Fallback/Quality/Constraint/Judge/O→E→C→R），只需一个适配层即可扩展为通用 Provider Router。

后续路线：
1. 修复现有问题（当前阶段 ✅）
2. 固化审计结果（本文件）
3. 设计 Capability + Provider 抽象接口（RFC）
4. 逐步迁移旧模块到新架构
