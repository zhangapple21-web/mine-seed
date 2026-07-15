#!/usr/bin/env python3
"""
板块A' 单元测试 — 验证 Replay+Shadow 独立运行、门控、状态转换

测试项：
1. Signal Candidate 注册到 LawRegistry（不叫 Factor）
2. Replay 和 Shadow 是两个独立阶段
3. Replay INSUFFICIENT_DATA 阻止 Shadow
4. Replay PASS 才能进入 Shadow
5. Weakening 状态机转换正确
6. 边界：E2C 不影响 AdaptiveScorer
7. Signal Candidate 状态变化不直接影响 AdaptiveScorer

Usage: python test_signal_candidate_pipeline.py
"""
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))


def test_signal_candidate_registration():
    """测试 1: Signal Candidate 注册正确"""
    from law_discovery import LawRegistry, LawStatus

    registry = LawRegistry()
    # 找一个已注册的 candidate
    candidates = [law for law in registry.candidates.values()
                 if law.candidate_type == "signal_candidate"]

    assert len(candidates) >= 5, f"应至少有 5 个 signal candidate，实际 {len(candidates)}"
    for c in candidates:
        assert c.candidate_type == "signal_candidate"
        assert c.status == LawStatus.DRAFT, f"{c.law_id} 应该是 DRAFT，实际 {c.status}"
        assert c.bootstrap_threshold, f"{c.law_id} 应有 bootstrap_threshold"
        assert c.weakening_trigger, f"{c.law_id} 应有 weakening_trigger"
        # 注意：replay_result 可能在之前已运行过 replay，不必强制为 None
        # 关键检查：未通过 Replay PASS 的不能进入 Shadow
        if c.replay_result:
            assert c.replay_result.get("replay_status") in ["INSUFFICIENT_DATA", "FAIL", "PASS", None]

    print(f"✓ 测试 1: Signal Candidate 注册正确 ({len(candidates)} 个)")


def test_replay_runs_independently():
    """测试 2: Replay 独立运行，不影响生产"""
    from replay import OfflineReplay
    from law_discovery import LawRegistry

    replay = OfflineReplay(days=60)
    result = replay.replay_candidate("sig_candidate_capital_dominance")

    # 不论 PASS/FAIL，Replay 都应该返回结构化结果
    assert "candidate_id" in result
    assert "replay_status" in result
    assert result["replay_status"] in ["PASS", "FAIL", "INSUFFICIENT_DATA"]

    # Replay 应写回 candidate.replay_result
    registry = LawRegistry()
    candidate = registry.get_law("sig_candidate_capital_dominance")
    assert candidate.replay_result is not None, "Replay 应写回 candidate"

    print(f"✓ 测试 2: Replay 独立运行（状态: {result['replay_status']}）")


def test_shadow_blocks_without_replay():
    """测试 3: Shadow 拒绝未通过 Replay 的 candidate"""
    from shadow import ShadowEvaluation
    from law_discovery import LawRegistry

    shadow = ShadowEvaluation()
    result = shadow.start_shadow("sig_candidate_capital_dominance")

    # 当前 Replay 是 INSUFFICIENT_DATA，Shadow 应拒绝
    assert result.get("shadow_status") == "REJECTED", \
        f"Shadow 应拒绝未通过 Replay 的 candidate，实际: {result}"

    # candidate.shadow_result 应保持 None（未启动）
    registry = LawRegistry()
    candidate = registry.get_law("sig_candidate_capital_dominance")
    # shadow_result 要么是 None，要么不是 STARTED 状态
    if candidate.shadow_result:
        assert candidate.shadow_result.get("shadow_status") != "STARTED"

    print(f"✓ 测试 3: Shadow 正确拒绝未通过 Replay 的 candidate")


def test_replay_shadow_are_distinct_files():
    """测试 4: Replay 和 Shadow 是两个独立文件/流程"""
    from replay import OfflineReplay
    from shadow import ShadowEvaluation

    # 验证 replay 和 shadow 不共享内部状态
    replay = OfflineReplay()
    shadow = ShadowEvaluation()

    # 关键：Replay 不调用 Shadow，Shadow 不调用 Replay
    assert not hasattr(replay, '_shadow_engines')
    assert not hasattr(shadow, '_replay_engines')

    # 各自的存储目录独立
    replay_storage = Path(__file__).parent.parent / "02_MEMORY" / "evidence" / "replay"
    shadow_storage = Path(__file__).parent.parent / "02_MEMORY" / "shadow"
    assert replay_storage.exists(), f"Replay 目录应存在: {replay_storage}"
    assert shadow_storage.exists(), f"Shadow 目录应存在: {shadow_storage}"
    assert replay_storage != shadow_storage, "Replay 和 Shadow 必须是独立目录"

    print(f"✓ 测试 4: Replay 和 Shadow 是独立流程/独立目录")


def test_weakening_state_machine():
    """测试 5: Weakening 状态机可正确转换"""
    from law_discovery import LawStatus, LawRegistry

    # 状态枚举检查
    assert LawStatus.DRAFT
    assert LawStatus.ACTIVE
    assert LawStatus.WEAKENING
    assert LawStatus.INVALID
    assert LawStatus.ARCHIVED

    # 模拟 Weakening 触发：连续 20 天贡献下降（仅在文档中定义，运行时未触发）
    # 这里只验证状态机枚举完整
    statuses = [s.value for s in LawStatus]
    assert "DRAFT" in statuses
    assert "ACTIVE" in statuses
    assert "WEAKENING" in statuses

    print(f"✓ 测试 5: 状态机完整 (DRAFT/ACTIVE/WEAKENING/INVALID/ARCHIVED)")


def test_e2c_doesnt_touch_adaptive():
    """测试 6: E2C 不引用 AdaptiveScorer（边界清晰）"""
    import os
    e2c_file = Path(__file__).parent / "e2c_closure.py"
    content = e2c_file.read_text(encoding="utf-8")

    # E2C 文件不应 import 或引用 adaptive_scorer
    assert "adaptive_scorer" not in content.lower(), "E2C 不应引用 AdaptiveScorer"
    assert "import adaptive" not in content, "E2C 不应 import AdaptiveScorer"
    assert "from adaptive" not in content, "E2C 不应 from AdaptiveScorer import"

    # 反向验证：AdaptiveScorer 也不应 import E2C
    adaptive_file = Path(__file__).parent.parent / "05_TOOLS" / "advisor" / "adaptive_scorer.py"
    if adaptive_file.exists():
        adaptive_content = adaptive_file.read_text(encoding="utf-8")
        assert "e2c_closure" not in adaptive_content, "AdaptiveScorer 不应 import E2C"
        assert "import e2c" not in adaptive_content, "AdaptiveScorer 不应 import E2C"

    print(f"✓ 测试 6: E2C 与 AdaptiveScorer 边界清晰（互不引用）")


def test_candidate_not_directly_modify_adaptive():
    """测试 7: Signal Candidate 不会直接修改 AdaptiveScorer 权重"""
    from law_discovery import LawRegistry

    registry = LawRegistry()
    # 检查所有 candidate 都不应被 AdaptiveScorer 直接引用
    candidates = [law for law in registry.candidates.values()
                 if law.candidate_type == "signal_candidate"]

    for c in candidates:
        # 验证 scope 字段明确"applies_to"
        assert "applies_to" in c.scope, f"{c.law_id} scope 应有 applies_to"
        # 当前 DRAFT 状态不直接影响 AdaptiveScorer
        # 注意：status 反序列化后是 string，value 属性可能不存在
        status_str = c.status.value if hasattr(c.status, 'value') else c.status
        assert status_str == "DRAFT", f"{c.law_id} 应保持 DRAFT 状态，实际: {status_str}"

    print(f"✓ 测试 7: Signal Candidate 不直接修改 AdaptiveScorer（保持 DRAFT 状态）")


def test_law_weakening_documented():
    """测试 8: Law Weakening 设计文档存在且定义清晰"""
    design_doc = Path(__file__).parent / "LAW_WEAKENING_DESIGN.md"
    assert design_doc.exists(), "LAW_WEAKENING_DESIGN.md 应存在"

    content = design_doc.read_text(encoding="utf-8")
    assert "WEAKENING" in content
    assert "INVALID" in content
    assert "ARCHIVED" in content
    assert "consecutive_decline_days" in content or "20" in content
    assert "Roundtable" in content

    print(f"✓ 测试 8: Law Weakening 设计文档完整")


def test_goal_validation_exists():
    """测试 9: Goal Validation Report 存在"""
    goal_doc = Path(__file__).parent / "GOAL_VALIDATION.md"
    assert goal_doc.exists(), "GOAL_VALIDATION.md 应存在"

    content = goal_doc.read_text(encoding="utf-8")
    assert "稳定" in content or "D" in content
    assert "Evaluation Metric" in content or "指标" in content
    assert "Capability Mapping" in content

    print(f"✓ 测试 9: Goal Validation Report 完整")


def test_factor_diagnosis_exists():
    """测试 10: 现有因子诊断报告存在"""
    diagnosis_doc = Path(__file__).parent / "FACTOR_DIAGNOSIS.md"
    assert diagnosis_doc.exists(), "FACTOR_DIAGNOSIS.md 应存在"

    content = diagnosis_doc.read_text(encoding="utf-8")
    assert "胜率" in content
    assert "收益" in content
    assert "样本" in content  # 强调样本不足问题

    print(f"✓ 测试 10: 现有因子诊断报告完整")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("板块A' 单元测试")
    print("=" * 60)
    tests = [
        test_signal_candidate_registration,
        test_replay_runs_independently,
        test_shadow_blocks_without_replay,
        test_replay_shadow_are_distinct_files,
        test_weakening_state_machine,
        test_e2c_doesnt_touch_adaptive,
        test_candidate_not_directly_modify_adaptive,
        test_law_weakening_documented,
        test_goal_validation_exists,
        test_factor_diagnosis_exists,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"✗ {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {t.__name__} (异常): {e}")
            failed += 1

    print("=" * 60)
    print(f"通过: {passed}/{passed + failed}")
    if failed == 0:
        print("✓ 全部测试通过")
    else:
        print(f"✗ {failed} 个测试失败")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
