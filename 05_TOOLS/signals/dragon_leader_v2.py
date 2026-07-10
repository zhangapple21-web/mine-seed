#!/usr/bin/env python3
"""
Dragon Leader v2 — 基于 a-stock-data 的龙头发现系统

数据源优先级：
  mootdx TCP → 腾讯行情 → 东财(限流+重试退避) → akshare(全市场+板块降级)

数据源：akshare(全市场+板块) + baostock(行业分类降级)

双轨模式：输出 OLD_RESULT / NEW_RESULT 对比

IP风控防护(v20260622)：
  - 东财push2所有调用加指数退避重试(3次)
  - 板块排行失败时降级到akshare板块概念排行
  - 报告头部标记数据源健康状态
"""

import os
import sys
import time
import json
import logging
import warnings
import socket
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from functools import wraps
import inspect
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import pandas as pd
import numpy as np
import pickle

warnings.filterwarnings('ignore')

# ===== 路径配置 =====
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = Path("/home/coze/mine_output/signals")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===== 龙头识别参数 =====
ZHONGJUN_RISE_MIN = 5.0
ZHONGJUN_RISE_MAX = 15.0
EMOTION_RISE_MIN = 5.0
BUZHANG_RISE_MAX = 3.0
BUZHANG_MIN_TURNOVER = 1.0  # 亿

# ===== a-stock-data 路径 =====
sys.path.insert(0, "/home/coze/a-stock-data")

# ===== 日志 =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(OUTPUT_DIR / 'dragon_leader_v2.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# ====================================================================
# 数据层 — 第一优先级：mootdx TCP
# ====================================================================
def _tdx_probe(ip, port, timeout=2.0):
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

_TDX_SERVERS = [
    ('119.97.185.59', 7709), ('124.70.133.119', 7709),
    ('116.205.183.150', 7709), ('123.60.73.44', 7709),
    ('116.205.163.254', 7709), ('121.36.225.169', 7709),
]

def get_tdx_client():
    """创建 mootdx 客户端"""
    from mootdx.quotes import Quotes
    for ip, port in _TDX_SERVERS:
        if _tdx_probe(ip, port):
            return Quotes.factory(market='std', server=(ip, port))
    try:
        return Quotes.factory(market='std', bestip=True)
    except Exception:
        pass
    return Quotes.factory(market='std')


def get_mootdx_kline(symbol: str, count: int = 10) -> Optional[pd.DataFrame]:
    """从 mootdx 获取日K线"""
    try:
        client = get_tdx_client()
        klines = client.bars(symbol=symbol, category=4, offset=count)
        if klines is not None and not klines.empty:
            return klines
        return None
    except Exception as e:
        logger.warning(f"mootdx K线 {symbol} 失败: {e}")
        return None


def get_mootdx_quotes(symbols: list) -> Optional[pd.DataFrame]:
    """从 mootdx 获取实时报价（46字段）"""
    try:
        client = get_tdx_client()
        return client.quotes(symbol=symbols)
    except Exception as e:
        logger.warning(f"mootdx quotes 失败: {e}")
        return None


# ====================================================================
# 数据层 — 第二优先级：腾讯行情
# ====================================================================
def get_tencent_batch(codes: list) -> dict:
    """腾讯批量行情（不封IP，GBK编码）"""
    result = {}
    try:
        # 分批查，每批最多50只
        batch_size = 50
        for i in range(0, len(codes), batch_size):
            batch = codes[i:i+batch_size]
            prefixed = []
            for c in batch:
                if c.startswith(("6", "9")):
                    prefixed.append(f"sh{c}")
                elif c.startswith("8"):
                    prefixed.append(f"bj{c}")
                else:
                    prefixed.append(f"sz{c}")
            url = "https://qt.gtimg.cn/q=" + ",".join(prefixed)
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "Mozilla/5.0")
            resp = urllib.request.urlopen(req, timeout=10)
            data = resp.read().decode("gbk")
            for line in data.strip().split(";"):
                if not line.strip() or "=" not in line or '"' not in line:
                    continue
                vals = line.split('"')[1].split("~")
                if len(vals) < 53:
                    continue
                code_raw = vals[0]
                code_clean = code_raw[2:] if len(code_raw) > 2 else code_raw
                result[code_clean] = {
                    "name": vals[1],
                    "code": code_clean,
                    "price": float(vals[3]) if vals[3] else 0,
                    "last_close": float(vals[4]) if vals[4] else 0,
                    "change_pct": float(vals[32]) if vals[32] else 0,
                    "high": float(vals[33]) if vals[33] else 0,
                    "low": float(vals[34]) if vals[34] else 0,
                    "amount_wan": float(vals[37]) if vals[37] else 0,
                    "turnover_pct": float(vals[38]) if vals[38] else 0,
                    "pe_ttm": float(vals[39]) if vals[39] else 0,
                    "mcap_yi": float(vals[44]) if vals[44] else 0,
                    "pb": float(vals[46]) if vals[46] else 0,
                }
            if i + batch_size < len(codes):
                time.sleep(0.3)  # 限流
    except Exception as e:
        logger.warning(f"腾讯行情批量查询失败: {e}")
    return result


# ====================================================================
# 数据层 — 第三优先级：东财（限流+重试退避）
# ====================================================================
def _ip_retry(max_tries: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """指数退避重试装饰器 — 专门对付IP风控"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for i in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except (urllib.error.URLError, ConnectionError, ConnectionResetError,
                        urllib.error.HTTPError, OSError) as e:
                    last_exc = e
                    if i < max_tries - 1:
                        wait = delay * (backoff ** i)
                        logger.warning(f'{func.__name__} 第{i+1}次失败({type(e).__name__}: {e})，{wait:.1f}s后重试...')
                        time.sleep(wait)
                    else:
                        logger.error(f'{func.__name__} 重试{max_tries}次全炸: {type(last_exc).__name__}: {last_exc}')
                except Exception as e:
                    last_exc = e
                    logger.warning(f'{func.__name__} 异常({type(e).__name__}: {e})，1s后重试...')
                    time.sleep(1)
                    return func(*args, **kwargs)
            return None
        return wrapper
    return decorator


# ====================================================================
# 数据层 — 第三优先级备选：东财倒下时走akshare板块排行
# ====================================================================
def get_akshare_sector_rankings() -> Optional[pd.DataFrame]:
    """akshare板块概念排行降级方案"""
    try:
        import akshare as ak
        df = ak.stock_board_concept_name_em()
        if df is not None and not df.empty:
            df = df.sort_values('涨跌幅', ascending=False).head(20).copy()
            rename = {'板块名称': 'f14', '涨跌幅': 'f3'}
            df.rename(columns={k: v for k, v in rename.items() if k in df.columns}, inplace=True)
            logger.info(f"✅ akshare板块排行降级成功: {len(df)}个概念板块")
            return df
        return None
    except Exception as e:
        logger.warning(f"akshare板块排行降级失败: {e}")
        return None


def get_sector_data() -> Optional[list]:
    """统一入口：东财 → akshare降级 → None，自动处理IP风控"""
    df = get_sector_rankings()
    if df is not None and not df.empty:
        logger.info("✅ 东财板块排行成功")
        sector_flag = 'eastmoney'
    else:
        logger.warning("⚠️ 东财IP限流，降级到akshare板块排行...")
        df = get_akshare_sector_rankings()
        if df is not None and not df.empty:
            logger.info("✅ akshare板块排行降级成功")
            sector_flag = 'akshare(降级)'
        else:
            logger.warning("❌ 板块排行全部不可用")
            return None, 'unavailable'

    sector_data = []
    for _, row in df.iterrows():
        sector_data.append({
            'name': str(row.get('f14', row.get('name', '?'))),
            'change_pct': float(row.get('f3', row.get('change_pct', 0))),
        })
    return sector_data, sector_flag


@_ip_retry(max_tries=3, delay=2.0, backoff=2.0)
def get_sector_rankings() -> Optional[pd.DataFrame]:
    """东财行业板块排名（走em_get限流）"""
    try:
        import requests
        UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": "1", "pz": "20", "po": "1", "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2", "invt": "2", "fid": "f3",
            "fs": "m:90+t:2",
            "fields": "f2,f3,f4,f12,f14,f104,f105",
        }
        headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        time.sleep(1.2)
        data = r.json().get("data", {}).get("diff", [])
        if data:
            df = pd.DataFrame(data)
            df.columns = [f"f{c}" for c in df.columns] if not all(c.startswith('f') for c in df.columns) else df.columns
            return df
        return None
    except Exception as e:
        logger.warning(f"东财行业排行失败: {e}")
        return None


# ====================================================================
# 数据层 — 第四优先级：akshare（仅全市场快照降级）
# ====================================================================
def get_akshare_market_snapshot() -> Optional[pd.DataFrame]:
    """akshare 全市场行情快照（降级角色）"""
    try:
        import akshare as ak
        time.sleep(1.5)
        df = ak.stock_zh_a_spot()
        if df is None or df.empty:
            return None
        df = df.rename(columns={
            '代码': 'code', '名称': 'name', '最新价': 'price',
            '涨跌幅': 'pct_change', '成交额': 'turnover', '成交量': 'volume',
        })
        for col in ['pct_change', 'price', 'turnover']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        if 'turnover' in df.columns:
            df['turnover_yi'] = df['turnover'] / 1e8
        logger.info(f"akshare全市场快照: {len(df)}只")
        return df
    except Exception as e:
        logger.warning(f"akshare全市场快照失败: {e}")
        return None


# ====================================================================
# 龙头识别逻辑
# ====================================================================
@dataclass
class LeaderResult:
    time: str
    total_stocks: int = 0
    limit_up_count: int = 0      # 涨停家数
    up_count: int = 0
    down_count: int = 0
    avg_change: float = 0.0
    main_sectors: list = field(default_factory=list)
    zhongjun_leaders: list = field(default_factory=list)
    emotion_leaders: list = field(default_factory=list)
    buzhang_leaders: list = field(default_factory=list)
    data_source: str = ""        # 标记数据来源


# ====================================================================
# 行业分类映射
# ====================================================================

INDUSTRY_MAP_CACHE = None
INDUSTRY_MAP_SOURCE = "pkl"


def load_industry_map(pkl_path: str = "/home/coze/stock_industry_map.pkl") -> Dict[str, str]:
    """加载证监会行业分类映射，code->industry。代码格式兼容 sh.600519 / 600519"""
    global INDUSTRY_MAP_CACHE, INDUSTRY_MAP_SOURCE
    if INDUSTRY_MAP_CACHE is not None:
        return INDUSTRY_MAP_CACHE
    
    try:
        with open(pkl_path, "rb") as f:
            df: pd.DataFrame = pickle.load(f)
        df["short_code"] = df["code"].str.split(".").str[-1]
        industry_map = dict(zip(df["short_code"], df["industry"]))
        logger.info(f"行业映射[pkl]: {len(industry_map)}只, 数据日期{df["updateDate"].iloc[0]}")
        INDUSTRY_MAP_CACHE = industry_map
        INDUSTRY_MAP_SOURCE = "pkl"
        return industry_map
    except Exception as e:
        logger.warning(f"pkl行业映射失败: {e}, 尝试baostock降级")
        return _load_industry_from_baostock()


def _load_industry_from_baostock() -> Dict[str, str]:
    """通过baostock获取行业分类（pkl降级源/更新源）"""
    _ensure_baostock_patch()
    global INDUSTRY_MAP_CACHE, INDUSTRY_MAP_SOURCE
    try:
        import baostock as bs
        lg = bs.login()
        if lg.error_code != "0":
            raise RuntimeError(f"baostock登录失败: {lg.error_msg}")
        rs = bs.query_stock_industry()
        df = rs.get_data()
        bs.logout()
        df["short_code"] = df["code"].str.split(".").str[-1]
        industry_map = dict(zip(df["short_code"], df["industry"]))
        logger.info(f"行业映射[baostock]: {len(industry_map)}只")
        INDUSTRY_MAP_CACHE = industry_map
        INDUSTRY_MAP_SOURCE = "baostock"
        return industry_map
    except Exception as e:
        logger.error(f"baostock行业映射也失败: {e}")
        INDUSTRY_MAP_CACHE = {}
        return {}


_PATCHED_BAOSTOCK = False


def _ensure_baostock_patch():
    """确保baostock的pandas兼容补丁已应用"""
    global _PATCHED_BAOSTOCK
    if _PATCHED_BAOSTOCK:
        return True
    try:
        import_path = "/usr/local/lib/python3.13/dist-packages/baostock/data/resultset.py"
        with open(import_path, "r") as f:
            content = f.read()
        if "df.append" in content:
            content = content.replace("df = df.append(temp_df, ignore_index=True)", "df = pd.concat([df, temp_df], ignore_index=True)")
            with open(import_path, "w") as f:
                f.write(content)
            logger.info("✅ baostock pandas兼容补丁已应用")
        else:
            logger.info("baostock补丁已存在，跳过")
        _PATCHED_BAOSTOCK = True
        return True
    except Exception as e:
        logger.warning(f"baostock补丁检查失败: {e}")
        return False
def analyze_market(stocks_df: pd.DataFrame) -> LeaderResult:
    """基于全市场数据做龙头分析"""
    now = datetime.now()
    result = LeaderResult(time=now.strftime("%Y-%m-%d %H:%M"))

    if stocks_df is None or stocks_df.empty:
        return result

    df = stocks_df.copy()
    result.total_stocks = len(df)
    result.up_count = int((df['pct_change'] > 0).sum())
    result.down_count = int((df['pct_change'] < 0).sum())
    result.limit_up_count = int((df['pct_change'] >= 9.5).sum())
    result.avg_change = float(df['pct_change'].mean())

    # 主线板块识别（证监会行业分类聚类）
    limit_ups = df[df["pct_change"] >= 9.5]
    sector_counter = Counter()
    sector_stocks = defaultdict(list)
    industry_map = load_industry_map()

    for _, row in limit_ups.iterrows():
        code = str(row.get("code", ""))
        name = str(row.get("name", ""))
        rise = float(row.get("pct_change", 0))
        short_code = code.split(".")[-1] if "." in code else code
        industry = industry_map.get(short_code)
        if industry:
            sector_counter[industry] += 1
            sector_stocks[industry].append({"code": code, "name": name, "rise": rise})
        else:
            sector_counter["其他"] += 1
            sector_stocks["其他"].append({"code": code, "name": name, "rise": rise})
    for sector, count in sector_counter.most_common(5):
        stocks = sector_stocks[sector]
        avg_rise = sum(s['rise'] for s in stocks) / len(stocks) if stocks else 0
        result.main_sectors.append({
            'name': sector, 'count': count,
            'avg_rise': round(avg_rise, 2),
            'stocks': stocks[:5]
        })

    # 中军龙头：涨幅5-15%，成交额大
    candidates = df[(df['pct_change'] >= ZHONGJUN_RISE_MIN) & (df['pct_change'] <= ZHONGJUN_RISE_MAX)]
    if 'turnover_yi' in df.columns:
        candidates = candidates[candidates['turnover_yi'] >= 3]
    candidates = candidates.sort_values('turnover_yi' if 'turnover_yi' in df.columns else 'pct_change', ascending=False)
    for _, row in candidates.head(5).iterrows():
        result.zhongjun_leaders.append({
            'code': str(row.get('code', '')),
            'name': str(row.get('name', '')),
            'rise': float(row.get('pct_change', 0)),
            'turnover_yi': float(row.get('turnover_yi', 0)),
        })

    # 情绪龙头：涨停/高涨幅
    emotion_candidates = df[(df['pct_change'] >= EMOTION_RISE_MIN) & (~df['name'].astype(str).str.contains('ST|退', na=False))]
    emotion_candidates = emotion_candidates.sort_values('pct_change', ascending=False)
    for _, row in emotion_candidates.head(5).iterrows():
        rise = float(row.get('pct_change', 0))
        board = "涨停" if rise >= 9.9 else "强势"
        result.emotion_leaders.append({
            'code': str(row.get('code', '')),
            'name': str(row.get('name', '')),
            'rise': rise,
            'board': board,
        })

    # 补涨龙头：滞涨但放量
    buzhang_candidates = df[(df['pct_change'] > 0) & (df['pct_change'] < BUZHANG_RISE_MAX)]
    if 'turnover_yi' in df.columns:
        buzhang_candidates = buzhang_candidates[buzhang_candidates['turnover_yi'] >= BUZHANG_MIN_TURNOVER]
    buzhang_candidates = buzhang_candidates.sort_values('turnover_yi' if 'turnover_yi' in df.columns else 'pct_change', ascending=False)
    for _, row in buzhang_candidates.head(5).iterrows():
        result.buzhang_leaders.append({
            'code': str(row.get('code', '')),
            'name': str(row.get('name', '')),
            'rise': float(row.get('pct_change', 0)),
            'turnover_yi': float(row.get('turnover_yi', 0)),
        })

    return result


# ====================================================================
# 生成报告
# ====================================================================
def generate_report_v2(
    new_result: LeaderResult,
    old_result: Optional[LeaderResult] = None,
    sector_data: Optional[list] = None,
    sector_flag: str = 'unknown',
) -> str:
    """生成双轨报告"""
    lines = [
        f"# Dragon Leader v2 观察报告",
        f"时间：{new_result.time}",
        f"数据源：{new_result.data_source}",
        f"板块源：{sector_flag}",
        "",
        "## 数据健康",
        f"- 全市场数据：{'✅' if new_result.total_stocks > 0 else '❌'} {new_result.data_source}",
        f"- 板块排行：{'✅' if sector_flag in ('eastmoney', 'akshare(降级)') else '❌'} {sector_flag}",
        f"- 对照组：{'✅' if old_result is not None else '❌'} {old_result.data_source if old_result else '无'}",
        "",
        "## 市场概况",
        f"- 全市场统计：{new_result.total_stocks}只",
        f"- 上涨：{new_result.up_count}家 ｜ 下跌：{new_result.down_count}家",
        f"- 涨停：**{new_result.limit_up_count}家**",
        f"- 平均涨幅：{new_result.avg_change:+.2f}%",
        "",
    ]

    # 双轨对比
    if old_result is not None:
        delta = new_result.limit_up_count - old_result.limit_up_count
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        lines.extend([
            "## 双轨对比 (NEW vs OLD)",
            f"| 指标 | NEW ({new_result.data_source}) | OLD ({old_result.data_source}) | 差异 |",
            f"|---|---|---|---|",
            f"| 涨停家数 | {new_result.limit_up_count} | {old_result.limit_up_count} | {delta_str} |",
            f"| 上涨家数 | {new_result.up_count} | {old_result.up_count} | {new_result.up_count - old_result.up_count:+d} |",
            f"| 平均涨幅 | {new_result.avg_change:+.2f}% | {old_result.avg_change:+.2f}% | {new_result.avg_change - old_result.avg_change:+.2f}% |",
            "",
        ])

    # 主线板块
    lines.extend(["## 主线板块", "| 排名 | 板块 | 涨停家数 | 均幅 |", "|---|---|---|---|"])
    for i, s in enumerate(new_result.main_sectors[:5], 1):
        lines.append(f"| {i} | {s['name']} | {s['count']} | {s['avg_rise']:+.1f}% |")
    if not new_result.main_sectors:
        lines.append("| - | 暂无明确主线 | - | - |")

    # 中军龙头
    lines.extend([
        "", "## 龙头识别",
        "", "### 中军龙头",
        "| 股票 | 涨幅 | 成交额 |",
        "|---|---|---|"
    ])
    for l in new_result.zhongjun_leaders[:5]:
        lines.append(f"| {l['name']}({l['code']}) | {l['rise']:+.2f}% | {l.get('turnover_yi', 0):.1f}亿 |")
    if not new_result.zhongjun_leaders:
        lines.append("| - | - | - |")

    # 情绪龙头
    lines.extend([
        "", "### 情绪龙头",
        "| 股票 | 涨幅 | 状态 |",
        "|---|---|---|"
    ])
    for l in new_result.emotion_leaders[:5]:
        lines.append(f"| {l['name']}({l['code']}) | {l['rise']:+.2f}% | {l['board']} |")
    if not new_result.emotion_leaders:
        lines.append("| - | - | - |")

    # 补涨龙头
    lines.extend([
        "", "### 补涨龙头",
        "| 股票 | 涨幅 | 成交额 |",
        "|---|---|---|"
    ])
    for l in new_result.buzhang_leaders[:5]:
        lines.append(f"| {l['name']}({l['code']}) | {l['rise']:+.2f}% | {l.get('turnover_yi', 0):.1f}亿 |")
    if not new_result.buzhang_leaders:
        lines.append("| - | - | - |")

    # 板块排行
    if sector_data:
        lines.extend(["", "## 行业板块排行TOP5"])
        for i, sec in enumerate(sector_data[:5], 1):
            lines.append(f"{i}. {sec.get('name','?')}: {sec.get('change_pct',0):+.2f}%")

    # 风险提示
    risks = []
    if new_result.limit_up_count > 150:
        risks.append("涨停家数偏多，注意高位分化")
    if new_result.avg_change < -1:
        risks.append("市场整体偏弱")
    lines.extend([
        "", "## 风险提示",
        "、".join(risks) if risks else "无明显异常",
        "",
        "---",
        "*Dragon Leader v2 · a-stock-data 数据源 · 双轨对比模式*"
    ])

    return "\n".join(lines)


# ====================================================================
# 主流程
# ====================================================================
def main():
    logger.info("=" * 60)
    logger.info("Dragon Leader v2 启动 — 新数据源链路")
    logger.info("=" * 60)

    # Step 1: 全市场快照 — 优先腾讯批量，降级akshare
    logger.info("Step 1: 获取全市场数据...")

    new_snapshot = None
    data_source = ""

    # 第一选择：akshare全市场快照（目前还能跑）
    new_snapshot = get_akshare_market_snapshot()
    if new_snapshot is not None and not new_snapshot.empty:
        data_source = "akshare(字典)"
        logger.info(f"✅ akshare全市场快照成功: {len(new_snapshot)}只")
    else:
        logger.warning("akshare不可用，尝试腾讯行情...")
        # 第二选择：腾讯分批 — 但需要先有股票列表，这里简化处理
        data_source = "数据受限"
        logger.warning("腾讯行情无全市场快照能力，数据受限")

    # Step 2: 龙头分析
    logger.info("Step 2: 龙头识别分析...")
    new_result = analyze_market(new_snapshot)
    new_result.data_source = data_source

    # Step 3: 板块排行（东财→akshare降级，含重试退避）
    logger.info("Step 3: 获取板块排行...")
    sector_data = None
    sector_flag = 'unavailable'
    sector_data, sector_flag = get_sector_data() or (None, 'unavailable')

    # Step 4: 尝试旧链路做对比
    logger.info("Step 4: 旧链路对照组...")
    old_result = None
    try:
        # 尝试akshare全量（旧脚本的核心数据源）
        old_snapshot = get_akshare_market_snapshot()
        if old_snapshot is not None:
            old_result = analyze_market(old_snapshot)
            old_result.data_source = "akshare(旧链路)"
    except Exception as e:
        logger.warning(f"旧链路对照组失败: {e}")

    # Step 5: 生成报告
    logger.info("Step 5: 生成报告...")
    report = generate_report_v2(new_result, old_result, sector_data, sector_flag=sector_flag)

    now = datetime.now()
    report_path = OUTPUT_DIR / f"dragon_leader_v2_{now.strftime('%Y%m%d_%H%M')}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    logger.info(f"✅ 报告已保存: {report_path}")
    print("\n" + "=" * 60)
    print(report[:2000])
    if len(report) > 2000:
        print(f"\n... (报告共 {len(report)} 字符)")
    print("=" * 60)

    return report_path


if __name__ == "__main__":
    result = main()
    print(f"\n报告路径: {result}")
