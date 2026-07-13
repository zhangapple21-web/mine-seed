#!/usr/bin/env python3
"""
Smelter Gate 单元测试

> ARCH-014 子任务2: 验证 gate 能拦截 FA 模式产出并记录
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from smelter_gate import SmelterGate


def test_fa_mode_intercept_and_record():
    """测试 FA 模式产出会被拦截并记录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        gate = SmelterGate(log_dir=Path(tmpdir))
        
        test_content = {"score": 85, "feedback": "这只票很好"}
        
        result = gate.pass_through(
            content=test_content,
            source="test_miner",
            source_type="audit",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        assert result["passed"] == True, "FA模式应该通过（最小版本）"
        assert result["gate_action"] == "INTERCEPTED_AND_RECORDED", "FA模式应该被标记为拦截记录"
        assert "record_id" in result, "应该返回记录ID"
        
        logs = gate.get_gate_log()
        assert len(logs) == 1, "应该只有一条日志"
        assert logs[0]["is_fa_mode"] == True, "日志应该标记为FA模式"
        assert logs[0]["source"] == "test_miner", "来源应该正确"
        assert logs[0]["content_type"] == "miner_score", "内容类型应该正确"
        assert logs[0]["action"] == "INTERCEPTED_AND_RECORDED", "动作应该是拦截记录"
        
        fa_records = gate.get_fa_mode_records()
        assert len(fa_records) == 1, "应该能筛选出FA模式记录"
        
        print("✅ test_fa_mode_intercept_and_record: 通过")


def test_non_fa_mode_pass_directly():
    """测试非 FA 模式产出直接通过"""
    with tempfile.TemporaryDirectory() as tmpdir:
        gate = SmelterGate(log_dir=Path(tmpdir))
        
        test_content = {"rule_score": 70}
        
        result = gate.pass_through(
            content=test_content,
            source="test_rule_engine",
            source_type="audit",
            is_fa_mode=False,
            content_type="rule_score"
        )
        
        assert result["passed"] == True, "非FA模式应该通过"
        assert result["gate_action"] == "PASSED", "非FA模式应该标记为直接通过"
        
        logs = gate.get_gate_log()
        assert len(logs) == 1, "应该只有一条日志"
        assert logs[0]["is_fa_mode"] == False, "日志应该标记为非FA模式"
        assert logs[0]["action"] == "PASSED", "动作应该是直接通过"
        
        fa_records = gate.get_fa_mode_records()
        assert len(fa_records) == 0, "不应该有FA模式记录"
        
        print("✅ test_non_fa_mode_pass_directly: 通过")


def test_content_hash():
    """测试内容哈希生成"""
    with tempfile.TemporaryDirectory() as tmpdir:
        gate = SmelterGate(log_dir=Path(tmpdir))
        
        content1 = {"key": "value"}
        content2 = {"key": "value"}
        content3 = {"key": "different"}
        
        result1 = gate.pass_through(content=content1, source="test", is_fa_mode=True)
        result2 = gate.pass_through(content=content2, source="test", is_fa_mode=True)
        result3 = gate.pass_through(content=content3, source="test", is_fa_mode=True)
        
        logs = gate.get_gate_log()
        assert logs[0]["content_hash"] == logs[1]["content_hash"], "相同内容应该有相同哈希"
        assert logs[0]["content_hash"] != logs[2]["content_hash"], "不同内容应该有不同哈希"
        
        print("✅ test_content_hash: 通过")


def test_multiple_records():
    """测试多条记录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        gate = SmelterGate(log_dir=Path(tmpdir))
        
        for i in range(5):
            gate.pass_through(
                content={"index": i},
                source="test",
                is_fa_mode=(i % 2 == 0)
            )
        
        logs = gate.get_gate_log()
        assert len(logs) == 5, "应该有5条日志"
        
        fa_records = gate.get_fa_mode_records()
        assert len(fa_records) == 3, "应该有3条FA模式记录"
        
        print("✅ test_multiple_records: 通过")


if __name__ == "__main__":
    print("=== Smelter Gate 单元测试 ===")
    test_fa_mode_intercept_and_record()
    test_non_fa_mode_pass_directly()
    test_content_hash()
    test_multiple_records()
    print("\n=== 全部测试通过 ===")
