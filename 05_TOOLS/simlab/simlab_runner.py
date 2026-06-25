"""
SimLab Runner (v1)

目标：跑通“推演实验室”的最小闭环：
- 输入：最近几天的日报（02_MEMORY/recent_memory/daily/*.md）
- 抽象：把文本归纳为“行为事件”计数（发现/整理/关系/报告）
- 输出：脱敏快照 JSON 到 output/simlab/

注意：
- 不输出原始文本内容（避免 PII）
- 不访问外部网络
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DAILY_DIR = os.path.join(REPO_ROOT, "02_MEMORY", "recent_memory", "daily")
OUT_DIR = os.path.join(REPO_ROOT, "output", "simlab")


@dataclass
class SimEventCounts:
    observe: int = 0
    organize: int = 0
    relate: int = 0
    report: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "observe": self.observe,
            "organize": self.organize,
            "relate": self.relate,
            "report": self.report,
        }


def _safe_read_text(path: str, max_bytes: int = 200_000) -> str:
    with open(path, "rb") as f:
        data = f.read(max_bytes)
    return data.decode("utf-8", errors="ignore")


def _count_events(text: str) -> SimEventCounts:
    """
    极简事件抽象：
    - 观察：发现/看到/扫描/证据/命中
    - 整理：整理/归档/压缩/总结/记录
    - 关系：关系/血缘/继承/演化/映射/链
    - 报告：报告/PR/提交/发布/更新
    """
    t = text.lower()
    c = SimEventCounts()

    def hit(patterns: List[str]) -> int:
        return sum(len(re.findall(p, t, flags=re.IGNORECASE)) for p in patterns)

    c.observe = hit([r"发现", r"看到", r"扫描", r"证据", r"命中"])
    c.organize = hit([r"整理", r"归档", r"压缩", r"总结", r"记录"])
    c.relate = hit([r"关系", r"血缘", r"继承", r"演化", r"映射", r"链"])
    c.report = hit([r"\bpr\b", r"提交", r"发布", r"更新", r"报告"])
    return c


def run(days: int = 7) -> Dict:
    if not os.path.isdir(DAILY_DIR):
        raise RuntimeError(f"daily dir not found: {DAILY_DIR}")

    os.makedirs(OUT_DIR, exist_ok=True)

    files = [f for f in os.listdir(DAILY_DIR) if f.endswith(".md")]
    files.sort(reverse=True)
    files = files[:days]

    per_file = []
    total = SimEventCounts()
    for fn in files:
        fp = os.path.join(DAILY_DIR, fn)
        text = _safe_read_text(fp)
        counts = _count_events(text)
        per_file.append(
            {
                "file": fn,
                "counts": counts.to_dict(),
            }
        )
        total.observe += counts.observe
        total.organize += counts.organize
        total.relate += counts.relate
        total.report += counts.report

    snapshot = {
        "simlab": "v1",
        "purpose": "BEHAVIORAL_SIMULATION_ONLY",
        "created_at": datetime.now().isoformat(),
        "input": {
            "source": "02_MEMORY/recent_memory/daily",
            "days": days,
            "files_count": len(files),
        },
        "output": {
            "event_counts_total": total.to_dict(),
            "event_counts_per_file": per_file,
        },
        "notes": [
            "本快照不包含原始文本内容，仅包含事件计数与结构化摘要。",
            "该 runner 仅用于证明 simlab 的‘可复现推演快照’闭环可跑通。",
        ],
    }

    out_name = f"simlab_snapshot_{int(time.time())}.json"
    out_path = os.path.join(OUT_DIR, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    return {"snapshot_path": out_path, "snapshot": snapshot}


if __name__ == "__main__":
    result = run(days=7)
    print("ok:", os.path.basename(result["snapshot_path"]))

