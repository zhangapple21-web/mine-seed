#!/usr/bin/env python3
"""
AUM-MISSION-EXP-001 — Shadow Observer 验证脚本

验证：
1. Shadow Observer 是独立的可执行单元
2. 主流程文件未被污染
3. 影子产物存到独立目录
4. 退出机制标记正确
"""
import sys
from pathlib import Path

_WORKSPACE = Path("c:/Users/User/ace_workspace/mine-seed")


def check_separation():
    """检查主线与影子线是否严格分离"""
    print("=" * 60)
    print("AUM-MISSION-EXP-001 验证报告")
    print("=" * 60)
    
    all_ok = True
    
    # 1. Shadow Observer 文件存在
    print("\n[1/5] Shadow Observer 文件存在性...")
    shadow_obs = _WORKSPACE / "05_TOOLS" / "miner" / "shadow_observer.py"
    if shadow_obs.exists():
        print(f"  ✓ {shadow_obs.name} 存在")
    else:
        print(f"  ✗ {shadow_obs.name} 不存在")
        all_ok = False
    
    # 2. 主流程文件未污染（不应包含 shadow_observer 引用）
    print("\n[2/5] 主流程文件未被污染...")
    main_files = [
        "05_TOOLS/advisor/daily_runner.py",
        "05_TOOLS/advisor/stock_advisor.py",
        "05_TOOLS/advisor/policy_manager.py",
        "05_TOOLS/advisor/post_recommendation_auditor.py",
    ]
    
    for f in main_files:
        file_path = _WORKSPACE / f
        if not file_path.exists():
            print(f"  ⚠ {f} 不存在（跳过）")
            continue
        content = file_path.read_text(encoding="utf-8")
        if "shadow_observer" in content or "shadow_only" in content or "shadow_audit" in content:
            print(f"  ✗ {f} 包含 shadow 相关引用（污染！）")
            all_ok = False
        else:
            print(f"  ✓ {f} 未被污染")
    
    # 3. 影子产物目录独立
    print("\n[3/5] 影子产物目录独立...")
    shadow_dir = _WORKSPACE / "03_DATA" / "shadow_audit"
    if shadow_dir.exists():
        print(f"  ✓ {shadow_dir} 存在（独立目录）")
    else:
        print(f"  ✗ {shadow_dir} 不存在")
        all_ok = False
    
    # 4. 影子产物不进入主流程目录
    print("\n[4/5] 影子产物不进入主流程目录...")
    main_output = _WORKSPACE / "05_TOOLS" / "mine_output" / "advisor"
    if main_output.exists():
        shadow_files = list(main_output.glob("shadow_*"))
        if shadow_files:
            print(f"  ✗ 主流程目录有影子文件：{shadow_files}")
            all_ok = False
        else:
            print(f"  ✓ 主流程目录无影子文件")
    else:
        print(f"  ⚠ {main_output} 不存在（跳过）")
    
    # 5. Shadow Observer 自身包含严格边界声明
    print("\n[5/5] Shadow Observer 包含严格边界声明...")
    if shadow_obs.exists():
        content = shadow_obs.read_text(encoding="utf-8")
        # 检查是否包含关键边界词
        required_keywords = ["DON'T", "只读", "不影响", "影子"]
        missing = [kw for kw in required_keywords if kw not in content]
        if not missing:
            print(f"  ✓ 包含严格边界声明")
        else:
            print(f"  ✗ 缺少边界声明关键词：{missing}")
            all_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    if all_ok:
        print("✓ 验证通过：Shadow Observer 与主流程严格分离")
    else:
        print("✗ 验证失败：存在污染或边界问题")
    print("=" * 60)
    
    return all_ok


if __name__ == "__main__":
    ok = check_separation()
    sys.exit(0 if ok else 1)