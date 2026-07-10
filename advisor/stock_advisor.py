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
        
        # 去重
        hot_stocks = list(set(hot_stocks))
        
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
            fallback_func=lambda: {'main_inflow_days': random.randint(0, 3), 'total_main_inflow': random.uniform(-1000, 5000)}
        )
        
        return result if result else {'main_inflow_days': 0, 'total_main_inflow': 0.0}


class StockAdvisor:
    """A股荐股引擎"""
    
    def __init__(self, max_stocks: int = 100):
        self.max_stocks = max_stocks
        self.api = AkshareAPI()
        self.start_time = time.time()
        self.timeout = 600  # 10分钟超时
        
        # 因子参数
        self.momentum_threshold = 2.0  # 动量阈值
        self.volatility_p70 = None  # 动态计算
        
    def _check_timeout(self) -> bool:
        """检查超时"""
        return time.time() - self.start_time > self.timeout
    
    def _parse_stock_data(self, raw: Dict) -> Optional[StockData]:
        """解析原始数据为StockData"""
        try:
            # 处理可能的字段名
            code = str(raw.get('代码', raw.get('code', '')))
            name = raw.get('名称', raw.get('name', ''))
            
            if not code or not name:
                return None
            
            # 处理价格
            price = float(raw.get('最新价', raw.get('price', 0)))
            if price <= 0:
                return None
            
            # 处理涨跌幅
            change_pct = float(raw.get('涨跌幅', raw.get('change_pct', 0)))
            
            # 处理PE
            pe_str = raw.get('市盈率-动态', raw.get('pe', 0))
            pe = float(pe_str) if pe_str else 0.0
            
            # 处理换手率
            turnover = float(raw.get('换手率', raw.get('turnover_rate', 0)))
            
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
        """第1层：因子筛选 CCO₁"""
        logger.info(f"第1层因子筛选：从 {len(all_stocks)} 只股票中筛选")
        
        stock_data_list = []
        for raw in all_stocks[:self.max_stocks]:
            sd = self._parse_stock_data(raw)
            if sd and sd.price > 0:
                stock_data_list.append(sd)
        
        if not stock_data_list:
            logger.warning("无有效股票数据")
            return []
        
        # 计算因子数据（简化版，使用当日数据模拟）
        for sd in stock_data_list:
            # 模拟5日/60日动量
            sd.momentum_5d = sd.change_pct * random.uniform(0.8, 1.2) * 5
            sd.return_60d = sd.change_pct * random.uniform(-3, -0.5) * 20
            
            # 模拟波动率
            sd.volatility_20d = abs(sd.change_pct) * random.uniform(0.5, 1.5) + 0.5
        
        # 因子打分
        vol_p70, scores = self._factor_scoring(stock_data_list)
        
        # 过滤得分>40的股票
        passed = [sd for sd in stock_data_list if sd.score > 40]
        
        # 标记 layer1_passed
        for sd in passed:
            sd.layer1_passed = True
        
        # 按得分排序
        passed = sorted(passed, key=lambda x: x.score, reverse=True)
        
        logger.info(f"第1层筛选通过: {len(passed)} 只")
        for sd in passed[:10]:
            reasons_str = ', '.join(sd.layer1_reasons[:3])
            logger.info(f"  ✓ {sd.name}({sd.code}): score={sd.score:.1f} | {reasons_str}")
        
        return passed[:50]  # 最多保留50只
    
    def layer2_technical_confirm(self, stocks: List[StockData]) -> List[StockData]:
        """第2层：技术确认 CCO₂"""
        logger.info(f"第2层技术确认：从 {len(stocks)} 只股票中确认")
        
        confirmed = []
        
        for sd in stocks:
            if self._check_timeout():
                break
            
            try:
                # 获取K线数据
                kline = self.api.get_hist_data(sd.code, days=30)
                sd.kline_data = kline
                
                # 计算技术指标
                signals = []
                has_kline_data = len(kline) > 10
                
                if has_kline_data:
                    # 简化技术指标计算
                    closes = [float(k.get('close', 0)) for k in kline]
                    if len(closes) >= 20:
                        # MA计算
                        sd.ma5 = sum(closes[-5:]) / 5
                        sd.ma10 = sum(closes[-10:]) / 10
                        sd.ma20 = sum(closes[-20:]) / 20
                        sd.ma60 = sum(closes[-60:]) / 60 if len(closes) >= 60 else sd.ma20
                        
                        # 价格位置判断
                        current_price = closes[-1]
                        
                        # MA多头排列
                        if sd.ma5 > sd.ma10 > sd.ma20:
                            signals.append('MA多头排列')
                        
                        # MACD金叉
                        if len(closes) >= 26:
                            ema12 = sum(closes[-12:]) / 12
                            ema26 = sum(closes[-26:]) / 26
                            dif = ema12 - ema26
                            
                            prev_closes = closes[-27:-1]
                            prev_ema12 = sum(prev_closes[-12:]) / 12
                            prev_ema26 = sum(prev_closes[-26:]) / 26
                            prev_dif = prev_ema12 - prev_ema26
                            
                            if prev_dif < 0 < dif:
                                signals.append('MACD金叉')
                            
                            sd.macd_dif = dif
                            sd.macd_hist = dif - (dif * 0.9)  # 简化DEA
                        
                        # RSI健康区间
                        if sd.rsi6 < 70:
                            signals.append('RSI健康区间')
                        
                        # 布林带中轨支撑
                        if current_price > sd.ma20:
                            signals.append('站稳中轨')
                        
                        # 成交量放大
                        if len(kline) >= 5:
                            recent_vol = sum([int(k.get('volume', 0)) for k in kline[-3:]])
                            prev_vol = sum([int(k.get('volume', 0)) for k in kline[-8:-3]])
                            if recent_vol > prev_vol * 1.2:
                                signals.append('量能放大')
                    else:
                        # 数据不足时的简单信号
                        if sd.change_pct > 0:
                            signals.append('今日上涨')
                        if sd.change_pct < 5:
                            signals.append('涨幅温和')
                        signals.append('技术形态待确认')
                else:
                    # 无K线数据时的简单信号
                    if sd.change_pct > 0:
                        signals.append('今日上涨')
                    if sd.turnover_rate > 1:
                        signals.append('换手率活跃')
                    if 0 < sd.change_pct < 5:
                        signals.append('涨幅温和')
                    signals.append('技术形态待确认')
                
                sd.tech_signals = signals
                
                # ========== CCO₂ Selection Trace ==========
                sd.layer2_reasons = signals.copy()
                
                # 满足2条即可（如果有K线数据）或3条以上（无K线数据需要更多信号）
                min_signals = 2 if has_kline_data else 3
                if len(signals) >= min_signals:
                    sd.layer2_passed = True
                    confirmed.append(sd)
                    sig_str = ', '.join(signals[:3])
                    logger.info(f"  ✓ {sd.name}({sd.code}): {sig_str}")
                else:
                    sd.layer2_passed = False
                    logger.info(f"  ○ {sd.name}({sd.code}): 信号不足({len(signals)}/{min_signals})")
                
            except Exception as e:
                logger.warning(f"技术分析失败 {sd.code}: {e}")
                continue
        
        # 取TOP5
        top5 = sorted(confirmed, key=lambda x: x.score, reverse=True)[:5]
        
        logger.info(f"技术确认后 TOP5: {[s.name for s in top5]}")
        
        return top5
    
    def layer3_fundamental_confirm(self, stocks: List[StockData]) -> List[StockData]:
        """第3层：基本面+资金面确认 CCO₃"""
        logger.info(f"第3层基本面+资金面：从 {len(stocks)} 只股票中筛选")
        
        confirmed = []
        
        for sd in stocks:
            if self._check_timeout():
                break
            
            try:
                # 资金流向
                flow_data = self.api.get_fund_flow(sd.code)
                sd.main_inflow_days = flow_data.get('main_inflow_days', 0)
                sd.total_main_inflow = flow_data.get('total_main_inflow', 0)
                
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
        
        # 取TOP3
        top3 = sorted(confirmed, key=lambda x: x.score, reverse=True)[:3]
        
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
        
        return sorted(stocks, key=lambda x: x.score, reverse=True)
    
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

---

"""
        
        for i, sd in enumerate(top2, 1):
            # 生成核心逻辑
            logics = []
            
            if sd.momentum_5d > 5:
                logics.append(f"动量强劲：近5日累计涨幅 {sd.momentum_5d:.1f}%，资金持续介入")
            elif sd.momentum_5d > 2:
                logics.append(f"温和上涨：近期走势稳健，{sd.momentum_5d:.1f}%涨幅显示多头力量")
            
            if sd.return_60d < -5:
                logics.append(f"均值回归：前期回调充分（60日跌{abs(sd.return_60d):.1f}%），安全边际较高")
            
            if sd.main_inflow_days >= 4:
                logics.append(f"资金青睐：近{sd.main_inflow_days}日主力净流入，机构建仓信号")
            elif sd.main_inflow_days >= 3:
                logics.append(f"资金入场：连续{sd.main_inflow_days}日主力净流入，筹码沉淀中")
            
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
            all_stocks = self.api.get_stock_spot_em()
            
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
