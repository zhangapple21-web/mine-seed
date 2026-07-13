#!/usr/bin/env python3
"""
Advisor Diagnostic — 荐股系统诊断工具

用于观察系统健康状态和运行质量，支持"跑两天观察"阶段。
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from performance_tracker import PerformanceTracker
from adaptive_scorer import AdaptiveScorer
from policy_manager import PolicyManager
from multi_data_source import DataSourceManager
from post_recommendation_auditor import PostRecommendationAuditor
from daily_event_logger import DailyEventLogger
from miner_assistant import MinerAssistant


def show_system_health():
    """显示系统整体健康状态"""
    print("=" * 60)
    print(f"荐股系统诊断报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 表现跟踪
    tracker = PerformanceTracker()
    summary = tracker.get_summary(30)
    
    print("\n【表现统计】")
    total = summary.get('total_recommendations', 0)
    print(f"  最近30天推荐次数: {total}")
    
    if total > 0:
        print(f"  完整跟踪记录: {summary.get('complete_records', 0)}")
        
        win_rates = summary.get('win_rates', {})
        avg_returns = summary.get('avg_returns', {})
        
        print("\n  各周期表现:")
        for period in ['T+1', 'T+3', 'T+5', 'T+10', 'T+20']:
            wr = win_rates.get(period)
            ret = avg_returns.get(period)
            if wr is not None and ret is not None:
                status = "OK" if wr >= 50 else "WARN" if wr >= 30 else "CRIT"
                print(f"    {period}: 胜率 {wr}% | 平均收益 {ret:+.2f}% [{status}]")
    else:
        print("  暂无推荐记录，需要运行荐股引擎生成推荐")
    
    # 2. 健康度
    print("\n【系统健康度】")
    scorer = AdaptiveScorer()
    health = scorer.get_health_score(tracker)
    score = health.get('score', 0)
    status = health.get('status', 'unknown')
    
    status_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴", "unknown": "⚪"}
    print(f"  {status_emoji.get(status, '⚪')} 评分: {score}/100 ({status})")
    
    details = health.get('details', {})
    for k, v in details.items():
        print(f"    {k}: {v:.1f}")
    
    # 3. 策略状态
    print("\n【策略状态】")
    pm = PolicyManager()
    current = pm.current_policy
    if current:
        print(f"  当前策略: {current.policy_id} v{current.version}")
        print(f"  状态: {current.status}")
        print(f"  生效时间: {current.applied_at[:19] if current.applied_at else 'N/A'}")
        
        all_policies = pm.get_all_policies()
        print(f"  历史策略数: {len(all_policies)}")
        
        candidates = pm.get_candidate_policies()
        if candidates:
            print(f"  待评审候选: {len(candidates)} 个")
    
    # 4. 权重调整历史
    print("\n【权重调整历史】")
    if scorer.adjustment_history:
        for adj in scorer.adjustment_history[-5:]:
            print(f"  {adj['factor']}: {adj['old_weight']:.1f} -> {adj['new_weight']:.1f} ({adj['reason']})")
    else:
        print("  暂无权重调整记录")
    
    # 5. 数据源状态
    print("\n【数据源状态】")
    dsm = DataSourceManager()
    sources = dsm.get_source_status()
    for source, status in sources.items():
        status_str = "✅" if status['available'] else "❌"
        print(f"  {status_str} {source}: priority={status['priority']}, latency={status['latency']}s")
    
    # 6. 审计状态
    print("\n【审计状态】")
    auditor = PostRecommendationAuditor()
    audit_summary = auditor.get_audit_summary(30)
    if 'message' in audit_summary:
        print(f"  {audit_summary['message']}")
    else:
        print(f"  最近30天审计数: {audit_summary['total_audits']}")
        print(f"  平均评分: {audit_summary['avg_score']}/100")
        print(f"  评级分布: A={audit_summary['ratings']['A']}, B={audit_summary['ratings']['B']}, C={audit_summary['ratings']['C']}, D={audit_summary['ratings']['D']}")
    
    # 7. 今日事件
    print("\n【今日事件】")
    evt_logger = DailyEventLogger()
    today_events = evt_logger.get_today_events()
    if today_events:
        for evt in today_events:
            print(f"  {evt['time']} [{evt['type']}] {evt['message']}")
    else:
        print("  暂无今日事件")
    
    # 8. Ollama 本地模型状态
    print("\n【Ollama 本地模型】")
    miner = MinerAssistant()
    ollama_health = miner.check_ollama_health()
    if ollama_health['available']:
        print(f"  状态: ✅ 运行中")
        print(f"  可用模型: {len(ollama_health['models'])} 个")
        print(f"  Fast 模型: {'✅' if ollama_health['fast_available'] else '❌'} {ollama_health['fast_model']}")
        print(f"  Heavy 模型: {'✅' if ollama_health['heavy_available'] else '❌'} {ollama_health['heavy_model']}")
    else:
        print(f"  状态: ❌ 未运行")
        print(f"  错误: {ollama_health.get('error', 'unknown')}")
    
    # 9. 文件检查
    print("\n【关键文件检查】")
    output_dir = Path(__file__).parent.parent / 'mine_output' / 'advisor'
    files_to_check = [
        ('performance_db.json', '表现数据库'),
        ('adaptive_weights.json', '自适应权重'),
        ('current_policy.json', '当前策略'),
        ('audit_results.json', '审计结果'),
        ('daily_events.json', '每日事件'),
    ]
    for filename, desc in files_to_check:
        fpath = output_dir / filename
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"  ✓ {desc}: {filename} ({size} bytes)")
        else:
            print(f"  ✗ {desc}: {filename} (不存在)")
    
    # 检查最近报告
    reports = sorted(output_dir.glob('advisor_*.md'), reverse=True)[:3]
    if reports:
        print(f"\n  最近报告:")
        for r in reports:
            print(f"    {r.name}")
    
    print("\n" + "=" * 60)


def main():
    show_system_health()


if __name__ == "__main__":
    main()
