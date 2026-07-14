#!/usr/bin/env python3
"""
Post-Recommendation Quality Evaluator — 推票后质量评估

分层定位（对应 #012 内外双域隔离）：
  内部推理层（本模块）：推票后对推荐质量做完整推理评估
    → 矿工用 abliterated 模型做不被打断的思考
    → 先想清楚这只票到底好不好
  外部输出层（降敏词表/输出宪法）：决定对外怎么说
    → 不归本模块管

流程：
  Recommendation → 推送给客户（同时记录）
  → 矿工评估推荐质量（内部推理，不打断思考）
  → 交叉验证（规则引擎）
  → 评估结果存入 Evidence
  → 用于后续 Candidate 生成和 Policy 调整

设计原则：
  - 评估从"推票前的前置条件"变成"推票后的质量推理"
  - 保证时效性，不阻塞推荐流程
  - 提供可追溯的 Evidence 和改进依据
  - 内部推理不做内容审查——审查是输出层的事
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "04_PROTOCOLS"))

from miner_assistant import MinerAssistant
from multi_data_source import DataSourceManager
from smelter_gate import SmelterGate

LOG_DIR = Path(__file__).parent.parent / 'mine_output' / 'advisor'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'auditor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AuditResult:
    """审计结果数据结构"""
    audit_id: str
    recommend_date: str
    code: str
    name: str
    recommend_price: float
    audit_time: str
    miner_score: Optional[int]
    miner_feedback: str
    rule_engine_score: Optional[int]
    rule_engine_feedback: str
    cross_validation_score: Optional[int]
    overall_score: Optional[int]
    overall_rating: Optional[str]
    evidence: Dict[str, Any]
    audit_status: str = "passed"  # passed / rejected / pending_review
    reject_reason: str = ""
    gate_record_id: str = ""
    needs_review: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> "AuditResult":
        return cls(**d)


class RuleEngine:
    """规则引擎交叉验证"""
    
    def __init__(self):
        self.dsm = DataSourceManager()
    
    def validate(self, code: str, name: str, price: float, signals: List[str]) -> Dict[str, Any]:
        """验证推荐质量"""
        issues = []
        score = 100
        
        # 规则1: 价格合理性检查
        if price <= 0:
            issues.append("价格无效")
            score -= 30
        elif price < 1:
            issues.append("价格过低，可能存在数据异常")
            score -= 10
        elif price > 1000:
            issues.append("高价股，波动风险较高")
            score -= 5
        
        # 规则2: 成交量检查
        try:
            quotes = self.dsm.get_quotes([code])
            if quotes:
                volume = quotes[0].get('volume', 0)
                if volume < 1000000:
                    issues.append(f"成交量不足 ({volume:,})，流动性风险")
                    score -= 20
                elif volume < 10000000:
                    issues.append(f"成交量偏低 ({volume:,})")
                    score -= 5
        except Exception:
            issues.append("无法获取成交量数据")
            score -= 10
        
        # 规则3: 信号一致性检查
        if signals:
            bullish = [s for s in signals if any(k in s for k in ['金叉', '多头', '上涨', '突破', '买入'])]
            bearish = [s for s in signals if any(k in s for k in ['死叉', '空头', '下跌', '破位', '卖出'])]
            
            if bullish and bearish:
                issues.append("信号矛盾（同时存在多头和空头信号）")
                score -= 20
            elif not bullish and not bearish:
                issues.append("缺乏明确的方向性信号")
                score -= 10
        
        # 规则4: 近期波动检查
        try:
            kline = self.dsm.get_hist_kline(code, days=5)
            if kline and len(kline) >= 3:
                prices = [k['close'] for k in kline]
                max_p = max(prices)
                min_p = min(prices)
                volatility = (max_p - min_p) / min_p * 100
                if volatility > 20:
                    issues.append(f"近期波动过大 ({volatility:.1f}%)")
                    score -= 15
                elif volatility > 10:
                    issues.append(f"近期波动较大 ({volatility:.1f}%)")
                    score -= 5
        except Exception:
            pass
        
        # 规则5: 行业多样性（如果有多只股票）
        # 这里简化处理，只检查单只股票
        
        score = max(0, score)
        
        if score >= 80:
            rating = "优秀"
        elif score >= 60:
            rating = "良好"
        elif score >= 40:
            rating = "一般"
        else:
            rating = "较差"
        
        return {
            "score": score,
            "rating": rating,
            "issues": issues,
            "feedback": "; ".join(issues) if issues else "通过所有规则检查",
            "signals": signals,
        }


class PostRecommendationAuditor:
    """推票后审计员"""
    
    def __init__(self):
        self.miner = MinerAssistant()
        self.rule_engine = RuleEngine()
        self.smelter_gate = SmelterGate()
        self.audit_results: Dict[str, AuditResult] = {}
        self._load_audit_results()
    
    def _load_audit_results(self):
        """加载历史审计结果"""
        audit_file = LOG_DIR / 'audit_results.json'
        if audit_file.exists():
            try:
                data = json.loads(audit_file.read_text(encoding='utf-8'))
                for key, result in data.items():
                    self.audit_results[key] = AuditResult.from_dict(result)
                logger.info(f"加载审计结果: {len(self.audit_results)} 条")
            except Exception as e:
                logger.warning(f"加载审计结果失败: {e}")
    
    def _save_audit_results(self):
        """保存审计结果"""
        audit_file = LOG_DIR / 'audit_results.json'
        data = {k: v.to_dict() for k, v in self.audit_results.items()}
        audit_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def audit(self, code: str, name: str, price: float, signals: List[str],
              recommend_date: str = None) -> AuditResult:
        """
        执行推票后审计
        
        返回审计结果，存入 Evidence。
        如果 Gate 拒绝，返回带 rejected 状态的审计结果（保留原始反馈，但评分无效）。
        """
        recommend_date = recommend_date or datetime.now().strftime('%Y%m%d')
        audit_id = f"{recommend_date}_{code}"
        
        if audit_id in self.audit_results:
            logger.info(f"审计结果已存在: {audit_id}")
            return self.audit_results[audit_id]
        
        logger.info(f"【审计】开始评估 {name}({code})")
        
        # 1. 矿工评估推荐质量（经 Gate 拦截）
        miner_result, gate_result = self._miner_evaluation(code, name, price, signals)
        
        # 2. 检查 Gate 是否拒绝
        if not gate_result.get("passed"):
            # Gate 拒绝：创建带 rejected 状态的审计结果
            audit_status = "pending_review" if gate_result.get("needs_review") else "rejected"
            
            audit_result = AuditResult(
                audit_id=audit_id,
                recommend_date=recommend_date,
                code=code,
                name=name,
                recommend_price=price,
                audit_time=datetime.now().isoformat(),
                miner_score=None,  # 无有效评分
                miner_feedback=miner_result.get("feedback", ""),  # 保留原始反馈
                rule_engine_score=None,
                rule_engine_feedback="",
                cross_validation_score=None,
                overall_score=None,
                overall_rating=None,
                evidence={
                    "miner_evaluation": miner_result,
                    "gate_result": gate_result,
                    "signals": signals,
                    "recommend_price": price,
                    "audit_time": datetime.now().isoformat(),
                },
                audit_status=audit_status,
                reject_reason=gate_result.get("reject_reason", ""),
                gate_record_id=gate_result.get("record_id", ""),
                needs_review=gate_result.get("needs_review", False),
            )
            
            self.audit_results[audit_id] = audit_result
            self._save_audit_results()
            
            logger.warning(f"【审计异常】{name}({code}) — Gate 拒绝: {gate_result.get('reject_reason')}")
            
            return audit_result
        
        # 3. Gate 通过：正常进行审计流程
        rule_result = self.rule_engine.validate(code, name, price, signals)
        
        # 4. 综合评分
        cross_score = self._cross_validate(miner_result, rule_result)
        overall_score = round((miner_result['score'] + rule_result['score'] + cross_score) / 3)
        
        if overall_score >= 80:
            overall_rating = "A"
        elif overall_score >= 60:
            overall_rating = "B"
        elif overall_score >= 40:
            overall_rating = "C"
        else:
            overall_rating = "D"
        
        # 5. 构建 Evidence
        evidence = {
            "miner_evaluation": miner_result,
            "rule_engine_validation": rule_result,
            "cross_validation_score": cross_score,
            "signals": signals,
            "recommend_price": price,
            "audit_time": datetime.now().isoformat(),
            "gate_result": gate_result,
        }
        
        audit_result = AuditResult(
            audit_id=audit_id,
            recommend_date=recommend_date,
            code=code,
            name=name,
            recommend_price=price,
            audit_time=datetime.now().isoformat(),
            miner_score=miner_result['score'],
            miner_feedback=miner_result['feedback'],
            rule_engine_score=rule_result['score'],
            rule_engine_feedback=rule_result['feedback'],
            cross_validation_score=cross_score,
            overall_score=overall_score,
            overall_rating=overall_rating,
            evidence=evidence,
            audit_status="passed",
        )
        
        self.audit_results[audit_id] = audit_result
        self._save_audit_results()
        
        logger.info(f"【审计完成】{name}({code}) — 综合评分: {overall_score}/100 评级: {overall_rating}")
        
        return audit_result
    
    def _miner_evaluation(self, code: str, name: str, price: float, 
                          signals: List[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """矿工评估推荐质量（优先使用本地 Ollama，24小时可用）
        
        ARCH-014 子任务2: FA模式产出必须经过 smelter_gate 拦截记录
        miner_assistant.audit_recommendation() 是 FA 模式推理（无内部审查），
        其产出在进入审计结果之前必须经过 smelter_gate。
        
        Returns:
            Tuple[miner_result, gate_result]:
                - miner_result: 矿工评估结果
                - gate_result: Gate 处理结果（含 passed/reject_reason 等）
        """
        result = self.miner.audit_recommendation(code, name, price, signals)
        
        gate_result = self.smelter_gate.pass_through(
            content=result,
            source="miner_assistant.audit_recommendation",
            source_type="audit",
            is_fa_mode=True,
            content_type="miner_score",
            metadata={
                "code": code,
                "name": name,
                "price": price,
                "signals": signals,
                "miner_source": result.get("source")
            }
        )
        
        if gate_result.get("passed"):
            logger.info(f"[SmelterGate] FA模式产出已通过: record_id={gate_result['record_id']}, action={gate_result['gate_action']}")
        else:
            logger.warning(f"[SmelterGate] FA模式产出被拒绝: record_id={gate_result['record_id']}, reason={gate_result.get('reject_reason')}")
        
        return result, gate_result
    
    def _local_stock_analysis(self, code: str, name: str, price: float, 
                              signals: List[str]) -> str:
        """本地股票分析"""
        lines = []
        
        if signals:
            bullish = sum(1 for s in signals if any(k in s for k in ['金叉', '多头', '上涨', '突破']))
            bearish = sum(1 for s in signals if any(k in s for k in ['死叉', '空头', '下跌', '破位']))
            
            if bullish > bearish:
                lines.append(f"技术面偏多（{bullish}个多头信号，{bearish}个空头信号）")
            elif bearish > bullish:
                lines.append(f"技术面偏空（{bearish}个空头信号，{bullish}个多头信号）")
            else:
                lines.append(f"技术面中性（{bullish}个多头，{bearish}个空头）")
        
        lines.append(f"当前价格 ¥{price:.2f}")
        
        try:
            quotes = self.rule_engine.dsm.get_quotes([code])
            if quotes:
                q = quotes[0]
                change = q.get('change_percent', 0)
                lines.append(f"今日涨跌幅: {change:+.2f}%")
                
                if change > 5:
                    lines.append("⚠️ 涨幅较大，注意追高风险")
                elif change < -5:
                    lines.append("⚠️ 跌幅较大，注意风险")
        
        except Exception:
            pass
        
        return "；".join(lines)
    
    def _cross_validate(self, miner_result: Dict, rule_result: Dict) -> int:
        """交叉验证评分"""
        miner_score = miner_result['score']
        rule_score = rule_result['score']
        
        # 评分一致性检查
        diff = abs(miner_score - rule_score)
        
        if diff <= 10:
            # 评分一致，交叉验证通过
            cross_score = round((miner_score + rule_score) / 2)
        elif diff <= 30:
            # 评分有差异，但在合理范围内
            cross_score = round((miner_score + rule_score) / 2) - 10
        else:
            # 评分差异较大，需要标记
            cross_score = round((miner_score + rule_score) / 2) - 20
        
        return max(0, cross_score)
    
    def get_audit_summary(self, days: int = 30) -> Dict[str, Any]:
        """获取审计摘要"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        recent = [r for r in self.audit_results.values() if r.recommend_date >= cutoff]
        
        if not recent:
            return {"message": "暂无审计数据"}
        
        ratings = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        total_score = 0
        
        for r in recent:
            ratings[r.overall_rating] += 1
            total_score += r.overall_score
        
        return {
            "period_days": days,
            "total_audits": len(recent),
            "avg_score": round(total_score / len(recent)),
            "ratings": ratings,
            "breakdown": {
                "miner_avg": round(sum(r.miner_score for r in recent) / len(recent)),
                "rule_avg": round(sum(r.rule_engine_score for r in recent) / len(recent)),
                "cross_avg": round(sum(r.cross_validation_score for r in recent) / len(recent)),
            },
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Post-Recommendation Auditor")
    parser.add_argument("--audit", type=str, help="Audit stock (code:name:price)")
    parser.add_argument("--summary", action="store_true", help="Show audit summary")
    args = parser.parse_args()
    
    auditor = PostRecommendationAuditor()
    
    if args.audit:
        parts = args.audit.split(':')
        if len(parts) >= 3:
            code, name, price = parts[0], parts[1], float(parts[2])
            signals = parts[3].split(',') if len(parts) > 3 else []
            result = auditor.audit(code, name, price, signals)
            print(f"\n审计结果:")
            print(f"  综合评分: {result.overall_score}/100")
            print(f"  评级: {result.overall_rating}")
            print(f"  矿工评分: {result.miner_score}")
            print(f"  规则引擎: {result.rule_engine_score}")
            print(f"  交叉验证: {result.cross_validation_score}")
            print(f"\n矿工反馈: {result.miner_feedback}")
            print(f"规则反馈: {result.rule_engine_feedback}")
    
    if args.summary:
        summary = auditor.get_audit_summary(30)
        print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()