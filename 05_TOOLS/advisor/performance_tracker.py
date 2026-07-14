#!/usr/bin/env python3
"""
Performance Tracker — 荐股表现跟踪器

追踪每次推荐后的实际表现，形成学习闭环：
  推荐 → 跟踪 → 评分 → 反馈 → 调整权重

追踪维度：
  - T+1 收益率（次日开盘买入，收盘卖出）
  - T+3 收益率（3日后）
  - T+5 收益率（5日后）
  - T+10 收益率（10日后）
  - T+20 收益率（20日后，约1个月）

表现数据持久化到 JSON，供 AdaptiveScorer 读取。
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent))
from stock_query import get_stock_query

LOG_DIR = Path(__file__).parent.parent / 'mine_output' / 'advisor'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'performance.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceRecord:
    """单条表现记录"""
    recommend_date: str       # 推荐日期 YYYYMMDD
    code: str                 # 股票代码
    name: str                 # 股票名称
    recommend_price: float    # 推荐时价格
    
    # 各周期收益率 (%)
    return_t1: Optional[float] = None
    return_t3: Optional[float] = None
    return_t5: Optional[float] = None
    return_t10: Optional[float] = None
    return_t20: Optional[float] = None
    
    # 最高价收益率（期间内最高）
    max_return_t20: Optional[float] = None
    
    # 状态
    status: str = "pending"   # pending / partial / complete
    
    # 元数据
    updated_at: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "PerformanceRecord":
        return cls(**d)


class PerformanceTracker:
    """荐股表现跟踪器"""
    
    DATA_FILE = LOG_DIR / 'performance_db.json'
    
    def __init__(self):
        self.records: Dict[str, PerformanceRecord] = {}  # key: "YYYYMMDD_CODE"
        self.query = get_stock_query()
        self._load_db()
    
    def _load_db(self):
        """加载历史表现数据库"""
        if self.DATA_FILE.exists():
            try:
                data = json.loads(self.DATA_FILE.read_text(encoding='utf-8'))
                for key, rec in data.items():
                    self.records[key] = PerformanceRecord.from_dict(rec)
                logger.info(f"加载表现数据库: {len(self.records)} 条记录")
            except Exception as e:
                logger.warning(f"加载表现数据库失败: {e}")
    
    def _save_db(self):
        """保存表现数据库"""
        try:
            data = {k: v.to_dict() for k, v in self.records.items()}
            self.DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
        except Exception as e:
            logger.warning(f"保存表现数据库失败: {e}")
    
    def register_recommendation(self, code: str, name: str, price: float, date_str: str = None):
        """注册一条新推荐记录"""
        date_str = date_str or datetime.now().strftime('%Y%m%d')
        key = f"{date_str}_{code}"
        
        if key in self.records:
            logger.info(f"表现记录已存在: {key}")
            return
        
        self.records[key] = PerformanceRecord(
            recommend_date=date_str,
            code=code,
            name=name,
            recommend_price=price,
            updated_at=datetime.now().isoformat()
        )
        self._save_db()
        logger.info(f"注册表现跟踪: {name}({code}) @ {price:.2f} on {date_str}")
    
    def _is_trading_day(self, date_obj) -> bool:
        """判断是否为交易日（简单版本：排除周末）"""
        if date_obj.weekday() >= 5:
            return False
        return True
    
    def _get_trading_day(self, start_date: datetime, offset_days: int) -> datetime:
        """获取从 start_date 开始的第 offset_days 个交易日"""
        current = start_date
        count = 0
        
        while count < offset_days:
            current = current + timedelta(days=1)
            if self._is_trading_day(current):
                count += 1
        
        return current
    
    def _get_historical_price(self, code: str, target_date: str) -> Optional[float]:
        """获取某只股票在某交易日的收盘价（多级降级）
        
        注意：对于未来日期，返回 None，不使用当前价格推断
        """
        target_dt = datetime.strptime(target_date, '%Y%m%d')
        today = datetime.now().date()
        
        # 对于未来日期，直接返回 None（不预测未来价格）
        if target_dt.date() > today:
            logger.debug(f"目标日期 {target_date} 是未来，跳过")
            return None
        
        # Level 1: akshare 历史数据
        try:
            import akshare as ak
            start_date = (target_dt - timedelta(days=30)).strftime('%Y%m%d')
            end_date = target_date
            
            df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                    start_date=start_date, end_date=end_date, adjust='qfq')
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    row_date = str(row.get('日期', '')).replace('-', '')
                    if row_date == target_date:
                        price = float(row.get('收盘', 0))
                        if price > 0:
                            return price
        except Exception as e:
            logger.debug(f"akshare 获取历史价格失败 {code} {target_date}: {e}")
        
        # Level 2: 腾讯 K线 API（含日期推断）
        try:
            kline = self.query.get_hist_kline(code, days=60)
            if kline:
                # 精确匹配
                for k in kline:
                    k_date = k.get('date', '').replace('-', '')
                    if k_date == target_date:
                        price = float(k.get('close', 0))
                        if price > 0:
                            return price
                
                # 日期推断：查找最近的交易日（仅用于节假日）
                kline_dates = []
                for k in kline:
                    k_date_str = k.get('date', '')
                    if k_date_str:
                        try:
                            k_date = datetime.strptime(k_date_str, '%Y-%m-%d').date()
                            kline_dates.append((k_date, k.get('close')))
                        except Exception:
                            pass
                
                if kline_dates:
                    target_date_obj = target_dt.date()
                    
                    previous_dates = [d for d in kline_dates if d[0] <= target_date_obj]
                    if previous_dates:
                        closest_date, closest_price = sorted(previous_dates, key=lambda x: x[0], reverse=True)[0]
                        days_diff = (target_date_obj - closest_date).days
                        if days_diff <= 3:
                            logger.info(f"日期推断: {target_date} -> {closest_date} ({days_diff}天前), price={closest_price}")
                            price = float(closest_price)
                            if price > 0:
                                return price
        
        except Exception as e:
            logger.debug(f"腾讯 K线 获取历史价格失败 {code} {target_date}: {e}")
        
        # Level 3: 只有 target_date 是今天时返回当前价格
        today_str = today.strftime('%Y%m%d')
        if target_date == today_str:
            try:
                market = 'sh' if code.startswith('6') else 'sz'
                quotes = self.query.get_quote([f"{market}{code}"])
                if quotes:
                    price = quotes[0].get('price')
                    if price and price > 0:
                        return price
            except Exception as e:
                logger.debug(f"腾讯行情 fallback 失败 {code}: {e}")
        
        logger.warning(f"获取历史价格失败 {code} {target_date}: 所有数据源均不可用")
        return None
    
    def update_all(self):
        """更新所有 pending 记录的表现数据（使用交易日计算）"""
        today = datetime.now().date()
        updated_count = 0
        
        for key, rec in self.records.items():
            if rec.status == "complete":
                continue
            
            recommend_date = datetime.strptime(rec.recommend_date, '%Y%m%d').date()
            
            # 计算交易日数（从推荐日期后一天到今天，包含今天）
            trading_days_since = 0
            current = recommend_date
            while current <= today:
                current = current + timedelta(days=1)
                if self._is_trading_day(current):
                    trading_days_since += 1
            
            if trading_days_since < 1:
                continue  # 还没有过任何交易日
            
            # 计算各周期收益率（使用交易日）
            periods = [
                (1, 'return_t1'),
                (3, 'return_t3'),
                (5, 'return_t5'),
                (10, 'return_t10'),
                (20, 'return_t20'),
            ]
            
            any_updated = False
            for days, attr in periods:
                if trading_days_since >= days and getattr(rec, attr) is None:
                    target_date = self._get_trading_day(recommend_date, days).strftime('%Y%m%d')
                    price = self._get_historical_price(rec.code, target_date)
                    if price and price > 0 and rec.recommend_price > 0:
                        ret = (price / rec.recommend_price - 1) * 100
                        setattr(rec, attr, round(ret, 2))
                        any_updated = True
                        logger.info(f"  {rec.name}({rec.code}) T+{days}: {ret:+.2f}%")
                        time.sleep(0.3)  # 限速
            
            # T+20 完成后标记为 complete
            if trading_days_since >= 20 and rec.return_t20 is not None:
                rec.status = "complete"
            elif any_updated:
                rec.status = "partial"
            
            if any_updated:
                rec.updated_at = datetime.now().isoformat()
                updated_count += 1
        
        if updated_count > 0:
            self._save_db()
            logger.info(f"更新了 {updated_count} 条表现记录")
    
    def get_summary(self, days: int = 30) -> Dict[str, Any]:
        """获取最近 N 天的表现摘要"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        recent_records = [r for r in self.records.values() if r.recommend_date >= cutoff]
        
        if not recent_records:
            return {"message": "暂无表现数据", "records": 0}
        
        # 统计各周期平均收益
        def avg_returns(attr: str) -> Optional[float]:
            vals = [getattr(r, attr) for r in recent_records if getattr(r, attr) is not None]
            return round(sum(vals) / len(vals), 2) if vals else None
        
        # 胜率统计
        def win_rate(attr: str) -> Optional[float]:
            vals = [getattr(r, attr) for r in recent_records if getattr(r, attr) is not None]
            if not vals:
                return None
            wins = sum(1 for v in vals if v > 0)
            return round(wins / len(vals) * 100, 1)
        
        summary = {
            "period_days": days,
            "total_recommendations": len(recent_records),
            "complete_records": sum(1 for r in recent_records if r.status == "complete"),
            "avg_returns": {
                "T+1": avg_returns('return_t1'),
                "T+3": avg_returns('return_t3'),
                "T+5": avg_returns('return_t5'),
                "T+10": avg_returns('return_t10'),
                "T+20": avg_returns('return_t20'),
            },
            "win_rates": {
                "T+1": win_rate('return_t1'),
                "T+3": win_rate('return_t3'),
                "T+5": win_rate('return_t5'),
                "T+10": win_rate('return_t10'),
                "T+20": win_rate('return_t20'),
            },
            "best_performers": self._get_best_performers(recent_records, 5),
            "worst_performers": self._get_worst_performers(recent_records, 5),
        }
        
        return summary
    
    def _get_best_performers(self, records: List[PerformanceRecord], n: int) -> List[Dict]:
        """获取表现最好的 N 只"""
        # 用 T+5 收益排序，如果没有用 T+3，再没有 T+1
        def sort_key(r: PerformanceRecord):
            return (r.return_t5 if r.return_t5 is not None else
                    r.return_t3 if r.return_t3 is not None else
                    r.return_t1 if r.return_t1 is not None else -999)
        
        sorted_records = sorted(records, key=sort_key, reverse=True)[:n]
        return [
            {
                "date": r.recommend_date,
                "code": r.code,
                "name": r.name,
                "recommend_price": r.recommend_price,
                "return_t1": r.return_t1,
                "return_t3": r.return_t3,
                "return_t5": r.return_t5,
            }
            for r in sorted_records
        ]
    
    def _get_worst_performers(self, records: List[PerformanceRecord], n: int) -> List[Dict]:
        """获取表现最差的 N 只"""
        def sort_key(r: PerformanceRecord):
            return (r.return_t5 if r.return_t5 is not None else
                    r.return_t3 if r.return_t3 is not None else
                    r.return_t1 if r.return_t1 is not None else 999)
        
        sorted_records = sorted(records, key=sort_key)[:n]
        return [
            {
                "date": r.recommend_date,
                "code": r.code,
                "name": r.name,
                "recommend_price": r.recommend_price,
                "return_t1": r.return_t1,
                "return_t3": r.return_t3,
                "return_t5": r.return_t5,
            }
            for r in sorted_records
        ]
    
    def get_factor_effectiveness(self, period: str = "T+5") -> Dict[str, Any]:
        """
        分析各因子的有效性（需要配合 trace 数据）
        返回各信号的成功率统计
        
        Args:
            period: 统计周期，支持 "T+1" / "T+5"
        
        Returns:
            Dict[factor, {count, win_rate, avg_return}]
        
        P0 修复：支持 T+1 数据，打破"没有T+5→没有调整→没有T+5"的死循环
        """
        # 确定使用哪个收益字段
        return_field = "return_t1" if period == "T+1" else "return_t5"
        
        # 读取 trace 文件，关联表现数据
        trace_dir = LOG_DIR
        factor_stats = {}
        
        for key, rec in self.records.items():
            # 使用指定的收益字段
            ret_value = getattr(rec, return_field, None)
            if ret_value is None:
                continue
            
            trace_file = trace_dir / f"advisor_{rec.recommend_date}_trace.json"
            if not trace_file.exists():
                continue
            
            try:
                trace = json.loads(trace_file.read_text(encoding='utf-8'))
                for candidate in trace.get("cco2_selection_trace", []):
                    if candidate.get("symbol") == rec.code:
                        # 统计 layer1 因子的成功率
                        for reason in candidate.get("layer1_reasons", []):
                            factor = reason.split()[0] if reason else "unknown"
                            if factor not in factor_stats:
                                factor_stats[factor] = {"count": 0, "wins": 0, "total_return": 0}
                            factor_stats[factor]["count"] += 1
                            if ret_value > 0:
                                factor_stats[factor]["wins"] += 1
                            factor_stats[factor]["total_return"] += ret_value
            except Exception:
                continue
        
        # 计算成功率（降低样本阈值到2，让调整更早启动）
        result = {}
        min_samples = 2 if period == "T+1" else 3  # T+1 样本更容易获得，阈值降低
        for factor, stats in factor_stats.items():
            if stats["count"] >= min_samples:
                result[factor] = {
                    "count": stats["count"],
                    "win_rate": round(stats["wins"] / stats["count"] * 100, 1),
                    "avg_return": round(stats["total_return"] / stats["count"], 2),
                }
        
        # 按胜率排序
        result = dict(sorted(result.items(), key=lambda x: x[1]["win_rate"], reverse=True))
        return result


def main():
    """CLI 入口"""
    import argparse
    parser = argparse.ArgumentParser(description="Performance Tracker")
    parser.add_argument("--update", action="store_true", help="Update all pending records")
    parser.add_argument("--summary", type=int, default=30, help="Show summary for N days")
    parser.add_argument("--factors", action="store_true", help="Show factor effectiveness")
    args = parser.parse_args()
    
    tracker = PerformanceTracker()
    
    if args.update:
        tracker.update_all()
    
    if args.summary:
        summary = tracker.get_summary(args.summary)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    if args.factors:
        factors = tracker.get_factor_effectiveness()
        print(json.dumps(factors, ensure_ascii=False, indent=2))
    
    if not any([args.update, args.summary, args.factors]):
        parser.print_help()


if __name__ == "__main__":
    main()
