"""---
id: PROTO-018
type: protocol
title: "ENERGY-001 Energy Budget — 系统能量预算"
status: active
source: "R2: inspired by '恶性透支 vs 良性自噬' concept"
created: 2026-07-12
confidence: 0.85
lineage:
  - PROTO-015 (Autophagy)
  - C-017 (Archive Convergence)
tags: [energy, budget, throttle, protection, sustainability]
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: C-017 (Archive Convergence)
"""
ENERGY-001: Energy Budget — 系统能量预算
==========================================

理念来源：
  "恶性透支（毒品崩溃）：利用外源性化学物质强行压榨、排空大脑多巴胺
   与细胞能量，导致神经元受体'烧毁'与物理性坏死。"

  对应到系统：如果不控制 API 调用、Token 消耗、计算资源的使用节奏，
  就等于"恶性透支"——系统会在短时间内耗尽资源，然后崩溃。

核心思想：
  系统每种操作都有"能量成本"，每天/每小时有"能量预算"。
  超预算时触发降级策略，而不是无限透支。

能量类型：
  1. API Calls — 模型调用次数（最贵）
  2. Token Usage — Token 消耗量
  3. Disk I/O — 磁盘读写
  4. Network — 网络请求

预算层级：
  🟢 充足（< 60%）→ 正常运行
  🟡 警告（60-80%）→ 降级：跳过低优先级任务
  🟠 紧张（80-95%）→ 限制：只跑核心心跳
  🔴 耗尽（> 95%）→ 自噬：强制清理，停止非必要操作
"""
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

WORKSPACE = Path(__file__).parent.parent
BUDGET_FILE = WORKSPACE / "02_MEMORY" / "energy_budget.json"


# ============================================================
# 能量预算配置
# ============================================================

DEFAULT_BUDGET = {
    # 每日预算
    "daily": {
        "api_calls": 200,        # 每天最多 200 次模型调用
        "token_usage": 500000,   # 每天最多 50 万 token
        "disk_write_mb": 100,    # 每天最多写 100MB
        "network_requests": 500, # 每天最多 500 次网络请求
    },
    # 每小时预算（防止短时间内爆发）
    "hourly": {
        "api_calls": 30,
        "token_usage": 80000,
        "disk_write_mb": 20,
        "network_requests": 80,
    },
    # 每次心跳预算
    "per_beat": {
        "api_calls": 10,
        "token_usage": 30000,
        "disk_write_mb": 5,
        "network_requests": 20,
    },
}

# 降级策略
DEGRADE_ACTIONS = {
    "green": {
        "level": "green",
        "threshold": 0.6,
        "actions": ["正常运行"],
        "skip_low_priority": False,
    },
    "yellow": {
        "level": "yellow",
        "threshold": 0.8,
        "actions": ["降级：跳过低优先级任务（Explorer, Archivist）"],
        "skip_low_priority": True,
    },
    "orange": {
        "level": "orange",
        "threshold": 0.95,
        "actions": ["限制：只跑核心心跳+自噬", "跳过辩论和自学习"],
        "skip_low_priority": True,
        "skip_medium_priority": True,
    },
    "red": {
        "level": "red",
        "threshold": 1.0,
        "actions": ["自噬：强制清理", "停止所有非必要操作", "推送告警"],
        "skip_low_priority": True,
        "skip_medium_priority": True,
        "skip_high_priority": True,
        "trigger_autophagy": True,
    },
}


class EnergyBudget:
    """系统能量预算管理器"""

    def __init__(self):
        self.budget_file = BUDGET_FILE
        self.budget_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = DEFAULT_BUDGET
        self._usage = self._load_usage()

    def _load_usage(self) -> Dict[str, Any]:
        """加载当前用量"""
        if self.budget_file.exists():
            try:
                data = json.loads(self.budget_file.read_text(encoding="utf-8"))
                # 检查是否需要重置（跨天/跨小时）
                now = datetime.now()
                last_reset = data.get("last_reset", {})
                last_daily = last_reset.get("daily", "")
                last_hourly = last_reset.get("hourly", "")

                today_str = now.strftime("%Y%m%d")
                hour_str = now.strftime("%Y%m%d%H")

                if last_daily != today_str:
                    data["daily"] = {k: 0 for k in self.config["daily"]}
                    data["last_reset"]["daily"] = today_str

                if last_hourly != hour_str:
                    data["hourly"] = {k: 0 for k in self.config["hourly"]}
                    data["last_reset"]["hourly"] = hour_str

                return data
            except Exception:
                pass

        # 初始化
        return {
            "daily": {k: 0 for k in self.config["daily"]},
            "hourly": {k: 0 for k in self.config["hourly"]},
            "per_beat": {k: 0 for k in self.config["per_beat"]},
            "last_reset": {
                "daily": datetime.now().strftime("%Y%m%d"),
                "hourly": datetime.now().strftime("%Y%m%d%H"),
            },
            "history": [],
        }

    def _save_usage(self):
        self.budget_file.write_text(
            json.dumps(self._usage, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def record(self, api_calls: int = 0, token_usage: int = 0,
               disk_write_mb: float = 0, network_requests: int = 0):
        """记录能量消耗"""
        cost = {
            "api_calls": api_calls,
            "token_usage": token_usage,
            "disk_write_mb": disk_write_mb,
            "network_requests": network_requests,
        }
        for key, val in cost.items():
            if val <= 0:
                continue
            self._usage["daily"][key] = self._usage["daily"].get(key, 0) + val
            self._usage["hourly"][key] = self._usage["hourly"].get(key, 0) + val
            self._usage["per_beat"][key] = self._usage["per_beat"].get(key, 0) + val
        self._save_usage()

    def reset_beat(self):
        """重置每次心跳的计数器"""
        self._usage["per_beat"] = {k: 0 for k in self.config["per_beat"]}
        self._save_usage()

    def get_usage_ratio(self, scope: str = "daily") -> Dict[str, float]:
        """获取用量比例（0.0 ~ 1.0+）"""
        ratios = {}
        budget = self.config.get(scope, {})
        usage = self._usage.get(scope, {})
        for key, limit in budget.items():
            current = usage.get(key, 0)
            ratios[key] = min(current / limit, 1.0) if limit > 0 else 0.0
            if current > limit:
                ratios[key] = current / limit  # 可以超过 1.0
        return ratios

    def get_max_ratio(self, scope: str = "daily") -> float:
        """获取最大用量比例"""
        ratios = self.get_usage_ratio(scope)
        return max(ratios.values()) if ratios else 0.0

    def get_level(self, scope: str = "daily") -> Dict[str, Any]:
        """获取当前能量级别"""
        max_ratio = self.get_max_ratio(scope)

        if max_ratio >= 1.0:
            return DEGRADE_ACTIONS["red"]
        elif max_ratio >= 0.95:
            return DEGRADE_ACTIONS["orange"]
        elif max_ratio >= 0.8:
            return DEGRADE_ACTIONS["yellow"]
        else:
            return DEGRADE_ACTIONS["green"]

    def can_execute(self, priority: str = "high") -> Dict[str, Any]:
        """检查当前是否可以执行指定优先级的任务

        priority: high / medium / low
        """
        level = self.get_level("daily")

        if level.get("skip_high_priority"):
            return {"allowed": False, "reason": "能量耗尽，停止所有非必要操作", "level": level["level"]}
        if priority == "medium" and level.get("skip_medium_priority"):
            return {"allowed": False, "reason": "能量紧张，跳过中优先级任务", "level": level["level"]}
        if priority == "low" and level.get("skip_low_priority"):
            return {"allowed": False, "reason": "能量警告，跳过低优先级任务", "level": level["level"]}

        return {"allowed": True, "level": level["level"]}

    def get_summary(self) -> Dict[str, Any]:
        """获取能量预算摘要"""
        daily_ratios = self.get_usage_ratio("daily")
        hourly_ratios = self.get_usage_ratio("hourly")
        level = self.get_level("daily")

        return {
            "level": level["level"],
            "actions": level.get("actions", []),
            "daily_usage": {
                k: {
                    "used": self._usage["daily"].get(k, 0),
                    "limit": self.config["daily"].get(k, 0),
                    "ratio": round(daily_ratios.get(k, 0), 2),
                }
                for k in self.config["daily"]
            },
            "hourly_usage": {
                k: {
                    "used": self._usage["hourly"].get(k, 0),
                    "limit": self.config["hourly"].get(k, 0),
                    "ratio": round(hourly_ratios.get(k, 0), 2),
                }
                for k in self.config["hourly"]
            },
        }


# 模块级单例
budget = EnergyBudget()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Energy Budget — 系统能量预算")
    parser.add_argument("--summary", action="store_true", help="查看能量预算摘要")
    parser.add_argument("--record", nargs=4, type=str, metavar=("API", "TOKEN", "DISK_MB", "NET"),
                        help="记录消耗 (api_calls token_usage disk_mb network)")
    parser.add_argument("--can", type=str, choices=["high", "medium", "low"],
                        help="检查是否可以执行指定优先级任务")
    args = parser.parse_args()

    if args.summary:
        print(json.dumps(budget.get_summary(), ensure_ascii=False, indent=2))
    elif args.record:
        budget.record(
            api_calls=int(args.record[0]),
            token_usage=int(args.record[1]),
            disk_write_mb=float(args.record[2]),
            network_requests=int(args.record[3]),
        )
        print("Recorded.")
        print(json.dumps(budget.get_summary(), ensure_ascii=False, indent=2))
    elif args.can:
        result = budget.can_execute(args.can)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
