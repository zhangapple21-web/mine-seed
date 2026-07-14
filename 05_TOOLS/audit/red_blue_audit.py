#!/usr/bin/env python3
"""
红蓝审计脚本 — Red Blue Audit for Recommendation Decisions

架构：
    推荐决策
        ├── GLM（看多）
        ├── NIM-DeepSeek（看空）
        └── 对比 → 产出 audit_YYYYMMDD.md

与 Publication Gate 的关系：
    红蓝审计和 Publication Gate 是两条独立的决策链路：
    - 红蓝审计：评估推荐决策的置信度，产出审计报告
    - Publication Gate：根据健康度决定是否发布推荐
    两者都独立运作，但审计结果可以作为 Publication Gate 的参考输入。
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent
OUTPUT_DIR = WORKSPACE / "05_TOOLS" / "mine_output" / "audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(WORKSPACE / "05_TOOLS" / "miner"))
from local_miner import call_model


class RedBlueAuditor:
    """红蓝审计器"""
    
    def __init__(self):
        self.audit_id = f"audit_{datetime.now().strftime('%Y%m%d')}"
    
    def audit_recommendation(self, stock_code: str, stock_name: str, 
                            recommendation: str, reasoning: str) -> dict:
        """
        对推荐决策进行红蓝审计
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            recommendation: 推荐方向（看多/看空/观望）
            reasoning: 推荐理由
        
        Returns:
            dict: 审计结果
        """
        red_prompt = f"""你是一位专业的股票分析专家（看多视角，Red Team）。
        
请分析以下股票的投资价值：
股票代码: {stock_code}
股票名称: {stock_name}
当前推荐: {recommendation}
推荐理由: {reasoning}

请从看多角度分析：
1. 该股票的优势和利好因素
2. 支持买入的理由
3. 潜在的上涨空间
4. 看多置信度（0-100）

请用简洁的中文回答，分点列出。"""
        
        blue_prompt = f"""你是一位专业的股票分析专家（看空视角，Blue Team）。
        
请分析以下股票的投资价值：
股票代码: {stock_code}
股票名称: {stock_name}
当前推荐: {recommendation}
推荐理由: {reasoning}

请从看空角度分析：
1. 该股票的劣势和利空因素
2. 支持卖出/规避的理由
3. 潜在的风险和下跌空间
4. 看空置信度（0-100）

请用简洁的中文回答，分点列出。"""
        
        print(f"[Red Blue Audit] 正在审计: {stock_name} ({stock_code})")
        
        red_result = call_model(red_prompt, max_tokens=500, capability="reasoning")
        blue_result = call_model(blue_prompt, max_tokens=500, capability="reasoning")
        
        red_confidence = self._extract_confidence(red_result)
        blue_confidence = self._extract_confidence(blue_result)
        
        result = {
            "audit_id": self.audit_id,
            "timestamp": datetime.now().isoformat(),
            "stock_code": stock_code,
            "stock_name": stock_name,
            "original_recommendation": recommendation,
            "original_reasoning": reasoning,
            "red_team": {
                "perspective": "看多",
                "analysis": self._get_content(red_result),
                "confidence": red_confidence,
                "provider": red_result.get("provider", ""),
                "model": red_result.get("model", ""),
            },
            "blue_team": {
                "perspective": "看空",
                "analysis": self._get_content(blue_result),
                "confidence": blue_confidence,
                "provider": blue_result.get("provider", ""),
                "model": blue_result.get("model", ""),
            },
            "consensus": self._calculate_consensus(red_confidence, blue_confidence),
        }
        
        return result
    
    def _extract_confidence(self, result: dict) -> int:
        """从模型输出中提取置信度"""
        content = self._get_content(result)
        try:
            import re
            match = re.search(r'置信度[：:]?\s*(\d+)', content)
            if match:
                return int(match.group(1))
            match = re.search(r'(\d+)%', content)
            if match:
                return int(match.group(1))
        except:
            pass
        return 50
    
    def _get_content(self, result: dict) -> str:
        """从API结果中提取内容"""
        if "error" in result:
            return f"Error: {result.get('error', '')}"
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _calculate_consensus(self, red_confidence: int, blue_confidence: int) -> dict:
        """计算红蓝共识"""
        diff = abs(red_confidence - blue_confidence)
        
        if diff <= 20:
            status = "共识一致"
            direction = "看多" if red_confidence >= blue_confidence else "看空"
        elif diff <= 40:
            status = "部分分歧"
            direction = "观望"
        else:
            status = "严重分歧"
            direction = "需进一步分析"
        
        return {
            "status": status,
            "direction": direction,
            "red_confidence": red_confidence,
            "blue_confidence": blue_confidence,
            "confidence_diff": diff,
            "overall_confidence": (red_confidence + blue_confidence) // 2,
        }
    
    def generate_report(self, audit_results: list) -> str:
        """生成审计报告"""
        report = f"""# 红蓝审计报告 — {datetime.now().strftime('%Y-%m-%d')}

> 审计对象：推荐决策
> 审计时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 审计ID：{self.audit_id}

---

## 审计概览

| # | 股票 | 原推荐 | 红蓝共识 | 红队置信度 | 蓝队置信度 | 分歧度 |
|---|---|---|---|---|---|---|
"""
        
        for i, result in enumerate(audit_results, 1):
            report += f"| {i} | {result['stock_name']} ({result['stock_code']}) | {result['original_recommendation']} | {result['consensus']['status']} | {result['consensus']['red_confidence']}% | {result['consensus']['blue_confidence']}% | {result['consensus']['confidence_diff']} |\n"
        
        report += "\n---\n\n## 详细分析\n\n"
        
        for i, result in enumerate(audit_results, 1):
            report += f"### {i}. {result['stock_name']} ({result['stock_code']})\n\n"
            report += f"**原推荐**: {result['original_recommendation']}\n\n"
            report += f"**原推荐理由**:\n{result['original_reasoning']}\n\n"
            
            report += "#### 🟥 红队（看多）\n\n"
            report += f"**置信度**: {result['consensus']['red_confidence']}%\n\n"
            report += f"**分析**:\n{result['red_team']['analysis']}\n\n"
            report += f"**模型**: {result['red_team']['provider']} / {result['red_team']['model']}\n\n"
            
            report += "#### 🟦 蓝队（看空）\n\n"
            report += f"**置信度**: {result['consensus']['blue_confidence']}%\n\n"
            report += f"**分析**:\n{result['blue_team']['analysis']}\n\n"
            report += f"**模型**: {result['blue_team']['provider']} / {result['blue_team']['model']}\n\n"
            
            report += "#### 📊 共识判断\n\n"
            report += f"**状态**: {result['consensus']['status']}\n"
            report += f"**建议方向**: {result['consensus']['direction']}\n"
            report += f"**分歧度**: {result['consensus']['confidence_diff']}\n"
            report += f"**综合置信度**: {result['consensus']['overall_confidence']}%\n\n"
            report += "---\n\n"
        
        report += """## 与 Publication Gate 的关系

**红蓝审计和 Publication Gate 是两条独立的决策链路**：

1. **红蓝审计**：评估推荐决策的置信度，产出审计报告
   - 输入：推荐决策（股票代码、推荐方向、理由）
   - 输出：红蓝双方的分析和共识判断
   - 目的：发现推荐中的盲点和风险

2. **Publication Gate**：根据健康度决定是否发布推荐
   - 输入：Health Score（来自 AdaptiveScorer）
   - 输出：四级路由（Public/Internal/Research/Discard）
   - 目的：控制是否对外发布

**两者关系**：
- 红蓝审计结果可以作为 Publication Gate 的参考输入
- 但两者独立运作，互不依赖
- 审计报告是内部参考，Publication Gate 是发布控制

---

## 审计结论

"""
        
        if audit_results:
            avg_diff = sum(r['consensus']['confidence_diff'] for r in audit_results) / len(audit_results)
            if avg_diff <= 20:
                report += "✅ 红蓝双方共识一致，推荐决策可信度较高。\n"
            elif avg_diff <= 40:
                report += "⚠️ 红蓝双方存在部分分歧，建议谨慎参考。\n"
            else:
                report += "🔴 红蓝双方严重分歧，建议暂停推荐，进一步分析。\n"
        else:
            report += "暂无审计结果。\n"
        
        return report
    
    def save_report(self, report: str) -> str:
        """保存审计报告"""
        filename = f"audit_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = OUTPUT_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="红蓝审计脚本")
    parser.add_argument("--code", type=str, help="股票代码")
    parser.add_argument("--name", type=str, help="股票名称")
    parser.add_argument("--recommendation", type=str, help="推荐方向")
    parser.add_argument("--reasoning", type=str, help="推荐理由")
    parser.add_argument("--from-advisor", action="store_true", help="从 advisor 报告读取推荐")
    
    args = parser.parse_args()
    
    auditor = RedBlueAuditor()
    
    if args.from_advisor:
        advisor_report = WORKSPACE / "05_TOOLS" / "mine_output" / "advisor" / f"advisor_{datetime.now().strftime('%Y%m%d')}.md"
        if advisor_report.exists():
            with open(advisor_report, "r", encoding="utf-8") as f:
                content = f.read()
            import re
            matches = re.findall(r'### (\d+)\. (\S+) \((\d+)\)', content)
            audit_results = []
            for i, name, code in matches:
                reasoning_match = re.search(rf'### {i}\. {name} \({code}\)(.*?)(?=\n###|$)', content, re.DOTALL)
                reasoning = reasoning_match.group(1) if reasoning_match else "无详细理由"
                result = auditor.audit_recommendation(code, name, "看多", reasoning)
                audit_results.append(result)
            
            report = auditor.generate_report(audit_results)
            saved_path = auditor.save_report(report)
            print(f"[Red Blue Audit] 审计报告已保存: {saved_path}")
            return
    
    if args.code and args.name:
        result = auditor.audit_recommendation(
            args.code, 
            args.name, 
            args.recommendation or "看多", 
            args.reasoning or "无"
        )
        report = auditor.generate_report([result])
        saved_path = auditor.save_report(report)
        print(f"[Red Blue Audit] 审计报告已保存: {saved_path}")
    else:
        print("请提供股票代码和名称，或使用 --from-advisor 从 advisor 报告读取")


if __name__ == "__main__":
    main()