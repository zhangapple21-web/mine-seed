#!/usr/bin/env python3
"""
Stock Advisor 次日收盘复核脚本
读取昨日的 lineage JSON，补填 close_price / return_pct / review_status
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path(__file__).parent.parent.parent
ADVISOR_DIR = WORKSPACE / "05_TOOLS" / "mine_output" / "advisor"

sys.path.insert(0, str(Path(__file__).parent))


def review_yesterday():
    """复核昨日推荐"""
    from trading_calendar import get_calendar
    from multi_data_source import DataSourceManager
    
    cal = get_calendar()
    dsm = DataSourceManager()
    
    today = datetime.now().date()
    prev_trading_day = cal.prev_trading_day(today)
    prev_date_str = prev_trading_day.strftime('%Y%m%d')
    
    lineage_file = ADVISOR_DIR / f'advisor_{prev_date_str}_lineage.json'
    
    if not lineage_file.exists():
        print(f"未找到上一交易日lineage文件: {lineage_file}")
        return False
    
    with open(lineage_file, 'r', encoding='utf-8') as f:
        lineage = json.load(f)
    
    codes = []
    rec_map = {}
    for rec in lineage.get("recommendations", []):
        if rec["review_status"] != "pending":
            continue
        ticker = rec["ticker"]
        if ticker.startswith('6') or ticker.startswith('68'):
            full_code = f"sh{ticker}"
        elif ticker.startswith('0') or ticker.startswith('3'):
            full_code = f"sz{ticker}"
        else:
            full_code = f"sz{ticker}"
        codes.append(full_code)
        rec_map[full_code] = rec
    
    if not codes:
        print("没有待复核的推荐")
        return False
    
    quotes = dsm.get_quotes(codes)
    
    updated = False
    for quote in quotes:
        full_code = quote.get('code', '')
        rec = rec_map.get(full_code)
        if not rec:
            continue
        
        close_price = float(quote.get('price', 0))
        if close_price > 0:
            rec["close_price"] = round(close_price, 2)
            rec["return_pct"] = round((close_price - rec["recommend_price"]) / rec["recommend_price"] * 100, 2)
            rec["review_status"] = "completed"
            updated = True
            print(f"  {rec['recommendation_id']}: 推荐¥{rec['recommend_price']} → 收盘¥{close_price} ({rec['return_pct']:+.2f}%)")
    
    if updated:
        with open(lineage_file, 'w', encoding='utf-8') as f:
            json.dump(lineage, f, ensure_ascii=False, indent=2)
        print(f"\nLineage已更新: {lineage_file}")
        
        completed = [r for r in lineage["recommendations"] if r["review_status"] == "completed"]
        if completed:
            avg_ret = sum(r["return_pct"] for r in completed) / len(completed)
            wins = sum(1 for r in completed if r["return_pct"] > 0)
            print(f"\n胜率统计: {wins}/{len(completed)} = {wins/len(completed)*100:.0f}% | 平均收益: {avg_ret:+.2f}%")
    
    return updated


def review_date(date_str: str):
    """复核指定日期的推荐"""
    from multi_data_source import DataSourceManager
    
    dsm = DataSourceManager()
    lineage_file = ADVISOR_DIR / f'advisor_{date_str}_lineage.json'
    
    if not lineage_file.exists():
        print(f"未找到lineage文件: {lineage_file}")
        return False
    
    with open(lineage_file, 'r', encoding='utf-8') as f:
        lineage = json.load(f)
    
    codes = []
    rec_map = {}
    for rec in lineage.get("recommendations", []):
        ticker = rec["ticker"]
        if ticker.startswith('6') or ticker.startswith('68'):
            full_code = f"sh{ticker}"
        elif ticker.startswith('0') or ticker.startswith('3'):
            full_code = f"sz{ticker}"
        else:
            full_code = f"sz{ticker}"
        codes.append(full_code)
        rec_map[full_code] = rec
    
    if not codes:
        print("没有推荐记录")
        return False
    
    quotes = dsm.get_quotes(codes)
    
    updated = False
    for quote in quotes:
        full_code = quote.get('code', '')
        rec = rec_map.get(full_code)
        if not rec:
            continue
        
        close_price = float(quote.get('price', 0))
        if close_price > 0:
            rec["close_price"] = round(close_price, 2)
            rec["return_pct"] = round((close_price - rec["recommend_price"]) / rec["recommend_price"] * 100, 2)
            rec["review_status"] = "completed"
            updated = True
            print(f"  {rec['recommendation_id']}: 推荐¥{rec['recommend_price']} → 收盘¥{close_price} ({rec['return_pct']:+.2f}%)")
    
    if updated:
        with open(lineage_file, 'w', encoding='utf-8') as f:
            json.dump(lineage, f, ensure_ascii=False, indent=2)
        print(f"\nLineage已更新: {lineage_file}")
    
    return updated


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Lineage Review - 荐股次日复核")
    parser.add_argument("--date", type=str, help="复核指定日期 (YYYYMMDD)")
    args = parser.parse_args()
    
    if args.date:
        review_date(args.date)
    else:
        review_yesterday()


if __name__ == '__main__':
    main()
