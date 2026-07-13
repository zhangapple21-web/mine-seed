"""---
id: PROTO-012
type: protocol
title: "Self-Learning Engine — 自学习引擎"
status: active
source: "Chip Huyen ML System Design + R2 Evolution"
created: 2026-07-12
confidence: 0.75
lineage:
  - OPS-005
  - PROTO-004
  - PROTO-011
related: [PROTO-004, PROTO-009, PROTO-011]
tags: [learning, evolution, experience, hypothesis]
archaeology:
  state: new
---
"""
#!/usr/bin/env python3
# TYPE: runtime
# Implements: OPS-005 (Self-Loop)
"""
SLE-001: Self-Learning Engine — 自学习引擎
============================================

核心思想（来自 Chip Huyen "Designing Machine Learning Systems"）:
  系统永远不会"完成"，只有部署、监控、持续迭代。
  ML 生产 = 75% 数据 + 25% 模型。
  漂移不可避免 — 必须持续学习。

ACE 系统的"学习"不是训练神经网络，而是系统级的持续演化:
  Experience → Pattern Extraction → Hypothesis Generation
  → Low-Risk Experiment → Validation → New Experience

执行语义:
  1. 扫描经验库，提取成功/失败模式
  2. 生成改进假设（Hypothesis）
  3. 选择低风险假设进行实验
  4. 验证实验结果
  5. 沉淀新经验，形成闭环

安全原则:
  1. 只在白名单范围内自动执行
  2. 高风险假设只生成建议，不自动执行
  3. 所有变更可回滚
  4. 学习结果写入 Experience，不直接改代码
"""
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

WORKSPACE = Path(__file__).parent.parent
EXPERIENCE_DIR = WORKSPACE / "02_MEMORY" / "experience"
HYPOTHESIS_DIR = WORKSPACE / "02_MEMORY" / "question_center"
LEARNING_DIR = WORKSPACE / "02_MEMORY" / "self_learning"
LEARNING_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Pattern Library — 模式库
# ============================================================

FAILURE_PATTERNS = {
    "provider_rate_limit": {
        "name": "Provider 限流",
        "keywords": ["rate limit", "rate_limit", "429", "限流", "too many requests"],
        "severity": "medium",
        "suggested_actions": [
            "降低该 Provider 的并发请求数",
            "增加重试间隔",
            "切换到备用 Provider",
        ],
    },
    "provider_timeout": {
        "name": "Provider 超时",
        "keywords": ["timeout", "超时", "timed out", "connection error", "连接超时"],
        "severity": "medium",
        "suggested_actions": [
            "增加超时时间",
            "添加降级 fallback",
            "检查网络状态",
        ],
    },
    "provider_auth_failure": {
        "name": "Provider 认证失败",
        "keywords": ["auth", "unauthorized", "401", "403", "认证失败", "invalid key"],
        "severity": "high",
        "suggested_actions": [
            "检查 API Key 配置",
            "切换备用凭证",
            "标记 Provider 为不可用",
        ],
    },
    "memory_dead_ratio": {
        "name": "记忆死亡比例过高",
        "keywords": ["dead", "死亡", "access_count=0", "未访问"],
        "severity": "low",
        "suggested_actions": [
            "激活沉睡记忆",
            "建立记忆索引关联",
            "清理僵尸记忆",
        ],
    },
    "repeated_failure": {
        "name": "重复失败",
        "keywords": ["retry", "重试", "failed again", "再次失败"],
        "severity": "high",
        "suggested_actions": [
            "分析失败根因",
            "调整重试策略",
            "添加熔断机制",
        ],
    },
}

SUCCESS_PATTERNS = {
    "fallback_chain_works": {
        "name": "降级链路生效",
        "keywords": ["fallback", "降级", "switched to", "切换到备用", "备用生效"],
        "value": "high",
        "reinforce": [
            "保持降级链路配置",
            "扩展更多 Provider 的 fallback",
        ],
    },
    "recovery_success": {
        "name": "恢复成功",
        "keywords": ["recovered", "恢复成功", "restored", "修复成功"],
        "value": "high",
        "reinforce": [
            "记录恢复路径",
            "优化恢复流程",
        ],
    },
    "new_discovery": {
        "name": "新发现",
        "keywords": ["discovery", "发现", "new insight", "新洞察", "insight"],
        "value": "medium",
        "reinforce": [
            "沉淀为知识",
            "关联到相关概念",
        ],
    },
}


class PatternExtractor:
    """从经验库中提取模式"""

    def __init__(self):
        self.experiences = []

    def load_experiences(self, limit: int = 50) -> List[Dict[str, Any]]:
        """加载经验文件"""
        if not EXPERIENCE_DIR.exists():
            return []

        exp_files = sorted(
            EXPERIENCE_DIR.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )[:limit]

        experiences = []
        for f in exp_files:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    exp = json.load(fp)
                    exp["_file"] = str(f)
                    experiences.append(exp)
            except Exception:
                continue

        self.experiences = experiences
        return experiences

    def extract_failure_patterns(self) -> List[Dict[str, Any]]:
        """提取失败模式"""
        results = []

        for pattern_id, pattern in FAILURE_PATTERNS.items():
            matches = []
            for exp in self.experiences:
                exp_text = json.dumps(exp, ensure_ascii=False).lower()
                hit_count = sum(
                    1 for kw in pattern["keywords"] if kw.lower() in exp_text
                )
                if hit_count > 0:
                    matches.append({
                        "exp_id": exp.get("id", exp.get("_file", "unknown")),
                        "hit_keywords": hit_count,
                        "title": exp.get("title", ""),
                    })

            if matches:
                results.append({
                    "pattern_id": pattern_id,
                    "name": pattern["name"],
                    "severity": pattern["severity"],
                    "occurrences": len(matches),
                    "recent_examples": matches[:3],
                    "suggested_actions": pattern["suggested_actions"],
                })

        results.sort(key=lambda x: x["occurrences"], reverse=True)
        return results

    def extract_success_patterns(self) -> List[Dict[str, Any]]:
        """提取成功模式"""
        results = []

        for pattern_id, pattern in SUCCESS_PATTERNS.items():
            matches = []
            for exp in self.experiences:
                exp_text = json.dumps(exp, ensure_ascii=False).lower()
                hit_count = sum(
                    1 for kw in pattern["keywords"] if kw.lower() in exp_text
                )
                if hit_count > 0:
                    matches.append({
                        "exp_id": exp.get("id", exp.get("_file", "unknown")),
                        "hit_keywords": hit_count,
                        "title": exp.get("title", ""),
                    })

            if matches:
                results.append({
                    "pattern_id": pattern_id,
                    "name": pattern["name"],
                    "value": pattern["value"],
                    "occurrences": len(matches),
                    "recent_examples": matches[:3],
                    "reinforce": pattern["reinforce"],
                })

        results.sort(key=lambda x: x["occurrences"], reverse=True)
        return results

    def compute_learning_metrics(self) -> Dict[str, Any]:
        """计算学习指标"""
        total = len(self.experiences)
        failure_count = sum(
            1 for exp in self.experiences
            if exp.get("type") == "failure" or "失败" in json.dumps(exp, ensure_ascii=False)
        )
        success_count = sum(
            1 for exp in self.experiences
            if exp.get("type") == "success" or "成功" in json.dumps(exp, ensure_ascii=False)
        )

        # 按时间分布
        by_date = defaultdict(int)
        for exp in self.experiences:
            ts = exp.get("timestamp", "")
            if ts and len(ts) >= 10:
                date = ts[:10]
                by_date[date] += 1

        return {
            "total_experiences": total,
            "failure_count": failure_count,
            "success_count": success_count,
            "unknown_count": total - failure_count - success_count,
            "success_ratio": round(success_count / total, 3) if total > 0 else 0,
            "failure_ratio": round(failure_count / total, 3) if total > 0 else 0,
            "daily_distribution": dict(sorted(by_date.items())),
            "learning_days": len(by_date),
        }


class HypothesisGenerator:
    """生成改进假设"""

    def __init__(self):
        pass

    def generate_from_failures(
        self, failure_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """从失败模式生成改进假设"""
        hypotheses = []

        for pattern in failure_patterns:
            if pattern["occurrences"] >= 1:
                hypo = {
                    "id": f"hypo_learn_{pattern['pattern_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "source": "failure_pattern",
                    "pattern": pattern["pattern_id"],
                    "title": f"改进：{pattern['name']}",
                    "description": f"检测到 {pattern['occurrences']} 次「{pattern['name']}」模式，建议采取改进措施",
                    "severity": pattern["severity"],
                    "confidence": min(0.9, 0.5 + pattern["occurrences"] * 0.1),
                    "actions": pattern["suggested_actions"],
                    "risk_level": "low" if pattern["severity"] == "low" else "medium",
                    "experiment_type": "config_change" if pattern["severity"] == "low" else "recommendation",
                    "created_at": datetime.now().isoformat(),
                    "status": "proposed",
                }
                hypotheses.append(hypo)

        return hypotheses

    def generate_from_successes(
        self, success_patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """从成功模式生成强化假设"""
        hypotheses = []

        for pattern in success_patterns:
            if pattern["occurrences"] >= 1:
                hypo = {
                    "id": f"hypo_reinforce_{pattern['pattern_id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "source": "success_pattern",
                    "pattern": pattern["pattern_id"],
                    "title": f"强化：{pattern['name']}",
                    "description": f"检测到 {pattern['occurrences']} 次「{pattern['name']}」成功模式，建议强化",
                    "value": pattern["value"],
                    "confidence": min(0.9, 0.5 + pattern["occurrences"] * 0.1),
                    "reinforce_actions": pattern["reinforce"],
                    "risk_level": "low",
                    "experiment_type": "reinforcement",
                    "created_at": datetime.now().isoformat(),
                    "status": "proposed",
                }
                hypotheses.append(hypo)

        return hypotheses

    def rank_hypotheses(
        self, hypotheses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """给假设排序（优先级 = 严重程度 × 置信度 × 发生次数）"""
        def score(h):
            sev_weight = {"high": 3, "medium": 2, "low": 1}
            sev = h.get("severity", h.get("value", "low"))
            w = sev_weight.get(sev, 1)
            conf = h.get("confidence", 0.5)
            return w * conf

        ranked = sorted(hypotheses, key=score, reverse=True)
        for i, h in enumerate(ranked):
            h["priority"] = i + 1
        return ranked


class LowRiskExperimenter:
    """低风险实验执行器
    
    安全原则：
    - 只执行低风险配置变更
    - 高风险假设只生成建议
    - 所有变更记录在案
    """

    def __init__(self):
        self.results = []

    def can_auto_execute(self, hypothesis: Dict[str, Any]) -> bool:
        """判断是否可以自动执行"""
        if hypothesis.get("risk_level") != "low":
            return False
        if hypothesis.get("experiment_type") not in ("config_change", "reinforcement"):
            return False
        return True

    def run_experiment(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """运行实验（当前版本：只记录建议，不实际修改配置）"""
        result = {
            "hypothesis_id": hypothesis["id"],
            "title": hypothesis["title"],
            "auto_executed": False,
            "reason": "safe_mode: 当前为安全模式，只生成建议不自动执行",
            "actions_proposed": hypothesis.get("actions", hypothesis.get("reinforce_actions", [])),
            "timestamp": datetime.now().isoformat(),
            "status": "recommended",
        }
        self.results.append(result)
        return result

    def run_all_low_risk(
        self, hypotheses: List[Dict[str, Any]], max_experiments: int = 3
    ) -> List[Dict[str, Any]]:
        """运行所有低风险实验"""
        results = []
        count = 0

        for hypo in hypotheses:
            if count >= max_experiments:
                break
            if self.can_auto_execute(hypo):
                result = self.run_experiment(hypo)
                results.append(result)
                count += 1

        return results


class ExperienceSeeder:
    """经验播种器 — 从系统各处自动提取经验，丰富经验库
    
    数据源：
    1. 心跳历史日志 — 从中提取失败/恢复事件
    2. 探索报告 — 从中提取新发现
    3. Provider 健康状态 — 从中提取降级/恢复事件
    4. 文明审计报告 — 从中提取问题发现
    """

    def __init__(self):
        self.seeded_count = 0
        self.skip_existing = True

    def seed_from_heartbeats(self) -> int:
        """从心跳历史日志中提取经验"""
        log_dir = WORKSPACE / "02_MEMORY" / "logs"
        if not log_dir.exists():
            return 0

        count = 0
        # 扫描最近7天的心跳日志
        for log_file in sorted(log_dir.glob("heartbeat_*.log"), reverse=True)[:7]:
            try:
                content = log_file.read_text(encoding="utf-8", errors="ignore")
                # 提取错误行
                for line in content.split("\n"):
                    if "ERROR" in line or "error" in line.lower():
                        exp = {
                            "type": "heartbeat_error",
                            "title": f"心跳错误: {line[:80]}",
                            "source": "heartbeat_log",
                            "timestamp": datetime.now().isoformat(),
                            "raw": line[:200],
                            "analysis": f"心跳日志中发现错误: {line[:100]}",
                        }
                        if self._save_experience(exp):
                            count += 1
                    # 提取恢复事件
                    if "recovered" in line.lower() or "恢复" in line:
                        exp = {
                            "type": "recovery_success",
                            "title": f"恢复成功: {line[:80]}",
                            "source": "heartbeat_log",
                            "timestamp": datetime.now().isoformat(),
                            "raw": line[:200],
                            "analysis": f"心跳日志中检测到恢复事件",
                        }
                        if self._save_experience(exp):
                            count += 1
            except Exception:
                continue

        return count

    def seed_from_explorations(self) -> int:
        """从探索报告中提取经验"""
        exp_dir = WORKSPACE / "02_MEMORY" / "exploration"
        if not exp_dir.exists():
            return 0

        count = 0
        for exp_file in sorted(exp_dir.glob("*.md"), reverse=True)[:5]:
            try:
                content = exp_file.read_text(encoding="utf-8", errors="ignore")
                # 提取关键发现
                for line in content.split("\n"):
                    if any(kw in line.lower() for kw in ["发现", "insight", "recommend", "建议"]):
                        exp = {
                            "type": "new_discovery",
                            "title": f"探索发现: {line[:80]}",
                            "source": "exploration",
                            "timestamp": datetime.now().isoformat(),
                            "raw": line[:200],
                            "analysis": f"探索报告中提取的发现: {line[:100]}",
                        }
                        if self._save_experience(exp):
                            count += 1
                            break  # 每篇报告只取一条
            except Exception:
                continue

        return count

    def seed_from_audits(self) -> int:
        """从文明审计报告中提取经验"""
        audit_dir = WORKSPACE / "02_MEMORY" / "civilization_audit"
        if not audit_dir.exists():
            return 0

        count = 0
        for audit_file in sorted(audit_dir.glob("*.json"), reverse=True)[:3]:
            try:
                with open(audit_file, "r", encoding="utf-8") as f:
                    audit = json.load(f)
                # 提取问题
                issues = audit.get("issues", audit.get("findings", []))
                for issue in issues[:3]:
                    exp = {
                        "type": "audit_finding",
                        "title": f"审计发现: {issue.get('description', issue.get('title', str(issue)[:80]))}",
                        "source": "civilization_audit",
                        "timestamp": datetime.now().isoformat(),
                        "raw": json.dumps(issue, ensure_ascii=False)[:200],
                        "analysis": f"文明审计发现的问题: {issue.get('description', str(issue)[:100])}",
                    }
                    if self._save_experience(exp):
                        count += 1
            except Exception:
                continue

        return count

    def seed_from_provider_health(self) -> int:
        """从 Provider 健康状态中提取经验"""
        try:
            sys.path.insert(0, str(WORKSPACE / "04_PROTOCOLS"))
            from local_miner import health as provider_health
            count = 0
            for provider, h in provider_health._health.items():
                if h.get("status") in ("degraded", "down"):
                    exp = {
                        "type": "provider_failure",
                        "title": f"Provider {provider} 状态: {h['status']}",
                        "source": "provider_health",
                        "provider": provider,
                        "timestamp": datetime.now().isoformat(),
                        "success_rate": h.get("success", 0) / max(h.get("total", 1), 1),
                        "total_calls": h.get("total", 0),
                        "analysis": f"Provider '{provider}' 当前状态为 '{h['status']}'，"
                                   f"成功率 {h.get('success',0)}/{h.get('total',0)}。",
                    }
                    if self._save_experience(exp):
                        count += 1
            return count
        except Exception:
            return 0

    def _save_experience(self, exp: Dict[str, Any]) -> bool:
        """保存经验到经验库，避免重复"""
        title = exp.get("title", "")
        # 检查是否已存在相似经验
        if self.skip_existing:
            for existing in EXPERIENCE_DIR.glob("*.json"):
                try:
                    with open(existing, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("title", "") == title:
                        return False
                except Exception:
                    continue

        fname = f"exp_seeded_{datetime.now().strftime('%Y%m%dT%H%M%S')}_{self.seeded_count}.json"
        try:
            EXPERIENCE_DIR.mkdir(parents=True, exist_ok=True)
            with open(EXPERIENCE_DIR / fname, "w", encoding="utf-8") as f:
                json.dump(exp, f, ensure_ascii=False, indent=2)
            self.seeded_count += 1
            return True
        except Exception:
            return False

    def run_all(self) -> Dict[str, int]:
        """运行所有播种器"""
        results = {
            "from_heartbeats": self.seed_from_heartbeats(),
            "from_explorations": self.seed_from_explorations(),
            "from_audits": self.seed_from_audits(),
            "from_provider_health": self.seed_from_provider_health(),
        }
        results["total_seeded"] = sum(results.values())
        return results


class SelfLearningEngine:
    """自学习引擎主类"""

    def __init__(self):
        self.extractor = PatternExtractor()
        self.generator = HypothesisGenerator()
        self.experimenter = LowRiskExperimenter()
        self.seeder = ExperienceSeeder()

    def run_learning_cycle(self) -> Dict[str, Any]:
        """运行一次完整的自学习循环"""
        cycle_id = f"learn_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cycle_start = datetime.now()

        # Step 0: 经验播种 — 从系统各处自动提取经验
        seed_results = self.seeder.run_all()

        # Step 1: 加载经验数据
        experiences = self.extractor.load_experiences(limit=100)

        # Step 2: 提取模式
        failure_patterns = self.extractor.extract_failure_patterns()
        success_patterns = self.extractor.extract_success_patterns()
        metrics = self.extractor.compute_learning_metrics()

        # Step 3: 生成假设
        failure_hypotheses = self.generator.generate_from_failures(failure_patterns)
        success_hypotheses = self.generator.generate_from_successes(success_patterns)
        all_hypotheses = failure_hypotheses + success_hypotheses
        ranked_hypotheses = self.generator.rank_hypotheses(all_hypotheses)

        # Step 4: 低风险实验
        experiments = self.experimenter.run_all_low_risk(
            ranked_hypotheses, max_experiments=3
        )

        # Step 5: 推送假设到 Question Center
        questions_pushed = self._push_to_question_center(ranked_hypotheses)

        # Step 6: 记录学习结果
        cycle_result = {
            "cycle_id": cycle_id,
            "started_at": cycle_start.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - cycle_start).total_seconds(),
            "seed_results": seed_results,
            "metrics": metrics,
            "patterns": {
                "failure_patterns_detected": len(failure_patterns),
                "success_patterns_detected": len(success_patterns),
                "failure_patterns": failure_patterns,
                "success_patterns": success_patterns,
            },
            "hypotheses": {
                "total_generated": len(ranked_hypotheses),
                "from_failures": len(failure_hypotheses),
                "from_successes": len(success_hypotheses),
                "ranked": ranked_hypotheses[:10],
                "pushed_to_question_center": questions_pushed,
            },
            "experiments": {
                "auto_executed": len([e for e in experiments if e["auto_executed"]]),
                "recommended": len(experiments),
                "details": experiments,
            },
        }

        # 保存学习结果
        self._save_cycle_result(cycle_id, cycle_result)

        # Step 7: 蒸馏到 Mission — 将学习成果登记到活跃任务的蒸馏资产中
        self._distill_to_missions(cycle_result)

        return cycle_result

    def _distill_to_missions(self, cycle_result: Dict[str, Any]):
        """将学习循环成果蒸馏到活跃 Mission 的蒸馏资产中"""
        try:
            from mission_protocol import protocol
            active_missions = protocol.list_active()
            if not active_missions:
                return
            
            # 新经验 → experience 蒸馏资产
            seeded = cycle_result.get("seed_results", {}).get("total_seeded", 0)
            if seeded > 0:
                for m in active_missions:
                    exp_path = f"02_MEMORY/experience/ (本次+{seeded})"
                    protocol.add_artifact(m.mid, exp_path, distill_type="experience")
            
            # 新模式 → blueprint 蒸馏资产（模式是结构蓝图的一部分）
            patterns = (cycle_result.get("patterns", {}).get("failure_patterns_detected", 0)
                       + cycle_result.get("patterns", {}).get("success_patterns_detected", 0))
            if patterns > 0:
                for m in active_missions:
                    bp_path = f"模式发现: {patterns} 个新模式"
                    protocol.add_artifact(m.mid, bp_path, distill_type="blueprint")
            
            # 新假设 → kernel 蒸馏资产（假设可能孕育出新芯片）
            hypotheses = cycle_result.get("hypotheses", {}).get("total_generated", 0)
            if hypotheses > 0:
                for m in active_missions:
                    kernel_path = f"假设生成: {hypotheses} 个新假设"
                    protocol.add_artifact(m.mid, kernel_path, distill_type="kernel")
        except Exception:
            pass

    def _push_to_question_center(self, hypotheses: List[Dict[str, Any]]) -> int:
        """把高优先级假设推送到 Question Center"""
        try:
            sys.path.insert(0, str(WORKSPACE / "04_PROTOCOLS"))
            from question_center import QuestionCenter
            qc = QuestionCenter()

            pushed = 0
            for hypo in hypotheses[:5]:  # 最多推送5个
                # 用 pattern_id 去重（比文本匹配更准确）
                pattern_id = hypo.get("pattern", "")
                desc = hypo.get("description", "")
                existing = []
                if pattern_id:
                    existing = [q for q in qc.questions
                                if pattern_id in q.get("question", "")
                                and q.get("source") == "self_learning"]
                if not existing:
                    existing = [q for q in qc.questions
                                if desc[:30] in q.get("question", "")
                                and q.get("source") == "self_learning"]
                if existing:
                    continue

                qid = qc.add_question(
                    question_text=f"[自学习] {desc}",
                    source="self_learning",
                    priority="P1" if hypo.get("risk_level") == "medium" else "P2",
                    capability="research",
                )
                if qid:
                    actions = hypo.get("actions", hypo.get("reinforce_actions", []))
                    hypo_text = "; ".join(actions[:2]) if actions else desc
                    qc.add_hypothesis(qid, hypo_text, confidence=hypo.get("confidence", 0.5))
                    pushed += 1

            return pushed
        except Exception:
            return 0

    def _save_cycle_result(self, cycle_id: str, result: Dict[str, Any]):
        """保存学习周期结果"""
        out_file = LEARNING_DIR / f"{cycle_id}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

    def get_summary(self, result: Dict[str, Any]) -> str:
        """生成学习周期摘要"""
        m = result["metrics"]
        lines = []
        lines.append("=" * 56)
        lines.append("  SELF-LEARNING CYCLE — 自学习周期报告")
        lines.append("=" * 56)
        lines.append(f"  周期: {result['cycle_id']}")
        lines.append(f"  耗时: {result['duration_seconds']:.2f}s")
        lines.append("")

        # 经验播种
        sr = result.get("seed_results", {})
        if sr:
            lines.append(f"  经验播种: +{sr.get('total_seeded', 0)} 条新经验")
            for k, v in sr.items():
                if k != "total_seeded" and v > 0:
                    lines.append(f"    — {k}: {v}")
            lines.append("")

        lines.append(f"  经验库: {m['total_experiences']} 条")
        lines.append(f"  成功/失败: {m['success_count']} / {m['failure_count']}")
        lines.append(f"  学习天数: {m['learning_days']} 天")
        lines.append("")

        fp = result["patterns"]["failure_patterns"]
        if fp:
            lines.append(f"  失败模式 ({len(fp)} 种):")
            for p in fp[:5]:
                lines.append(f"    [{p['severity']}] {p['name']:20s} × {p['occurrences']}")
            lines.append("")

        sp = result["patterns"]["success_patterns"]
        if sp:
            lines.append(f"  成功模式 ({len(sp)} 种):")
            for p in sp[:5]:
                lines.append(f"    [{p['value']}] {p['name']:20s} × {p['occurrences']}")
            lines.append("")

        hypos = result["hypotheses"]["ranked"]
        if hypos:
            lines.append(f"  改进假设 (Top 5):")
            for h in hypos[:5]:
                risk = h.get("risk_level", "unknown")
                lines.append(f"    #{h['priority']} [{risk}] {h['title']}")
            lines.append("")

        pushed = result["hypotheses"].get("pushed_to_question_center", 0)
        exps = result["experiments"]
        lines.append(f"  问题中心: 推送 {pushed} 个假设")
        lines.append(f"  实验: 推荐 {exps['recommended']} 个, 自动执行 {exps['auto_executed']} 个")
        lines.append("")
        lines.append("=" * 56)

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Self-Learning Engine")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--summary", action="store_true", help="Output summary only")
    args = parser.parse_args()

    engine = SelfLearningEngine()
    result = engine.run_learning_cycle()

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.summary:
        print(engine.get_summary(result))
    else:
        print(engine.get_summary(result))


if __name__ == "__main__":
    import argparse
    main()
