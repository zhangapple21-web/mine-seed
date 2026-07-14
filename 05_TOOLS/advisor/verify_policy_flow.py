#!/usr/bin/env python3
"""
验证 Candidate → Admission 流程能跑通

P0 修复验证脚本：
1. 获取 T+1 因子统计数据
2. 触发 analyze_and_adjust()
3. 检查是否创建了 Candidate Policy
4. 运行 Roundtable 评审
5. 检查 Admission 是否能批准策略
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from performance_tracker import PerformanceTracker
from adaptive_scorer import AdaptiveScorer
from policy_manager import PolicyManager


def main():
    print("=" * 60)
    print("验证 Candidate → Admission 流程")
    print("=" * 60)
    
    # 1. 获取 T+1 因子统计数据
    print("\n[1/5] 获取 T+1 因子统计数据...")
    tracker = PerformanceTracker()
    factor_stats = tracker.get_factor_effectiveness("T+1")
    
    if not factor_stats:
        print("  ⚠ 没有 T+1 因子统计数据")
        print("  可能需要先更新一些推荐记录的 T+1 收益")
        return
    
    print(f"  ✓ 获取到 {len(factor_stats)} 个因子统计:")
    for factor, stats in list(factor_stats.items())[:5]:
        print(f"    - {factor}: 胜率 {stats['win_rate']}%, 样本 {stats['count']}")
    
    # 2. 触发 analyze_and_adjust()
    print("\n[2/5] 触发 analyze_and_adjust()...")
    scorer = AdaptiveScorer()
    adjusted, adjustments = scorer.analyze_and_adjust(tracker, period="T+1")
    
    if not adjusted:
        print("  ⚠ 没有触发权重调整")
        print("  可能因子胜率都在 40%-60% 区间内")
    else:
        print(f"  ✓ 触发 {len(adjustments)} 项权重调整:")
        for adj in adjustments[:5]:
            print(f"    - {adj['factor']}: {adj['old_weight']:.1f} → {adj['new_weight']:.1f} ({adj['reason']})")
    
    # 3. 检查是否创建了 Candidate Policy
    print("\n[3/5] 检查 Candidate Policy...")
    pm = PolicyManager()
    candidates = pm.get_candidate_policies()
    
    if not candidates:
        print("  ⚠ 没有候选策略")
        print("  需要权重调整才会创建 Candidate Policy")
    else:
        print(f"  ✓ 发现 {len(candidates)} 个候选策略:")
        for c in candidates:
            print(f"    - {c.policy_id}: 状态={c.status}, 创建时间={c.created_at}")
    
    # 4. 运行 Roundtable 评审
    if candidates:
        print("\n[4/5] 运行 Roundtable 评审...")
        candidate = candidates[0]
        summary = tracker.get_summary(10)
        review = pm.roundtable_review(candidate.policy_id, summary, factor_stats)
        
        print(f"  评审结果: {review.get('approved', False)}")
        print(f"  评审原因: {review.get('reason', 'N/A')}")
        
        # 5. 检查 Admission 是否能批准策略
        if review.get("approved"):
            print("\n[5/5] 批准策略...")
            success = pm.approve_policy(candidate.policy_id, review)
            
            if success:
                print(f"  ✓ 策略 {candidate.policy_id} 已批准并生效")
                print(f"  当前策略: {pm.current_policy.policy_id}")
                print(f"  历史记录: {len(pm.current_policy.history)} 条")
            else:
                print(f"  ✗ 策略批准失败")
        else:
            print("\n[5/5] 策略未通过评审，跳过批准")
    else:
        print("\n[4/5] 跳过 Roundtable 评审（没有候选策略）")
        print("\n[5/5] 跳过 Admission（没有候选策略）")
    
    # 总结
    print("\n" + "=" * 60)
    print("验证结果:")
    print(f"  - T+1 因子统计: {len(factor_stats)} 个")
    print(f"  - 权重调整: {len(adjustments)} 项")
    print(f"  - 候选策略: {len(candidates)} 个")
    print(f"  - 当前策略版本: {pm.current_policy.version}")
    print(f"  - 策略历史: {len(pm.current_policy.history)} 条")
    
    if len(factor_stats) > 0:
        print("\n✓ Candidate → Admission 流程可以启动")
        print("  （如果有权重调整，就会创建 Candidate Policy）")
    else:
        print("\n⚠ 需要先积累一些 T+1 数据")


if __name__ == "__main__":
    main()