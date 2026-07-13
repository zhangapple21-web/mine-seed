#!/usr/bin/env python3
"""
Policy Manager — 策略管理器

管理荐股系统的策略生命周期：
  Candidate Policy → Roundtable → Admission → Approved Policy → Archived Policy

设计原则（遵循 AUM-MISSION-ADVISOR-001）：
  1. Learning 永远不能直接修改 Recommendation Engine
  2. Evidence First — 策略变更必须基于证据
  3. Policy 必须可回滚、可追溯、可审计
  4. Recommendation Immutable — 推荐记录不可修改

策略格式：
  {
    "policy_id": "POLICY-001",
    "version": 1,
    "status": "approved",
    "weights": {...},
    "rules": {...},
    "evidence": {...},
    "created_at": "...",
    "approved_at": "...",
    "applied_at": "...",
    "approved_by": "roundtable",
    "history": [...]
  }
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent))

LOG_DIR = Path(__file__).parent.parent / 'mine_output' / 'advisor'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'policy.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Policy:
    """策略数据结构"""
    policy_id: str
    version: int
    status: str  # draft / candidate / approved / archived
    weights: Dict[str, float]
    rules: Dict[str, Any]
    evidence: Dict[str, Any]
    created_at: str
    approved_at: Optional[str] = None
    applied_at: Optional[str] = None
    approved_by: Optional[str] = None
    history: List[Dict] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "Policy":
        return cls(**d)


class PolicyManager:
    """策略管理器"""

    POLICY_DIR = LOG_DIR / 'policies'
    CURRENT_POLICY_FILE = LOG_DIR / 'current_policy.json'
    ARCHIVE_FILE = LOG_DIR / 'policy_archive.json'

    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.current_policy: Optional[Policy] = None
        self._init_dirs()
        self._load_policies()
        self._load_current_policy()

    def _init_dirs(self):
        """初始化目录"""
        self.POLICY_DIR.mkdir(parents=True, exist_ok=True)

    def _load_policies(self):
        """加载所有历史策略"""
        if self.POLICY_DIR.exists():
            for policy_file in self.POLICY_DIR.glob('POLICY-*.json'):
                try:
                    data = json.loads(policy_file.read_text(encoding='utf-8'))
                    policy = Policy.from_dict(data)
                    self.policies[policy.policy_id] = policy
                except Exception as e:
                    logger.warning(f"加载策略失败 {policy_file}: {e}")

        if not self.policies:
            self._create_initial_policy()

    def _load_current_policy(self):
        """加载当前生效的策略"""
        if self.CURRENT_POLICY_FILE.exists():
            try:
                data = json.loads(self.CURRENT_POLICY_FILE.read_text(encoding='utf-8'))
                self.current_policy = Policy.from_dict(data)
                logger.info(f"当前策略: {self.current_policy.policy_id} v{self.current_policy.version}")
            except Exception as e:
                logger.warning(f"加载当前策略失败: {e}")

        if self.current_policy is None and self.policies:
            # 使用最新的 approved 策略
            approved = [p for p in self.policies.values() if p.status == 'approved']
            if approved:
                self.current_policy = sorted(approved, key=lambda p: p.approved_at or '', reverse=True)[0]

    def _create_initial_policy(self):
        """创建初始策略（默认权重）"""
        initial_weights = {
            "price_range": 15,
            "change_moderate": 25,
            "change_small": 10,
            "turnover_healthy": 20,
            "turnover_low_penalty": -5,
            "cap_mid_large": 15,
            "cap_small_penalty": -5,
            "pe_reasonable": 15,
            "pe_high_penalty": -5,
            "liquidity_ok": 10,
        }

        policy = Policy(
            policy_id="POLICY-001",
            version=1,
            status="approved",
            weights=initial_weights,
            rules={
                "min_score_threshold": 40,
                "max_stocks_per_day": 2,
                "diversity_required": True,
                "recent_dedup_days": 7,
                "consecutive_loss_threshold": 3,
                "win_rate_threshold": 50,
            },
            evidence={
                "source": "initial",
                "description": "系统启动时的默认策略配置",
            },
            created_at=datetime.now().isoformat(),
            approved_at=datetime.now().isoformat(),
            approved_by="system_init",
            applied_at=datetime.now().isoformat(),
        )

        self._save_policy(policy)
        self._save_current_policy(policy)
        logger.info("创建初始策略 POLICY-001")

    def _save_policy(self, policy: Policy):
        """保存策略文件"""
        policy_file = self.POLICY_DIR / f'{policy.policy_id}.json'
        policy_file.write_text(json.dumps(policy.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
        self.policies[policy.policy_id] = policy

    def _save_current_policy(self, policy: Policy):
        """保存当前生效策略"""
        self.CURRENT_POLICY_FILE.write_text(json.dumps(policy.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
        self.current_policy = policy

    def create_candidate_policy(self, new_weights: Dict[str, float],
                               evidence: Dict[str, Any],
                               reason: str = "") -> Policy:
        """
        创建候选策略（由 Learning System 调用）
        
        遵循原则：Learning 只生成 Candidate Policy，不直接修改推荐引擎
        """
        # 生成新策略 ID
        max_id = max(int(p.policy_id.split('-')[1]) for p in self.policies.values()) if self.policies else 0
        new_id = f"POLICY-{max_id + 1:03d}"

        # 获取当前策略的规则
        current_rules = self.current_policy.rules if self.current_policy else {}

        policy = Policy(
            policy_id=new_id,
            version=1,
            status="candidate",
            weights=new_weights,
            rules=current_rules,
            evidence={
                **evidence,
                "reason": reason,
                "generated_by": "learning_system",
                "generated_at": datetime.now().isoformat(),
            },
            created_at=datetime.now().isoformat(),
        )

        self._save_policy(policy)
        logger.info(f"创建候选策略 {new_id}: {reason}")

        return policy

    def get_candidate_policies(self) -> List[Policy]:
        """获取所有候选策略"""
        return [p for p in self.policies.values() if p.status == 'candidate']

    def roundtable_review(self, policy_id: str,
                         performance_summary: Dict,
                         factor_effectiveness: Dict) -> Dict[str, Any]:
        """
        Roundtable 评审 — 基于证据评估候选策略
        
        返回评审结果：是否通过、评审意见、风险评估
        """
        policy = self.policies.get(policy_id)
        if not policy or policy.status != 'candidate':
            return {"success": False, "error": "无效的候选策略"}

        review = {
            "policy_id": policy_id,
            "review_time": datetime.now().isoformat(),
            "reviewer": "roundtable",
            "performance_summary": performance_summary,
            "factor_effectiveness": factor_effectiveness,
            "analysis": {},
            "approved": False,
            "reason": "",
        }

        # 分析权重变化
        current_weights = self.current_policy.weights if self.current_policy else {}
        weight_changes = {}
        for factor, new_weight in policy.weights.items():
            old_weight = current_weights.get(factor, 0)
            diff = new_weight - old_weight
            if abs(diff) > 0.5:
                weight_changes[factor] = {"old": old_weight, "new": new_weight, "diff": diff}

        review["analysis"]["weight_changes"] = weight_changes

        # 评估变化合理性
        if len(weight_changes) == 0:
            review["approved"] = False
            review["reason"] = "权重无变化，无需更新策略"
            return review

        # 检查是否有严重的负向变化
        extreme_changes = [k for k, v in weight_changes.items() if abs(v["diff"]) > 10]
        if extreme_changes:
            review["analysis"]["risk_level"] = "high"
            review["analysis"]["extreme_changes"] = extreme_changes
            review["approved"] = False
            review["reason"] = f"检测到剧烈权重变化: {', '.join(extreme_changes)}，需要人工审查"
            return review

        # 基于证据评估
        avg_win_rate = performance_summary.get('win_rates', {}).get('T+5', 50)
        if avg_win_rate is not None and avg_win_rate < 40:
            review["analysis"]["risk_level"] = "medium"
            review["approved"] = True
            review["reason"] = f"当前胜率({avg_win_rate}%)较低，允许策略调整以尝试改进"
        else:
            review["analysis"]["risk_level"] = "low"
            review["approved"] = True
            review["reason"] = "策略变化温和且基于证据，自动批准"

        # 添加评审记录到策略历史
        policy.history.append({
            "event": "roundtable_review",
            "timestamp": datetime.now().isoformat(),
            "review": review,
        })

        return review

    def approve_policy(self, policy_id: str, review_result: Dict) -> bool:
        """
        批准策略（Admission 是唯一更新 Policy 的入口）
        
        遵循原则：Admission 是唯一允许更新 Policy 的入口
        """
        policy = self.policies.get(policy_id)
        if not policy or policy.status != 'candidate':
            logger.error(f"无法批准策略 {policy_id}: 状态不是 candidate")
            return False

        if not review_result.get('approved', False):
            logger.warning(f"策略 {policy_id} 未通过评审")
            policy.status = "rejected"
            policy.history.append({
                "event": "rejected",
                "timestamp": datetime.now().isoformat(),
                "reason": review_result.get('reason', ''),
            })
            self._save_policy(policy)
            return False

        # 更新策略状态
        policy.status = "approved"
        policy.approved_at = datetime.now().isoformat()
        policy.approved_by = review_result.get('reviewer', 'roundtable')
        policy.history.append({
            "event": "approved",
            "timestamp": datetime.now().isoformat(),
            "review": review_result,
        })

        # 归档旧策略
        if self.current_policy and self.current_policy.status == 'approved':
            self.archive_policy(self.current_policy.policy_id)

        # 设置为当前策略
        self._save_policy(policy)
        self._save_current_policy(policy)

        logger.info(f"策略 {policy_id} 已批准并生效")
        return True

    def apply_policy(self, policy_id: str) -> bool:
        """应用策略（设置为当前生效策略）"""
        policy = self.policies.get(policy_id)
        if not policy or policy.status != 'approved':
            logger.error(f"无法应用策略 {policy_id}: 状态不是 approved")
            return False

        # 归档旧策略
        if self.current_policy and self.current_policy.policy_id != policy_id:
            self.archive_policy(self.current_policy.policy_id)

        policy.applied_at = datetime.now().isoformat()
        policy.history.append({
            "event": "applied",
            "timestamp": datetime.now().isoformat(),
        })

        self._save_policy(policy)
        self._save_current_policy(policy)

        logger.info(f"策略 {policy_id} 已应用")
        return True

    def archive_policy(self, policy_id: str) -> bool:
        """归档策略"""
        policy = self.policies.get(policy_id)
        if not policy:
            return False

        policy.status = "archived"
        policy.history.append({
            "event": "archived",
            "timestamp": datetime.now().isoformat(),
        })

        self._save_policy(policy)
        logger.info(f"策略 {policy_id} 已归档")
        return True

    def rollback_policy(self, target_policy_id: str) -> bool:
        """
        回滚到指定策略（可回滚原则）
        
        遵循原则：Policy 必须可回滚
        """
        policy = self.policies.get(target_policy_id)
        if not policy:
            logger.error(f"回滚失败：策略 {target_policy_id} 不存在")
            return False

        if policy.status not in ['approved', 'archived']:
            logger.error(f"回滚失败：策略 {target_policy_id} 状态不允许回滚")
            return False

        # 恢复为 approved 状态
        policy.status = "approved"
        policy.applied_at = datetime.now().isoformat()
        policy.history.append({
            "event": "rollback",
            "timestamp": datetime.now().isoformat(),
            "rolled_back_from": self.current_policy.policy_id if self.current_policy else "none",
        })

        # 归档当前策略
        if self.current_policy:
            self.archive_policy(self.current_policy.policy_id)

        # 应用回滚策略
        self._save_policy(policy)
        self._save_current_policy(policy)

        logger.info(f"已回滚到策略 {target_policy_id}")
        return True

    def get_current_weights(self) -> Dict[str, float]:
        """获取当前生效的权重配置"""
        if self.current_policy:
            return self.current_policy.weights.copy()
        return {}

    def get_current_rules(self) -> Dict[str, Any]:
        """获取当前生效的规则配置"""
        if self.current_policy:
            return self.current_policy.rules.copy()
        return {}

    def get_policy_history(self, policy_id: str) -> List[Dict]:
        """获取策略的完整历史记录（可追溯原则）"""
        policy = self.policies.get(policy_id)
        if not policy:
            return []
        return policy.history.copy()

    def get_all_policies(self) -> List[Policy]:
        """获取所有策略列表"""
        return sorted(self.policies.values(), key=lambda p: p.created_at)

    def generate_audit_report(self) -> Dict[str, Any]:
        """
        生成审计报告（可审计原则）
        
        返回所有策略变更的完整审计记录
        """
        report = {
            "report_time": datetime.now().isoformat(),
            "current_policy": self.current_policy.policy_id if self.current_policy else None,
            "total_policies": len(self.policies),
            "policies": [],
            "change_summary": {},
        }

        for policy in sorted(self.policies.values(), key=lambda p: p.created_at):
            policy_info = {
                "policy_id": policy.policy_id,
                "version": policy.version,
                "status": policy.status,
                "created_at": policy.created_at,
                "approved_at": policy.approved_at,
                "applied_at": policy.applied_at,
                "approved_by": policy.approved_by,
                "event_count": len(policy.history),
            }
            report["policies"].append(policy_info)

            # 统计变更类型
            for event in policy.history:
                event_type = event.get('event', '')
                report["change_summary"][event_type] = report["change_summary"].get(event_type, 0) + 1

        return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Policy Manager")
    parser.add_argument("--list", action="store_true", help="List all policies")
    parser.add_argument("--current", action="store_true", help="Show current policy")
    parser.add_argument("--audit", action="store_true", help="Generate audit report")
    parser.add_argument("--rollback", type=str, help="Rollback to policy ID")
    args = parser.parse_args()

    pm = PolicyManager()

    if args.list:
        policies = pm.get_all_policies()
        for p in policies:
            print(f"{p.policy_id} v{p.version} | {p.status} | {p.created_at[:19]}")

    if args.current:
        if pm.current_policy:
            print(json.dumps({
                "policy_id": pm.current_policy.policy_id,
                "status": pm.current_policy.status,
                "weights": pm.current_policy.weights,
                "rules": pm.current_policy.rules,
                "applied_at": pm.current_policy.applied_at,
            }, ensure_ascii=False, indent=2))
        else:
            print("No current policy")

    if args.audit:
        report = pm.generate_audit_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.rollback:
        success = pm.rollback_policy(args.rollback)
        print(f"Rollback {'success' if success else 'failed'}")

    if not any([args.list, args.current, args.audit, args.rollback]):
        parser.print_help()


if __name__ == "__main__":
    main()