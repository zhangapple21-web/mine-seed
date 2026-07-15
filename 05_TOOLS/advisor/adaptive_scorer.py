#!/usr/bin/env python3
"""
Adaptive Scorer — 自适应评分权重调整器

根据 PerformanceTracker 的历史表现数据，动态调整评分权重：
  - 连续失败时降低相关因子权重
  - 高胜率因子增加权重
  - 自动触发矿工分析失败原因

设计原则：
  - 无外部依赖
  - 权重调整有上下限（防止过度拟合）
  - 调整幅度与样本量相关（样本越多，调整越保守）
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
from performance_tracker import PerformanceTracker
from policy_manager import PolicyManager

LOG_DIR = Path(__file__).parent.parent / 'mine_output' / 'advisor'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'adaptive.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdaptiveScorer:
    """
    自适应评分权重管理器
    
    权重配置文件: adaptive_weights.json
    结构:
    {
      "version": 1,
      "updated_at": "...",
      "base_weights": {
        "price_range": 15,
        "change_moderate": 25,
        "turnover_healthy": 20,
        "cap_mid_large": 15,
        "pe_reasonable": 15,
        "liquidity_ok": 10
      },
      "adjusted_weights": { ... },
      "factor_performance": {
        "price_range": {"wins": 5, "total": 10, "avg_return": 2.3},
        ...
      },
      "adjustment_history": []
    }
    """
    
    WEIGHTS_FILE = LOG_DIR / 'adaptive_weights.json'
    
    # 默认权重（与 stock_advisor.py 中 layer1 打分一致）
    DEFAULT_WEIGHTS = {
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
    
    # 权重调整限制
    MIN_WEIGHT = 5
    MAX_WEIGHT = 40
    ADJUSTMENT_RATE = 0.2  # 每次调整幅度不超过20%
    
    def __init__(self):
        self.policy_manager = PolicyManager()
        self.weights = self._load_effective_weights()
        self.factor_perf = {}
        self.adjustment_history = []
        self._load_weights()
    
    def _load_effective_weights(self) -> Dict[str, float]:
        """从 PolicyManager 获取当前生效的权重"""
        policy_weights = self.policy_manager.get_current_weights()
        if policy_weights:
            logger.info(f"从策略管理器加载权重: {len(policy_weights)} 个因子")
            return policy_weights
        return self.DEFAULT_WEIGHTS.copy()
    
    def _load_weights(self):
        """加载权重配置"""
        if self.WEIGHTS_FILE.exists():
            try:
                data = json.loads(self.WEIGHTS_FILE.read_text(encoding='utf-8'))
                self.weights = data.get('adjusted_weights', self.DEFAULT_WEIGHTS.copy())
                self.factor_perf = data.get('factor_performance', {})
                self.adjustment_history = data.get('adjustment_history', [])
                logger.info(f"加载自适应权重: {len(self.weights)} 个因子")
            except Exception as e:
                logger.warning(f"加载权重失败: {e}，使用默认值")
    
    def _save_weights(self):
        """保存权重配置"""
        data = {
            "version": 2,
            "updated_at": datetime.now().isoformat(),
            "base_weights": self.DEFAULT_WEIGHTS,
            "adjusted_weights": self.weights,
            "factor_performance": self.factor_perf,
            "adjustment_history": self.adjustment_history[-20:],  # 保留最近20条
        }
        try:
            self.WEIGHTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception as e:
            logger.warning(f"保存权重失败: {e}")
    
    def get_weight(self, factor: str) -> float:
        """获取某个因子的当前权重"""
        return self.weights.get(factor, self.DEFAULT_WEIGHTS.get(factor, 10))
    
    def get_all_weights(self) -> Dict[str, float]:
        """获取所有权重"""
        return self.weights.copy()
    
    def analyze_and_adjust(self, tracker: PerformanceTracker, period: str = "T+1"):
        """
        分析历史表现并调整权重
        
        Args:
            tracker: PerformanceTracker 实例
            period: 统计周期，支持 "T+1" / "T+5"，默认 T+1
        
        返回:
          - 是否触发了权重调整
          - 调整详情
        
        P0 修复：默认使用 T+1 数据，打破"没有T+5→没有调整→没有T+5"的死循环
        """
        # 获取因子有效性统计（使用指定周期）
        factor_stats = tracker.get_factor_effectiveness(period)
        if not factor_stats:
            logger.info(f"因子统计不足（{period}），跳过调整")
            return False, "insufficient data"
        
        adjusted = False
        adjustments = []
        
        # 降低样本阈值，让调整更早启动
        min_samples = 2 if period == "T+1" else 5
        
        for factor, stats in factor_stats.items():
            count = stats.get('count', 0)
            win_rate = stats.get('win_rate', 50)
            avg_return = stats.get('avg_return', 0)
            
            if count < min_samples:
                continue  # 样本不足，不调整
            
            current_weight = self.weights.get(factor, self.DEFAULT_WEIGHTS.get(factor, 10))
            base_weight = self.DEFAULT_WEIGHTS.get(factor, 10)
            
            # 计算调整方向
            # 胜率 > 60%: 增加权重
            # 胜率 < 40%: 降低权重
            # 40%-60%: 小幅向基准回归
            if win_rate > 60:
                direction = 1
                reason = f"高胜率({win_rate}%)"
            elif win_rate < 40:
                direction = -1
                reason = f"低胜率({win_rate}%)"
            else:
                # 向基准回归
                if current_weight > base_weight:
                    direction = -0.5
                    reason = "胜率中性，向基准回归"
                elif current_weight < base_weight:
                    direction = 0.5
                    reason = "胜率中性，向基准回归"
                else:
                    continue
            
            # 计算调整幅度（与样本量成反比，样本越多调整越保守）
            confidence = min(count / 20, 1.0)  # 20个样本达到最大置信度
            adjustment = base_weight * self.ADJUSTMENT_RATE * direction * confidence
            new_weight = current_weight + adjustment
            
            # 限制在范围内
            new_weight = max(self.MIN_WEIGHT, min(self.MAX_WEIGHT, new_weight))
            
            if abs(new_weight - current_weight) > 0.5:
                self.weights[factor] = round(new_weight, 1)
                adjusted = True
                adj_record = {
                    "timestamp": datetime.now().isoformat(),
                    "factor": factor,
                    "old_weight": current_weight,
                    "new_weight": round(new_weight, 1),
                    "reason": reason,
                    "win_rate": win_rate,
                    "avg_return": avg_return,
                    "sample_count": count,
                    "period": period,
                }
                self.adjustment_history.append(adj_record)
                adjustments.append(adj_record)
                logger.info(f"调整权重: {factor} {current_weight:.1f} -> {new_weight:.1f} ({reason})")
        
        if adjusted:
            self.factor_perf = factor_stats
            self._save_weights()
            
            # 创建候选策略并提交 Roundtable 评审
            self._submit_policy_candidate(adjustments, factor_stats)
        
        return adjusted, adjustments
    
    def _submit_policy_candidate(self, adjustments: List[Dict], factor_stats: Dict):
        """
        创建候选策略并提交 Roundtable 评审
        
        遵循 AUM-MISSION-ADVISOR-001 原则：
        - Learning 只生成 Candidate Policy
        - 通过 Roundtable 评审后才能批准
        - Admission 是唯一更新 Policy 的入口
        
        Evidence 来源：
        - PerformanceTracker: 历史表现数据
        - PostRecommendationAuditor: 推票后审计质量评估
        - RuleEngine: 规则验证结果
        """
        try:
            # 获取当前表现摘要作为证据
            tracker = PerformanceTracker()
            summary = tracker.get_summary(20)
            
            # 获取审计 Evidence（推票后质量评估）
            audit_evidence = self._get_audit_evidence()
            
            # 创建候选策略
            reason = f"自适应调整: {len(adjustments)} 个因子权重变化"
            policy = self.policy_manager.create_candidate_policy(
                new_weights=self.weights,
                evidence={
                    "performance_summary": summary,
                    "factor_effectiveness": factor_stats,
                    "adjustments": adjustments,
                    "audit_evidence": audit_evidence,
                },
                reason=reason
            )
            
            logger.info(f"候选策略已创建: {policy.policy_id}")
            
            # Roundtable 评审（含审计证据）
            review = self.policy_manager.roundtable_review(
                policy_id=policy.policy_id,
                performance_summary=summary,
                factor_effectiveness=factor_stats,
                audit_evidence=audit_evidence
            )
            
            if review.get('approved', False):
                # Admission 批准策略
                self.policy_manager.approve_policy(policy.policy_id, review)
                logger.info(f"策略 {policy.policy_id} 已通过评审并生效")
            else:
                logger.info(f"策略 {policy.policy_id} 评审未通过: {review.get('reason', '')}")
                
        except Exception as e:
            logger.warning(f"策略提交失败: {e}")
    
    def _get_audit_evidence(self) -> Dict[str, Any]:
        """
        获取推票后审计 Evidence（经压缩门）
        
        C-019 约束：策略调整必须引用压缩后的审计数据，
        不能直接读 audit_results.json。
        
        返回最近30天的审计统计，用于策略优化决策：
        - 平均审计评分
        - 评级分布
        - 主要风险点
        - 规则引擎验证结果统计
        """
        try:
            # 通过 Compression Gate 获取审计数据
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_MEMORY"))
            from experience_engine import ExperienceEngine
            ee = ExperienceEngine()
            compressed = ee.get_audit_compression_latest()
            
            if "error" in compressed:
                logger.debug(f"审计压缩数据不可用: {compressed.get('error')}")
                return {"source": "unavailable", "error": compressed.get("error")}
            
            return {
                "source": "audit_compression_gate",
                "period_days": 30,
                "summary": compressed,
                "strategy_adjustments": compressed.get("strategy_adjustments", []),
            }
        except Exception as e:
            logger.debug(f"获取审计证据失败: {e}")
            return {"source": "unavailable", "error": str(e)}
    
    def should_trigger_optimization(self, tracker: PerformanceTracker, 
                                    consecutive_losses_threshold: int = 3) -> bool:
        """
        判断是否应触发因子优化任务
        
        条件：
        - 最近 N 次推荐中，连续失败次数 >= threshold
        - 或最近 10 次推荐胜率 < 30%
        
        支持多周期数据降级：T+5 → T+3 → T+2 → T+1
        防止"没有T+5→没有调整→没有T+5"的死循环
        """
        summary = tracker.get_summary(10)
        if summary.get('total_recommendations', 0) < 5:
            return False
        
        win_rates = summary.get('win_rates', {})
        
        # 按优先级检查各周期胜率
        periods = ['T+5', 'T+3', 'T+2', 'T+1']
        for period in periods:
            win_rate = win_rates.get(period)
            if win_rate is not None and win_rate < 30:
                logger.warning(f"触发优化: 最近10次{period}胜率仅 {win_rate}%")
                return True
        
        # 检查连续失败（通过读取最近记录，支持多周期降级）
        recent = sorted(tracker.records.values(), 
                       key=lambda r: r.recommend_date, reverse=True)[:10]
        
        # 按优先级选择收益字段
        return_fields = ['return_t5', 'return_t3', 'return_t2', 'return_t1']
        for return_field in return_fields:
            consecutive_losses = 0
            for rec in recent:
                ret_value = getattr(rec, return_field, None)
                if ret_value is not None:
                    if ret_value < 0:
                        consecutive_losses += 1
                        if consecutive_losses >= consecutive_losses_threshold:
                            logger.warning(f"触发优化: 连续 {consecutive_losses} 次{return_field.replace('return_', '')}亏损")
                            return True
                    else:
                        consecutive_losses = 0
        
        return False
    
    def generate_optimization_task(self, tracker: PerformanceTracker) -> Dict[str, Any]:
        """生成因子优化任务规格"""
        summary = tracker.get_summary(20)
        
        # 尝试获取有效周期的因子统计（支持 T+1/T+5）
        factor_stats_t5 = tracker.get_factor_effectiveness("T+5")
        factor_stats_t1 = tracker.get_factor_effectiveness("T+1")
        factor_stats = factor_stats_t5 if factor_stats_t5 else factor_stats_t1
        
        # 确定有效周期
        win_rates = summary.get('win_rates', {})
        periods = ['T+5', 'T+3', 'T+2', 'T+1']
        effective_period = None
        effective_win_rate = None
        
        for period in periods:
            wr = win_rates.get(period)
            if wr is not None:
                effective_period = period
                effective_win_rate = wr
                break
        
        task = {
            "task_type": "factor_optimization",
            "created_at": datetime.now().isoformat(),
            "trigger_reason": "consecutive_losses_or_low_winrate",
            "effective_period": effective_period,
            "current_performance": summary,
            "factor_effectiveness": factor_stats,
            "current_weights": self.weights,
            "suggested_actions": [],
        }
        
        # 自动生成建议
        if factor_stats:
            worst_factors = sorted(factor_stats.items(), 
                                  key=lambda x: x[1].get('win_rate', 50))[:3]
            for factor, stats in worst_factors:
                if stats.get('win_rate', 50) < 40:
                    task["suggested_actions"].append({
                        "action": "review_factor",
                        "factor": factor,
                        "reason": f"胜率仅 {stats['win_rate']}%，建议重新评估该因子逻辑",
                        "current_weight": self.weights.get(factor, 10),
                    })
        
        # 如果整体胜率低，建议扩大样本或调整筛选标准
        if effective_win_rate is not None and effective_win_rate < 40:
            task["suggested_actions"].append({
                "action": "tighten_criteria",
                "reason": f"整体{effective_period}胜率仅 {effective_win_rate}%，建议收紧筛选条件",
            })
        
        return task
    
    def get_health_score(self, tracker: PerformanceTracker) -> Dict[str, Any]:
        """
        计算推荐系统健康度分数
        
        返回 0-100 的健康度分数和详细指标
        
        支持多周期数据降级：T+5 → T+3 → T+2 → T+1
        防止"没有T+5→健康度虚高"的指标作弊问题
        
        Goal Validation Rule:
        任何生产优化，必须证明优化目标与最终业务价值一致。
        否则，禁止进入 Learning。
        """
        summary = tracker.get_summary(30)
        
        if summary.get('total_recommendations', 0) == 0:
            return {"score": 50, "status": "unknown", "reason": "暂无推荐记录"}
        
        win_rates = summary.get('win_rates', {})
        avg_returns = summary.get('avg_returns', {})
        
        # 按优先级选择可用的周期数据
        periods = ['T+5', 'T+3', 'T+2', 'T+1']
        effective_period = None
        effective_win_rate = None
        effective_avg_return = None
        
        for period in periods:
            wr = win_rates.get(period)
            ret = avg_returns.get(period)
            if wr is not None and ret is not None:
                effective_period = period
                effective_win_rate = wr
                effective_avg_return = ret
                break
        
        # 如果完全没有数据，使用默认值
        if effective_period is None:
            return {"score": 50, "status": "unknown", "reason": "无可用收益数据"}
        
        # 各维度分数（0-100）
        scores = {}
        
        # 1. 胜率分数（权重 40%）
        scores['win_rate'] = min(100, effective_win_rate * 1.5)
        
        # 2. 平均收益分数（权重 30%）
        scores['avg_return'] = min(100, max(0, 50 + effective_avg_return * 10))
        
        # 3. 数据完整度分数（权重 20%）
        total = summary.get('total_recommendations', 0)
        complete = summary.get('complete_records', 0)
        if total > 0:
            scores['data_completeness'] = min(100, complete / total * 100)
        else:
            scores['data_completeness'] = 0
        
        # 4. 系统稳定性分数（权重 10%）
        # 基于是否有连续失败
        if self.should_trigger_optimization(tracker, consecutive_losses_threshold=5):
            scores['stability'] = 30
        elif self.should_trigger_optimization(tracker, consecutive_losses_threshold=3):
            scores['stability'] = 60
        else:
            scores['stability'] = 100
        
        # 加权总分
        total_score = (
            scores['win_rate'] * 0.4 +
            scores['avg_return'] * 0.3 +
            scores['data_completeness'] * 0.2 +
            scores['stability'] * 0.1
        )
        
        # 状态判定
        if total_score >= 80:
            status = "healthy"
        elif total_score >= 60:
            status = "warning"
        else:
            status = "critical"
        
        return {
            "score": round(total_score, 1),
            "status": status,
            "effective_period": effective_period,
            "details": scores,
            "summary": summary,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Adaptive Scorer")
    parser.add_argument("--adjust", action="store_true", help="Analyze and adjust weights")
    parser.add_argument("--health", action="store_true", help="Show health score")
    parser.add_argument("--weights", action="store_true", help="Show current weights")
    args = parser.parse_args()
    
    scorer = AdaptiveScorer()
    tracker = PerformanceTracker()
    
    if args.adjust:
        adjusted, details = scorer.analyze_and_adjust(tracker)
        print(json.dumps({"adjusted": adjusted, "details": details}, ensure_ascii=False, indent=2))
    
    if args.health:
        health = scorer.get_health_score(tracker)
        print(json.dumps(health, ensure_ascii=False, indent=2))
    
    if args.weights:
        print(json.dumps(scorer.get_all_weights(), ensure_ascii=False, indent=2))
    
    if not any([args.adjust, args.health, args.weights]):
        parser.print_help()


if __name__ == "__main__":
    main()
