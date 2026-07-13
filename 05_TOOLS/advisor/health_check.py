#!/usr/bin/env python3
"""
Health Check — 荐股系统健康检查脚本

验证所有核心模块是否正常工作：
  - 数据源管理器
  - 审计系统
  - 事件日志器
  - 表现追踪器
  - 策略管理器
  - 自适应评分器
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def check_module(module_name: str, import_statement: str, test_func: str = None) -> bool:
    """检查单个模块是否正常"""
    try:
        exec(f"{import_statement}")
        if test_func:
            exec(f"{test_func}")
        return True
    except Exception as e:
        print(f"  ✗ {module_name}: {e}")
        return False


def main():
    print("=" * 60)
    print("荐股系统健康检查")
    print("=" * 60)
    
    checks = [
        ("数据源管理器", "from multi_data_source import DataSourceManager", "dsm = DataSourceManager()"),
        ("审计系统", "from post_recommendation_auditor import PostRecommendationAuditor", "auditor = PostRecommendationAuditor()"),
        ("事件日志器", "from daily_event_logger import DailyEventLogger", "logger = DailyEventLogger()"),
        ("表现追踪器", "from performance_tracker import PerformanceTracker", "tracker = PerformanceTracker()"),
        ("策略管理器", "from policy_manager import PolicyManager", "pm = PolicyManager()"),
        ("自适应评分器", "from adaptive_scorer import AdaptiveScorer", "scorer = AdaptiveScorer()"),
        ("交易日历", "from trading_calendar import get_calendar", "cal = get_calendar()"),
        ("lineage复核", "from lineage_review import review_yesterday", None),
        ("advisor追踪器", "from advisor_tracker import AdvisorTracker", "tracker = AdvisorTracker()"),
        ("矿工助手(Ollama)", "from miner_assistant import MinerAssistant", "m = MinerAssistant(); h = m.check_ollama_health()"),
    ]
    
    results = []
    for name, import_stmt, test in checks:
        result = check_module(name, import_stmt, test)
        results.append((name, result))
        if result:
            print(f"  ✓ {name}")
    
    # 统计
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"健康检查完成: {passed}/{total} 通过")
    
    if passed == total:
        print("状态: 所有模块正常 ✓")
    else:
        print("状态: 存在异常模块 ✗")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)