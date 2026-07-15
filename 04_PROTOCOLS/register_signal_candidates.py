#!/usr/bin/env python3
"""
Register Signal Candidates — 板块A' Deliverable 2

注册 5 个 Signal Candidate 到 LawRegistry（复用现有治理结构）
- 不创建新的 Registry
- 不直接进 AdaptiveScorer
- 必须经过 Replay + Shadow + Roundtable + Admission

Usage:
  python register_signal_candidates.py            # 注册
  python register_signal_candidates.py --list     # 查看已注册
  python register_signal_candidates.py --reset    # 清空重新注册（仅 DRAFT 状态）
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from law_discovery import Law, LawStatus, LawRegistry


# 5 个 Signal Candidate 定义
# scope 明确"作用于哪一层"——避免与 E2C 调度层或 AdaptiveScorer 评分层混淆
SIGNAL_CANDIDATES = [
    {
        "law_id": "sig_candidate_capital_dominance",
        "statement": "资金主导度：买一/卖一席位资金比≥1.5为强势信号，连续3日主力净流入占比>30%的票T+3收益更稳",
        "conditions": {
            "factor": "capital_dominance",
            "buy_sell_ratio": ">= 1.5",  # 待校准（Bootstrap Threshold）
            "min_main_inflow_days": 3,
            "min_inflow_ratio": 0.30,     # 待校准
        },
        "expected_outcome": "T+3 胜率 >= 55%, avg_return >= 1%",
        "scope": {
            "layer": "layer1",
            "applies_to": "scoring",
            "not_applies_to": "scheduler",
        },
        "bootstrap_threshold": {
            "min_evidence": 30,
            "min_win_rate": 0.55,
            "min_avg_return": 1.0,
            "max_drawdown": 10.0,
        },
        "weakening_trigger": {
            "consecutive_decline_days": 20,
            "win_rate_floor": 0.40,
        },
        "evidence_source": "External Knowledge (游资席位数据经验规则), Not Verified",
    },
    {
        "law_id": "sig_candidate_fund_type_quality",
        "statement": "资金类型质量：区分机构净买入（延续性强）vs 游资净买入（单一游资独食次日高开低走概率高，需多路游资合力才是真信号）",
        "conditions": {
            "factor": "fund_type_quality",
            "institution_inflow": ">0",       # 机构净买入
            "multi_hot_money": ">= 2",         # 多路游资合力（待校准）
            "single_hot_money_risk": "HIGH",   # 单一游资独食风险
        },
        "expected_outcome": "T+3 胜率 >= 55%",
        "scope": {
            "layer": "layer1",
            "applies_to": "scoring",
            "not_applies_to": "scheduler",
        },
        "bootstrap_threshold": {
            "min_evidence": 30,
            "min_win_rate": 0.55,
        },
        "weakening_trigger": {
            "consecutive_decline_days": 20,
            "win_rate_floor": 0.40,
        },
        "evidence_source": "External Knowledge (A股资金面经验规则), Not Verified",
    },
    {
        "law_id": "sig_candidate_limit_up_timing",
        "statement": "涨停封板时间梯度：10点前封板=强抢筹信号，14点后封板=偷板嫌疑，午后涨停的延续性判断需结合封单质量",
        "conditions": {
            "factor": "limit_up_timing",
            "strong_limit_up_time": "< 10:00",     # 强抢筹
            "suspicious_limit_up_time": ">= 14:00",  # 偷板嫌疑
            "limit_up_strength": "hard_limit",
        },
        "expected_outcome": "T+1 胜率 >= 60%, T+3 胜率 >= 50%",
        "scope": {
            "layer": "layer2",
            "applies_to": "scoring",
            "not_applies_to": "scheduler",
        },
        "bootstrap_threshold": {
            "min_evidence": 30,
            "min_win_rate": 0.55,
        },
        "weakening_trigger": {
            "consecutive_decline_days": 20,
            "win_rate_floor": 0.40,
        },
        "evidence_source": "External Knowledge (涨停板实战经验), Not Verified",
    },
    {
        "law_id": "sig_candidate_seal_quality",
        "statement": "封单质量：封单金额/流通市值、封成比、撤单率综合评估，封单金额/流通市值>5%的票有更高突破概率",
        "conditions": {
            "factor": "seal_quality",
            "seal_amount_ratio": ">= 0.05",   # 待校准
            "seal_deal_ratio": "HIGH",         # 封成比
            "cancel_rate": "LOW",              # 撤单率
        },
        "expected_outcome": "T+3 胜率 >= 55%",
        "scope": {
            "layer": "layer2",
            "applies_to": "scoring",
            "not_applies_to": "scheduler",
        },
        "bootstrap_threshold": {
            "min_evidence": 30,
            "min_win_rate": 0.55,
        },
        "weakening_trigger": {
            "consecutive_decline_days": 20,
            "win_rate_floor": 0.40,
        },
        "evidence_source": "External Knowledge (封单质量经验规则), Not Verified",
    },
    {
        "law_id": "sig_candidate_auction_premium",
        "statement": "次日集合竞价溢价：1.5%-3%为游资接力标准区间，溢价过高(>3%)可能是诱多，过低(<0.5%)关注度不够",
        "conditions": {
            "factor": "auction_premium",
            "optimal_premium_range": [1.5, 3.0],    # 游资接力标准区间（待校准）
            "trap_premium": "> 3.0",                 # 诱多区间
            "low_interest_premium": "< 0.5",         # 关注度不够
        },
        "expected_outcome": "T+2 胜率 >= 55%, avg_return >= 0.5%",
        "scope": {
            "layer": "layer1",
            "applies_to": "scoring",
            "not_applies_to": "scheduler",
        },
        "bootstrap_threshold": {
            "min_evidence": 30,
            "min_win_rate": 0.55,
        },
        "weakening_trigger": {
            "consecutive_decline_days": 20,
            "win_rate_floor": 0.40,
        },
        "evidence_source": "External Knowledge (集合竞价实战经验), Not Verified",
    },
]


def register_candidates(reset: bool = False):
    """注册 5 个 Signal Candidate 到 LawRegistry"""
    registry = LawRegistry()

    if reset:
        # 仅清空 DRAFT 状态（防止误删已激活的 law）
        to_remove = [lid for lid, law in registry.candidates.items()
                     if law.candidate_type == "signal_candidate"]
        for lid in to_remove:
            del registry.candidates[lid]
        print(f"清空 {len(to_remove)} 个旧 signal candidate")

    registered = []
    skipped = []

    for sig_def in SIGNAL_CANDIDATES:
        # 检查是否已存在
        if sig_def["law_id"] in registry.laws or sig_def["law_id"] in registry.candidates:
            skipped.append(sig_def["law_id"])
            continue

        # 构造 Law 对象（作为 Signal Candidate）
        law = Law(
            law_id=sig_def["law_id"],
            timestamp=datetime.now().isoformat(),
            hypothesis_id="bootstrap_hypo",  # bootstrap 阶段暂无 hypothesis
            statement=sig_def["statement"],
            conditions=sig_def["conditions"],
            expected_outcome=sig_def["expected_outcome"],
            evidence_count=0,  # bootstrap 阶段无证据
            confidence=0.0,
            scope=sig_def["scope"],
            status=LawStatus.DRAFT,  # 候选状态
            created_time=datetime.now().isoformat(),
            last_verified=datetime.now().isoformat(),
            verification_count=0,
            # 板块A' 扩展字段
            candidate_type="signal_candidate",
            bootstrap_threshold=sig_def["bootstrap_threshold"],
            weakening_trigger=sig_def["weakening_trigger"],
            replay_result=None,
            shadow_result=None,
            version="v0.1-bootstrap",
            evidence_source=sig_def.get("evidence_source", ""),
        )

        if registry.register_law(law):
            registered.append(sig_def["law_id"])
            print(f"  ✓ 注册: {sig_def['law_id']}")
            print(f"     statement: {sig_def['statement'][:60]}")
            print(f"     scope: layer={sig_def['scope']['layer']}, applies_to={sig_def['scope']['applies_to']}")
        else:
            skipped.append(sig_def["law_id"])

    # 保存
    registry._save()

    print(f"\n=== 注册汇总 ===")
    print(f"新增: {len(registered)} 个")
    print(f"跳过: {len(skipped)} 个 (已存在)")
    print(f"状态: 全部为 DRAFT（未激活）")
    print(f"下一步: 启动 Offline Replay (replay.py --candidate <law_id>)")

    return registered, skipped


def list_candidates():
    """列出已注册的 Signal Candidate"""
    registry = LawRegistry()
    candidates = [law for law in registry.candidates.values()
                  if law.candidate_type == "signal_candidate"]

    if not candidates:
        print("尚未注册 Signal Candidate")
        return

    print(f"\n=== Signal Candidate Registry ({len(candidates)} 个) ===\n")
    for law in candidates:
        status_display = law.status.value if hasattr(law.status, 'value') else law.status
        print(f"📋 {law.law_id}")
        print(f"   状态: {status_display}")
        print(f"   描述: {law.statement[:60]}")
        print(f"   作用域: {law.scope}")
        print(f"   Bootstrap门槛: {law.bootstrap_threshold}")
        print(f"   弱化触发: {law.weakening_trigger}")
        print(f"   Replay结果: {'有' if law.replay_result else '无'}")
        print(f"   Shadow结果: {'有' if law.shadow_result else '无'}")
        print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Register Signal Candidates")
    parser.add_argument("--list", action="store_true", help="List registered candidates")
    parser.add_argument("--reset", action="store_true", help="Clear and re-register (DRAFT only)")
    args = parser.parse_args()

    if args.list:
        list_candidates()
    else:
        register_candidates(reset=args.reset)
