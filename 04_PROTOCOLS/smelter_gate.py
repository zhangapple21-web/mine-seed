#!/usr/bin/env python3
"""
Smelter Gate — 废墟熔炼厂最小护栏

> ARCH-014 子任务2: 实现最小功能的废墟熔炼厂护栏
> 考古依据: [2026-06-28_R1_五大加工厂_废墟熔炼厂_孟婆人格考古.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/recent_memory/daily/2026-06-28_R1_五大加工厂_废墟熔炼厂_孟婆人格考古.md)

## 当前实现状态

这是**最小版本**的 smelter gate，仅实现：
- ✅ 实时拦截：FA模式产出的内容必须经过此 gate 才能进入下游
- ✅ 基本记录：记录每次通过/拦截的详细信息
- ✅ 拒绝分支：发现高风险特征时可以拒绝（ARCH-014 追加）

**当前没有实现**（明确标注为未来扩展）：
- ❌ 遗忘层（孟婆过滤）
- ❌ 自动收敛机制
- ❌ 五大工厂协同（仿造/标记/回收/快递站）

## 设计原则

1. 职责单一：只做拦截和记录，不做压缩、不做决策、不做遗忘
2. 透明性：所有通过 gate 的内容都有完整记录，可追溯
3. 可扩展：预留扩展点，未来可增加遗忘层、收敛机制等
4. 不可绕过：任何 FA 模式产出的内容，必须调用 pass_through() 才能继续
5. 真实拒绝：高风险内容会被拒绝，不只是记录

## 与 FA 模式的关系

FA 模式（Full Access）允许内部推理不做自我审查，
但这道 gate 确保 FA 模式产出的内容在进入影响真实决策的路径前，
至少被记录和标记。

## 拒绝触发条件（ARCH-014 追加）

拒绝条件（任一满足即拒绝）：
1. source 为空或异常
2. feedback 包含操纵性表述（内部消息/必涨/庄家拉升等）
3. feedback 长度 < 5 字符
4. overall_score 与 miner_score 偏差 > 40
5. 评分极端 + 反馈不匹配（如：评分<10但反馈偏多）

不触发拒绝（只是标记）：
- 单纯评分极端（<5 或 >98）不拒绝，只是标记"极端评分"

## rejected vs pending_review 的区别

两种状态在"是否影响真实决策"上**完全一致**：
- 都会写入 audit_results.json
- 都会带 audit_status 标记
- 报告里都显示"审计异常"

区别仅在于：
- rejected：终局状态，明确拒绝，不需要人工干预
- pending_review：需要人工复核，但当前系统没有自动复核机制

因此当前实现将 pending_review 也视为拒绝，等未来有复核流程再区分。
"""
import json
import os
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict


# 高风险特征：操纵性表述
HIGH_RISK_PATTERNS = [
    r"内部消息",
    r"必涨",
    r"稳赚",
    r"内幕",
    r"庄家.*拉升",
    r"主力.*进场",
    r"消息灵通",
    r"确定.*大涨",
]


@dataclass
class GateRecord:
    """Gate 记录数据结构"""
    record_id: str
    timestamp: str
    source: str
    source_type: str
    is_fa_mode: bool
    content_type: str
    content_hash: str
    action: str
    reason: str
    metadata: Dict[str, Any]


class SmelterGate:
    """废墟熔炼厂最小护栏
    
    核心方法:
        pass_through(): FA模式产出必须调用此方法才能进入下游
        get_gate_log(): 查询 gate 日志
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path(__file__).parent.parent / "02_MEMORY" / "smelter_gate"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "gate_log.jsonl"
    
    def _hash_content(self, content: Any) -> str:
        """生成内容哈希（简化版）"""
        import hashlib
        s = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(s.encode()).hexdigest()[:16]
    
    def _generate_id(self) -> str:
        """生成唯一记录ID"""
        ts = int(time.time() * 1000)
        return f"gate_{ts}"
    
    def _check_score_feedback_mismatch(self, score: int, feedback: str) -> Tuple[bool, str]:
        """检查评分与反馈是否自相矛盾
        
        评分极端 + 反馈不匹配才触发拒绝。
        单纯评分极端不拒绝。
        """
        # 极低分（<10）但反馈说"好"
        if score < 10:
            positive_keywords = ["强劲", "看好", "买入", "多头", "突破", "上涨", "推荐"]
            if any(kw in feedback for kw in positive_keywords):
                return True, f"评分({score})与反馈矛盾：极低分但反馈偏多"
        
        # 极高分（>95）但反馈说"差"
        if score > 95:
            negative_keywords = ["风险", "下跌", "空头", "破位", "卖出", "规避", "谨慎"]
            if any(kw in feedback for kw in negative_keywords):
                return True, f"评分({score})与反馈矛盾：极高分但反馈偏空"
        
        return False, ""
    
    def _check_risk(self, content: Any, metadata: Optional[Dict] = None) -> Tuple[bool, str, bool]:
        """检查是否应该拒绝
        
        Args:
            content: 要检查的内容（期望是 dict）
            metadata: 额外元数据
        
        Returns:
            (should_reject: bool, reason: str, needs_review: bool)
        
        拒绝条件：
        1. source 为空或异常
        2. feedback 包含操纵性表述
        3. feedback 长度 < 5 字符
        4. overall_score 与 miner_score 偏差 > 40
        5. 评分极端 + 反馈不匹配
        """
        if not isinstance(content, dict):
            return False, "", False
        
        metadata = metadata or {}
        
        # 1. 检查来源
        source = content.get("source", metadata.get("miner_source", ""))
        if not source or source in ["unknown", "error", ""]:
            return True, "来源不可信", False
        
        # 2. 检查反馈长度
        feedback = content.get("feedback", "")
        if len(feedback) < 5:
            return True, "反馈内容过短", True  # 需要复核
        
        # 3. 检查操纵性表述
        for pattern in HIGH_RISK_PATTERNS:
            if re.search(pattern, feedback):
                return True, f"发现高风险模式: {pattern}", False
        
        # 4. 检查评分一致性
        overall_score = content.get("overall_score")
        miner_score = content.get("score", 50)
        if overall_score is not None:
            deviation = abs(overall_score - miner_score)
            if deviation > 40:
                return True, f"评分偏差过大 ({deviation})", True  # 需要复核
        
        # 5. 检查评分与反馈不匹配
        mismatch, mismatch_reason = self._check_score_feedback_mismatch(miner_score, feedback)
        if mismatch:
            return True, mismatch_reason, True  # 需要复核
        
        return False, "", False
    
    def pass_through(
        self,
        content: Any,
        source: str,
        source_type: str = "unknown",
        is_fa_mode: bool = False,
        content_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        FA模式产出必须经过此 gate 才能进入下游
        
        Args:
            content: 要通过 gate 的内容（任意可序列化对象）
            source: 来源标识（如 "miner_assistant.audit_recommendation"）
            source_type: 来源类型（如 "audit", "recommendation", "experience"）
            is_fa_mode: 是否为 FA 模式产出
            content_type: 内容类型（如 "audit_result", "miner_score", "feedback"）
            metadata: 额外元数据
        
        Returns:
            dict: {
                "passed": bool,
                "record_id": str,
                "gate_action": str,
                "message": str,
                "reject_reason": str (如果拒绝),
                "needs_review": bool (如果拒绝),
                "flags": list (辅助标记)
            }
        """
        metadata = metadata or {}
        record_id = self._generate_id()
        content_hash = self._hash_content(content)
        flags = []
        
        # 检查风险（FA 模式下才检查）
        should_reject = False
        reject_reason = ""
        needs_review = False
        
        if is_fa_mode:
            should_reject, reject_reason, needs_review = self._check_risk(content, metadata)
            
            # 单纯评分极端不拒绝，只是标记
            if isinstance(content, dict):
                score = content.get("score", 50)
                if score < 5 or score > 98:
                    flags.append(f"极端评分({score})，需留意")
        
        # 决定 action
        if should_reject:
            action = "REJECTED"
            reason = f"拒绝: {reject_reason}"
        elif is_fa_mode:
            action = "INTERCEPTED_AND_RECORDED"
            reason = "FA模式产出必须经过 smelter_gate 记录"
        else:
            action = "PASSED"
            reason = "非FA模式，直接通过"
        
        record = GateRecord(
            record_id=record_id,
            timestamp=datetime.now().isoformat(),
            source=source,
            source_type=source_type,
            is_fa_mode=is_fa_mode,
            content_type=content_type,
            content_hash=content_hash,
            action=action,
            reason=reason,
            metadata=metadata
        )
        
        self._write_log(record)
        
        result = {
            "passed": not should_reject,
            "record_id": record_id,
            "gate_action": action,
            "message": reason,
            "flags": flags
        }
        
        if should_reject:
            result["reject_reason"] = reject_reason
            result["needs_review"] = needs_review
        
        return result
    
    def _write_log(self, record: GateRecord):
        """写入 gate 日志"""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    
    def get_gate_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取 gate 日志"""
        if not self.log_file.exists():
            return []
        
        logs = []
        with open(self.log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except:
                        continue
        
        return logs[-limit:]
    
    def get_fa_mode_records(self) -> List[Dict[str, Any]]:
        """获取所有 FA 模式产出的记录"""
        all_logs = self.get_gate_log(limit=1000)
        return [log for log in all_logs if log.get("is_fa_mode")]
    
    def get_rejected_records(self) -> List[Dict[str, Any]]:
        """获取所有被拒绝的记录"""
        all_logs = self.get_gate_log(limit=1000)
        return [log for log in all_logs if log.get("action") == "REJECTED"]


def main():
    """CLI 接口"""
    import argparse
    parser = argparse.ArgumentParser(description="Smelter Gate — 废墟熔炼厂最小护栏")
    parser.add_argument("--pass", dest="pass_content", type=str, help="测试通过 gate 的内容（JSON）")
    parser.add_argument("--source", type=str, default="test", help="来源标识")
    parser.add_argument("--fa", action="store_true", help="标记为 FA 模式产出")
    parser.add_argument("--log", action="store_true", help="输出 gate 日志")
    parser.add_argument("--fa-log", action="store_true", help="输出 FA 模式记录")
    parser.add_argument("--rejected-log", action="store_true", help="输出被拒绝的记录")
    
    args = parser.parse_args()
    
    gate = SmelterGate()
    
    if args.pass_content:
        try:
            content = json.loads(args.pass_content)
        except:
            content = args.pass_content
        
        result = gate.pass_through(
            content=content,
            source=args.source,
            is_fa_mode=args.fa,
            content_type="test"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if args.log:
        logs = gate.get_gate_log()
        print(f"Gate logs ({len(logs)}):")
        for log in logs:
            print(f"  {log['timestamp']} [{log['action']}] {log['source']}")
    
    if args.fa_log:
        fa_records = gate.get_fa_mode_records()
        print(f"FA mode records ({len(fa_records)}):")
        for record in fa_records:
            print(f"  {record['timestamp']} {record['source']} → {record['content_type']}")
    
    if args.rejected_log:
        rejected = gate.get_rejected_records()
        print(f"Rejected records ({len(rejected)}):")
        for record in rejected:
            print(f"  {record['timestamp']} {record['source']} → {record['reason']}")


if __name__ == "__main__":
    main()