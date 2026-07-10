#!/usr/bin/env python3
"""
O→E→C Auto-Sync Module
自动将experience_engine.compress()产生的新规则同步到routing_constraints.json

集成方式：在experience_engine.py的compress()末尾调用 sync_to_constraints()
"""
import json
import os
from datetime import datetime

CONSTRAINTS_PATH = "/home/coze/routing_constraints.json"
EXPERIENCE_PATH = "/home/coze/mine_output/experience.json"


def sync_to_constraints(experience_path=EXPERIENCE_PATH, 
                        constraints_path=CONSTRAINTS_PATH, 
                        dry_run=False):
    """
    从experience.json的routing_rules同步新规则到routing_constraints.json
    
    返回: (new_count, skipped_count, details)
    """
    if not os.path.exists(experience_path):
        return 0, 0, ["experience.json not found"]
    
    with open(experience_path) as f:
        exp = json.load(f)
    
    exp_rules = exp.get("routing_rules", [])
    if not exp_rules:
        return 0, 0, ["no routing_rules in experience"]
    
    if not os.path.exists(constraints_path):
        return 0, 0, ["routing_constraints.json not found"]
    
    with open(constraints_path) as f:
        constraints = json.load(f)
    
    existing_rules = constraints.get("rules", [])
    
    # 构建已有规则索引: (worker, task_pattern) -> rule
    existing_index = {}
    for r in existing_rules:
        key = (r.get("worker", ""), r.get("task_pattern", ""))
        existing_index[key] = r
    
    new_rules = []
    skipped = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for exp_rule in exp_rules:
        worker = exp_rule.get("worker", "")
        pattern = exp_rule.get("task_pattern", "")
        action = exp_rule.get("action", "AVOID")
        key = (worker, pattern)
        
        # 反过拟合检查：同一worker+pattern已有规则则跳过
        if key in existing_index:
            existing = existing_index[key]
            if existing.get("status") in ("ACTIVE", "REVIEW", "PENDING_REVIEW"):
                skipped.append(f"skip {worker}+{pattern}: already {existing.get('status')}")
                continue
            # DISABLED规则允许复活
            if existing.get("status") == "DISABLED":
                existing["status"] = "PENDING_REVIEW"
                existing["updated_date"] = today
                existing["source"] = "experience_auto_resurrect"
                skipped.append(f"resurrect {worker}+{pattern}: DISABLED->PENDING_REVIEW")
                continue
        
        # 新增规则（不直接ACTIVE，先PENDING_REVIEW观察）
        new_rule = {
            "worker": worker,
            "task_pattern": pattern,
            "action": action,
            "confidence": exp_rule.get("confidence", 0.5),
            "sample_count": exp_rule.get("sample_count", 1),
            "status": "PENDING_REVIEW",
            "created_date": today,
            "updated_date": today,
            "source": "experience_auto",
            "anti_overfit": {
                "days_active": 0,
                "success_rate_since_activate": None,
                "review_date": None
            }
        }
        new_rules.append(new_rule)
        existing_index[key] = new_rule
    
    if not new_rules and not skipped:
        return 0, 0, ["no new rules to sync"]
    
    # 写入constraints
    all_rules = existing_rules + new_rules
    constraints["rules"] = all_rules
    constraints["updated_date"] = today
    
    # 版本自增
    version_str = constraints.get("version", "2.3")
    try:
        major, minor = version_str.split(".")
        constraints["version"] = f"{major}.{int(minor)+1}"
    except Exception:
        constraints["version"] = "2.4"
    
    if not dry_run:
        with open(constraints_path, "w") as f:
            json.dump(constraints, f, indent=2, ensure_ascii=False)
    
    details = [f"added: {r['worker']}+{r['task_pattern']}={r['action']}" for r in new_rules]
    details.extend(skipped)
    
    return len(new_rules), len(skipped), details


if __name__ == "__main__":
    import sys
    dry = "--dry-run" in sys.argv
    new, skipped, details = sync_to_constraints(dry_run=dry)
    print(f"New: {new}, Skipped: {skipped}")
    for d in details:
        print(f"  {d}")
