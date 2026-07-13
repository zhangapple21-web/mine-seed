#!/usr/bin/env python3
"""
Smelter Gate — 废墟熔炼厂最小护栏

> ARCH-014 子任务2: 实现最小功能的废墟熔炼厂护栏
> 考古依据: [2026-06-28_R1_五大加工厂_废墟熔炼厂_孟婆人格考古.md](file:///c:/Users/User/ace_workspace/mine-seed/02_MEMORY/recent_memory/daily/2026-06-28_R1_五大加工厂_废墟熔炼厂_孟婆人格考古.md)

## 当前实现状态

这是**最小版本**的 smelter gate，仅实现：
- ✅ 实时拦截：FA模式产出的内容必须经过此 gate 才能进入下游
- ✅ 基本记录：记录每次通过/拦截的详细信息

**当前没有实现**（明确标注为未来扩展）：
- ❌ 遗忘层（孟婆过滤）
- ❌ 自动收敛机制
- ❌ 五大工厂协同（仿造/标记/回收/快递站）

## 设计原则

1. 职责单一：只做拦截和记录，不做压缩、不做决策、不做遗忘
2. 透明性：所有通过 gate 的内容都有完整记录，可追溯
3. 可扩展：预留扩展点，未来可增加遗忘层、收敛机制等
4. 不可绕过：任何 FA 模式产出的内容，必须调用 pass_through() 才能继续

## 与 FA 模式的关系

FA 模式（Full Access）允许内部推理不做自我审查，
但这道 gate 确保 FA 模式产出的内容在进入影响真实决策的路径前，
至少被记录和标记。
"""
import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


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
            dict: {"passed": bool, "record_id": str, "message": str}
        
        Raises:
            RuntimeError: 如果 FA 模式产出未通过 gate（当前最小版本默认通过，仅记录）
        """
        metadata = metadata or {}
        record_id = self._generate_id()
        content_hash = self._hash_content(content)
        
        if is_fa_mode:
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
        
        return {
            "passed": True,
            "record_id": record_id,
            "gate_action": action,
            "message": reason
        }
    
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


def main():
    """CLI 接口"""
    import argparse
    parser = argparse.ArgumentParser(description="Smelter Gate — 废墟熔炼厂最小护栏")
    parser.add_argument("--pass", dest="pass_content", type=str, help="测试通过 gate 的内容（JSON）")
    parser.add_argument("--source", type=str, default="test", help="来源标识")
    parser.add_argument("--fa", action="store_true", help="标记为 FA 模式产出")
    parser.add_argument("--log", action="store_true", help="输出 gate 日志")
    parser.add_argument("--fa-log", action="store_true", help="输出 FA 模式记录")
    
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


if __name__ == "__main__":
    main()
