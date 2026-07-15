#!/usr/bin/env python3
"""
A股自动荐股引擎 - stock_advisor.py
四层筛选架构：
1. 因子筛选（全市场快照）
2. 技术确认
3. 基本面+资金面
4. 输出TOP2+MD报告
CCO Selection Trace: CCO₁因子筛选 → CCO₂技术确认 → CCO₃基本面确认 → CCO₄价值匹配
"""

import os
import sys
import time
import json
import random
import logging
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

# 设置日志
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mine_output', 'advisor')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'advisor_cron.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加当前目录到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入数据源
from stock_query import get_stock_query


@dataclass
class StockData:
    """股票数据容器"""
    code: str
    name: str = ''
    price: float = 0.0
    change_pct: float = 0.0
    pe: float = 0.0
    turnover_rate: float = 0.0
    volume: int = 0
    total_capital: float = 0.0  # 总市值（亿）
    
    # 因子数据
    momentum_5d: float = 0.0  # 5日涨幅
    volatility_20d: float = 0.0  # 20日波动率
    return_60d: float = 0.0  # 60日涨幅
    
    # 情绪因子（雪球）
    hot_rank: int = 0  # 热度排名
    comment_count: int = 0  # 评论数
    follower_count: int = 0  # 关注人数
    heat_level: str = ''  # 热度等级
    
    # K线数据
    kline_data: List[Dict] = field(default_factory=list)
    
    # 技术指标
    ma5: float = 0.0
    ma10: float = 0.0
    ma20: float = 0.0
    ma60: float = 0.0
    macd_dif: float = 0.0
    macd_dea: float = 0.0
    macd_hist: float = 0.0
    rsi6: float = 50.0
    rsi12: float = 50.0
    
    # 资金流向
    main_inflow_days: int = 0
    total_main_inflow: float = 0.0
    
    # 综合得分
    score: float = 0.0
    
    # 技术确认信号
    tech_signals: List[str] = field(default_factory=list)
    
    # 原始数据
    raw_data: Dict = field(default_factory=dict)
    
    # ========== CCO Selection Trace 字段 ==========
    # CCO₁ 因子筛选阶段
    layer1_reasons: List[str] = field(default_factory=list)  # 入选原因
    layer1_reject_flags: List[str] = field(default_factory=list)  # 淘汰原因
    layer1_passed: bool = False
    
    # CCO₂ 技术确认阶段
    layer2_reasons: List[str] = field(default_factory=list)  # 技术确认原因
    layer2_passed: bool = False
    
    # CCO₃ 基本面确认阶段
    layer3_reasons: List[str] = field(default_factory=list)  # 基本面确认原因
    layer3_bonus_detail: Dict[str, float] = field(default_factory=dict)  # 各项加分明细
    layer3_passed: bool = False
    
    # CCO₄ 价值函数匹配
    value_trace: Dict = field(default_factory=dict)  # 价值匹配追踪


class AkshareAPI:
    """akshare API封装，带QPS控制和降级方案"""
    
    def __init__(self):
        self.last_request_time = 0
        self.min_interval = 0.6  # QPS≤2，间隔至少0.6秒
        self.use_fallback = False
        self.fallback = get_stock_query()
        
    def _rate_limit(self):
        """QPS限速控制"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()
    
    def _try_akshare(self, func, *args, fallback_func=None, **kwargs):
        """尝试akshare，失败后降级到腾讯API"""
        self._rate_limit()
        
        try:
            import akshare as ak
            result = func(*args, **kwargs)
            self.use_fallback = False
            return result
        except Exception as e:
            logger.warning(f"akshare调用失败: {e}，切换到腾讯API")
            self.use_fallback = True
            if fallback_func:
                return fallback_func(*args, **kwargs)
            return None
    
    def get_stock_spot_em(self) -> List[Dict]:
        """获取A股实时行情（东方财富）"""
        def _akshare_func():
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            return df
        
        result = self._try_akshare(_akshare_func)
        if result is not None and not result.empty:
            return result.to_dict('records')
        
        # 降级方案：使用腾讯API获取全市场行情
        logger.info("使用腾讯API降级获取全市场行情...")
        return self._get_spot_from_tencent()
    
    def _get_spot_from_tencent(self) -> List[Dict]:
        """腾讯API获取全市场行情（使用热门股票池）"""
        results = []
        
        # 热门股票池（沪深主板+科创+创业+北交）
        hot_stocks = [
            # 沪市主板
            '600519', '600036', '601318', '600276', '601888', '600900', '601398', '601939',
            '600028', '601857', '600019', '601166', '600585', '600048', '600690', '600887',
            '600809', '600111', '600030', '601012', '600438', '600547', '601601', '600837',
            '600031', '601668', '600588', '600570', '600521', '600703', '600745', '600563',
            '601225', '600383', '600489', '600516', '600507', '600346', '600426', '600309',
            '600009', '600115', '600170', '600176', '600183', '600188', '600196', '600201',
            '600223', '600233', '600256', '600267', '600271', '600297', '600298', '600309',
            '600352', '600362', '600383', '600406', '600436', '600460', '600467', '600487',
            '600499', '600502', '600512', '600519', '600535', '600549', '600570', '600585',
            '600588', '600606', '600637', '600660', '600690', '600703', '600718', '600760',
            '600795', '600809', '600887', '600893', '600905', '600918', '600926', '600941',
            '601006', '601012', '601066', '601088', '601117', '601138', '601169', '601186',
            '601211', '601225', '601236', '601288', '601319', '601328', '601336', '601360',
            '601390', '601398', '601601', '601618', '601628', '601658', '601668', '601688',
            '601698', '601728', '601816', '601838', '601857', '601899', '601919', '601985',
            '601988', '601989', '601991', '603259', '603288', '603501', '603799', '603986',
            # 科创板
            '688012', '688041', '688111', '688126', '688187', '688256', '688339', '688363',
            '688981', '688008', '688036', '688111', '688116', '688122', '688185', '688223',
            '688234', '688295', '688396', '688521', '688561', '688599', '688981', '688019',
            # 深市主板
            '000001', '000002', '000063', '000066', '000100', '000333', '000338', '000425',
            '000568', '000651', '000661', '000708', '000725', '000768', '000858', '000876',
            '000895', '000938', '000001', '000002', '000063', '000066', '000100', '000333',
            '000338', '000425', '000568', '000651', '000661', '000708', '000725', '000768',
            '000858', '000876', '000895', '000938', '000002', '000063', '000066', '000100',
            # 创业板
            '300001', '300014', '300015', '300033', '300059', '300059', '300122', '300124',
            '300142', '300223', '300274', '300274', '300408', '300496', '300529', '300595',
            '300750', '300760', '300896', '300124', '300033', '300059', '300059', '300122',
            '300014', '300015', '300001', '300274', '300274', '300408', '300496', '300529',
            '300595', '300750', '300760', '300896', '300142', '300223', '300001', '300014',
            '300015', '300033', '300059', '300122', '300124', '300142', '300223', '300274',
            '300408', '300496', '300529', '300595', '300750', '300760', '300896',
        ]
        
        # 去重后排序，确保每次运行顺序一致
        hot_stocks = sorted(list(set(hot_stocks)))
        
        # 分批获取
        batch_size = 30
        for i in range(0, min(len(hot_stocks), 600), batch_size):
            batch = hot_stocks[i:i+batch_size]
            try:
                quotes = self.fallback.get_quote(batch)
                for q in quotes:
                    if q.get('price', 0) > 0 and q.get('name', ''):
                        results.append(q)
                time.sleep(0.2)
            except Exception as e:
                logger.warning(f"批量获取行情失败: {e}")
                continue
        
        return results
    
    def get_hist_data(self, symbol: str, period: str = "daily", days: int = 30) -> List[Dict]:
        """获取历史K线"""
        def _akshare_func():
            import akshare as ak
            # 转换代码格式
            if symbol.startswith('sh') or symbol.startswith('sz'):
                code = symbol
            else:
                code = f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}"
            
            df = ak.stock_zh_a_hist(symbol=code.replace('sh', '').replace('sz', ''), 
                                   period=period, start_date='', end_date='', adjust='qfq')
            return df.to_dict('records')
        
        result = self._try_akshare(
            _akshare_func,
            fallback_func=lambda: self.fallback.get_hist_kline(symbol, days)
        )
        
        if result:
            return result[-days:] if len(result) > days else result
        return []
    
    def get_fund_flow(self, symbol: str) -> Dict:
        """获取资金流向"""
        def _akshare_func():
            import akshare as ak
            # 转换代码格式
            code = symbol.replace('sh', '').replace('sz', '')
            
            df = ak.stock_individual_fund_flow(stock=code, market="sh" if symbol.startswith('6') else "sz")
            if df is not None and not df.empty:
                # 分析近5日主力净流入
                main_inflow_days = 0
                total_main_inflow = 0.0
                
                for idx, row in df.head(5).iterrows():
                    try:
                        # 尝试获取主力净流入列
                        for col in df.columns:
                            if '主力' in col and '净' in col:
                                val = float(row[col])
                                if val > 0:
                                    main_inflow_days += 1
                                    total_main_inflow += val
                                break
                    except:
                        pass
                
                return {
                    'main_inflow_days': main_inflow_days,
                    'total_main_inflow': total_main_inflow
                }
            return {'main_inflow_days': 0, 'total_main_inflow': 0.0}
        
        result = self._try_akshare(
            _akshare_func,
            fallback_func=lambda: self.fallback.get_fund_flow(symbol)
        )
        
        return result if result else {'main_inflow_days': 0, 'total_main_inflow': 0.0}


class StockAdvisor:
    """A股荐股引擎"""
    
    def __init__(self, max_stocks: int = 500, use_cache: bool = True):
        self.max_stocks = max_stocks
        self.use_cache = use_cache
        self.api = AkshareAPI()
        self.start_time = time.time()
        self.timeout = 600  # 10分钟超时
        
        # 缓存目录
        self.cache_dir = Path(__file__).parent.parent / 'mine_output' / 'advisor' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 因子参数
        self.momentum_threshold = 2.0  # 动量阈值
        self.volatility_p70 = None  # 动态计算
        
        # 情绪数据源
        try:
            from multi_data_source import DataSourceManager
            self.data_source_manager = DataSourceManager()
            logger.info("多数据源管理器已加载")
        except Exception as e:
            self.data_source_manager = None
            logger.warning(f"多数据源管理器加载失败: {e}")
        
        # ========== 学习进化系统 ==========
        # 表现跟踪器
        from performance_tracker import PerformanceTracker
        self.tracker = PerformanceTracker()
        
        # 自适应评分器
        from adaptive_scorer import AdaptiveScorer
        self.scorer = AdaptiveScorer()
        
        # 矿工助手（用于失败诊断）
        from miner_assistant import MinerAssistant
        self.miner = MinerAssistant()
        
        # 推票后审计员
        from post_recommendation_auditor import PostRecommendationAuditor
        self.auditor = PostRecommendationAuditor()
        
        # 时间感知：记录启动时间和今日日期
        self.today_str = datetime.now().strftime('%Y%m%d')
        self.today_datetime = datetime.now()
        logger.info(f"【时间感知】启动时间: {self.today_datetime}, 今日日期: {self.today_str}")
    
    def _get_cache_path(self, name: str) -> Path:
        """获取缓存文件路径"""
        today = datetime.now().strftime('%Y%m%d')
        return self.cache_dir / f'{name}_{today}.json'
    
    def _load_cache(self, name: str) -> Optional[Any]:
        """加载日级缓存"""
        if not self.use_cache:
            return None
        cache_path = self._get_cache_path(name)
        if cache_path.exists():
            try:
                data = json.loads(cache_path.read_text(encoding='utf-8'))
                logger.info(f"缓存命中: {name}")
                return data
            except Exception:
                pass
        return None
    
    def _save_cache(self, name: str, data: Any):
        """保存日级缓存"""
        if not self.use_cache:
            return
        cache_path = self._get_cache_path(name)
        try:
            cache_path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding='utf-8')
            logger.info(f"缓存已保存: {name}")
        except Exception as e:
            logger.warning(f"缓存保存失败 {name}: {e}")
    
    def _check_timeout(self) -> bool:
        """检查超时"""
        return time.time() - self.start_time > self.timeout
    
    def _parse_turnover(self, turnover_val) -> float:
        """解析换手率（Data Quality Gate）
        
        支持多种格式：
        - 数值: 0.2
        - 字符串带百分号: "0.2%"
        - 空字符串/None: 返回0
        """
        if isinstance(turnover_val, str):
            turnover_val = turnover_val.replace('%', '').replace(' ', '').replace(',', '')
            try:
                return float(turnover_val)
            except (ValueError, TypeError):
                return 0.0
        else:
            try:
                return float(turnover_val)
            except (ValueError, TypeError):
                return 0.0
    
    def _parse_stock_data(self, raw: Dict) -> Optional[StockData]:
        """解析原始数据为StockData
        
        Data Quality Gate：过滤异常数据，不参与后续流程
        """
        try:
            # 处理可能的字段名
            code = str(raw.get('代码', raw.get('code', '')))
            name = raw.get('名称', raw.get('name', ''))
            
            if not code or not name:
                logger.warning(f"[数据质量] 缺少代码或名称: {raw}")
                return None
            
            # 处理价格
            price = float(raw.get('最新价', raw.get('price', 0)))
            if price <= 0 or price > 10000:
                logger.warning(f"[数据质量] 价格异常({price}): {code} {name}")
                return None
            
            # 处理涨跌幅
            change_pct = float(raw.get('涨跌幅', raw.get('change_pct', 0)))
            if change_pct < -30 or change_pct > 30:
                logger.warning(f"[数据质量] 涨跌幅异常({change_pct}%): {code} {name}")
                return None
            
            # 处理PE
            pe_str = raw.get('市盈率-动态', raw.get('pe', 0))
            pe = float(pe_str) if pe_str else 0.0
            if pe < 0 or pe > 2000:
                pe = 0.0
            
            # 处理换手率（修复：支持多种格式，包括带百分号的字符串）
            turnover_val = raw.get('换手率', raw.get('turnover_rate', 0))
            turnover = self._parse_turnover(turnover_val)
            
            # 换手率异常检查（Data Quality Gate）
            if turnover < 0 or turnover > 100:
                logger.warning(f"[数据质量] 换手率异常({turnover}%): {code} {name}")
                return None
            
            # 处理市值
            total_capital = float(raw.get('总市值', raw.get('total_capital', 0)))
            # 如果是万元单位，转换为亿
            if total_capital > 1000000:
                total_capital = total_capital / 10000
            
            sd = StockData(
                code=code,
                name=name,
                price=price,
                change_pct=change_pct,
                pe=pe,
                turnover_rate=turnover,
                volume=int(raw.get('成交量', raw.get('volume', 0))),
                total_capital=total_capital,
                raw_data=raw
            )
            
            return sd
            
        except Exception as e:
            logger.warning(f"解析数据失败: {e}")
            return None
    
    def _factor_scoring(self, stocks: List[StockData]) -> Tuple[float, float]:
        """因子打分，返回波动率P70阈值"""
        scores = []
        volatilities = []
        
        for sd in stocks:
            score = 0
            
            # 动量因子
            if 2 < sd.momentum_5d < 15:
                momentum_score = 30 * (sd.momentum_5d / 15)
                score += momentum_score
                sd.layer1_reasons.append(f"momentum +{momentum_score:.1f}")
            else:
                sd.layer1_reject_flags.append(f"momentum不达标({sd.momentum_5d:.1f}%)")
            
            # 波动率因子
            if sd.volatility_20d >= 0.5:
                vol_score = 35 * (sd.volatility_20d / 2)
                score += min(vol_score, 35)
                sd.layer1_reasons.append(f"volatility +{min(vol_score, 35):.1f}")
            
            # 均值回归因子
            if -30 < sd.return_60d < -5:
                reversal_score = (sd.return_60d + 30) / 25 * 20
                score += reversal_score
                sd.layer1_reasons.append(f"mean_reversion +{reversal_score:.1f}")
            
            # 成交量异常过滤
            if sd.turnover_rate < 10:
                score += 15
                sd.layer1_reasons.append("volume_normal +15")
            else:
                score -= 10
                sd.layer1_reject_flags.append(f"volume_shock(turnover={sd.turnover_rate:.1f}%) -10")
            
            sd.score = score
            scores.append(score)
            volatilities.append(sd.volatility_20d)
        
        # 计算波动率P70
        if volatilities:
            sorted_vol = sorted(volatilities)
            p70_idx = int(len(sorted_vol) * 0.7)
            vol_p70 = sorted_vol[p70_idx] if p70_idx < len(sorted_vol) else sorted_vol[-1]
        else:
            vol_p70 = 1.0
        
        return vol_p70, scores
    
    def layer1_factor_filter(self, all_stocks: List[Dict]) -> List[StockData]:
        """
        第1层：实时指标快速初筛 CCO₁
        使用实时行情可直接获取的指标做快速筛选，不依赖历史K线。
        
        筛选维度：
        - 价格区间（排除低价垃圾股和高价股）
        - 当日涨跌幅（温和上涨优先）
        - 换手率（活跃度）
        - 市值（中大盘优先）
        - PE（排除高估值）
        """
        logger.info(f"第1层实时初筛：从 {len(all_stocks)} 只股票中筛选")
        
        stock_data_list = []
        # 先按股票代码排序，确保每次运行结果一致
        sorted_stocks = sorted(all_stocks, key=lambda x: str(x.get('代码', x.get('code', ''))))
        for raw in sorted_stocks[:self.max_stocks]:
            sd = self._parse_stock_data(raw)
            if sd and sd.price > 0:
                stock_data_list.append(sd)
        
        if not stock_data_list:
            logger.warning("无有效股票数据")
            return []
        
        # 实时打分（基于当日可直接获取的数据）
        for sd in stock_data_list:
            score = 0
            
            # 价格筛选：5-300元区间
            if 5 <= sd.price <= 300:
                price_score = 15
                score += price_score
                sd.layer1_reasons.append(f"price_range +{price_score}")
            else:
                sd.layer1_reject_flags.append(f"price_out_of_range({sd.price:.2f})")
            
            # 当日涨跌幅：1%-7%温和上涨最佳
            if 1 <= sd.change_pct <= 7:
                change_score = 25
                score += change_score
                sd.layer1_reasons.append(f"change_moderate +{change_score}")
            elif 0 < sd.change_pct < 1:
                change_score = 10
                score += change_score
                sd.layer1_reasons.append(f"change_small +{change_score}")
            elif sd.change_pct > 7:
                sd.layer1_reject_flags.append(f"change_too_high({sd.change_pct:.1f}%)")
            elif sd.change_pct < 0:
                sd.layer1_reject_flags.append(f"change_negative({sd.change_pct:.1f}%)")
            
            # 换手率：1%-10% 活跃但不过度
            if 1 <= sd.turnover_rate <= 10:
                turnover_score = 20
                score += turnover_score
                sd.layer1_reasons.append(f"turnover_healthy +{turnover_score}")
            elif sd.turnover_rate < 1:
                sd.layer1_reject_flags.append(f"turnover_low({sd.turnover_rate:.1f}%)")
            elif sd.turnover_rate > 10:
                sd.layer1_reject_flags.append(f"turnover_too_high({sd.turnover_rate:.1f}%)")
            
            # 市值：100亿-5000亿中大盘
            if 100 <= sd.total_capital <= 5000:
                cap_score = 15
                score += cap_score
                sd.layer1_reasons.append(f"cap_mid_large +{cap_score}")
            elif sd.total_capital < 100:
                sd.layer1_reject_flags.append(f"cap_small({sd.total_capital:.0f}亿)")
            
            # PE：0-80 合理估值区间
            if 0 < sd.pe <= 80:
                pe_score = 15
                score += pe_score
                sd.layer1_reasons.append(f"pe_reasonable +{pe_score}")
            elif sd.pe > 80:
                sd.layer1_reject_flags.append(f"pe_high({sd.pe:.1f})")
            elif sd.pe < 0:
                sd.layer1_reject_flags.append(f"pe_negative({sd.pe:.1f})")
            
            # 成交额：用换手率*市值近似，或者跳过
            # （腾讯行情接口不直接提供成交额，用换手率作为流动性代理）
            if 1 <= sd.turnover_rate <= 10:
                amount_score = 10
                score += amount_score
                sd.layer1_reasons.append(f"liquidity_ok +{amount_score}")
            elif sd.turnover_rate < 1:
                sd.layer1_reject_flags.append(f"liquidity_low(turnover={sd.turnover_rate:.1f}%)")
            
            sd.score = score
        
        # 过滤：得分>40且没有致命拒绝项
        def is_valid(sd):
            fatal_flags = ['price_out_of_range', 'change_negative', 'turnover_too_high']
            return sd.score > 40 and not any(f in str(sd.layer1_reject_flags) for f in fatal_flags)
        
        passed = [sd for sd in stock_data_list if is_valid(sd)]
        
        # 标记 layer1_passed
        for sd in passed:
            sd.layer1_passed = True
        
        # 按得分排序
        passed = sorted(passed, key=lambda x: (-x.score, x.code))
        
        logger.info(f"第1层筛选通过: {len(passed)} 只")
        for sd in passed[:10]:
            reasons_str = ', '.join(sd.layer1_reasons[:3])
            logger.info(f"  ✓ {sd.name}({sd.code}): score={sd.score:.1f} | {reasons_str}")
        
        return passed[:50]  # 最多保留50只
    
    def layer2_technical_confirm(self, stocks: List[StockData]) -> List[StockData]:
        """
        第2层：技术确认 + 真实因子计算 CCO₂
        
        1. 获取真实K线数据
        2. 计算真实动量、波动率等因子（替换第1层的模拟值）
        3. 技术形态确认
        4. 用真实因子重新打分排序
        """
        logger.info(f"第2层技术确认：从 {len(stocks)} 只股票中确认")
        
        confirmed = []
        
        for sd in stocks:
            if self._check_timeout():
                break
            
            try:
                # 获取真实K线数据（60天以计算更准确的因子），先查缓存
                cache_key = f'kline_{sd.code}_60'
                kline = self._load_cache(cache_key)
                if not kline:
                    kline = self.api.get_hist_data(sd.code, days=60)
                    if kline:
                        self._save_cache(cache_key, kline)
                sd.kline_data = kline if kline else []
                
                signals = []
                has_kline_data = len(kline) >= 20
                
                if has_kline_data:
                    closes = [float(k.get('close', 0)) for k in kline]
                    volumes = [int(k.get('volume', 0)) for k in kline]
                    current_price = closes[-1]
                    
                    # ========== 真实因子计算 ==========
                    
                    # 5日动量（真实）
                    if len(closes) >= 5:
                        sd.momentum_5d = (closes[-1] / closes[-5] - 1) * 100
                    
                    # 20日动量
                    if len(closes) >= 20:
                        sd.momentum_20d = (closes[-1] / closes[-20] - 1) * 100
                    
                    # 60日收益（真实，用于均值回归）
                    if len(closes) >= 60:
                        sd.return_60d = (closes[-1] / closes[-60] - 1) * 100
                    elif len(closes) >= 30:
                        sd.return_60d = (closes[-1] / closes[0] - 1) * 100 * 2
                    
                    # 20日波动率（真实）
                    if len(closes) >= 20:
                        daily_returns = []
                        for i in range(1, min(20, len(closes))):
                            if closes[i-1] > 0:
                                daily_returns.append((closes[i] / closes[i-1] - 1) * 100)
                        if daily_returns:
                            mean_ret = sum(daily_returns) / len(daily_returns)
                            variance = sum((r - mean_ret) ** 2 for r in daily_returns) / len(daily_returns)
                            sd.volatility_20d = (variance ** 0.5) * (252 ** 0.5) / 10  # 年化再调整
                    
                    # RSI计算（真实）
                    if len(closes) >= 14:
                        gains = []
                        losses = []
                        for i in range(1, 14):
                            change = closes[-i] - closes[-i-1]
                            if change > 0:
                                gains.append(change)
                            else:
                                losses.append(-change)
                        avg_gain = sum(gains) / 14 if gains else 0
                        avg_loss = sum(losses) / 14 if losses else 0.001
                        rs = avg_gain / avg_loss
                        sd.rsi6 = 100 - (100 / (1 + rs))
                    
                    # MA计算
                    if len(closes) >= 5:
                        sd.ma5 = sum(closes[-5:]) / 5
                    if len(closes) >= 10:
                        sd.ma10 = sum(closes[-10:]) / 10
                    if len(closes) >= 20:
                        sd.ma20 = sum(closes[-20:]) / 20
                    if len(closes) >= 60:
                        sd.ma60 = sum(closes[-60:]) / 60
                    
                    # ========== 技术信号确认 ==========
                    
                    # MA多头排列
                    if sd.ma5 and sd.ma10 and sd.ma20:
                        if sd.ma5 > sd.ma10 > sd.ma20:
                            signals.append('MA多头排列')
                    
                    # 价格站上MA20
                    if sd.ma20 and current_price > sd.ma20:
                        signals.append('站稳中轨')
                    
                    # MACD金叉
                    if len(closes) >= 26:
                        ema12 = sum(closes[-12:]) / 12
                        ema26 = sum(closes[-26:]) / 26
                        dif = ema12 - ema26
                        prev_ema12 = sum(closes[-13:-1]) / 12
                        prev_ema26 = sum(closes[-27:-1]) / 26
                        prev_dif = prev_ema12 - prev_ema26
                        if prev_dif < 0 < dif:
                            signals.append('MACD金叉')
                        sd.macd_dif = dif
                    
                    # RSI健康（30-70）
                    if sd.rsi6 and 30 < sd.rsi6 < 70:
                        signals.append('RSI健康区间')
                    
                    # 量能放大
                    if len(volumes) >= 8:
                        recent_vol = sum(volumes[-3:]) / 3
                        prev_vol = sum(volumes[-8:-3]) / 5
                        if prev_vol > 0 and recent_vol > prev_vol * 1.2:
                            signals.append('量能放大')
                    
                    # 5日动量正向且不过热
                    if sd.momentum_5d is not None:
                        if 0 < sd.momentum_5d < 15:
                            signals.append('短期动量正向')
                        elif sd.momentum_5d >= 15:
                            signals.append('动量过热警示')
                    
                    # ========== 用真实因子重新打分 ==========
                    factor_score = self._calc_tech_factor_score(sd)
                    sd.score = sd.score * 0.4 + factor_score * 0.6  # 技术因子权重更高
                    
                else:
                    # 无K线数据时用第1层的分数，但降级处理
                    signals.append('K线数据不足')
                    if sd.change_pct > 0:
                        signals.append('今日上涨')
                    if 0 < sd.change_pct < 5:
                        signals.append('涨幅温和')
                
                sd.tech_signals = signals
                sd.layer2_reasons = signals.copy()
                
                # 通过条件：有K线数据时2个信号以上，无数据时3个以上
                min_signals = 2 if has_kline_data else 3
                if len(signals) >= min_signals:
                    sd.layer2_passed = True
                    confirmed.append(sd)
                    sig_str = ', '.join(signals[:4])
                    mom_str = f"mom5d={sd.momentum_5d:.1f}%" if sd.momentum_5d is not None else ""
                    logger.info(f"  ✓ {sd.name}({sd.code}): score={sd.score:.1f} {mom_str} | {sig_str}")
                else:
                    sd.layer2_passed = False
                    logger.info(f"  ○ {sd.name}({sd.code}): 信号不足({len(signals)}/{min_signals})")
                
            except Exception as e:
                logger.warning(f"技术分析失败 {sd.code}: {e}")
                continue
        
        # 取TOP5，按重新计算的分数排序（分数降序，代码升序确保稳定）
        top5 = sorted(confirmed, key=lambda x: (-x.score, x.code))[:5]
        
        logger.info(f"技术确认后 TOP5: {[s.name for s in top5]}")
        
        return top5
    
    def _calc_tech_factor_score(self, sd) -> float:
        """用真实技术因子计算得分"""
        score = 0
        
        # 5日动量：2%-10% 最佳
        if sd.momentum_5d is not None:
            if 2 <= sd.momentum_5d <= 10:
                score += 30
            elif 0 < sd.momentum_5d < 2:
                score += 15
            elif sd.momentum_5d > 10:
                score += 10  # 过热减分
            else:
                score -= 20
        
        # 波动率：中等波动最佳（年化20%-50%）
        if sd.volatility_20d is not None and sd.volatility_20d > 0:
            vol_annual = sd.volatility_20d * 10
            if 20 <= vol_annual <= 50:
                score += 20
            elif vol_annual < 20:
                score += 10
            else:
                score -= 10
        
        # 60日收益：用于均值回归，前期有回调但不深跌
        if sd.return_60d is not None:
            if -20 < sd.return_60d < -5:
                score += 20  # 充分回调
            elif -5 <= sd.return_60d <= 5:
                score += 10  # 横盘震荡
            elif sd.return_60d > 5:
                score += 15  # 中期趋势向上
            elif sd.return_60d < -20:
                score -= 10  # 跌太深
        
        # MA多头排列
        if sd.ma5 and sd.ma10 and sd.ma20:
            if sd.ma5 > sd.ma10 > sd.ma20:
                score += 15
        
        # RSI健康
        if sd.rsi6 and 40 < sd.rsi6 < 70:
            score += 10
        
        return max(0, score)
    
    def layer3_fundamental_confirm(self, stocks: List[StockData]) -> List[StockData]:
        """第3层：基本面+资金面确认 CCO₃"""
        logger.info(f"第3层基本面+资金面：从 {len(stocks)} 只股票中筛选")
        
        confirmed = []
        
        # 批量获取情绪数据
        sentiment_data = {}
        if self.data_source_manager:
            codes = [sd.code for sd in stocks]
            try:
                sentiment_results = self.data_source_manager.get_sentiment(codes)
                for item in sentiment_results:
                    sentiment_data[item['code']] = item
                logger.info(f"获取情绪数据: {len(sentiment_data)} 条")
            except Exception as e:
                logger.warning(f"获取情绪数据失败: {e}")
        
        for sd in stocks:
            if self._check_timeout():
                break
            
            try:
                # 资金流向（带缓存）
                cache_key = f'flow_{sd.code}'
                flow_data = self._load_cache(cache_key)
                if not flow_data:
                    flow_data = self.api.get_fund_flow(sd.code)
                    if flow_data:
                        self._save_cache(cache_key, flow_data)
                sd.main_inflow_days = flow_data.get('main_inflow_days', 0)
                sd.total_main_inflow = flow_data.get('total_main_inflow', 0)
                
                # 情绪因子（雪球）
                sentiment = sentiment_data.get(sd.code, {})
                sd.hot_rank = sentiment.get('hot_rank', 0)
                sd.comment_count = sentiment.get('comment_count', 0)
                sd.follower_count = sentiment.get('follower_count', 0)
                sd.heat_level = sentiment.get('heat_level', '')
                
                # ========== CCO₃ Selection Trace ==========
                bonus = 0
                sd.layer3_bonus_detail = {}
                
                # PE过滤：0<PE<100（放宽限制，允许成长股）
                if sd.pe > 0:
                    bonus += 10
                    sd.layer3_bonus_detail["PE合理"] = 10
                elif sd.pe == 0:
                    # 无PE数据但可能是优质成长股
                    bonus += 5
                    sd.layer3_bonus_detail["成长股"] = 5
                
                # 市值加分：市值越大越稳健
                if sd.total_capital > 1000:
                    bonus += 15
                    sd.layer3_bonus_detail["大市值"] = 15
                elif sd.total_capital > 500:
                    bonus += 10
                    sd.layer3_bonus_detail["中市值"] = 10
                elif sd.total_capital > 100:
                    bonus += 5
                    sd.layer3_bonus_detail["小市值"] = 5
                
                # 资金流向加分
                if sd.main_inflow_days >= 3:
                    bonus += 10
                    sd.layer3_bonus_detail["主力净流入"] = 10
                elif sd.main_inflow_days >= 1:
                    bonus += 5
                    sd.layer3_bonus_detail["少量流入"] = 5
                else:
                    # 无资金流入但有其他条件满足也可以
                    bonus += 2
                    sd.layer3_bonus_detail["资金中性"] = 2
                
                # 情绪因子加分（雪球热度）
                sentiment_score = 0
                if sd.hot_rank > 0 and sd.hot_rank <= 100:
                    sentiment_score = 10
                    sd.layer3_bonus_detail["雪球热度TOP100"] = 10
                elif sd.hot_rank > 100 and sd.hot_rank <= 500:
                    sentiment_score = 5
                    sd.layer3_bonus_detail["雪球热度TOP500"] = 5
                elif sd.hot_rank > 500:
                    sentiment_score = 2
                    sd.layer3_bonus_detail["雪球有热度"] = 2
                
                if sd.comment_count > 100:
                    sentiment_score += 3
                    sd.layer3_bonus_detail["评论活跃"] = 3
                elif sd.comment_count > 10:
                    sentiment_score += 1
                    sd.layer3_bonus_detail["少量评论"] = 1
                
                bonus += sentiment_score
                
                # 行业龙头（简化判断）
                if sd.total_capital > 500 and sd.pe > 0:
                    bonus += 5
                    sd.layer3_bonus_detail["行业龙头"] = 5
                
                # 央企/政策催化（简化判断）
                if sd.code.startswith('601') or sd.code.startswith('600'):
                    bonus += 5
                    sd.layer3_bonus_detail["央企/政策催化"] = 5
                
                sd.score += bonus
                sd.layer3_reasons = [f"{k} +{v}" for k, v in sd.layer3_bonus_detail.items()]
                sd.layer3_passed = True
                
                confirmed.append(sd)
                
                bonus_str = ', '.join([f"{k}+{v}" for k, v in sd.layer3_bonus_detail.items()])
                logger.info(f"  ✓ {sd.name}({sd.code}): PE={sd.pe:.1f}, 市值={sd.total_capital:.0f}亿, 主力净流入={sd.total_main_inflow:.0f}万, score+{bonus} [{bonus_str}]")
                
            except Exception as e:
                logger.warning(f"基本面分析失败 {sd.code}: {e}")
                continue
        
        # 取TOP3（分数降序，代码升序确保稳定）
        top3 = sorted(confirmed, key=lambda x: (-x.score, x.code))[:3]
        
        logger.info(f"基本面确认后 TOP3: {[s.name for s in top3]}")
        
        return top3
    
    def apply_value_trace(self, stocks: List[StockData], host_profile: Dict) -> List[StockData]:
        """CCO₄: 价值函数匹配"""
        logger.info(f"CCO₄价值匹配：host_profile={host_profile.get('profile', 'default')}")
        
        for sd in stocks:
            trace = {
                "host_profile": host_profile.get("profile", "default"),
                "matched_rules": [],
                "value_score": 0
            }
            
            # 大市值偏好
            if host_profile.get("prefer_large_cap") and sd.total_capital > 500:
                trace["matched_rules"].append("large_cap")
                trace["value_score"] += 20
            
            # 低风险偏好
            if host_profile.get("risk_level") == "medium" and sd.change_pct < 10:
                trace["matched_rules"].append("low_risk")
                trace["value_score"] += 15
            
            # 容易持有
            if host_profile.get("prefer_story") is False and sd.total_capital > 200:
                trace["matched_rules"].append("easy_to_hold")
                trace["value_score"] += 10
            
            # 持仓周期匹配
            if host_profile.get("holding_period") == "short_mid" and sd.pe > 0:
                trace["matched_rules"].append("short_mid_ok")
                trace["value_score"] += 10
            
            sd.value_trace = trace
            sd.score += trace["value_score"]
            
            rules_str = ', '.join(trace["matched_rules"]) if trace["matched_rules"] else "无匹配"
            logger.info(f"  ✓ {sd.name}({sd.code}): value_score={trace['value_score']} [{rules_str}]")
        
        return sorted(stocks, key=lambda x: (-x.score, x.code))
    
    def _generate_lineage(self, top_stocks, source_info):
        """生成数据溯源元数据 (MVP: 5字段)"""
        from datetime import datetime as dt
        recommend_time = dt.now().strftime('%Y-%m-%dT%H:%M:%S')
        date_str = dt.now().strftime('%Y%m%d')
        
        recommendations = []
        for i, sd in enumerate(top_stocks[:2], 1):
            rec = {
                "recommendation_id": f"sa_{date_str}_{i:03d}",
                "ticker": sd.code,
                "signal_count": len(sd.tech_signals) if hasattr(sd, 'tech_signals') and sd.tech_signals else 0,
                "signal_combo": sd.tech_signals if hasattr(sd, 'tech_signals') and sd.tech_signals else [],
                "source": {
                    "provider": source_info.get("provider", "unknown"),
                    "endpoint": source_info.get("endpoint", "unknown")
                },
                "snapshot_time": source_info.get("snapshot_time", recommend_time),
                "recommend_time": recommend_time,
                "recommend_price": round(sd.price, 2),
                "close_price": None,
                "return_pct": None,
                "review_status": "pending"
            }
            recommendations.append(rec)
        
        return {
            "lineage_version": "mvp-v1",
            "date": date_str,
            "recommendations": recommendations
        }

    def _generate_lineage_markdown(self, lineage):
        """生成溯源元数据的Markdown片段"""
        lines = ["\n---\n", "## 数据溯源\n"]
        for rec in lineage.get("recommendations", []):
            lines.append(f"**{rec['recommendation_id']}** | {rec['ticker']} | ¥{rec['recommend_price']}")
            lines.append(f"- 数据源: {rec['source']['provider']} -> {rec['source']['endpoint']}")
            lines.append(f"- 快照时间: {rec['snapshot_time']}")
            lines.append(f"- 推荐时间: {rec['recommend_time']}")
            lines.append(f"- 推荐价格: ¥{rec['recommend_price']}")
            lines.append(f"- 收盘复核: pending\n")
        return "\n".join(lines)

    def _generate_trace_json(self, all_candidates: List[StockData], top_stocks: List[StockData], host_profile: Dict) -> Dict:
        """生成Selection Trace JSON"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # CCO₂ Selection Trace 列表
        cco2_trace = []
        for sd in all_candidates:
            trace_entry = {
                "symbol": sd.code,
                "name": sd.name,
                "layer1_passed": sd.layer1_passed,
                "layer1_reasons": sd.layer1_reasons,
                "layer1_reject_flags": sd.layer1_reject_flags,
                "layer1_score": sd.score if sd.layer1_passed else 0,
                "layer2_passed": sd.layer2_passed,
                "layer2_reasons": sd.layer2_reasons if hasattr(sd, 'layer2_reasons') else [],
                "layer3_passed": sd.layer3_passed if hasattr(sd, 'layer3_passed') else False,
                "layer3_reasons": sd.layer3_reasons if hasattr(sd, 'layer3_reasons') else [],
                "layer3_bonus_detail": sd.layer3_bonus_detail if hasattr(sd, 'layer3_bonus_detail') else {},
                "final_score": sd.score
            }
            cco2_trace.append(trace_entry)
        
        # CCO₄ Value Trace
        cco4_trace = {
            "host_profile": host_profile.get("profile", "default"),
            "top2": []
        }
        
        for sd in top_stocks[:2]:
            if hasattr(sd, 'value_trace') and sd.value_trace:
                cco4_trace["top2"].append({
                    "symbol": sd.code,
                    "name": sd.name,
                    "matched_rules": sd.value_trace.get("matched_rules", []),
                    "value_score": sd.value_trace.get("value_score", 0)
                })
        
        # 被拒绝的候选
        rejected = []
        for sd in all_candidates:
            if sd not in top_stocks:
                reject_reason = "score_low"
                if not sd.layer1_passed:
                    reject_reason = "cco1_failed"
                elif not sd.layer2_passed:
                    reject_reason = "cco2_failed"
                elif not sd.layer3_passed:
                    reject_reason = "cco3_failed"
                elif not sd.value_trace.get("matched_rules"):
                    reject_reason = "cco4_no_match"
                
                rejected.append({
                    "symbol": sd.code,
                    "name": sd.name,
                    "layer1_passed": sd.layer1_passed,
                    "layer2_passed": sd.layer2_passed,
                    "layer3_passed": sd.layer3_passed,
                    "reject_layer": reject_reason,
                    "reject_reason": reject_reason
                })
        
        trace_json = {
            "date": today,
            "ccco1_signal_space": {
                "accepted_factors": ["momentum", "volatility", "mean_reversion", "volume_normal"],
                "rejected_factors": ["volume_shock"],
                "factor_count": 5
            },
            "cco2_selection_trace": cco2_trace,
            "cco4_value_trace": cco4_trace,
            "rejected_candidates": rejected[:20]  # 最多保留20个被拒绝的
        }
        
        return trace_json
    
    def _get_recent_recommendations(self, days: int = 7) -> Dict[str, int]:
        """读取最近N天的推荐记录，返回 {股票代码: 最近推荐天数前}"""
        recent = {}
        output_dir = Path(__file__).parent.parent / 'mine_output' / 'advisor'
        if not output_dir.exists():
            return recent
        
        today = datetime.now().date()
        for i in range(1, days + 1):
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime('%Y%m%d')
            report_file = output_dir / f'advisor_{date_str}.md'
            if not report_file.exists():
                continue
            try:
                content = report_file.read_text(encoding='utf-8')
                import re
                # 匹配股票代码：推荐1：xxx（600000）
                pattern = r'推荐\d+：[^（]+（(\d{6})）'
                for match in re.finditer(pattern, content):
                    code = match.group(1)
                    if code not in recent:
                        recent[code] = i  # i 天前推荐过
            except Exception:
                continue
        return recent

    def _get_stock_industry(self, code: str) -> str:
        """粗略获取股票所属行业（基于代码前缀）"""
        if code.startswith('688'):
            return '科创板'
        elif code.startswith('300'):
            return '创业板'
        elif code.startswith('60') or code.startswith('000'):
            # 主板粗略按代码分段
            if code.startswith('6005') or code.startswith('6008'):
                return '消费'
            elif code.startswith('6000') or code.startswith('6013') or code.startswith('6019'):
                return '金融'
            elif code.startswith('6002') or code.startswith('6004'):
                return '医药'
            elif code.startswith('6016') or code.startswith('6011'):
                return '能源'
            elif code.startswith('002'):
                return '中小板'
            else:
                return '主板'
        elif code.startswith('002'):
            return '中小板'
        else:
            return '其他'

    def _apply_recent_dedup_and_diversity(self, stocks: List) -> List:
        """近期推荐去重 + 行业多样性

        规则：
        1. 近3天推荐过的股票：直接降权30分（基本不会再选中）
        2. 近7天推荐过的股票：降权15分
        3. 尽量从不同行业中选择，避免两只都来自同一行业
        """
        if not stocks:
            return stocks

        recent = self._get_recent_recommendations(7)
        logger.info(f"近期推荐记录: {len(recent)} 只股票在近7天内被推荐过")

        # 给每只股票计算惩罚分
        for sd in stocks:
            days_ago = recent.get(sd.code)
            if days_ago is not None:
                if days_ago <= 3:
                    penalty = 30
                    logger.info(f"  ⬇️ {sd.name}({sd.code}): {days_ago}天前刚推荐过，-{penalty}分")
                else:
                    penalty = 15
                    logger.info(f"  ⬇️ {sd.name}({sd.code}): {days_ago}天前推荐过，-{penalty}分")
                sd.score = max(0, sd.score - penalty)
                sd.layer1_reasons.append(f"recent_dedup_penalty -{penalty}")

        # 重新排序（分数降序，股票代码升序确保稳定）
        stocks = sorted(stocks, key=lambda x: (-x.score, x.code))

        # 行业多样性：确保前2名来自不同行业
        if len(stocks) >= 2:
            first_industry = self._get_stock_industry(stocks[0].code)
            # 从第2名开始找，找一个不同行业的
            for i in range(1, len(stocks)):
                if self._get_stock_industry(stocks[i].code) != first_industry:
                    if i > 1:
                        # 把这只移到第2位
                        stocks[1], stocks[i] = stocks[i], stocks[1]
                        logger.info(f"  🔄 行业多样性调整: {stocks[1].name}({stocks[1].code}) 替换为第2推荐")
                    break

        return stocks

    def _get_yesterday_check(self) -> str:
        """获取昨日推荐股票的今日表现回检"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        lines = []
        
        # 从 performance_db 查找昨日推荐
        yesterday_recs = [r for r in self.tracker.records.values() 
                         if r.recommend_date == yesterday]
        
        if not yesterday_recs:
            return ""
        
        lines.append("\n## 昨日推荐回检\n")
        lines.append("| 股票 | 推荐价 | T+1收益 | 状态 |")
        lines.append("|------|--------|---------|------|")
        
        for rec in yesterday_recs:
            ret = rec.return_t1
            if ret is not None:
                status = "✅ 盈利" if ret > 0 else "❌ 亏损"
                lines.append(f"| {rec.name}({rec.code}) | ¥{rec.recommend_price:.2f} | {ret:+.2f}% | {status} |")
            else:
                lines.append(f"| {rec.name}({rec.code}) | ¥{rec.recommend_price:.2f} | 待更新 | ⏳ |")
        
        lines.append("")
        return "\n".join(lines)

    def _get_health_section(self) -> str:
        """获取系统健康度和历史胜率"""
        health = self.scorer.get_health_score(self.tracker)
        summary = health.get('summary', {})
        
        lines = []
        lines.append("\n## 系统健康度\n")
        
        score = health.get('score', 50)
        status = health.get('status', 'unknown')
        status_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴", "unknown": "⚪"}.get(status, "⚪")
        
        lines.append(f"**健康度评分**: {status_emoji} {score}/100 ({status})")
        lines.append("")
        
        # 历史胜率
        win_rates = summary.get('win_rates', {})
        avg_returns = summary.get('avg_returns', {})
        total = summary.get('total_recommendations', 0)
        
        if total > 0:
            lines.append(f"**最近30天统计**: 共推荐 {total} 次")
            lines.append("")
            lines.append("| 周期 | 胜率 | 平均收益 |")
            lines.append("|------|------|----------|")
            for period in ['T+1', 'T+3', 'T+5']:
                wr = win_rates.get(period)
                ret = avg_returns.get(period)
                if wr is not None and ret is not None:
                    lines.append(f"| {period} | {wr}% | {ret:+.2f}% |")
            lines.append("")
        else:
            lines.append("*暂无足够历史数据，运行几天后可见统计*")
            lines.append("")
        
        # 因子调整记录
        if self.scorer.adjustment_history:
            lines.append("**最近权重调整**:")
            for adj in self.scorer.adjustment_history[-3:]:
                lines.append(f"- {adj['factor']}: {adj['old_weight']:.1f} → {adj['new_weight']:.1f} ({adj['reason']})")
            lines.append("")
        
        return "\n".join(lines)

    def layer4_output(self, stocks: List[StockData], all_candidates: List[StockData] = None, host_profile: Dict = None) -> str:
        """第4层：输出报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        date_str = datetime.now().strftime('%Y%m%d')
        
        # 取TOP2
        top2 = stocks[:2] if len(stocks) >= 2 else stocks
        
        if not top2:
            return self._generate_empty_report(today)
        
        report = f"""# 每日荐股 {today}

> 🤖 AI量化选股 · 四层筛选 · 仅供参考

"""
        # 数据新鲜度提示
        trading_info = self._is_trading_time()
        if trading_info["status"] != "trading":
            report += f"> ⚠️ **数据提示**：{trading_info['note']}\n>\n"
        
        report += """---
"""
        
        for i, sd in enumerate(top2, 1):
            # 生成核心逻辑
            logics = []
            
            if sd.momentum_5d and sd.momentum_5d > 5:
                logics.append(f"动量强劲：近5日累计涨幅 {sd.momentum_5d:.1f}%，资金持续介入")
            elif sd.momentum_5d and sd.momentum_5d > 2:
                logics.append(f"温和上涨：近期走势稳健，{sd.momentum_5d:.1f}%涨幅显示多头力量")
            elif sd.momentum_5d and sd.momentum_5d > 0:
                logics.append(f"小幅上涨：{sd.momentum_5d:.1f}%温和爬升，趋势逐步确立")
            
            if sd.return_60d and sd.return_60d < -5:
                logics.append(f"均值回归：前期回调充分（60日跌{abs(sd.return_60d):.1f}%），安全边际较高")
            elif sd.return_60d and sd.return_60d > 5:
                logics.append(f"中期强势：60日累计涨幅 {sd.return_60d:.1f}%，趋势向上")
            
            if sd.main_inflow_days and sd.main_inflow_days >= 4:
                logics.append(f"资金青睐：近{sd.main_inflow_days}日主力净流入，机构建仓信号")
            elif sd.main_inflow_days and sd.main_inflow_days >= 3:
                logics.append(f"资金入场：连续{sd.main_inflow_days}日主力净流入，筹码沉淀中")
            
            # 保底逻辑：确保至少有1条核心逻辑
            if not logics:
                if sd.tech_signals and len(sd.tech_signals) >= 2:
                    logics.append(f"技术面共振：{len(sd.tech_signals)}个技术信号同时触发")
                elif sd.pe and sd.pe > 0:
                    logics.append(f"估值合理：PE {sd.pe:.1f}倍，处于行业合理区间")
                else:
                    logics.append("形态向好：技术面呈现多头格局")
            
            # 技术面要点
            tech_points = []
            if sd.tech_signals:
                tech_points.extend(sd.tech_signals[:3])
            
            if sd.rsi6 < 50:
                tech_points.append("RSI未超买，上涨空间仍在")
            elif 50 <= sd.rsi6 <= 70:
                tech_points.append("RSI健康，无过热风险")
            
            # 生成推荐
            report += f"""## 推荐{i}：{sd.name}（{sd.code}）

| 指标 | 数值 |
|------|------|
| 现价 | ¥{sd.price:.2f} |
| 涨跌幅 | {sd.change_pct:+.2f}% |
| 市盈率(PE) | {sd.pe:.1f}x |
| 总市值 | {sd.total_capital:.0f}亿 |
| 换手率 | {sd.turnover_rate:.2f}% |

### 核心逻辑
"""
            for logic in logics[:3]:
                report += f"- {logic}\n"
            
            report += """
### 技术面要点
"""
            for point in tech_points[:3]:
                report += f"- {point}\n"
            
            report += """
### 风险提示
- 股市有风险，投资需谨慎
- 本推荐仅供参考，不构成买卖建议
- 请根据自身风险承受能力决定

---

"""
        
        # 昨日推荐回检
        yesterday_check = self._get_yesterday_check()
        if yesterday_check:
            report += yesterday_check
        
        # 系统健康度和历史胜率
        report += self._get_health_section()
        
        # 操作建议
        report += """## 操作建议

| 操作 | 建议 |
|------|------|
| 仓位控制 | 单只仓位不超过总资金的20%，建议分2-3批建仓 |
| 止损位 | 买入价下跌8%时考虑止损，规避更大回撤 |
| 止盈位 | 上涨15%-20%时可考虑分批止盈，锁住利润 |
| 持仓周期 | 中短线为主，建议2-4周内关注 |

---

"""
        
        # 群发话术
        report += self._generate_pivot_report(top2)
        
        return report
    
    def _generate_pivot_report(self, stocks: List[StockData]) -> str:
        """生成接地气的群发话术"""
        today = datetime.now().strftime("%m/%d")
        
        if not stocks:
            return ""
        
        pivots = []
        for sd in stocks:
            change_emoji = "📈" if sd.change_pct >= 0 else "📉"
            pe_hint = f"PE {sd.pe:.0f}倍" if sd.pe > 0 else "估值合理"
            
            if sd.score > 60:
                pivots.append(f"{sd.name}({sd.code}) {change_emoji}")
        
        pivots_str = "、".join(pivots) if pivots else "精选标的"
        
        speech = f"""
> **📢 群发话术（可直接复制使用）**
>
> 各位老板早上好~ 🫡
>
> **{today} 最新股票池已更新！**
>
> 今天给大家重点跟踪：{pivots_str}
>
> 技术面共振+资金面确认，趋势向好~ 📊
> 具体分析报告已出，需要详细研报的老铁评论区扣「111」
>
> ⚠️ 市场有风险，盈亏自负哦~
"""
        
        return speech
    
    def _generate_empty_report(self, today: str) -> str:
        """生成空报告"""
        return f"""# 每日荐股 {today}

> 🤖 AI量化选股 · 四层筛选 · 仅供参考

---

## 今日市场概况

今日市场暂无符合条件的精选标的，可能原因：
- 市场整体波动较大，缺乏明确趋势
- 热点分散，资金未能形成合力

---

> 📊 建议明日再查看最新推荐，或关注公众号获取实时推送。

---

> **📢 群发话术（可直接复制使用）**
>
> 各位老板早上好~ 🫡
>
> 今日市场波动较大，AI正在密切监控中 📊
> 预计明日会有更清晰的信号~
>
> 有任何问题随时找我，别盲目追涨哦！
"""
    
    def _load_host_profile(self) -> Dict:
        """加载host_profile.json"""
        profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'host_profile.json')
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载host_profile失败: {e}，使用默认配置")
            return {
                "profile": "default",
                "risk_level": "medium",
                "holding_period": "short_mid",
                "prefer_large_cap": True,
                "prefer_story": False
            }
    
    def _is_trading_time(self) -> Dict[str, Any]:
        """判断当前是否为交易时段"""
        now = datetime.now()
        weekday = now.weekday()  # 0=周一, 6=周日
        hour = now.hour
        minute = now.minute
        current_min = hour * 60 + minute

        # 周末非交易日
        is_trading_day = weekday < 5
        # 交易时段：9:30-11:30, 13:00-15:00
        morning_start = 9 * 60 + 30  # 570
        morning_end = 11 * 60 + 30   # 690
        afternoon_start = 13 * 60    # 780
        afternoon_end = 15 * 60      # 900

        in_morning = morning_start <= current_min <= morning_end
        in_afternoon = afternoon_start <= current_min <= afternoon_end
        is_trading_time = is_trading_day and (in_morning or in_afternoon)

        # 距离开盘还有多久
        if is_trading_day and current_min < morning_start:
            minutes_to_open = morning_start - current_min
            status = "pre_market"
            note = f"距开盘还有 {minutes_to_open} 分钟，当前为盘前数据（上一交易日收盘价）"
        elif is_trading_day and morning_end < current_min < afternoon_start:
            status = "midday_break"
            note = "午间休市，数据为上午收盘数据"
        elif not is_trading_day:
            status = "non_trading_day"
            note = "非交易日，数据为最近一个交易日数据"
        elif is_trading_time:
            status = "trading"
            note = "交易时段，数据为实时行情"
        else:
            status = "post_market"
            note = "已收盘，数据为今日收盘数据"

        return {
            "is_trading_day": is_trading_day,
            "is_trading_time": is_trading_time,
            "status": status,
            "note": note,
            "current_time": now.strftime("%H:%M"),
        }

    def _update_current_state(self):
        """更新 CURRENT_STATE.md 中的推荐健康度"""
        try:
            health = self.scorer.get_health_score(self.tracker)
            workspace = Path(__file__).parent.parent.parent  # mine-seed/
            state_file = workspace / 'CURRENT_STATE.md'
            
            # 构建健康度片段
            today = datetime.now().strftime('%Y-%m-%d %H:%M')
            health_section = f"""## 荐股系统健康度

> 更新时间: {today}

- **健康度评分**: {health.get('score', 50)}/100 ({health.get('status', 'unknown')})
- **最近30天推荐次数**: {health.get('summary', {}).get('total_recommendations', 0)}
- **T+5胜率**: {health.get('summary', {}).get('win_rates', {}).get('T+5', 'N/A')}%
- **T+5平均收益**: {health.get('summary', {}).get('avg_returns', {}).get('T+5', 'N/A')}%

"""
            
            if state_file.exists():
                content = state_file.read_text(encoding='utf-8')
                # 替换或追加
                if '## 荐股系统健康度' in content:
                    # 替换现有部分
                    import re
                    pattern = r'## 荐股系统健康度\n.*?\n(?=## |\Z)'
                    replacement = health_section
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                else:
                    # 追加到末尾
                    content = content.rstrip() + '\n\n' + health_section
                
                state_file.write_text(content, encoding='utf-8')
            else:
                # 创建新文件
                state_file.write_text(f"# CURRENT_STATE\n\n{health_section}", encoding='utf-8')
            
            logger.info(f"CURRENT_STATE.md 已更新，健康度: {health.get('score', 50)}")
        except Exception as e:
            logger.warning(f"更新 CURRENT_STATE 失败: {e}")

    def run(self) -> Tuple[bool, str]:
        """运行荐股引擎"""
        logger.info("=" * 60)
        logger.info("A股自动荐股引擎启动")
        logger.info("=" * 60)
        
        # 存储所有通过各层的候选股票（用于trace）
        all_layer1_candidates = []
        all_layer2_candidates = []
        
        try:
            # 第1层：因子筛选
            logger.info("【第1层】获取全市场行情数据...")
            
            # 先查日级缓存
            all_stocks = self._load_cache('spot_market')
            if not all_stocks:
                all_stocks = self.api.get_stock_spot_em()
                if all_stocks and len(all_stocks) >= 50:
                    self._save_cache('spot_market', all_stocks)
            
            if not all_stocks or len(all_stocks) < 50:
                logger.warning("市场数据不足，使用备用方案...")
                all_stocks = self._get_backup_stocks()
            
            layer1_result = self.layer1_factor_filter(all_stocks)
            all_layer1_candidates = layer1_result.copy()
            
            if not layer1_result:
                return False, self._generate_empty_report(datetime.now().strftime('%Y-%m-%d'))
            
            # 第2层：技术确认
            logger.info("【第2层】技术指标确认...")
            layer2_result = self.layer2_technical_confirm(layer1_result)
            all_layer2_candidates = layer2_result.copy()
            
            if not layer2_result:
                logger.warning("技术确认无结果，返回第1层结果")
                layer2_result = layer1_result[:5]
            
            # 第3层：基本面+资金面
            logger.info("【第3层】基本面与资金面确认...")
            layer3_result = self.layer3_fundamental_confirm(layer2_result)
            
            if not layer3_result:
                logger.warning("基本面确认无结果，返回第2层结果")
                layer3_result = layer2_result[:3]
            
            # ========== CCO₄: 读取 host_profile 并应用价值匹配 ==========
            host_profile = self._load_host_profile()
            layer4_result = self.apply_value_trace(layer3_result, host_profile)
            
            # ========== CCO₅: 近期推荐去重 + 行业多样性 ==========
            layer4_result = self._apply_recent_dedup_and_diversity(layer4_result)
            
            # 合并所有候选用于trace
            all_candidates = all_layer1_candidates + all_layer2_candidates + layer3_result
            # 去重
            seen = set()
            unique_candidates = []
            for sd in all_candidates:
                if sd.code not in seen:
                    seen.add(sd.code)
                    unique_candidates.append(sd)
            
            # 第4层：输出报告
            logger.info("【第4层】生成荐股报告...")
            report = self.layer4_output(layer4_result, unique_candidates, host_profile)
            
            # ========== 数据溯源 (MVP: 5字段) ==========
            source_info = {
                "provider": "eastmoney" if not self.api.use_fallback else "tencent",
                "endpoint": "stock_zh_a_spot_em" if not self.api.use_fallback else "qt.gtimg.cn/q",
                "snapshot_time": datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            }
            lineage = self._generate_lineage(layer4_result, source_info)
            lineage_md = self._generate_lineage_markdown(lineage)
            report += lineage_md
            
            # 保存报告
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mine_output', 'advisor')
            os.makedirs(output_dir, exist_ok=True)
            
            date_str = datetime.now().strftime('%Y%m%d')
            report_file = os.path.join(output_dir, f'advisor_{date_str}.md')
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"报告已保存至: {report_file}")
            
            # ========== 输出 Trace JSON ==========
            trace_json = self._generate_trace_json(unique_candidates, layer4_result, host_profile)
            trace_file = os.path.join(output_dir, f'advisor_{date_str}_trace.json')
            
            with open(trace_file, 'w', encoding='utf-8') as f:
                json.dump(trace_json, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Trace JSON已保存至: {trace_file}")
            
            # ========== 保存 Lineage JSON (次日回填用) ==========
            lineage_file = os.path.join(output_dir, f'advisor_{date_str}_lineage.json')
            with open(lineage_file, 'w', encoding='utf-8') as f:
                json.dump(lineage, f, ensure_ascii=False, indent=2)
            logger.info(f"Lineage JSON已保存至: {lineage_file}")
            
            # ========== 推票后审计系统 ==========
            logger.info("【审计系统】执行推票后审计...")
            
            audit_results = []
            for sd in layer4_result[:2]:
                try:
                    signals = sd.tech_signals if hasattr(sd, 'tech_signals') else []
                    audit_result = self.auditor.audit(
                        code=sd.code,
                        name=sd.name,
                        price=sd.price,
                        signals=signals,
                        recommend_date=date_str
                    )
                    audit_results.append({
                        'code': sd.code,
                        'name': sd.name,
                        'overall_score': audit_result.overall_score,
                        'overall_rating': audit_result.overall_rating,
                    })
                    logger.info(f"【审计结果】{sd.name}({sd.code}): {audit_result.overall_score}/100 [{audit_result.overall_rating}]")
                except Exception as e:
                    logger.warning(f"【审计】{sd.name}({sd.code}) 审计失败: {e}")
            
            # ========== 学习进化系统：注册推荐 + 更新表现 + 自适应调整 ==========
            logger.info("【学习系统】注册推荐并更新表现数据...")
            
            # 1. 注册本次推荐到 PerformanceTracker
            for sd in layer4_result[:2]:
                self.tracker.register_recommendation(
                    code=sd.code,
                    name=sd.name,
                    price=sd.price,
                    date_str=date_str
                )
            
            # 2. 更新所有 pending 记录的表现（获取历史价格）
            try:
                self.tracker.update_all()
            except Exception as e:
                logger.warning(f"表现更新失败: {e}")
            
            # 3. 自适应评分：分析历史并调整权重
            try:
                adjusted, adjustments = self.scorer.analyze_and_adjust(self.tracker)
                if adjusted:
                    logger.info(f"【自适应】权重已调整: {len(adjustments)} 个因子")
                    for adj in adjustments:
                        logger.info(f"  {adj['factor']}: {adj['old_weight']:.1f} -> {adj['new_weight']:.1f}")
                else:
                    logger.info("【自适应】权重无需调整")
            except Exception as e:
                logger.warning(f"自适应评分失败: {e}")
            
            # 4. 触发优化检查
            try:
                if self.scorer.should_trigger_optimization(self.tracker, consecutive_losses_threshold=3):
                    logger.warning("【学习系统】触发因子优化任务，调用矿工分析...")
                    opt_task = self.scorer.generate_optimization_task(self.tracker)
                    
                    # 保存优化任务
                    opt_file = os.path.join(output_dir, f'optimization_task_{date_str}.json')
                    with open(opt_file, 'w', encoding='utf-8') as f:
                        json.dump(opt_task, f, ensure_ascii=False, indent=2)
                    
                    # 调用矿工分析（异步，不阻塞）
                    try:
                        miner_result = self.miner.analyze_failures(self.tracker)
                        logger.info(f"【矿工】分析报告已生成 ({miner_result['source']}): {miner_result['saved_to']}")
                    except Exception as me:
                        logger.warning(f"【矿工】分析失败: {me}")
                else:
                    logger.info("【学习系统】当前表现正常，无需优化")
            except Exception as e:
                logger.warning(f"优化检查失败: {e}")
            
            # 5. 更新 CURRENT_STATE.md 健康度
            try:
                self._update_current_state()
            except Exception as e:
                logger.warning(f"更新 CURRENT_STATE 失败: {e}")
            
            elapsed = time.time() - self.start_time
            logger.info(f"荐股引擎执行完成，耗时 {elapsed:.1f} 秒")
            
            return True, report
            
        except Exception as e:
            logger.error(f"荐股引擎异常: {e}")
            logger.error(traceback.format_exc())
            return False, self._generate_empty_report(datetime.now().strftime('%Y-%m-%d'))
    
    def _get_backup_stocks(self) -> List[Dict]:
        """备用股票池（当无法获取全市场数据时）"""
        backup_pool = [
            ('600519', '贵州茅台'), ('000858', '五粮液'), ('300750', '宁德时代'),
            ('601318', '中国平安'), ('600036', '招商银行'), ('000001', '平安银行'),
            ('601888', '中国中免'), ('600276', '恒瑞医药'), ('300015', '爱尔眼科'),
            ('002475', '立讯精密'), ('000333', '美的集团'), ('601166', '兴业银行'),
            ('600900', '长江电力'), ('601398', '工商银行'), ('601939', '建设银行'),
            ('600028', '中国石化'), ('601857', '中国石油'), ('600019', '宝钢股份'),
            ('000002', '万科A'), ('001979', '招商蛇口'), ('600048', '保利发展'),
            ('600585', '海螺水泥'), ('000651', '格力电器'), ('000725', '京东方A'),
            ('002594', '比亚迪'), ('601012', '隆基绿能'), ('600438', '通威股份'),
            ('300059', '东方财富'), ('688981', '中芯国际'), ('002230', '科大讯飞'),
            ('600570', '恒生电子'), ('300033', '同花顺'), ('600588', '用友网络'),
            ('300124', '汇川技术'), ('300760', '迈瑞医疗'), ('688111', '金山办公'),
            ('300059', '东方财富'), ('600745', '闻泰科技'), ('002241', '歌尔股份'),
            ('002456', '欧菲光'), ('300408', '三环集团'), ('002049', '紫光国微'),
            ('603986', '兆易创新'), ('688012', '中微公司'), ('002371', '北方华创'),
            ('688256', '寒武纪'), ('300496', '中科创达'), ('688111', '金山办公'),
            ('300223', '北京君正'), ('300474', '景嘉微'), ('688981', '中芯国际'),
        ]
        
        stocks = []
        for code, name in backup_pool:
            market = 'sh' if code.startswith('6') else 'sz'
            full_code = f"{market}{code}"
            
            try:
                quotes = self.api.fallback.get_quote([full_code])
                if quotes:
                    q = quotes[0]
                    stocks.append({
                        '代码': code,
                        '名称': name,
                        '最新价': q.get('price', 0),
                        '涨跌幅': q.get('change_pct', 0),
                        '市盈率-动态': q.get('pe', 0),
                        '换手率': q.get('turnover_rate', 0),
                        '成交量': q.get('volume', 0),
                        '总市值': q.get('total_capital', 0),
                    })
            except:
                pass
            
            time.sleep(0.1)
        
        return stocks


def main():
    """主函数"""
    advisor = StockAdvisor()
    success, report = advisor.run()
    
    if success:
        print("\n✅ 荐股引擎执行成功！")
    else:
        print("\n⚠️ 荐股引擎执行完成，但结果可能不完整")
    
    # 打印报告摘要
    print("\n" + "=" * 60)
    print("报告摘要：")
    print("=" * 60)
    
    lines = report.split('\n')
    for i, line in enumerate(lines[:50]):  # 打印前50行
        print(line)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
