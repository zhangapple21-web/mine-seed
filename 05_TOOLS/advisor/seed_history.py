#!/usr/bin/env python3
"""
从历史报告中提取推荐记录，初始化 PerformanceTracker 数据库。
用于"跑两天观察"前的数据种子填充。
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from performance_tracker import PerformanceTracker


def extract_recommendations_from_report(report_path: Path) -> list:
    """从报告文件中提取推荐信息"""
    if not report_path.exists():
        return []
    
    content = report_path.read_text(encoding='utf-8')
    recommendations = []
    
    # 匹配推荐股票：推荐1：xxx（000000）
    rec_pattern = r'推荐\d+：([^（]+)（(\d{6})）'
    
    # 匹配价格：| 现价 | ¥xx.xx |
    price_pattern = r'\| 现价 \| ¥([\d.]+) \|'
    
    names_codes = re.findall(rec_pattern, content)
    prices = re.findall(price_pattern, content)
    
    for i, (name, code) in enumerate(names_codes):
        price = float(prices[i]) if i < len(prices) else 0.0
        recommendations.append({
            'name': name.strip(),
            'code': code,
            'price': price,
        })
    
    return recommendations


def seed_tracker_from_reports():
    """从历史报告种子化 tracker"""
    tracker = PerformanceTracker()
    
    output_dir = Path(__file__).parent.parent / 'mine_output' / 'advisor'
    reports = sorted(output_dir.glob('advisor_*.md'), reverse=True)
    
    seeded = 0
    
    for report in reports:
        # 从文件名提取日期 advisor_YYYYMMDD.md
        date_match = re.search(r'advisor_(\d{8})\.md', report.name)
        if not date_match:
            continue
        
        date_str = date_match.group(1)
        
        # 跳过今天之后的日期
        if date_str > datetime.now().strftime('%Y%m%d'):
            continue
        
        recs = extract_recommendations_from_report(report)
        
        for rec in recs:
            key = f"{date_str}_{rec['code']}"
            if key not in tracker.records:
                tracker.register_recommendation(
                    code=rec['code'],
                    name=rec['name'],
                    price=rec['price'],
                    date_str=date_str
                )
                seeded += 1
                print(f"  注册: {rec['name']}({rec['code']}) @ {rec['price']:.2f} on {date_str}")
    
    print(f"\n共注册 {seeded} 条历史推荐记录")


if __name__ == "__main__":
    seed_tracker_from_reports()