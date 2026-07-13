#!/usr/bin/env python3
"""
Advisor Tracker — 荐股追踪器
==============================

核心功能:
  1. 汇总所有 lineage JSON 到统一追踪文件
  2. 多周期复核: T+1 / T+7 / T+15 / T+30
  3. 胜率统计持久化 (不再只打印到 stdout)
  4. 生成胜率报告 (JSON + Markdown)

复核周期:
  - T+1:  次日收盘价 (已有 lineage_review.py 的逻辑)
  - T+7:  1周后收盘价
  - T+15: 半个月后收盘价
  - T+30: 1个月后收盘价

胜率定义:
  - 单条胜: return_pct > 0
  - 周期胜率: wins / total * 100%

输出:
  02_MEMORY/advisor_tracker/
    ├── tracker.json          — 所有荐股记录汇总
    ├── review_log.json       — 复核日志
    ├── win_rate_report.json  — 胜率统计
    └── win_rate_report.md    — 胜率报告 (人读)
"""
import json, sys, os, argparse
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

WORKSPACE = Path(__file__).parent.parent.parent
ADVISOR_DIR = WORKSPACE / "05_TOOLS" / "mine_output" / "advisor"
TRACKER_DIR = WORKSPACE / "02_MEMORY" / "advisor_tracker"
TRACKER_DIR.mkdir(parents=True, exist_ok=True)

# 复核周期 (交易日)
REVIEW_PERIODS = {
    "T+1": 1,
    "T+7": 7,
    "T+15": 15,
    "T+30": 30,
}

# 追踪文件路径
TRACKER_FILE = TRACKER_DIR / "tracker.json"
WIN_RATE_FILE = TRACKER_DIR / "win_rate_report.json"
WIN_RATE_MD = TRACKER_DIR / "win_rate_report.md"


class AdvisorTracker:
    """荐股追踪器"""

    def __init__(self):
        from trading_calendar import get_calendar
        self.cal = get_calendar()
        self.tracker = self._load_tracker()

    def _load_tracker(self) -> Dict[str, Any]:
        """加载追踪文件"""
        if TRACKER_FILE.exists():
            return json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
        return {"records": {}, "last_updated": None}

    def _save_tracker(self):
        """保存追踪文件"""
        self.tracker["last_updated"] = datetime.now().isoformat()
        TRACKER_FILE.write_text(
            json.dumps(self.tracker, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load_lineage_files(self) -> List[Dict[str, Any]]:
        """加载所有 lineage JSON 文件"""
        files = sorted(ADVISOR_DIR.glob("advisor_*_lineage.json"))
        lineages = []
        for f in files:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["_file"] = str(f)
                lineages.append(data)
            except Exception:
                pass
        return lineages

    def sync_records(self):
        """从 lineage JSON 同步记录到 tracker"""
        lineages = self.load_lineage_files()
        records = self.tracker.setdefault("records", {})
        new_count = 0

        for lin in lineages:
            date_str = lin.get("date", "")
            for rec in lin.get("recommendations", []):
                rec_id = rec.get("recommendation_id", "")
                if not rec_id:
                    continue

                # 新记录
                if rec_id not in records:
                    records[rec_id] = {
                        "recommendation_id": rec_id,
                        "date": date_str,
                        "ticker": rec.get("ticker"),
                        "recommend_price": rec.get("recommend_price"),
                        "signal_combo": rec.get("signal_combo", []),
                        "snapshot_time": rec.get("snapshot_time"),
                        "reviews": {},  # T+1, T+7, T+15, T+30
                    }
                    new_count += 1

                # 同步已有的复核结果
                existing = records[rec_id]
                if rec.get("close_price") and rec.get("review_status") == "completed":
                    # 从 lineage 同步 T+1 复核
                    if "T+1" not in existing["reviews"]:
                        existing["reviews"]["T+1"] = {
                            "close_price": rec.get("close_price"),
                            "return_pct": rec.get("return_pct"),
                            "reviewed_at": datetime.now().isoformat(),
                        }

        self._save_tracker()
        return new_count

    def get_price(self, ticker: str) -> Optional[float]:
        """获取最新价格（使用多数据源）"""
        try:
            from multi_data_source import DataSourceManager
            dsm = DataSourceManager()

            if ticker.startswith('6') or ticker.startswith('68'):
                full_code = f"sh{ticker}"
            elif ticker.startswith('0') or ticker.startswith('3'):
                full_code = f"sz{ticker}"
            else:
                full_code = f"sz{ticker}"

            quotes = dsm.get_quotes([full_code])
            if quotes and len(quotes) > 0:
                return float(quotes[0].get("price", 0))
        except Exception:
            pass
        return None

    def review_pending(self, dry_run: bool = False) -> Dict[str, Any]:
        """复核所有需要更新的记录

        对每条记录检查:
        - T+1: 推荐日 + 1 交易日后的收盘价
        - T+7: 推荐日 + 7 交易日后的收盘价
        - T+15: 推荐日 + 15 交易日后的收盘价
        - T+30: 推荐日 + 30 交易日后的收盘价
        """
        records = self.tracker.get("records", {})
        today = date.today()
        reviewed = []
        skipped = []

        for rec_id, rec in records.items():
            rec_date_str = rec.get("date", "")
            if not rec_date_str:
                continue
            try:
                rec_date = datetime.strptime(rec_date_str, "%Y%m%d").date()
            except Exception:
                continue

            rec_price = rec.get("recommend_price")
            if not rec_price:
                continue

            ticker = rec.get("ticker")
            if not ticker:
                continue

            # 检查每个周期
            for period_name, period_days in REVIEW_PERIODS.items():
                if period_name in rec["reviews"]:
                    continue  # 已复核

                # 计算目标日期 (推荐日 + N 交易日)
                target_date = rec_date
                for _ in range(period_days):
                    target_date = self.cal.next_trading_day(target_date)

                # 如果目标日期还没到，跳过
                if target_date > today:
                    skipped.append({
                        "rec_id": rec_id,
                        "period": period_name,
                        "target_date": target_date.isoformat(),
                        "reason": "not yet"
                    })
                    continue

                # 如果今天是目标日期或之后，但还没复核，获取价格
                if dry_run:
                    reviewed.append({
                        "rec_id": rec_id,
                        "period": period_name,
                        "target_date": target_date.isoformat(),
                        "would_review": True
                    })
                    continue

                # 获取最新价格
                price = self.get_price(ticker)
                if price and price > 0:
                    return_pct = round(
                        (price - rec_price) / rec_price * 100, 2
                    )
                    rec["reviews"][period_name] = {
                        "close_price": price,
                        "return_pct": return_pct,
                        "reviewed_at": datetime.now().isoformat(),
                        "target_date": target_date.isoformat(),
                    }
                    reviewed.append({
                        "rec_id": rec_id,
                        "period": period_name,
                        "target_date": target_date.isoformat(),
                        "close_price": price,
                        "return_pct": return_pct,
                    })
                else:
                    skipped.append({
                        "rec_id": rec_id,
                        "period": period_name,
                        "reason": "price fetch failed"
                    })

        self._save_tracker()
        return {"reviewed": reviewed, "skipped": skipped}

    def generate_win_rate_report(self) -> Dict[str, Any]:
        """生成胜率报告"""
        records = self.tracker.get("records", {})
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_records": len(records),
            "periods": {},
        }

        for period_name in REVIEW_PERIODS:
            completed = []
            for rec in records.values():
                review = rec.get("reviews", {}).get(period_name)
                if review and review.get("return_pct") is not None:
                    completed.append({
                        "rec_id": rec["recommendation_id"],
                        "ticker": rec["ticker"],
                        "date": rec["date"],
                        "recommend_price": rec["recommend_price"],
                        "close_price": review["close_price"],
                        "return_pct": review["return_pct"],
                        "signal_combo": rec.get("signal_combo", []),
                    })

            if not completed:
                report["periods"][period_name] = {
                    "total": 0,
                    "wins": 0,
                    "losses": 0,
                    "win_rate": 0,
                    "avg_return": 0,
                    "best_return": 0,
                    "worst_return": 0,
                }
                continue

            returns = [c["return_pct"] for c in completed]
            wins = sum(1 for r in returns if r > 0)
            losses = sum(1 for r in returns if r <= 0)

            report["periods"][period_name] = {
                "total": len(completed),
                "wins": wins,
                "losses": losses,
                "win_rate": round(wins / len(completed) * 100, 1),
                "avg_return": round(sum(returns) / len(returns), 2),
                "best_return": max(returns),
                "worst_return": min(returns),
                "details": completed,
            }

        # 保存 JSON
        WIN_RATE_FILE.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        # 生成 Markdown
        self._generate_markdown_report(report)

        return report

    def _generate_markdown_report(self, report: Dict[str, Any]):
        """生成 Markdown 胜率报告"""
        lines = [
            f"# 荐股胜率报告",
            f"",
            f"生成时间: {report['generated_at'][:19]}",
            f"总荐股数: {report['total_records']}",
            f"",
            f"## 各周期胜率",
            f"",
            f"| 周期 | 样本数 | 胜 | 负 | 胜率 | 平均收益 | 最佳 | 最差 |",
            f"|------|--------|---|---|------|----------|------|------|",
        ]

        for period_name in REVIEW_PERIODS:
            p = report["periods"].get(period_name, {})
            lines.append(
                f"| {period_name} | {p.get('total', 0)} | "
                f"{p.get('wins', 0)} | {p.get('losses', 0)} | "
                f"{p.get('win_rate', 0)}% | "
                f"{p.get('avg_return', 0):+.2f}% | "
                f"{p.get('best_return', 0):+.2f}% | "
                f"{p.get('worst_return', 0):+.2f}% |"
            )

        lines.append("")

        # 详细记录
        for period_name in REVIEW_PERIODS:
            p = report["periods"].get(period_name, {})
            details = p.get("details", [])
            if not details:
                continue

            lines.append(f"## {period_name} 详细记录")
            lines.append("")
            lines.append("| 日期 | 代码 | 推荐价 | 收盘价 | 收益 | 信号 |")
            lines.append("|------|------|--------|--------|------|------|")
            for d in details:
                signals = ", ".join(d.get("signal_combo", []))[:30]
                lines.append(
                    f"| {d['date']} | {d['ticker']} | "
                    f"¥{d['recommend_price']} | ¥{d['close_price']} | "
                    f"{d['return_pct']:+.2f}% | {signals} |"
                )
            lines.append("")

        # 分析建议
        lines.append("## 分析建议")
        lines.append("")

        # 比较 T+1 vs T+7 vs T+30 胜率趋势
        t1 = report["periods"].get("T+1", {}).get("win_rate", 0)
        t7 = report["periods"].get("T+7", {}).get("win_rate", 0)
        t30 = report["periods"].get("T+30", {}).get("win_rate", 0)

        if t1 > 0 or t7 > 0 or t30 > 0:
            if t30 > t7 > t1:
                lines.append("- 胜率随周期提升, 说明选股逻辑在中长期更有效")
            elif t1 > t7 > t30:
                lines.append("- 胜率随周期下降, 说明选股逻辑偏向短线, 需关注持仓周期")
            elif t1 < 50:
                lines.append("- T+1 胜率低于 50%, 建议检查入场时机选择")
            else:
                lines.append("- 胜率稳定, 继续保持当前策略")

            # 找出亏损的信号组合
            all_details = []
            for p_name in REVIEW_PERIODS:
                all_details.extend(
                    report["periods"].get(p_name, {}).get("details", [])
                )
            loss_signals = {}
            for d in all_details:
                if d["return_pct"] < 0:
                    for s in d.get("signal_combo", []):
                        loss_signals[s] = loss_signals.get(s, 0) + 1
            if loss_signals:
                sorted_losses = sorted(loss_signals.items(), key=lambda x: -x[1])[:3]
                lines.append(f"- 亏损中出现频率最高的信号: {', '.join(f'{s}({c}次)' for s, c in sorted_losses)}")

        lines.append("")

        WIN_RATE_MD.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Advisor Tracker")
    parser.add_argument("--sync", action="store_true", help="同步 lineage 文件")
    parser.add_argument("--review", action="store_true", help="复核待检查记录")
    parser.add_argument("--report", action="store_true", help="生成胜率报告")
    parser.add_argument("--dry-run", action="store_true", help="只看不改")
    args = parser.parse_args()

    tracker = AdvisorTracker()

    if args.sync:
        new_count = tracker.sync_records()
        print(f"同步完成: {new_count} 条新记录")

    if args.review:
        result = tracker.review_pending(dry_run=args.dry_run)
        print(f"复核完成: {len(result['reviewed'])} 条已复核, {len(result['skipped'])} 条跳过")
        for r in result["reviewed"][:5]:
            print(f"  ✓ {r['rec_id']} {r['period']}: {r.get('return_pct', '?')}%")

    if args.report:
        report = tracker.generate_win_rate_report()
        print(f"\n胜率报告已生成:")
        print(f"  JSON: {WIN_RATE_FILE}")
        print(f"  MD:   {WIN_RATE_MD}")
        print(f"\n总荐股数: {report['total_records']}")
        for period_name in REVIEW_PERIODS:
            p = report["periods"].get(period_name, {})
            print(f"  {period_name}: {p.get('wins', 0)}/{p.get('total', 0)} = {p.get('win_rate', 0)}% "
                  f"(平均 {p.get('avg_return', 0):+.2f}%)")

    if not any([args.sync, args.review, args.report]):
        # 默认执行全部
        new_count = tracker.sync_records()
        print(f"同步: {new_count} 条新记录")
        result = tracker.review_pending(dry_run=args.dry_run)
        print(f"复核: {len(result['reviewed'])} 条已复核, {len(result['skipped'])} 条跳过")
        report = tracker.generate_win_rate_report()
        print(f"\n胜率报告:")
        for period_name in REVIEW_PERIODS:
            p = report["periods"].get(period_name, {})
            print(f"  {period_name}: {p.get('wins', 0)}/{p.get('total', 0)} = {p.get('win_rate', 0)}%")


if __name__ == "__main__":
    main()
