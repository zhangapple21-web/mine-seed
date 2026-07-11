#!/usr/bin/env python3
"""
Trading Calendar — A股交易日历
================================

功能:
  - is_trading_day(date) — 判断是否为交易日
  - next_trading_day(date) — 下一个交易日
  - prev_trading_day(date) — 上一个交易日
  - get_recent_trading_days(n) — 最近 n 个交易日

数据源:
  1. akshare tool_trade_date_hist_sina (如果可用)
  2. fallback: 内置节假日列表 + weekday 判断

内置节假日覆盖 2025-2027 年中国A股法定节假日 + 调休补班日。
"""
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List

# A股法定节假日 (YYYY-MM-DD 格式)
# 来源: 上海证券交易所/深圳证券交易所公告
HOLIDAYS = {
    # === 2025 ===
    "2025-01-01",                          # 元旦
    "2025-01-28", "2025-01-29", "2025-01-30", "2025-01-31",  # 春节
    "2025-02-01", "2025-02-02", "2025-02-03", "2025-02-04",
    "2025-04-04", "2025-04-05", "2025-04-06",                # 清明
    "2025-05-01", "2025-05-02", "2025-05-03", "2025-05-04", "2025-05-05",  # 劳动节
    "2025-05-31", "2025-06-01", "2025-06-02",                # 端午
    "2025-10-01", "2025-10-02", "2025-10-03", "2025-10-04",  # 国庆+中秋
    "2025-10-05", "2025-10-06", "2025-10-07", "2025-10-08",

    # === 2026 ===
    "2026-01-01",                                            # 元旦
    "2026-02-15", "2026-02-16", "2026-02-17", "2026-02-18",  # 春节
    "2026-02-19", "2026-02-20", "2026-02-21",
    "2026-04-04", "2026-04-05", "2026-04-06",                # 清明
    "2026-05-01", "2026-05-02", "2026-05-03", "2026-05-04", "2026-05-05",  # 劳动节
    "2026-06-19", "2026-06-20", "2026-06-21",                # 端午
    "2026-09-25", "2026-09-26", "2026-09-27",                # 中秋
    "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04",  # 国庆
    "2026-10-05", "2026-10-06", "2026-10-07",

    # === 2027 === (预估，待交易所公告确认)
    "2027-01-01",                                            # 元旦
    "2027-02-06", "2027-02-07", "2027-02-08", "2027-02-09",  # 春节
    "2027-02-10", "2027-02-11", "2027-02-12",
    "2027-04-04", "2027-04-05", "2027-04-06",                # 清明
    "2027-05-01", "2027-05-02", "2027-05-03",                # 劳动节
    "2027-06-19",                                            # 端午
    "2027-09-25",                                            # 中秋
    "2027-10-01", "2027-10-02", "2027-10-03", "2027-10-04",  # 国庆
    "2027-10-05", "2027-10-06", "2027-10-07",
}

# 调休补班日 (周末但开市)
WORKDAY_WEEKENDS = {
    "2025-01-26", "2025-02-08",          # 春节调休
    "2025-04-27",                        # 劳动节调休
    "2025-09-28", "2025-10-11",          # 国庆调休
    "2026-02-14", "2026-02-28",          # 春节调休
    "2026-04-26",                        # 劳动节调休
    "2026-09-30", "2026-10-10",          # 国庆调休
}


class TradingCalendar:
    """A股交易日历"""

    def __init__(self):
        self.holidays = HOLIDAYS.copy()
        self.workday_weekends = WORKDAY_WEEKENDS.copy()
        self._try_load_akshare()

    def _try_load_akshare(self):
        """尝试用 akshare 加载交易日历 (更准确)"""
        try:
            import akshare as ak
            df = ak.tool_trade_date_hist_sina()
            # df 有 trade_date 列
            trade_dates = set()
            for d in df["trade_date"]:
                trade_dates.add(str(d).replace("-", ""))
            # 转换为 YYYY-MM-DD 格式
            self.akshare_dates = {f"{d[:4]}-{d[4:6]}-{d[6:8]}" for d in trade_dates}
        except Exception:
            self.akshare_dates = None

    def is_trading_day(self, d: date) -> bool:
        """判断是否为交易日"""
        date_str = d.strftime("%Y-%m-%d")

        # 优先用 akshare 数据
        if self.akshare_dates:
            return date_str in self.akshare_dates

        # fallback: 节假日列表 + 调休补班 + weekday
        if date_str in self.holidays:
            return False
        if date_str in self.workday_weekends:
            return True
        # 周六周日不开市
        if d.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return False
        return True

    def next_trading_day(self, d: date) -> date:
        """下一个交易日"""
        d = d + timedelta(days=1)
        while not self.is_trading_day(d):
            d = d + timedelta(days=1)
        return d

    def prev_trading_day(self, d: date) -> date:
        """上一个交易日"""
        d = d - timedelta(days=1)
        while not self.is_trading_day(d):
            d = d - timedelta(days=1)
        return d

    def get_recent_trading_days(self, n: int = 30, end_date: date = None) -> List[date]:
        """获取最近 n 个交易日"""
        if end_date is None:
            end_date = date.today()
        days = []
        d = end_date
        while len(days) < n:
            if self.is_trading_day(d):
                days.append(d)
            d = d - timedelta(days=1)
        return list(reversed(days))

    def get_trading_days_between(self, start: date, end: date) -> List[date]:
        """获取两个日期之间的所有交易日"""
        days = []
        d = start
        while d <= end:
            if self.is_trading_day(d):
                days.append(d)
            d = d + timedelta(days=1)
        return days

    def count_trading_days(self, start: date, end: date) -> int:
        """计算两个日期之间的交易日数"""
        return len(self.get_trading_days_between(start, end))


# 全局单例
_calendar = None


def get_calendar() -> TradingCalendar:
    global _calendar
    if _calendar is None:
        _calendar = TradingCalendar()
    return _calendar


def is_trading_day(d: date = None) -> bool:
    if d is None:
        d = date.today()
    return get_calendar().is_trading_day(d)


def next_trading_day(d: date = None) -> date:
    if d is None:
        d = date.today()
    return get_calendar().next_trading_day(d)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="A股交易日历")
    parser.add_argument("--date", help="检查指定日期 (YYYY-MM-DD)")
    parser.add_argument("--recent", type=int, help="最近 N 个交易日")
    args = parser.parse_args()

    cal = get_calendar()

    if args.date:
        d = datetime.strptime(args.date, "%Y-%m-%d").date()
        print(f"{args.date} is_trading_day: {cal.is_trading_day(d)}")
        if cal.is_trading_day(d):
            print(f"  next: {cal.next_trading_day(d)}")
            print(f"  prev: {cal.prev_trading_day(d)}")
    elif args.recent:
        days = cal.get_recent_trading_days(args.recent)
        print(f"最近 {args.recent} 个交易日:")
        for d in days:
            print(f"  {d} ({d.strftime('%a')})")
    else:
        today = date.today()
        print(f"今天: {today} is_trading_day: {cal.is_trading_day(today)}")
        if cal.is_trading_day(today):
            print(f"  next: {cal.next_trading_day(today)}")
        else:
            print(f"  下一个交易日: {cal.next_trading_day(today)}")
