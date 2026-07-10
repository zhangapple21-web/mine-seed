# A股数据源迁移方案 — baostock→mootdx+adata

**创建时间**: 2026-06-21 10:34
**背景**: baostock IP被黑名单(error_code=10001011), AkShare反爬TLS不可用, 知识班05:00起已两班无产出

---

## 接口验证结果

### mootdx (通达信TCP协议) — 主力 ✅ 可靠

| 接口 | 状态 | 示例 |
|------|------|------|
| 个股日K | ✅ | `client.bars(symbol='000001', frequency=9, start=0, offset=100)` |
| 指数日K | ✅ | `client.index(market=1, symbol='000001', frequency=9, start=0, offset=5)` |
| 5分钟K | ✅ | `client.bars(symbol='000001', frequency=0, start=0, offset=5)` |
| 周K/月K | ✅ | frequency=10/11 |
| 股票列表 | ✅ | `client.stocks(market=0)` 返回23485条SZ |
| 批量个股 | ⚠️ | 需循环调用,无批量接口 |

**频率编码**: 0=5min, 1=15min, 4=30min, 5=60min, 9=day, 10=week, 11=month

**日K返回列**: open, close, high, low, vol, amount, year, month, day, hour, minute, datetime, volume

**指数日K额外列**: up_count, down_count

**关键优势**: TCP协议,几乎不封IP,不依赖HTTP反爬

**安装**: `pip install mootdx` (0.11.7, 依赖httpx/tdxpy/tenacity)

**连接方式**: 
```python
from mootdx.quotes import Quotes
client = Quotes.factory(market='std', multithread=True, heartbeat=True)
# 用完 client.close() 非必须,连接池自动管理
```

**指数market编码**: SZ=0, SH=1
**指数symbol编码**: 上证指数='000001'(market=1), 深证成指='399001'(market=0)

### adata (HTTP多源) — 补充 ⚠️ 部分接口有问题

| 接口 | 状态 | 备注 |
|------|------|------|
| 股票代码列表 | ✅ | `adata.stock.info.all_code()` 5965条 |
| 指数日K | ✅ | `adata.stock.market.get_market_index(index_code='000001')` |
| 指数成分股 | ✅ | `adata.stock.info.index_constituent(index_code='000300')` 300条 |
| 北向资金 | ⚠️ | `adata.sentiment.north.north_flow()` 返回但数据滞后到5月 |
| 个股日K | ❌ | `adata.stock.market.get_market(stock_code='000001')` 返回空 |
| 实时行情 | ❌ | `adata.stock.market.list_market_current()` 返回空 |
| 概念板块 | ❌ | 缓存文件缺失 |
| ETF | ❌ | 连接被拒 |

**安装**: `pip install adata` (2.9.5, 需py_mini_racer)

**判断**: adata半年没更新(最后commit 2025-12-26), 个股/实时接口已失效, 只保留指数成分股和指数日K两个可用接口作为补充

---

## knowledge_shift.py 适配方案

### 数据获取替换逻辑

```python
# 替换 baostock 的行情获取
# 原: bs.query_history_k_data_plus()
# 新: mootdx client.bars() / client.index()

def get_market_data_mootdx(stock_codes, days=30):
    """用mootdx获取个股日K数据"""
    from mootdx.quotes import Quotes
    client = Quotes.factory(market='std', multithread=True, heartbeat=True)
    
    results = {}
    for code in stock_codes:
        try:
            market = 1 if code.startswith('6') else 0  # 6开头=SH, 其他=SZ
            df = client.bars(symbol=code, frequency=9, start=0, offset=days)
            if len(df) > 0:
                results[code] = df[['open','close','high','low','volume','amount']]
        except Exception as e:
            results[code] = None
    return results

def get_index_data_mootdx(days=30):
    """用mootdx获取指数日K"""
    from mootdx.quotes import Quotes
    client = Quotes.factory(market='std', multithread=True, heartbeat=True)
    
    indices = {
        '上证指数': (1, '000001'),
        '深证成指': (0, '399001'),
    }
    results = {}
    for name, (market, symbol) in indices.items():
        df = client.index(market=market, symbol=symbol, frequency=9, start=0, offset=days)
        if len(df) > 0:
            results[name] = df[['open','close','high','low','volume']]
    return results

def get_index_constituents_adata(index_code='000300'):
    """用adata获取指数成分股(adata独有能力)"""
    import adata
    return adata.stock.info.index_constituent(index_code=index_code)
```

### Guard逻辑更新

原有guard: `market_data=none且lab01=0时不生产`
新增逻辑:
1. 优先尝试mootdx(TCP)
2. mootdx失败→尝试adata(HTTP,仅指数)
3. 两者都失败→guard触发,不生产

### 注意事项

- mootdx首次连接会自动选择最快服务器,生成`~/.mootdx/config.json`
- mootdx的bars()返回的datetime带时分(15:00),需parse日期部分
- 个股循环调用需注意速率,建议每次间隔0.1秒
- adata的index_constituent()目前可用,但如果东财接口变动可能随时失效
- 非交易日(周末/节假日)mootdx仍能获取历史数据,不受影响

---

## 迁移优先级

1. **P0**: knowledge_shift.py中baostock→mootdx替换(疯子部署)
2. **P1**: Guard逻辑增加双源fallback
3. **P2**: adata成分股接口集成(知识班需要知道关注哪些股)
4. **P3**: adata北向资金/龙虎榜接口监控(目前半废,等更新)
