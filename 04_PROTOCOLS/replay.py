#!/usr/bin/env python3
"""
Offline Replay — 板块A' Deliverable 3 第一段

目的：用历史 2 个月数据回放，验证 Signal Candidate 是否有统计价值。
- 不影响生产（不调用 stock_advisor.run()）
- 不修改 AdaptiveScorer
- 复用 PerformanceTracker 的 K线数据 + observation_log
- 复用 LawRegistry 作为 Signal Candidate 存储

与 Shadow Evaluation 的区别：
- Replay：历史数据回放，回答"过去 2 个月这个 signal 表现如何"
- Shadow：实时运行 5 天，回答"这个 signal 在当前市场环境下表现如何"

Usage:
  python replay.py --candidate sig_candidate_capital_dominance
  python replay.py --all          # 跑所有 DRAFT 状态的 candidate
  python replay.py --days 60      # 指定回放天数（默认60）
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from law_discovery import LawRegistry, LawStatus


WORKSPACE = Path(__file__).parent.parent
ADVISOR_OUTPUT = WORKSPACE / "05_TOOLS" / "advisor" / "..\..\.." / "05_TOOLS" / "mine_output" / "advisor"
ADVISOR_OUTPUT = WORKSPACE / "05_TOOLS" / "mine_output" / "advisor"
EVIDENCE_DIR = WORKSPACE / "02_MEMORY" / "evidence"
REPLAY_DIR = EVIDENCE_DIR / "replay"
REPLAY_DIR.mkdir(parents=True, exist_ok=True)


class OfflineReplay:
    """Offline Replay Engine — 历史回放验证"""

    def __init__(self, days: int = 60):
        self.days = days
        self.registry = LawRegistry()

    def _load_observation_log(self) -> List[Dict]:
        """加载历史 observation_log（如有）
        板块A' 改造点：当前 observation_log 是调度层用的（target/worker_id），
        荐股 observation 需要从 trace.json 补全。
        """
        obs_log_path = WORKSPACE / "05_TOOLS" / "mine_output" / "observation_log.json"
        if obs_log_path.exists():
            try:
                data = json.loads(obs_log_path.read_text(encoding="utf-8"))
                return data.get("observations", [])
            except Exception:
                return []
        return []

    def _load_recommendation_history(self) -> List[Dict]:
        """从 trace.json 加载历史推荐 + 表现数据
        复用 stock_advisor.run() 输出的 trace.json
        """
        history = []
        # 找到所有 advisor_YYYYMMDD_trace.json
        pattern_files = list(WORKSPACE.glob("05_TOOLS/mine_output/advisor/advisor_*_trace.json"))

        for tf in pattern_files:
            try:
                trace = json.loads(tf.read_text(encoding="utf-8"))
                # 从 cco2_selection_trace 提取每只股票的入选信息
                for entry in trace.get("cco2_selection_trace", []):
                    history.append({
                        "date": trace.get("date", ""),
                        "code": entry.get("symbol", ""),
                        "name": entry.get("name", ""),
                        "layer1_reasons": entry.get("layer1_reasons", []),
                        "layer1_reject_flags": entry.get("layer1_reject_flags", []),
                        "layer2_reasons": entry.get("layer2_reasons", []),
                        "layer3_reasons": entry.get("layer3_reasons", []),
                        "final_score": entry.get("final_score", 0),
                    })
            except Exception:
                continue

        return history

    def _load_performance_data(self) -> Dict[str, Dict]:
        """从 performance_db.json 加载表现数据
        复用 PerformanceTracker 写入的数据
        """
        perf_file = WORKSPACE / "05_TOOLS" / "mine_output" / "advisor" / "performance_db.json"
        if not perf_file.exists():
            return {}

        try:
            data = json.loads(perf_file.read_text(encoding="utf-8"))
            return data
        except Exception:
            return {}

    def _signal_matches(self, sig_def: Dict, history_entry: Dict) -> bool:
        """判断历史推荐是否触发该 signal 条件

        简化实现：基于 layer1_reasons/layer2_reasons 关键词匹配
        bootstrap 阶段足够，后续可换真实数据源
        """
        conditions = sig_def.get("conditions", {})
        factor = conditions.get("factor", "")

        if not factor:
            return False

        # 简单关键词匹配（bootstrap 阶段足够）
        factor_keywords = {
            "capital_dominance": ["主力净流入", "main_inflow"],
            "fund_type_quality": ["北向", "north"],
            "limit_up_timing": ["涨停", "limit_up"],
            "seal_quality": ["封单", "seal"],
            "auction_premium": ["竞价", "auction"],
        }

        keywords = factor_keywords.get(factor, [factor])

        all_reasons = " ".join(
            history_entry.get("layer1_reasons", []) +
            history_entry.get("layer2_reasons", []) +
            history_entry.get("layer3_reasons", [])
        )

        return any(kw in all_reasons for kw in keywords)

    def replay_candidate(self, candidate_id: str) -> Dict[str, Any]:
        """回放单个 Signal Candidate"""
        candidate = self.registry.get_law(candidate_id)
        if not candidate:
            return {"error": f"Candidate {candidate_id} not found"}

        # 加载数据
        history = self._load_recommendation_history()
        perf = self._load_performance_data()

        if not history:
            replay_result = {
                "candidate_id": candidate_id,
                "replay_status": "INSUFFICIENT_DATA",
                "reason": "无历史推荐数据（需要至少运行 daily_runner.py 一段时间）",
                "evidence_count": 0,
            }
            self._save_replay(candidate, replay_result)
            return replay_result

        # 筛选符合 signal 条件的样本
        matched = [h for h in history if self._signal_matches(candidate.conditions, h)]

        # 统计表现
        results = []
        for entry in matched:
            perf_key = f"{entry['date']}_{entry['code']}"
            perf_data = perf.get(perf_key, {})
            if perf_data:
                results.append({
                    "date": entry["date"],
                    "code": entry["code"],
                    "return_t1": perf_data.get("return_t1"),
                    "return_t2": perf_data.get("return_t2"),
                    "return_t3": perf_data.get("return_t3"),
                    "return_t5": perf_data.get("return_t5"),
                })

        if not results:
            replay_result = {
                "candidate_id": candidate_id,
                "replay_status": "INSUFFICIENT_DATA",
                "reason": f"无匹配样本（{len(history)} 条历史中 0 条匹配 {candidate.conditions.get('factor', '')}）",
                "evidence_count": 0,
            }
            self._save_replay(candidate, replay_result)
            return replay_result

        # 评估指标
        t1_returns = [r["return_t1"] for r in results if r.get("return_t1") is not None]
        t2_returns = [r["return_t2"] for r in results if r.get("return_t2") is not None]
        t3_returns = [r["return_t3"] for r in results if r.get("return_t3") is not None]
        t5_returns = [r["return_t5"] for r in results if r.get("return_t5") is not None]

        def calc_stats(returns):
            if not returns:
                return None
            return {
                "count": len(returns),
                "win_rate": round(sum(1 for r in returns if r > 0) / len(returns) * 100, 1),
                "avg_return": round(sum(returns) / len(returns), 2),
                "max_drawdown": round(min(returns), 2),
            }

        stats = {
            "T+1": calc_stats(t1_returns),
            "T+2": calc_stats(t2_returns),
            "T+3": calc_stats(t3_returns),
            "T+5": calc_stats(t5_returns),
        }

        # 判断是否通过 bootstrap 门槛
        threshold = candidate.bootstrap_threshold
        pass_t3 = (stats.get("T+3") and
                   stats["T+3"]["count"] >= threshold.get("min_evidence", 30) and
                   stats["T+3"]["win_rate"] / 100 >= threshold.get("min_win_rate", 0.55))

        # 同时检查样本数门槛
        sample_sufficient = any(
            s and s["count"] >= threshold.get("min_evidence", 30)
            for s in stats.values() if s
        )

        replay_result = {
            "candidate_id": candidate_id,
            "replay_status": "PASS" if pass_t3 else ("SAMPLE_INSUFFICIENT" if not sample_sufficient else "FAIL"),
            "statement": candidate.statement,
            "matched_samples": len(matched),
            "evaluated_samples": len(results),
            "period_stats": stats,
            "threshold": threshold,
            "pass_t3_criteria": pass_t3,
            "replay_time": datetime.now().isoformat(),
            "replay_window_days": self.days,
        }

        # 写回 candidate
        candidate.replay_result = replay_result
        candidate.last_verified = datetime.now().isoformat()
        self.registry._save()

        # 持久化
        self._save_replay(candidate, replay_result)

        return replay_result

    def _save_replay(self, candidate, replay_result: Dict):
        """统一保存 Replay 结果（无论成功或 INSUFFICIENT_DATA）"""
        candidate.replay_result = replay_result
        candidate.last_verified = datetime.now().isoformat()
        self.registry._save()
        replay_file = REPLAY_DIR / f"replay_{candidate.law_id}_{datetime.now().strftime('%Y%m%d')}.json"
        replay_file.write_text(json.dumps(replay_result, ensure_ascii=False, indent=2), encoding="utf-8")

    def replay_all_drafts(self) -> List[Dict]:
        """回放所有 DRAFT 状态的 candidate"""
        candidates = [law for law in self.registry.candidates.values()
                     if law.candidate_type == "signal_candidate"]
        results = []
        for law in candidates:
            print(f"\n回放: {law.law_id}")
            r = self.replay_candidate(law.law_id)
            print(f"  状态: {r.get('replay_status')}")
            if "evaluated_samples" in r:
                print(f"  评估样本: {r['evaluated_samples']}")
                t3 = r.get("period_stats", {}).get("T+3", {})
                if t3:
                    print(f"  T+3 胜率: {t3.get('win_rate', 'N/A')}% / 平均收益: {t3.get('avg_return', 'N/A')}%")
            results.append(r)
        return results


def main():
    parser = argparse.ArgumentParser(description="Offline Replay — Signal Candidate 历史回放")
    parser.add_argument("--candidate", type=str, help="指定 candidate_id")
    parser.add_argument("--all", action="store_true", help="回放所有 DRAFT 状态的 candidate")
    parser.add_argument("--days", type=int, default=60, help="回放天数（默认60）")
    args = parser.parse_args()

    replay = OfflineReplay(days=args.days)

    if args.candidate:
        result = replay.replay_candidate(args.candidate)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.all:
        print("=== Offline Replay — All Draft Candidates ===")
        replay.replay_all_drafts()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
