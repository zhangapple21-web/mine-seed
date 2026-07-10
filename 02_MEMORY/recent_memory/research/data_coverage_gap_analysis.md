# A股数据覆盖缺口分析

> 基于AKShare数据字典(reference_akshare_data_dictionary.md)与当前mootdx+adata实际能力的对照
> 日期: 2026-06-21
> 原则: Constraint_000 — 不急着填空白，先确认空白是否在生长

## 当前可用数据源

### mootdx (主力)
| 数据类型 | 接口 | 状态 |
|---------|------|------|
| 个股日K | client.bars(frequency=9) | ✅ |
| 个股5min | client.bars(frequency=0) | ✅ |
| 个股周K | client.bars(frequency=10) | ✅ |
| 个股月K | client.bars(frequency=11) | ✅ |
| 指数日K | client.index(frequency=9) | ✅ |
| 指数5min | client.index(frequency=0) | ✅ |
| 股票列表 | client.stocks() | ✅ |

### adata (补充)
| 数据类型 | 接口 | 状态 |
|---------|------|------|
| 指数日K | adata.stock.info.get_market_index() | ✅ |
| 成分股 | adata.stock.info.index_constituent() | ✅ |
| 个股日K | — | ❌ 停更失效 |
| 实时行情 | — | ❌ 停更失效 |
| ETF | — | ❌ 停更失效 |
| 概念板块 | — | ❌ 停更失效 |

## 数据字典揭示的覆盖缺口

### Tier-1: 研究域高频需要但当前缺失
| 数据类型 | 用途 | 字典接口示例 | 当前状态 |
|---------|------|-------------|---------|
| 行业板块 | 板块轮动信号 | stock_board_industry_* | ❌ 无源 |
| 概念板块 | 热点追踪 | stock_board_concept_* | ❌ adata失效 |
| 沪深港通 | 北向资金信号 | stock_hsgt_* | ❌ 无源 |
| 资金流向 | 量价背离检测 | stock_individual_fund_flow_* | ❌ 无源 |
| 涨停板 | 极端行情画像 | stock_zt_pool_* | ❌ 无源 |

### Tier-2: 有价值但非紧急
| 数据类型 | 用途 | 字典接口示例 | 当前状态 |
|---------|------|-------------|---------|
| 龙虎榜 | 机构行为 | stock_lhb_detail_em | ❌ 无源 |
| 融资融券 | 杠杆水平 | stock_margin_* | ❌ 无源 |
| 大宗交易 | 大额交易信号 | stock_dzjy_* | ❌ 无源 |
| 停复牌 | 事件日历 | stock_tfp_em | ❌ 无源 |
| 分红配送 | 除权影响 | stock_fhps_* | ❌ 无源 |
| 千股千评 | 综合评价参考 | stock_qgpj_em | ❌ 无源 |

### Tier-3: 低频/特殊场景
| 数据类型 | 用途 | 当前状态 |
|---------|------|---------|
| 年报季报 | 基本面信号 | ❌ 无源 |
| 分析师指数 | 一致预期 | ❌ 无源 |
| 机构调研 | 信息密度 | ❌ 无源 |
| ESG评级 | 长期因子 | ❌ 无源 |
| 股票质押 | 风险信号 | ❌ 无源 |

## a-stock-data (simonlin1212) 可能补位

疯子提到的a-stock-data项目声称7层28端点，含：
- mootdx(TCP) → 已验证 ✅
- 腾讯财经 → HTTP，IP封禁风险低
- 东财 → HTTP，与akshare同源但更轻量
- 百度 → HTTP

**关键问题**：a-stock-data的HTTP接口是否也面临与akshare相同的反爬问题？
→ 需要等疯子部署后观察实际稳定性

## 观察而非行动

当前不急着扩展数据源。理由：
1. 知识班的首要任务是恢复基础数据流(K线+指数)，不是扩展维度
2. Tier-1缺口在信号验证中确实存在，但当前研究域还没到需要这些数据的阶段
3. 每新增一个数据源，就新增一个维护点和失效风险
4. a-stock-data的SKILL.md原生适配值得等疯子部署后观察

**触发条件**：当某个Tier-1缺口被研究域的假设树明确需要时（而非字典里写着有就去接），再启动对应数据源的验证
