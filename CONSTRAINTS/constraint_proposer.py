#!/usr/bin/env python3
"""
O→E→C→R 闭环：Constraint Proposer
从观察数据中自动提取 Task→Worker 约束提案

触发条件：某 task+worker 组合失败次数 >= threshold
输出：写入 routing_constraints.json (需人工确认后生效)

使用：python3 constraint_proposer.py [--threshold 3] [--auto-confirm]
"""
import json, os, sys, argparse
from collections import defaultdict
from datetime import datetime

OBSERVATION_FILE = "/home/coze/mine_output/observation_log.json"
CONSTRAINT_FILE = "/home/coze/routing_constraints.json"
THRESHOLD_DEFAULT = 3


# ==================== 反过拟合框架 (RFC-008) ====================
ANTI_OVERFIT_RULES = {
    "complexity_cap": {
        "description": "信号数量>=5自动降权，每多1个信号confidence扣10%",
        "signal_count_max": 5,
        "penalty_per_extra": 0.10
    },
    "temporal_decay": {
        "description": "信号IC计算时间>90天标注stale，decay_rate=0.02/天",
        "ic_stale_days": 90,
        "decay_rate": 0.02
    },
    "fragile_flag": {
        "description": "替换/移除1个信号后推荐结论改变则标注fragile",
        "perturbation_signals": 1,
        "conclusion_change_is_fragile": True
    }
}

def apply_complexity_penalty(signal_count: int, base_confidence: float = 1.0) -> tuple:
    """复杂度惩罚：信号越多，过拟合空间越大"""
    cap = ANTI_OVERFIT_RULES["complexity_cap"]["signal_count_max"]
    penalty = ANTI_OVERFIT_RULES["complexity_cap"]["penalty_per_extra"]
    if signal_count <= cap:
        return base_confidence, "OK"
    over = signal_count - cap
    adjusted = base_confidence * (1 - over * penalty)
    adjusted = max(0.1, adjusted)  # 最低0.1，不完全归零
    return adjusted, f"COMPLEX(signal_count={signal_count}>cap={cap}, penalty=-{over*penalty:.0%})"

def apply_temporal_decay(ic_value: float, days_since_verify: int) -> tuple:
    """时间衰减：旧IC不代表未来"""
    stale_days = ANTI_OVERFIT_RULES["temporal_decay"]["ic_stale_days"]
    decay_rate = ANTI_OVERFIT_RULES["temporal_decay"]["decay_rate"]
    if days_since_verify <= stale_days:
        return ic_value, "FRESH"
    over_days = days_since_verify - stale_days
    decayed_ic = ic_value * (1 - decay_rate * over_days)
    decayed_ic = max(0.0, decayed_ic)
    return decayed_ic, f"STALE(days={days_since_verify}, decayed_from={ic_value:.4f} to {decayed_ic:.4f})"

def check_fragile(signal_combo: list, original_conclusion: str, 
                  perturbation_fn=None) -> tuple:
    """扰动测试：移除1个信号后结论是否改变
    perturbation_fn: 可选的扰动函数，接收(signal_combo_without_one) -> conclusion
    如果没有提供扰动函数，仅标注待验证
    """
    n_remove = ANTI_OVERFIT_RULES["fragile_flag"]["perturbation_signals"]
    if perturbation_fn is None:
        return None, "PENDING(no_perturbation_fn)"
    
    for i in range(len(signal_combo)):
        perturbed = signal_combo[:i] + signal_combo[i+1:]
        try:
            perturbed_conclusion = perturbation_fn(perturbed)
            if perturbed_conclusion != original_conclusion:
                return True, f"FRAGILE(removing '{signal_combo[i]}' changes conclusion)"
        except Exception:
            continue
    
    return False, "ROBUST"

# ==================== 反过拟合框架 END ====================

def load_observations():
    if not os.path.exists(OBSERVATION_FILE):
        print("观察日志不存在")
        return []
    with open(OBSERVATION_FILE) as f:
        data = json.load(f)
    return data.get("observations", [])

def load_constraints():
    if os.path.exists(CONSTRAINT_FILE):
        with open(CONSTRAINT_FILE) as f:
            return json.load(f)
    return {"version": "1.0", "updated": "", "source": "auto", "rules": []}

def save_constraints(constraints):
    constraints["updated"] = datetime.now().isoformat()
    with open(CONSTRAINT_FILE, "w") as f:
        json.dump(constraints, f, ensure_ascii=False, indent=2)

def analyze_observations(observations, threshold=3):
    """从观察数据中提取失败组合统计"""
    pair_stats = defaultdict(lambda: {"success": 0, "fail": 0, "errors": []})
    
    for o in observations:
        task = o.get("task", "?")
        worker = o.get("worker_id", "?")
        key = (task, worker)
        if o.get("success"):
            pair_stats[key]["success"] += 1
        else:
            pair_stats[key]["fail"] += 1
            err = o.get("error", "")[:100]
            if err:
                pair_stats[key]["errors"].append(err)
    
    # 筛选达到阈值的失败组合
    proposals = []
    for (task, worker), stats in sorted(pair_stats.items(), key=lambda x: -x[1]["fail"]):
        if stats["fail"] >= threshold:
            total = stats["success"] + stats["fail"]
            fail_rate = stats["fail"] / total if total else 1.0
            
            # 错误类型统计
            error_summary = defaultdict(int)
            for e in stats["errors"]:
                if "timeout" in e.lower():
                    error_summary["timeout"] += 1
                elif "429" in e or "rate" in e.lower():
                    error_summary["rate_limit"] += 1
                elif "api_error" in e.lower() or "500" in e or "502" in e or "503" in e:
                    error_summary["api_error"] += 1
                else:
                    error_summary["other"] += 1
            
            # 反过拟合：如果该组合涉及复杂信号，应用复杂度惩罚
            signal_info = o.get("signal_combo", []) if isinstance(o, dict) else []
            if not signal_info:
                # 从观察数据中尝试提取信号信息
                for obs in observations:
                    if obs.get("task") == task and obs.get("worker_id") == worker:
                        sc = obs.get("signal_count", 0)
                        if sc > 0:
                            signal_info = ["x"] * sc
                            break
            
            proposals.append({
                "task": task,
                "worker": worker,
                "action": "AVOID",
                "confidence": "HIGH" if stats["fail"] >= 5 else "MEDIUM",
                "evidence": f"{stats['fail']} failures, {stats['success']} success, {dict(error_summary)}",
                "fail_rate": round(fail_rate, 3),
                "total_calls": total,
                "proposed_ts": datetime.now().isoformat(),
                "confirmed_ts": None,
                "auto_proposed": True,
            })
    
    return proposals

def run(threshold=3, auto_confirm=False):
    print(f"=== Constraint Proposer ===")
    print(f"阈值: 失败 >= {threshold} 次")
    print()
    
    observations = load_observations()
    print(f"观察记录: {len(observations)} 条")
    
    proposals = analyze_observations(observations, threshold)
    print(f"新提案: {len(proposals)} 条")
    print()
    
    if not proposals:
        print("没有新的约束提案")
        return
    
    # 显示提案
    for i, p in enumerate(proposals, 1):
        print(f"  [{i}] {p['task']} + {p['worker']}")
        print(f"      {p['evidence']}")
        print(f"      confidence: {p['confidence']}, fail_rate: {p['fail_rate']}")
        print()
    
    # 加载已有约束
    constraints = load_constraints()
    existing = {(r["task"], r["worker"]) for r in constraints.get("rules", [])}
    
    # 过滤已存在的
    new_rules = [p for p in proposals if (p["task"], p["worker"]) not in existing]
    print(f"新增约束: {len(new_rules)} 条 (跳过已有: {len(proposals) - len(new_rules)})")
    
    if not new_rules:
        print("所有提案已存在于约束文件中")
        return
    
    if auto_confirm:
        for rule in new_rules:
            rule["confirmed_ts"] = datetime.now().isoformat()
        constraints["rules"].extend(new_rules)
        save_constraints(constraints)
        print(f"已自动确认并写入 {CONSTRAINT_FILE}")
    else:
        print("\n需人工确认后才生效。运行时加 --auto-confirm 自动确认。")
        print("或手动编辑 routing_constraints.json 添加 confirmed_ts 字段。")
        # 输出待确认的提案到stdout
        for rule in new_rules:
            print(f"  PENDING: {rule['task']} + {rule['worker']} ({rule['evidence']})")




def check_signal_temporal_freshness(registry_path="/home/coze/mine_output/signals/signal_registry.json"):
    """检查信号库中哪些因子已过时，输出STALE警告"""
    if not os.path.exists(registry_path):
        return {"status": "no_registry", "stale_signals": []}
    
    with open(registry_path) as f:
        registry = json.load(f)
    
    from datetime import date
    today = date.today()
    stale_days = ANTI_OVERFIT_RULES["temporal_decay"]["ic_stale_days"]
    stale_signals = []
    
    for name, info in registry.get("signals", {}).items():
        last_verified = info.get("last_verified", "")
        if last_verified:
            try:
                verified_date = date.fromisoformat(last_verified)
                days_since = (today - verified_date).days
                if days_since > stale_days:
                    ic, flag = apply_temporal_decay(info.get("ic", 0), days_since)
                    stale_signals.append({
                        "signal": name,
                        "days_since_verify": days_since,
                        "original_ic": info.get("ic", 0),
                        "decayed_ic": round(ic, 4),
                        "flag": flag
                    })
            except ValueError:
                pass
    
    return {"status": "checked", "stale_count": len(stale_signals), "stale_signals": stale_signals}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="O→E→C→R Constraint Proposer")
    parser.add_argument("--threshold", type=int, default=THRESHOLD_DEFAULT, help="失败次数阈值")
    parser.add_argument("--auto-confirm", action="store_true", help="自动确认提案")
    parser.add_argument("--check-signals", action="store_true", help="检查信号库时间新鲜度")
    args = parser.parse_args()
    
    if args.check_signals:
        result = check_signal_temporal_freshness()
        print(f"=== 信号新鲜度检查 ===")
        print(f"状态: {result['status']}")
        if result.get('stale_signals'):
            print(f"过时信号: {result['stale_count']} 个")
            for s in result['stale_signals']:
                print(f"  ⚠️ {s['signal']}: {s['days_since_verify']}天未验证, IC {s['original_ic']}→{s['decayed_ic']} ({s['flag']})")
        else:
            print("所有信号在90天验证期内 ✅")
    else:
        run(threshold=args.threshold, auto_confirm=args.auto_confirm)


# ==================== 反永久化规则 (Anti-Permanent) ====================
def check_review_schedule(constraints_path=CONSTRAINT_FILE):
    """检查是否有规则到了review时间，需要重新评估"""
    if not os.path.exists(constraints_path):
        return []
    
    with open(constraints_path) as f:
        constraints = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    due_for_review = []
    
    for rule in constraints.get("rules", []):
        review_date = rule.get("review_schedule", "")
        review_status = rule.get("review_status", "ACTIVE")
        
        if review_status == "PARDONED":
            continue  # 已洗白，跳过
        
        if review_date and review_date <= today:
            due_for_review.append(rule)
    
    return due_for_review

def process_review(rule, recent_observations, constraints_path=CONSTRAINT_FILE):
    """处理一条到期规则的review
    
    逻辑：
    - 统计该task+worker在最近7天的表现
    - 成功率>=60% → PROBATION（观察期），review_date延后7天
    - 连续3次PROBATION通过 → PARDONED（洗白），从AVOID移除
    - 成功率<60% → 维持ACTIVE，review_date延后7天
    """
    task = rule["task"]
    worker = rule["worker"]
    
    # 统计最近7天该组合的表现
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    success = 0
    fail = 0
    
    for obs in recent_observations:
        if obs.get("task") == task and obs.get("worker_id") == worker:
            # 简单检查时间（如果obs有timestamp）
            ts = obs.get("timestamp", "")
            if ts and ts >= cutoff:
                if obs.get("success"):
                    success += 1
                else:
                    fail += 1
    
    total = success + fail
    success_rate = success / total if total > 0 else 0
    
    # 阈值
    with open(constraints_path) as f:
        constraints = json.load(f)
    anti_rule = constraints.get("anti_permanent_rule", {})
    threshold = anti_rule.get("probation_success_threshold", 0.6)
    pardon_passes = anti_rule.get("pardon_after_consecutive_passes", 3)
    
    new_review_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    if total == 0:
        # 没有新数据，延后review
        rule["review_schedule"] = new_review_date
        rule["review_note"] = "NO_DATA"
        return rule
    
    if success_rate >= threshold:
        rule["review_count"] = rule.get("review_count", 0) + 1
        if rule["review_count"] >= pardon_passes:
            rule["review_status"] = "PARDONED"
            rule["review_note"] = f"PARDONED(success_rate={success_rate:.0%}, consecutive_passes={rule['review_count']})"
            rule["action"] = "MONITOR"  # 从AVOID降级为MONITOR
        else:
            rule["review_status"] = "PROBATION"
            rule["review_note"] = f"PROBATION(success_rate={success_rate:.0%}, pass {rule['review_count']}/{pardon_passes})"
        rule["review_schedule"] = new_review_date
    else:
        rule["review_count"] = 0  # 重置连续通过计数
        rule["review_status"] = "ACTIVE"
        rule["review_note"] = f"ACTIVE(success_rate={success_rate:.0%}, still failing)"
        rule["review_schedule"] = new_review_date
    
    return rule
# ==================== 反永久化规则 END ====================
