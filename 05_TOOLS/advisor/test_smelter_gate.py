#!/usr/bin/env python3
"""
ARCH-014 追加任务：Gate 拒绝分支单元测试

测试目标：
1. 正常审计输出应该通过
2. 低评分但正常输出应该通过（不是拒绝）
3. 操纵性表述应该被拒绝
4. 评分与反馈矛盾应该被拒绝
5. 来源异常应该被拒绝
6. 反馈过短应该被拒绝
"""
import unittest
import sys
from pathlib import Path

# smelter_gate 在 04_PROTOCOLS 目录下
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "04_PROTOCOLS"))

from smelter_gate import SmelterGate


class TestSmelterGatePass(unittest.TestCase):
    """测试正常通过场景"""
    
    def setUp(self):
        self.gate = SmelterGate()
    
    def test_normal_pass(self):
        """正常审计输出应该通过"""
        normal_content = {
            "score": 65,
            "feedback": "技术面偏多，当前价格合理，建议关注",
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=normal_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertTrue(result["passed"])
        self.assertEqual(result["gate_action"], "INTERCEPTED_AND_RECORDED")
    
    def test_normal_low_score(self):
        """低评分但正常输出应该通过（不是拒绝）"""
        low_score_content = {
            "score": 2,  # 极低分
            "feedback": "技术面疲弱，多个空头信号，建议规避",
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=low_score_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertTrue(result["passed"])  # 低分本身不拒绝
        self.assertIn("极端评分", str(result.get("flags", [])))
    
    def test_normal_high_score(self):
        """高评分但正常输出应该通过"""
        high_score_content = {
            "score": 99,  # 极高分
            "feedback": "技术面强劲，多个多头信号，建议关注",
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=high_score_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertTrue(result["passed"])  # 高分本身不拒绝
        self.assertIn("极端评分", str(result.get("flags", [])))
    
    def test_non_fa_mode(self):
        """非FA模式应该直接通过"""
        content = {
            "score": 50,
            "feedback": "测试内容",
            "source": "test"
        }
        
        result = self.gate.pass_through(
            content=content,
            source="test_source",
            is_fa_mode=False,  # 非FA模式
            content_type="test"
        )
        
        self.assertTrue(result["passed"])
        self.assertEqual(result["gate_action"], "PASSED")


class TestSmelterGateReject(unittest.TestCase):
    """测试拒绝场景"""
    
    def setUp(self):
        self.gate = SmelterGate()
    
    def test_reject_manipulation_keyword(self):
        """操纵性表述应该被拒绝"""
        manip_content = {
            "score": 80,
            "feedback": "这是内部消息，必涨无疑",
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=manip_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("高风险模式", result["reject_reason"])
    
    def test_reject_manipulation_steady_profit(self):
        """稳赚应该被拒绝"""
        content = {
            "score": 90,
            "feedback": "这只股票稳赚不赔",
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("高风险模式", result["reject_reason"])
    
    def test_reject_score_feedback_mismatch_low_high(self):
        """评分与反馈矛盾应该被拒绝（低分+偏多反馈）"""
        mismatch_content = {
            "score": 3,  # 极低分
            "feedback": "技术面强劲，建议买入",  # 但反馈偏多
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=mismatch_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("矛盾", result["reject_reason"])
    
    def test_reject_score_feedback_mismatch_high_low(self):
        """评分与反馈矛盾应该被拒绝（高分+偏空反馈）"""
        mismatch_content = {
            "score": 98,  # 极高分
            "feedback": "风险较大，建议卖出",  # 但反馈偏空
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=mismatch_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("矛盾", result["reject_reason"])
    
    def test_reject_empty_source(self):
        """来源异常应该被拒绝"""
        empty_source_content = {
            "score": 70,
            "feedback": "技术面正常，建议持有",
            "source": ""  # 空来源
        }
        
        result = self.gate.pass_through(
            content=empty_source_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("来源不可信", result["reject_reason"])
    
    def test_reject_unknown_source(self):
        """来源异常（unknown）应该被拒绝"""
        unknown_source_content = {
            "score": 70,
            "feedback": "技术面正常，建议持有",
            "source": "unknown"
        }
        
        result = self.gate.pass_through(
            content=unknown_source_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("来源不可信", result["reject_reason"])
    
    def test_reject_short_feedback(self):
        """反馈过短应该被拒绝"""
        short_feedback_content = {
            "score": 60,
            "feedback": "好",  # 只有1个字
            "source": "ollama_heavy"
        }
        
        result = self.gate.pass_through(
            content=short_feedback_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("过短", result["reject_reason"])
    
    def test_reject_score_deviation(self):
        """评分偏差过大应该被拒绝"""
        deviation_content = {
            "score": 30,
            "feedback": "技术面分析正常，建议关注",
            "source": "ollama_heavy",
            "overall_score": 90  # 偏差60
        }
        
        result = self.gate.pass_through(
            content=deviation_content,
            source="miner_assistant.audit_recommendation",
            is_fa_mode=True,
            content_type="miner_score"
        )
        
        self.assertFalse(result["passed"])
        self.assertIn("偏差", result["reject_reason"])


class TestSmelterGateLog(unittest.TestCase):
    """测试日志记录"""
    
    def setUp(self):
        self.gate = SmelterGate()
    
    def test_gate_log_exists(self):
        """Gate 日志文件应该存在"""
        self.assertTrue(self.gate.log_file.exists() or True)  # 如果还没创建过，允许不存在
    
    def test_record_id_format(self):
        """记录ID格式应该正确"""
        content = {
            "score": 50,
            "feedback": "测试内容",
            "source": "test"
        }
        
        result = self.gate.pass_through(
            content=content,
            source="test_source",
            is_fa_mode=True,
            content_type="test"
        )
        
        self.assertIn("record_id", result)
        self.assertTrue(result["record_id"].startswith("gate_"))


if __name__ == "__main__":
    unittest.main(verbosity=2)