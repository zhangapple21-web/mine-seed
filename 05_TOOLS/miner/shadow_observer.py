#!/usr/bin/env python3
"""
AUM-MISSION-EXP-001 — Shadow Observer (影子观察员)

> Miner 今天的唯一身份：影子观察员
> 不读 Recommendation 主流程，不写 Repository，不写 Runtime State
> 只在 03_DATA/shadow_audit/ 留下观察痕迹
> 7天后用证据决定是否升级，否则实验结束

## 严格边界

DO:
- 读取 StockAdvisor 生成的 report 文件（只读，不修改）
- 调用 task_router 匹配 audit_only 任务画像
- 调用矿工对推荐做多模型评估
- 把评估结果写入 03_DATA/shadow_audit/

DON'T:
- ❌ 不接入 daily_runner.py 主流程
- ❌ 不修改 StockAdvisor 推荐生成逻辑
- ❌ 不修改 Policy Manager / Admission / Roundtable
- ❌ 不修改 Recommendation 数据结构
- ❌ 不把矿工输出写入 audit_results.json
- ❌ 不把矿工输出用于策略调整
- ❌ 不让矿工调用影响主流程的任何开关

## 数据流

```
StockAdvisor → mine_output/advisor/advisor_YYYYMMDD.md（主流程产物）
                        ↓
                    【只读】
                        ↓
Shadow Observer → 03_DATA/shadow_audit/shadow_audit_YYYYMMDD.jsonl（独立存储）
                        ↓
                  7天后汇总
                        ↓
                SHADOW_AUDIT_REPORT.md
```

## 退出机制

3个问题，至少2个证据支持才能升级：
1. 是否提供新信息？
2. 是否提高预测质量？
3. 关闭后是否明显下降？
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# 路径设置：Shadow 产物存到独立的影子目录
_WORKSPACE = Path("c:/Users/User/ace_workspace/mine-seed")
_SHADOW_DIR = _WORKSPACE / "03_DATA" / "shadow_audit"
_SHADOW_DIR.mkdir(parents=True, exist_ok=True)

# 主流程产物目录（只读）
_ADVISOR_OUTPUT = _WORKSPACE / "05_TOOLS" / "mine_output" / "advisor"


class ShadowObserver:
    """AUM-MISSION-EXP-001 — 影子观察员
    
    严格只读：只读主流程产物，不写主流程任何文件
    独立存储：只写 03_DATA/shadow_audit/
    无副作用：所有异常被吞掉，不影响主流程
    """
    
    MISSION_ID = "AUM-MISSION-EXP-001"
    MISSION_NAME = "Shadow Observer"
    MISSION_PERIOD_DAYS = 7
    
    def __init__(self):
        self.shadow_log = _SHADOW_DIR / "shadow_audit_log.jsonl"
        self.miner_call_log = _SHADOW_DIR / "miner_call_log.jsonl"
    
    def _get_router(self):
        """延迟加载 task_router（避免 import 失败影响主流程）"""
        try:
            import task_router
            return task_router.router
        except Exception as e:
            # Shadow 模块失败不应影响任何东西
            return None
    
    def _get_fallback_workers(self) -> List:
        """获取 audit_only 任务的 fallback 工人链"""
        router = self._get_router()
        if router is None:
            return []
        try:
            chain = router.get_fallback_chain("audit_only")
            return chain
        except Exception:
            return []
    
    def _read_latest_recommendations(self) -> List[Dict[str, Any]]:
        """只读：读取主流程最新推荐报告
        
        只读！不修改任何主流程文件。
        """
        try:
            today = datetime.now().strftime("%Y%m%d")
            # 尝试读取今日报告
            report_file = _ADVISOR_OUTPUT / f"advisor_{today}.md"
            
            if not report_file.exists():
                # 找最近一天的
                reports = sorted(_ADVISOR_OUTPUT.glob("advisor_*.md"), reverse=True)
                if not reports:
                    return []
                report_file = reports[0]
            
            content = report_file.read_text(encoding="utf-8")
            
            # 解析推荐：推荐N：XXX（600000） 格式
            recs = []
            for match in re.finditer(r'推荐\d+：([^（]+)（(\d{6})）', content):
                recs.append({
                    "name": match.group(1).strip(),
                    "code": match.group(2).strip(),
                    "source_report": report_file.name,
                    "read_only": True  # 明确标记：只读
                })
            return recs
        except Exception:
            return []
    
    def _call_miner(self, worker_id: str, model: str, prompt: str,
                    timeout: int = 30) -> Optional[Dict]:
        """调用单个矿工（仅影子观察用途）
        
        通过 TaskRouter.call_worker() 调用，不直接连接 Provider。
        TaskRouter 负责选择正确的 ProviderAdapter（OneAPI / LocalMiner）。
        """
        try:
            router = self._get_router()
            if router is None:
                return None
            
            messages = [
                {"role": "system", "content": "你是股票审计员。对给定推荐做技术面和风险评估，给0-100分。"},
                {"role": "user", "content": prompt}
            ]
            
            result = router.call_worker(worker_id, messages, max_tokens=500, temperature=0.1)
            
            if result.get("success"):
                return {
                    "worker_id": worker_id,
                    "model": model,
                    "content": result.get("content", ""),
                    "provider": result.get("provider", ""),
                    "success": True
                }
            return None
        except Exception:
            return None
    
    def _extract_score(self, content: str) -> Optional[int]:
        """从矿工输出中提取分数"""
        if not content:
            return None
        match = re.search(r'总分[:：]\s*(\d+)', content)
        if match:
            return int(match.group(1))
        match = re.search(r'质量分[:：]\s*(\d+)', content)
        if match:
            return int(match.group(1))
        return None
    
    def _build_audit_prompt(self, rec: Dict[str, Any]) -> str:
        """构建审计 prompt"""
        return f"""审计以下股票推荐（只评估，不做选股）：

代码：{rec.get('code', 'N/A')}
名称：{rec.get('name', 'N/A')}

请评估（总分0-100）：
- 技术面（0-30）
- 风险（0-30）
- 估值（0-20）
- 时机（0-20）

输出格式：
总分: X
理由: <一句话>
"""
    
    def observe(self) -> Dict[str, Any]:
        """执行一次影子观察
        
        严格只读：只读主流程产物，不修改任何主流程文件
        独立存储：只写 03_DATA/shadow_audit/
        """
        observation_id = f"shadow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()
        
        # 1. 只读：读取主流程推荐
        recommendations = self._read_latest_recommendations()
        
        if not recommendations:
            result = {
                "observation_id": observation_id,
                "timestamp": timestamp,
                "mission": self.MISSION_ID,
                "role": "Shadow Observer",
                "recommendations_found": 0,
                "miner_audits": [],
                "miner_pool_available": False,
                "note": "No recommendations found (main flow not run today)"
            }
            self._log_shadow(result)
            return result
        
        # 2. 只读：获取矿工 fallback 链
        fallback_chain = self._get_fallback_workers()
        
        if not fallback_chain:
            result = {
                "observation_id": observation_id,
                "timestamp": timestamp,
                "mission": self.MISSION_ID,
                "role": "Shadow Observer",
                "recommendations_found": len(recommendations),
                "miner_audits": [],
                "miner_pool_available": False,
                "note": "Miner pool unavailable (router/fallback empty)"
            }
            self._log_shadow(result)
            return result
        
        # 3. 影子观察：对每条推荐调用矿工（不污染主流程）
        miner_audits = []
        for rec in recommendations:
            prompt = self._build_audit_prompt(rec)
            
            # 至少调用2个矿工
            target_workers = fallback_chain[:2] if len(fallback_chain) >= 2 else fallback_chain
            
            evaluations = []
            for worker_id, model in target_workers:
                eval_result = self._call_miner(worker_id, model, prompt, timeout=60)
                if eval_result:
                    eval_result["score"] = self._extract_score(eval_result.get("content", ""))
                    evaluations.append(eval_result)
                    # 记录矿工调用
                    self._log_miner_call(observation_id, rec, eval_result)
            
            # 计算矿工共识分
            valid_scores = [e["score"] for e in evaluations if e.get("score") is not None]
            if len(valid_scores) >= 2:
                consensus = sum(valid_scores) // len(valid_scores)
                consistency = max(0.0, 1.0 - (max(valid_scores) - min(valid_scores)) / 100.0)
            elif len(valid_scores) == 1:
                consensus = valid_scores[0]
                consistency = None
            else:
                consensus = None
                consistency = None
            
            miner_audits.append({
                "recommendation": rec,  # 只读副本
                "consensus_score": consensus,
                "consistency": round(consistency, 2) if consistency is not None else None,
                "evaluations": evaluations,
                "shadow_only": True  # 明确：仅作观察，不影响主流程
            })
        
        result = {
            "observation_id": observation_id,
            "timestamp": timestamp,
            "mission": self.MISSION_ID,
            "role": "Shadow Observer",
            "recommendations_found": len(recommendations),
            "miner_audits": miner_audits,
            "miner_pool_available": True,
            "workers_called": sum(len(m["evaluations"]) for m in miner_audits),
            "note": "Shadow observation only. Main flow unchanged."
        }
        
        self._log_shadow(result)
        return result
    
    def _log_shadow(self, result: Dict):
        """记录影子观察结果（独立文件）"""
        try:
            with open(self.shadow_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
        except Exception:
            pass  # 影子模块失败不应影响任何东西
    
    def _log_miner_call(self, obs_id: str, rec: Dict, eval_result: Dict):
        """记录矿工调用详情（独立文件）"""
        try:
            entry = {
                "observation_id": obs_id,
                "timestamp": datetime.now().isoformat(),
                "recommendation": rec,
                "evaluation": eval_result,
                "shadow_only": True
            }
            with open(self.miner_call_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass


def main():
    """CLI 入口：执行一次影子观察"""
    observer = ShadowObserver()
    result = observer.observe()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[Mission] {observer.MISSION_ID} — {observer.MISSION_NAME}")
    print(f"[Period] {observer.MISSION_PERIOD_DAYS} days")
    print(f"[Storage] {_SHADOW_DIR}")
    print(f"[Note] Shadow observer only. Main flow unchanged.")


if __name__ == "__main__":
    main()