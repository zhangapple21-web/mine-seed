#!/usr/bin/env python3
"""
Stock Advisor 次日收盘复核脚本
读取昨日的 lineage JSON，补填 close_price / return_pct / review_status
"""
import json
import os
import sys
from datetime import datetime, timedelta

ADVISOR_DIR = "/home/coze/mine_output/advisor"

def review_yesterday():
    """复核昨日推荐"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    lineage_file = os.path.join(ADVISOR_DIR, f'advisor_{yesterday}_lineage.json')
    
    if not os.path.exists(lineage_file):
        print(f"❌ 未找到昨日lineage文件: {lineage_file}")
        return False
    
    with open(lineage_file, 'r', encoding='utf-8') as f:
        lineage = json.load(f)
    
    # 用腾讯API获取收盘价
    try:
        from stock_query import get_stock_query
        sq = get_stock_query()
    except ImportError:
        sys.path.insert(0, '/home/coze/stock_advisor')
        from stock_query import get_stock_query
        sq = get_stock_query()
    
    updated = False
    for rec in lineage.get("recommendations", []):
        if rec["review_status"] != "pending":
            continue
        
        ticker = rec["ticker"]
        # 补全代码格式
        if ticker.startswith('6'):
            full_code = f"sh{ticker}"
        elif ticker.startswith('0') or ticker.startswith('3'):
            full_code = f"sz{ticker}"
        elif ticker.startswith('68'):
            full_code = f"sh{ticker}"
        else:
            full_code = f"sz{ticker}"
        
        quote = sq.get_quote([full_code])
        if quote and len(quote) > 0:
            close_price = float(quote[0].get('price', 0))
            if close_price > 0:
                rec["close_price"] = round(close_price, 2)
                rec["return_pct"] = round((close_price - rec["recommend_price"]) / rec["recommend_price"] * 100, 2)
                rec["review_status"] = "completed"
                updated = True
                print(f"✅ {rec['recommendation_id']}: 推荐¥{rec['recommend_price']} → 收盘¥{close_price} ({rec['return_pct']:+.2f}%)")
        else:
            print(f"⚠️ {rec['recommendation_id']}: 无法获取收盘价，保持pending")
    
    if updated:
        with open(lineage_file, 'w', encoding='utf-8') as f:
            json.dump(lineage, f, ensure_ascii=False, indent=2)
        print(f"\n📝 Lineage已更新: {lineage_file}")
        
        # 打印统计摘要
        completed = [r for r in lineage["recommendations"] if r["review_status"] == "completed"]
        if completed:
            avg_ret = sum(r["return_pct"] for r in completed) / len(completed)
            wins = sum(1 for r in completed if r["return_pct"] > 0)
            print(f"\n📊 胜率统计: {wins}/{len(completed)} = {wins/len(completed)*100:.0f}% | 平均收益: {avg_ret:+.2f}%")
    
    return updated

if __name__ == '__main__':
    review_yesterday()
