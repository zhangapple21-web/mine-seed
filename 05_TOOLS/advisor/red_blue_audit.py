#!/usr/bin/env python3
"""
Red-Blue Auditor — 红蓝审计脚本

审计对象：荐股推荐决策
核心机制：红方（GLM，看多）vs 蓝方（NIM-DeepSeek，看空）对同一推荐进行正反方辩论
输出：共识点 / 分歧点 / 风险标记 / 最终置信度

与 Smelter Gate 的关系：
------------------------
当前版本（v1）：
  red_blue_audit.py 是独立审计工具，产出报告供人查看。
  不直接修改任何自动化决策，不影响 Gate 的拒绝逻辑。
  
  接入链路：
    adata_advisor.py → red_blue_audit.py → audit_YYYYMMDD.md（报告）
    
  Smelter Gate 的拒绝逻辑保持独立运行：
    advisor 推荐 → Smelter Gate 检查 → PASS / REJECT
    
未来版本（v2，待 Governor 批准）：
  当 audit 报告的 "分歧指数" > 阈值 或 "风险标记" = HIGH 时，
  自动将推荐标记为 "需人工复核"，反馈进 Gate 的决策链路。
  
  接入链路：
    adata_advisor.py → red_blue_audit.py → audit_YYYYMMDD.md
                                    ↓
                              若风险高 → Smelter Gate 降级处理
                                    ↓
                              若风险低 → Smelter Gate 正常放行

当前两者是并行关系，不是嵌套关系。

用法：
  python3 red_blue_audit.py --stocks "000001,600519"    # 审计指定股票
  python3 red_blue_audit.py --file advisor_20260714.md  # 从荐股报告读取
"""

import os
import sys
import json
import re
import logging
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 加载 free_llm
sys.path.insert(0, str(Path(__file__).parent / ".." / "miner"))
from free_llm import call

# 日志
LOG_DIR = Path(__file__).parent / ".." / "mine_output" / "audit"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "red_blue_audit.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("red_blue_audit")

CLOUD_DIR = Path(os.environ.get("CLOUD_DIR", "/workspace/fengzi-repos/mine-seed/cloud/audit"))


class RedBlueAuditor:
    """红蓝审计引擎"""

    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.today_compact = datetime.now().strftime("%Y%m%d")

    def _red_team(self, stock_code: str, stock_name: str) -> dict:
        """红方：看多理由（GLM）"""
        prompt = f"""对股票 {stock_code} ({stock_name}) 进行看多分析。

请从以下角度给出看多的理由（每个角度1-2句话）：
1. 技术面：趋势、支撑、量价关系
2. 基本面：业绩、行业地位、成长性
3. 资金面：主力动向、北向资金、机构持仓
4. 催化剂：近期可能的利好事件

输出格式：
- 看多总评级：强烈看好 / 看好 / 中性偏看好
- 核心理由（3条以内，每条50字以内）
- 目标价位区间（如有）
- 风险提醒（1条）
"""
        try:
            result = call(
                prompt,
                system="你是专业的A股买方分析师，擅长发现投资机会。",
                max_tokens=800,
                temperature=0.3,
                prefer='glm'
            )
            return {
                "side": "red",
                "stance": "看多",
                "content": result["content"],
                "channel": result["channel"],
                "model": result["model"],
                "elapsed": result.get("elapsed", 0),
            }
        except Exception as e:
            logger.error(f"[RED] {stock_code} 失败: {e}")
            return {"side": "red", "stance": "看多", "content": f"调用失败: {e}", "error": True}

    def _blue_team(self, stock_code: str, stock_name: str) -> dict:
        """蓝方：看空理由（NIM-DeepSeek）"""
        prompt = f"""对股票 {stock_code} ({stock_name}) 进行看空/风险提示分析。

请从以下角度给出看空或风险提示的理由（每个角度1-2句话）：
1. 技术面：趋势转弱、压力位、量价背离
2. 基本面：业绩下滑、估值过高、行业风险
3. 资金面：主力流出、大股东减持、筹码松动
4. 催化剂：近期可能的利空事件

输出格式：
- 看空总评级：强烈看空 / 看空 / 中性偏空 / 仅风险提示
- 核心风险（3条以内，每条50字以内）
- 止损建议（如有）
- 唯一看多理由（1条，用于平衡视角）
"""
        try:
            result = call(
                prompt,
                system="你是专业的A股风险分析师，擅长发现潜在风险。",
                max_tokens=800,
                temperature=0.3,
                prefer='nim'
            )
            return {
                "side": "blue",
                "stance": "看空",
                "content": result["content"],
                "channel": result["channel"],
                "model": result["model"],
                "elapsed": result.get("elapsed", 0),
            }
        except Exception as e:
            logger.error(f"[BLUE] {stock_code} 失败: {e}")
            return {"side": "blue", "stance": "看空", "content": f"调用失败: {e}", "error": True}

    def _extract_key_points(self, text: str) -> list:
        """从 LLM 输出中提取关键要点"""
        points = []
        # 匹配 "- " 或 "* " 或数字开头的行
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\.', line):
                clean = line.lstrip('- *').lstrip('0123456789.').strip()
                if clean and len(clean) > 10:
                    points.append(clean)
        return points[:5]  # 最多取5条

    def _debate(self, stock_code: str, stock_name: str) -> dict:
        """红蓝辩论：并行调用红方和蓝方"""
        logger.info(f"[DEBATE] {stock_code} {stock_name}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            red_future = executor.submit(self._red_team, stock_code, stock_name)
            blue_future = executor.submit(self._blue_team, stock_code, stock_name)
            red = red_future.result()
            blue = blue_future.result()

        # 提取关键要点
        red_points = self._extract_key_points(red["content"])
        blue_points = self._extract_key_points(blue["content"])

        # 共识点：双方提到的共同主题（简单文本匹配）
        consensus = []
        for rp in red_points:
            for bp in blue_points:
                # 如果有共同关键词
                rp_words = set(rp[:20].split())
                bp_words = set(bp[:20].split())
                if len(rp_words & bp_words) >= 2:
                    consensus.append(f"双方均关注: {rp[:30]}...")
                    break

        # 分歧点：红方看多 vs 蓝方看空的核心差异
        divergence = [
            f"红方: {red_points[0][:40]}..." if red_points else "红方未提供要点",
            f"蓝方: {blue_points[0][:40]}..." if blue_points else "蓝方未提供要点",
        ]

        # 风险标记
        risk_mark = "LOW"
        blue_text = blue["content"].lower()
        if "强烈看空" in blue_text or "高风险" in blue_text or "止损" in blue_text:
            risk_mark = "HIGH"
        elif "看空" in blue_text or "估值过高" in blue_text or "减持" in blue_text:
            risk_mark = "MEDIUM"

        # 最终置信度（简化算法）
        # 红方看多强度 + 蓝方风险等级 → 综合评分
        confidence = 50  # 基准
        if "强烈看好" in red["content"]:
            confidence += 20
        elif "看好" in red["content"]:
            confidence += 10

        if risk_mark == "HIGH":
            confidence -= 30
        elif risk_mark == "MEDIUM":
            confidence -= 15

        confidence = max(0, min(100, confidence))

        # 分歧指数（0-100，越高分歧越大）
        divergence_score = 50  # 基准
        if risk_mark == "HIGH":
            divergence_score += 30
        if "强烈看好" in red["content"] and risk_mark == "HIGH":
            divergence_score += 20
        divergence_score = min(100, divergence_score)

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "red": red,
            "blue": blue,
            "consensus": list(set(consensus))[:3],
            "divergence": divergence,
            "risk_mark": risk_mark,
            "confidence": confidence,
            "divergence_score": divergence_score,
            "audit_time": datetime.now().isoformat(),
        }

    def audit_stocks(self, stocks: list) -> list:
        """审计多只股票"""
        logger.info(f"[AUDIT] 开始审计 {len(stocks)} 只股票")
        results = []
        for stock in stocks:
            code = stock.get("code", "")
            name = stock.get("name", "")
            if not code:
                continue
            result = self._debate(code, name)
            results.append(result)
        return results

    def generate_report(self, results: list) -> str:
        """生成 Markdown 审计报告"""
        lines = [
            f"# Red-Blue Audit Report — {self.today}",
            "",
            "> 红方(GLM)看多 vs 蓝方(NIM-DeepSeek)看空",
            "> 当前版本：v1（独立审计，不接入自动化决策）",
            f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 审计摘要",
            "",
            f"- 审计股票数: {len(results)}",
            f"- 高风险标记: {sum(1 for r in results if r['risk_mark'] == 'HIGH')}",
            f"- 中等风险: {sum(1 for r in results if r['risk_mark'] == 'MEDIUM')}",
            f"- 低风险: {sum(1 for r in results if r['risk_mark'] == 'LOW')}",
            f"- 平均置信度: {sum(r['confidence'] for r in results) / len(results):.0f}/100" if results else "- 平均置信度: N/A",
            "",
            "---",
            "",
        ]

        for i, r in enumerate(results, 1):
            risk_icon = "🔴" if r["risk_mark"] == "HIGH" else "🟡" if r["risk_mark"] == "MEDIUM" else "🟢"
            lines.extend([
                f"## {i}. {r['stock_code']} {r['stock_name']}",
                "",
                f"- **风险标记**: {risk_icon} {r['risk_mark']}",
                f"- **最终置信度**: {r['confidence']}/100",
                f"- **分歧指数**: {r['divergence_score']}/100",
                "",
                "### 红方观点（看多）",
                f"> 渠道: {r['red']['channel']}/{r['red']['model']}",
                "",
            ])
            for p in self._extract_key_points(r["red"]["content"]):
                lines.append(f"- {p}")
            lines.append("")

            lines.extend([
                "### 蓝方观点（看空/风险）",
                f"> 渠道: {r['blue']['channel']}/{r['blue']['model']}",
                "",
            ])
            for p in self._extract_key_points(r["blue"]["content"]):
                lines.append(f"- {p}")
            lines.append("")

            if r["consensus"]:
                lines.extend([
                    "### 共识点",
                    "",
                ])
                for c in r["consensus"]:
                    lines.append(f"- {c}")
                lines.append("")

            lines.extend([
                "### 分歧点",
                "",
            ])
            for d in r["divergence"]:
                lines.append(f"- {d}")
            lines.append("")

            lines.extend(["---", ""])

        # 与 Smelter Gate 的关系说明
        lines.extend([
            "## 与 Smelter Gate 的关系",
            "",
            "**当前状态（v1）**:",
            "- Red-Blue Audit 是独立审计工具，产出报告供人查看",
            "- 不直接修改任何自动化决策",
            "- Smelter Gate 的拒绝逻辑保持独立运行",
            "",
            "**未来状态（v2，待 Governor 批准）**:",
            "- 当 `分歧指数 > 80` 或 `风险标记 = HIGH` 时，",
            "- 自动标记推荐为 '需人工复核'",
            "- 反馈进 Gate 决策链路，触发降级处理",
            "",
            "---",
            "",
            "*本报告由 Red-Blue Auditor 自动生成，仅供参考，不构成投资建议。*",
        ])

        return "\n".join(lines)

    def save(self, results: list, report_md: str):
        """保存审计结果"""
        CLOUD_DIR.mkdir(parents=True, exist_ok=True)

        json_file = CLOUD_DIR / f"audit_{self.today_compact}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        md_file = CLOUD_DIR / f"audit_{self.today_compact}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(report_md)

        logger.info(f"[SAVE] JSON: {json_file}")
        logger.info(f"[SAVE] Markdown: {md_file}")
        return json_file, md_file

    def run(self, stocks: list = None):
        """完整运行"""
        if not stocks:
            logger.warning("[RUN] 未提供股票列表，生成空报告")
            report_md = f"# Red-Blue Audit — {self.today}\n\n未提供审计对象。\n"
            return {"results": [], "md_file": None}

        logger.info("=" * 50)
        logger.info("Red-Blue Auditor 启动")
        logger.info("=" * 50)

        results = self.audit_stocks(stocks)
        report_md = self.generate_report(results)
        json_file, md_file = self.save(results, report_md)

        logger.info(f"[DONE] 审计完成: {len(results)} 只股票")
        return {
            "results": results,
            "json_file": str(json_file),
            "md_file": str(md_file),
        }


def parse_advisor_report(filepath: str) -> list:
    """从荐股报告中提取股票列表"""
    stocks = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单匹配：找 "代码 名称" 格式
        # 如 "000001 平安银行" 或 "sh600519 贵州茅台"
        pattern = r'[shszbj]?\d{6}\s+[^\n\d]{2,10}'
        matches = re.findall(pattern, content)
        for m in matches:
            parts = m.strip().split()
            if len(parts) >= 2:
                code = parts[0]
                name = parts[1]
                stocks.append({"code": code, "name": name})

        # 去重
        seen = set()
        unique = []
        for s in stocks:
            key = s["code"]
            if key not in seen:
                seen.add(key)
                unique.append(s)
        return unique
    except Exception as e:
        logger.error(f"解析荐股报告失败: {e}")
        return []


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Red-Blue Auditor")
    parser.add_argument("--stocks", help="股票代码列表，逗号分隔，如 '000001,600519'")
    parser.add_argument("--file", help="荐股报告文件路径")
    parser.add_argument("--names", help="股票名称列表，逗号分隔，与 --stocks 对应")
    args = parser.parse_args()

    stocks = []

    if args.file:
        stocks = parse_advisor_report(args.file)
        logger.info(f"从报告解析到 {len(stocks)} 只股票")

    if args.stocks:
        codes = args.stocks.split(',')
        names = args.names.split(',') if args.names else codes
        for code, name in zip(codes, names):
            stocks.append({"code": code.strip(), "name": name.strip()})

    if not stocks:
        # 默认审计示例
        stocks = [
            {"code": "000001", "name": "平安银行"},
            {"code": "600519", "name": "贵州茅台"},
        ]
        logger.info("使用默认示例股票")

    auditor = RedBlueAuditor()
    result = auditor.run(stocks)
    print(f"\n审计完成: {len(result['results'])} 只股票")
    if result.get("md_file"):
        print(f"报告: {result['md_file']}")


if __name__ == "__main__":
    main()
