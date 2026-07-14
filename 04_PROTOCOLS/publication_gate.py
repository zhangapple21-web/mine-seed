#!/usr/bin/env python3
"""
Publication Gate — 发布闸门

## 设计理念

执行不停，学习不停，只有发布有条件。
(Execution Never Stops. Learning Never Stops. Publication Is Conditional.)

本模块是同一种 Gate 模式的第三个实例，前两个是：
- Smelter Gate（smelter_gate.py）：FA内部推理 → 真实决策的护栏
- Admission Engine（civilization_contract.py）：Runtime → Civilization Repository 的写入护栏

**未来方向**：三个 Gate 实例应抽象为统一的 Gate 基类，共享记录、日志、审计能力。
本次暂不重构，仅在代码注释中明确标注。

## 四级路由

| 路由级别 | 阈值（健康度） | 说明 | 是否进入 Learning |
|----------|---------------|------|------------------|
| Public | ≥70 | 客户可见，可推送 | ✅ |
| Internal | ≥50 | 内部观察，不推送 | ✅ |
| Research | ≥30 | 研究样本，不推送 | ✅ |
| Discard | <30 | 直接废弃 | ❌ |

**重要说明**：以上阈值是初始估计值，需要至少两周真实数据验证后校准，不是最终结论。
真实数据包括：各路由级别推荐的实际胜率、客户反馈、市场环境变化等。

## 职责边界

1. 输入：Health Score（来自 AdaptiveScorer）
2. 输出：四级路由决策
3. 不负责：
   - 不负责计算 Health Score（那是 AdaptiveScorer 的职责）
   - 不负责数据质量过滤（那是 Publication Gate 之前的独立关卡）
   - 不负责 Learning 流程（那是 PerformanceTracker 的职责）
   - 不负责 Recommendation 生成（那是 StockAdvisor 的职责）
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict


# Bootstrap Threshold — 初始实验值，非固定规则
# 所有阈值最终应来自真实数据校准（Observation），不是来自 Prompt 猜测。
# 当前仅用于系统启动，两周后需基于真实运行数据复核。
ROUTE_LEVELS = {
    "PUBLIC": {
        "name": "Public",
        "description": "客户可见，可推送",
        "min_score": 70,  # Bootstrap Threshold: 需数据校准
        "allow_publication": True,
        "allow_learning": True,
    },
    "INTERNAL": {
        "name": "Internal",
        "description": "内部观察，不推送",
        "min_score": 50,  # Bootstrap Threshold: 需数据校准
        "allow_publication": False,
        "allow_learning": True,
    },
    "RESEARCH": {
        "name": "Research",
        "description": "研究样本，不推送",
        "min_score": 30,  # Bootstrap Threshold: 需数据校准
        "allow_publication": False,
        "allow_learning": True,
    },
    "DISCARD": {
        "name": "Discard",
        "description": "直接废弃，不进学习",
        "min_score": -1,  # Bootstrap Threshold: 需数据校准
        "allow_publication": False,
        "allow_learning": False,
    },
}


@dataclass
class PublicationRecord:
    record_id: str
    timestamp: str
    health_score: float
    route_level: str
    route_name: str
    allow_publication: bool
    allow_learning: bool
    metadata: Dict[str, Any]


class PublicationGate:
    """发布闸门
    
    核心方法:
        route(): 根据健康度决定发布路由
        get_route_log(): 查询路由日志
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path(__file__).parent.parent / "02_MEMORY" / "publication_gate"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "publication_log.jsonl"
    
    def _generate_id(self) -> str:
        ts = int(time.time() * 1000)
        return f"pubgate_{ts}"
    
    def route(self, health_score: float, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据健康度决定发布路由
        
        Args:
            health_score: 健康度评分（0-100）
            metadata: 额外元数据（如推荐股票代码、策略版本等）
        
        Returns:
            dict: {
                "route_level": str (PUBLIC/INTERNAL/RESEARCH/DISCARD),
                "route_name": str,
                "description": str,
                "allow_publication": bool,
                "allow_learning": bool,
                "record_id": str,
                "health_score": float,
                "threshold_note": str (阈值说明)
            }
        """
        metadata = metadata or {}
        
        if health_score >= 70:
            level_key = "PUBLIC"
        elif health_score >= 50:
            level_key = "INTERNAL"
        elif health_score >= 30:
            level_key = "RESEARCH"
        else:
            level_key = "DISCARD"
        
        level_info = ROUTE_LEVELS[level_key]
        
        record_id = self._generate_id()
        record = PublicationRecord(
            record_id=record_id,
            timestamp=datetime.now().isoformat(),
            health_score=health_score,
            route_level=level_key,
            route_name=level_info["name"],
            allow_publication=level_info["allow_publication"],
            allow_learning=level_info["allow_learning"],
            metadata=metadata
        )
        
        self._write_log(record)
        
        result = {
            "route_level": level_key,
            "route_name": level_info["name"],
            "description": level_info["description"],
            "allow_publication": level_info["allow_publication"],
            "allow_learning": level_info["allow_learning"],
            "record_id": record_id,
            "health_score": health_score,
            "threshold_note": "⚠ 阈值为初始估计值，需两周真实数据校准"
        }
        
        return result
    
    def _write_log(self, record: PublicationRecord):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")
    
    def get_route_log(self, limit: int = 100) -> List[Dict[str, Any]]:
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
    
    def get_public_routes(self) -> List[Dict[str, Any]]:
        all_logs = self.get_route_log(limit=1000)
        return [log for log in all_logs if log.get("allow_publication")]
    
    def get_discarded_routes(self) -> List[Dict[str, Any]]:
        all_logs = self.get_route_log(limit=1000)
        return [log for log in all_logs if log.get("route_level") == "DISCARD"]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publication Gate — 发布闸门")
    parser.add_argument("--score", type=float, required=True, help="健康度评分")
    parser.add_argument("--metadata", type=str, help="额外元数据（JSON）")
    parser.add_argument("--log", action="store_true", help="输出路由日志")
    parser.add_argument("--public", action="store_true", help="输出 Public 路由记录")
    parser.add_argument("--discarded", action="store_true", help="输出 Discard 路由记录")
    
    args = parser.parse_args()
    
    gate = PublicationGate()
    
    if args.score is not None:
        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except:
                pass
        
        result = gate.route(args.score, metadata)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if args.log:
        logs = gate.get_route_log()
        print(f"Publication logs ({len(logs)}):")
        for log in logs:
            print(f"  {log['timestamp']} [{log['route_level']}] score={log['health_score']}")
    
    if args.public:
        public_records = gate.get_public_routes()
        print(f"Public records ({len(public_records)}):")
        for record in public_records:
            print(f"  {record['timestamp']} score={record['health_score']}")
    
    if args.discarded:
        discarded = gate.get_discarded_routes()
        print(f"Discarded records ({len(discarded)}):")
        for record in discarded:
            print(f"  {record['timestamp']} score={record['health_score']}")


if __name__ == "__main__":
    main()