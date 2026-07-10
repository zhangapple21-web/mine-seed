#!/usr/bin/env python3
"""
Fitness Tracker — Task→Worker适配度记录器
不评判，只记录。30天后让数据说话。

原则：
- 每次 signal_cron 执行都记录，无论成功失败
- 记录 task_type + worker + outcome + error_type
- 禁止泛化：只记录观察，不生成 category 级约束
- 30天/5+样本后才允许从 specific 升级到 category
"""
import json, os
from datetime import datetime

FITNESS_LOG = "/home/coze/mine_output/fitness_log.jsonl"
TAXONOMY_FILE = "/home/coze/signal_taxonomy.json"

def classify_signal(signal_name: str) -> str:
    """根据信号名推断分类，未知类型归入待分类"""
    name = signal_name.lower()
    simple_keywords = ["momentum", "breakout", "trend", "volume_spike", "price_level", "simple"]
    complex_keywords = ["mean_reversion", "divergence", "cross_factor", "multi_window", 
                       "conditional", "complex", "pair", "spread", "relative"]
    
    for kw in simple_keywords:
        if kw in name:
            return "simple_signal"
    for kw in complex_keywords:
        if kw in name:
            return "complex_signal"
    return "unclassified"

def record(worker: str, task_type: str, outcome: str, error_type: str = "", 
           signal_name: str = "", model: str = "", extra: dict = None):
    """记录一次fitness观察"""
    entry = {
        "ts": datetime.now().isoformat(),
        "worker": worker,
        "model": model or worker,
        "task_type": task_type,
        "signal_name": signal_name,
        "signal_category": classify_signal(signal_name) if signal_name else "unknown",
        "outcome": outcome,  # SUCCESS / FAIL / PARTIAL
        "error_type": error_type,
        "extra": extra or {}
    }
    
    os.makedirs(os.path.dirname(FITNESS_LOG), exist_ok=True)
    with open(FITNESS_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    return entry

def stats(days: int = 30) -> dict:
    """统计fitness数据，返回按worker×category的成功率"""
    from collections import defaultdict
    
    if not os.path.exists(FITNESS_LOG):
        return {"note": "no data yet"}
    
    cutoff = datetime.now().timestamp() - days * 86400
    buckets = defaultdict(lambda: {"success": 0, "fail": 0, "total": 0, "errors": defaultdict(int)})
    
    with open(FITNESS_LOG) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                ts = datetime.fromisoformat(entry["ts"]).timestamp()
                if ts < cutoff:
                    continue
                
                key = f"{entry['worker']}|{entry.get('signal_category', 'unknown')}"
                buckets[key]["total"] += 1
                if entry["outcome"] == "SUCCESS":
                    buckets[key]["success"] += 1
                else:
                    buckets[key]["fail"] += 1
                    if entry.get("error_type"):
                        buckets[key]["errors"][entry["error_type"]] += 1
            except:
                continue
    
    result = {}
    for key, data in buckets.items():
        worker, cat = key.split("|", 1)
        rate = data["success"] / data["total"] * 100 if data["total"] > 0 else 0
        result[key] = {
            "worker": worker,
            "category": cat,
            "success_rate": f"{rate:.0f}%",
            "success": data["success"],
            "fail": data["fail"],
            "total": data["total"],
            "top_errors": dict(sorted(data["errors"].items(), key=lambda x: -x[1])[:3])
        }
    
    return result

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        s = stats()
        print(json.dumps(s, indent=2, ensure_ascii=False))
    else:
        print("Usage: fitness_tracker.py stats")
