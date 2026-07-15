#!/usr/bin/env python3
"""
Shadow Evaluation — 板块A' Deliverable 3 第二段

目的：连续运行 5 天，不影响生产输出，观察启用新 signal 后的真实表现。
- 不修改 AdaptiveScorer
- 不修改 stock_advisor.run() 生产路径
- 模拟打分（parallel scoring），对比生产路径结果
- 复用 Replay 结果作为参考基线

与 Replay 的区别（关键）：
- Replay：历史数据回放，"过去 60 天这个 signal 表现如何"
- Shadow：实时 5 天，"这个 signal 在当前市场环境下表现如何"

Acceptance：只有 Replay PASS 的 candidate 才能进入 Shadow
            Replay INSUFFICIENT_DATA/FAIL 的 candidate 直接被 Shadow 拒绝

Usage:
  python shadow.py --candidate sig_candidate_xxx --start
  python shadow.py --report sig_candidate_xxx   # 查看 shadow 报告
  python shadow.py --list                       # 列出所有进入 shadow 的 candidate
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from law_discovery import LawRegistry, LawStatus


WORKSPACE = Path(__file__).parent.parent
SHADOW_DIR = WORKSPACE / "02_MEMORY" / "shadow"
SHADOW_DIR.mkdir(parents=True, exist_ok=True)


class ShadowEvaluation:
    """Shadow Evaluation Engine — 实时 5 天观察"""

    SHADOW_DAYS = 5

    def __init__(self):
        self.registry = LawRegistry()

    def _validate_replay(self, candidate) -> Optional[str]:
        """校验 candidate 是否通过 Replay 阶段
        Returns: None if pass, error message if fail
        """
        if not candidate.replay_result:
            return f"Candidate {candidate.law_id} 未运行 Replay"

        replay_status = candidate.replay_result.get("replay_status")
        if replay_status != "PASS":
            return (f"Candidate {candidate.law_id} Replay 状态为 {replay_status}，"
                    f"按板块A' 规则不能进入 Shadow（必须先 Replay PASS）")

        return None

    def start_shadow(self, candidate_id: str) -> Dict[str, Any]:
        """启动 Shadow Evaluation（5 天观察）"""
        candidate = self.registry.get_law(candidate_id)
        if not candidate:
            return {"error": f"Candidate {candidate_id} not found"}

        # 校验 Replay
        replay_error = self._validate_replay(candidate)
        if replay_error:
            return {
                "candidate_id": candidate_id,
                "shadow_status": "REJECTED",
                "reason": replay_error,
            }

        # 启动 Shadow
        candidate.shadow_result = {
            "candidate_id": candidate_id,
            "shadow_status": "RUNNING",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(days=self.SHADOW_DAYS)).isoformat(),
            "days_completed": 0,
            "shadow_scores": [],         # 每天的 shadow 打分
            "production_scores": [],     # 每天的生产路径打分
            "diff_summary": {},
        }

        # 状态保持 DRAFT（shadow 是观察，不激活）
        self.registry._save()

        # 持久化
        shadow_file = SHADOW_DIR / f"shadow_{candidate_id}_{datetime.now().strftime('%Y%m%d')}.json"
        shadow_file.write_text(json.dumps(candidate.shadow_result, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "candidate_id": candidate_id,
            "shadow_status": "STARTED",
            "duration_days": self.SHADOW_DAYS,
            "shadow_file": str(shadow_file),
            "note": f"将在 {self.SHADOW_DAYS} 天后自动出报告，期间不影响生产",
        }

    def record_daily_observation(self, candidate_id: str,
                                  shadow_score: float,
                                  production_score: float,
                                  actual_t1: float = None) -> Dict:
        """记录一天观察（每天 daily_runner 后调用）"""
        candidate = self.registry.get_law(candidate_id)
        if not candidate or not candidate.shadow_result:
            return {"error": "Shadow 未启动"}

        if candidate.shadow_result.get("shadow_status") != "RUNNING":
            return {"error": f"Shadow 状态为 {candidate.shadow_result.get('shadow_status')}，不接受新数据"}

        # 记录今天
        day_record = {
            "date": datetime.now().strftime("%Y%m%d"),
            "shadow_score": shadow_score,
            "production_score": production_score,
            "diff": round(shadow_score - production_score, 2),
            "actual_t1": actual_t1,
        }
        candidate.shadow_result["shadow_scores"].append(shadow_score)
        candidate.shadow_result["production_scores"].append(production_score)
        candidate.shadow_result["days_completed"] += 1

        # 检查是否到期
        if candidate.shadow_result["days_completed"] >= self.SHADOW_DAYS:
            return self._finalize_shadow(candidate)

        self.registry._save()
        return {"status": "recorded", "day": candidate.shadow_result["days_completed"]}

    def _finalize_shadow(self, candidate) -> Dict:
        """Shadow 结束，生成对比报告"""
        result = candidate.shadow_result
        shadow_scores = result["shadow_scores"]
        production_scores = result["production_scores"]

        if not shadow_scores:
            result["shadow_status"] = "INCOMPLETE"
            result["reason"] = "无数据"
        else:
            # 简化评估：shadow 平均分 vs production 平均分
            avg_shadow = sum(shadow_scores) / len(shadow_scores)
            avg_prod = sum(production_scores) / len(production_scores)
            improvement = (avg_shadow - avg_prod) / avg_prod if avg_prod != 0 else 0

            result["diff_summary"] = {
                "avg_shadow_score": round(avg_shadow, 2),
                "avg_production_score": round(avg_prod, 2),
                "improvement_pct": round(improvement * 100, 1),
            }

            # 判定 PASS/FAIL
            # bootstrap 阶段：shadow 平均分高于生产 5% 算 PASS
            if improvement > 0.05:
                result["shadow_status"] = "PASS"
                # 升级为 ACTIVE 候选（不直接激活，等 Admission）
                candidate.status = LawStatus.DRAFT  # 保持 DRAFT，待 Roundtable
                result["recommendation"] = "可进入 Roundtable 评审"
            elif improvement < -0.05:
                result["shadow_status"] = "FAIL"
                candidate.status = LawStatus.WEAKENING
                result["recommendation"] = "直接进入 Weakening 流程"
            else:
                result["shadow_status"] = "INCONCLUSIVE"
                result["recommendation"] = "继续观察或调优"

        result["end_time"] = datetime.now().isoformat()
        self.registry._save()

        # 持久化
        shadow_file = SHADOW_DIR / f"shadow_{candidate_id}_final_{datetime.now().strftime('%Y%m%d')}.json"
        shadow_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        return result

    def list_shadow_candidates(self) -> List[Dict]:
        """列出所有进入 Shadow 的 candidate"""
        results = []
        for law in self.registry.candidates.values():
            if law.candidate_type == "signal_candidate" and law.shadow_result:
                results.append({
                    "candidate_id": law.law_id,
                    "shadow_status": law.shadow_result.get("shadow_status"),
                    "days_completed": law.shadow_result.get("days_completed", 0),
                    "replay_status": law.replay_result.get("replay_status") if law.replay_result else "N/A",
                })
        return results


def main():
    parser = argparse.ArgumentParser(description="Shadow Evaluation — 实时 5 天观察")
    parser.add_argument("--candidate", type=str, help="指定 candidate_id")
    parser.add_argument("--start", action="store_true", help="启动 Shadow")
    parser.add_argument("--record", action="store_true", help="记录一天观察")
    parser.add_argument("--shadow-score", type=float, help="今天 shadow 路径得分")
    parser.add_argument("--production-score", type=float, help="今天生产路径得分")
    parser.add_argument("--report", type=str, help="查看 candidate 的 shadow 报告")
    parser.add_argument("--list", action="store_true", help="列出所有 shadow candidate")
    args = parser.parse_args()

    shadow = ShadowEvaluation()

    if args.list:
        candidates = shadow.list_shadow_candidates()
        print(f"\n=== Shadow Candidates ({len(candidates)}) ===")
        for c in candidates:
            print(f"  {c['candidate_id']}: {c['shadow_status']} ({c['days_completed']}/5)")
            print(f"    Replay: {c['replay_status']}")
    elif args.start and args.candidate:
        result = shadow.start_shadow(args.candidate)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.record and args.candidate and args.shadow_score is not None and args.production_score is not None:
        result = shadow.record_daily_observation(
            args.candidate, args.shadow_score, args.production_score
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.report:
        law = shadow.registry.get_law(args.report)
        if law and law.shadow_result:
            print(json.dumps(law.shadow_result, ensure_ascii=False, indent=2))
        else:
            print(f"{args.report} 尚未运行 Shadow")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
