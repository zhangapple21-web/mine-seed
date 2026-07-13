"""
---
id: PROTO-012
type: protocol
title: "Worker Registry — Worker 注册中心"
status: active
source: "Router Chip Enhancement"
created: 2026-07-12
confidence: 0.90
lineage:
  - PROTO-008
  - PROTO-001
related: [PROTO-008, PROTO-001]
tags: [worker, registry, router, capability]
archaeology:
  state: original
  sources: 0
---
Worker Registry — Worker 注册中心。

统一管理系统中的所有 Worker，包含：
- Worker 元信息（id, name, description）
- Capabilities（能做什么）
- 状态（active/inactive/maintenance）
- 成本与优先级
- 健康检查

用法:
    from worker_registry import WorkerRegistry
    registry = WorkerRegistry()
    registry.register(...)
    workers = registry.find_by_capability("recovery")
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


WORKSPACE = Path(__file__).resolve().parent.parent
REGISTRY_PATH = WORKSPACE / "03_DATA" / "worker_registry.json"


DEFAULT_WORKERS = [
    {
        "id": "miner",
        "name": "Miner",
        "chinese": "矿工",
        "description": "执行考古扫描、文件恢复、信息采集任务",
        "capabilities": ["recovery", "scanner", "mining", "archaeology", "tg_scan", "github_scan"],
        "status": "active",
        "cost": 1,
        "priority": 1,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "governor",
        "name": "Governor",
        "chinese": "治理者",
        "description": "决策、辩论、规则制定与自我约束",
        "capabilities": ["governance", "debate", "decision", "constraint", "roundtable"],
        "status": "active",
        "cost": 3,
        "priority": 1,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "auditor",
        "name": "Auditor",
        "chinese": "审计员",
        "description": "文明健康审计、重复检测、断链检测",
        "capabilities": ["audit", "health_check", "duplicate_detection", "graph_scan"],
        "status": "active",
        "cost": 2,
        "priority": 2,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "archivist",
        "name": "Archivist",
        "chinese": "档案员",
        "description": "记忆管理、经验沉淀、知识库维护",
        "capabilities": ["memory", "archive", "knowledge", "experience", "constraint"],
        "status": "active",
        "cost": 1,
        "priority": 2,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "heartbeat",
        "name": "Heartbeat",
        "chinese": "心跳",
        "description": "系统主循环、任务调度、状态监控",
        "capabilities": ["execution", "scheduler", "monitor", "observer", "self_evolution"],
        "status": "active",
        "cost": 1,
        "priority": 0,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "scanner",
        "name": "Recovery Scanner",
        "chinese": "恢复扫描器",
        "description": "7层文明恢复扫描器",
        "capabilities": ["recovery", "scanner", "archaeology", "fingerprint", "dna"],
        "status": "active",
        "cost": 2,
        "priority": 1,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "fingerprint",
        "name": "Fingerprint Engine",
        "chinese": "指纹引擎",
        "description": "文明指纹扫描与芯片恢复",
        "capabilities": ["fingerprint", "chip_recovery", "gene_detection", "structure_detection"],
        "status": "active",
        "cost": 2,
        "priority": 2,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "question_center",
        "name": "Question Center",
        "chinese": "问题中心",
        "description": "问题管理、假设追踪、决策记录",
        "capabilities": ["question", "hypothesis", "decision", "tracking"],
        "status": "active",
        "cost": 1,
        "priority": 1,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "self_evolution",
        "name": "Self Evolution",
        "chinese": "自演化引擎",
        "description": "自我演化、规则修改、系统升级",
        "capabilities": ["evolution", "self_modify", "adaptation", "learning"],
        "status": "active",
        "cost": 3,
        "priority": 2,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
    {
        "id": "notifier",
        "name": "Notifier",
        "chinese": "通知器",
        "description": "TG推送、消息通知、状态上报",
        "capabilities": ["notification", "tg_push", "messaging", "report"],
        "status": "active",
        "cost": 1,
        "priority": 3,
        "health": 1.0,
        "last_run": None,
        "run_count": 0,
    },
]


class WorkerRegistry:
    """Worker 注册中心"""

    def __init__(self):
        self.workers: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if REGISTRY_PATH.exists():
            try:
                data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
                for w in data.get("workers", []):
                    self.workers[w["id"]] = w
            except Exception:
                self._init_defaults()
        else:
            self._init_defaults()

    def _init_defaults(self):
        for w in DEFAULT_WORKERS:
            self.workers[w["id"]] = dict(w)
        self._save()

    def _save(self):
        REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "total_workers": len(self.workers),
            "active_workers": len([w for w in self.workers.values() if w["status"] == "active"]),
            "workers": list(self.workers.values()),
        }
        REGISTRY_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def register(self, worker: Dict[str, Any]) -> bool:
        wid = worker.get("id")
        if not wid:
            return False
        if wid in self.workers:
            return False
        default = {
            "status": "active",
            "cost": 1,
            "priority": 2,
            "health": 1.0,
            "last_run": None,
            "run_count": 0,
        }
        full = {**default, **worker}
        self.workers[wid] = full
        self._save()
        return True

    def unregister(self, worker_id: str) -> bool:
        if worker_id in self.workers:
            del self.workers[worker_id]
            self._save()
            return True
        return False

    def get(self, worker_id: str) -> Optional[Dict[str, Any]]:
        return self.workers.get(worker_id)

    def list_all(self) -> List[Dict[str, Any]]:
        return list(self.workers.values())

    def list_active(self) -> List[Dict[str, Any]]:
        return [w for w in self.workers.values() if w["status"] == "active"]

    def find_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        results = []
        cap_lower = capability.lower()
        for w in self.workers.values():
            if w["status"] != "active":
                continue
            for cap in w.get("capabilities", []):
                if cap_lower in cap.lower():
                    results.append(w)
                    break
        results.sort(key=lambda w: (w["priority"], w["cost"]))
        return results

    def find_best(self, capabilities: List[str]) -> Optional[Dict[str, Any]]:
        candidates = self.list_active()
        best = None
        best_score = -1
        for w in candidates:
            w_caps = set(c.lower() for c in w.get("capabilities", []))
            matched = sum(1 for c in capabilities if c.lower() in w_caps)
            coverage = matched / len(capabilities) if capabilities else 0
            cost_eff = 1.0 / (w["cost"] + 1)
            priority_bonus = 1.0 / (w["priority"] + 1)
            score = coverage * 0.6 + cost_eff * 0.2 + priority_bonus * 0.2
            if score > best_score:
                best_score = score
                best = w
        return best

    def record_run(self, worker_id: str, success: bool = True):
        if worker_id not in self.workers:
            return
        w = self.workers[worker_id]
        w["last_run"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        w["run_count"] = w.get("run_count", 0) + 1
        if success:
            w["health"] = min(1.0, w.get("health", 1.0) + 0.01)
        else:
            w["health"] = max(0.0, w.get("health", 1.0) - 0.1)
        self._save()

    def set_status(self, worker_id: str, status: str) -> bool:
        if worker_id not in self.workers:
            return False
        self.workers[worker_id]["status"] = status
        self._save()
        return True

    def summary(self) -> Dict[str, Any]:
        active = [w for w in self.workers.values() if w["status"] == "active"]
        all_caps = set()
        for w in self.workers.values():
            for c in w.get("capabilities", []):
                all_caps.add(c)
        return {
            "total": len(self.workers),
            "active": len(active),
            "inactive": len(self.workers) - len(active),
            "total_capabilities": len(all_caps),
            "avg_health": sum(w.get("health", 0) for w in self.workers.values()) / len(self.workers) if self.workers else 0,
        }


if __name__ == "__main__":
    import sys
    registry = WorkerRegistry()
    s = registry.summary()
    print(f"Worker Registry: {s['active']}/{s['total']} active, {s['total_capabilities']} capabilities")
    print(f"Avg health: {s['avg_health']:.2f}")
    print()
    for w in registry.list_active():
        caps = ", ".join(w["capabilities"][:5])
        print(f"  [{w['id']}] {w['name']:20s} ({w['chinese']})")
        print(f"       caps: {caps}")
        print(f"       cost={w['cost']} priority={w['priority']} health={w['health']:.2f} runs={w.get('run_count', 0)}")
        print()
