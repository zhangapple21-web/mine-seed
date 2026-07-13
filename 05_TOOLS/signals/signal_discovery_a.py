#!/usr/bin/env python3
"""
Signal Discovery Pipeline v2 — 0 依赖，free_llm 驱动

功能：
- 每日自动发现市场量化信号（当前默认 A 股市场）
- 信号类型：动量突破、均值回归、量价背离、资金流异动、业绩超预期
- 数据源：adata 多源融合 → 降级到 free_llm 直接分析
- 输出：Markdown 信号报告 + JSON 信号卡片

可复用 Blueprint：
- 信号类型定义（5 种）与具体数据源解耦
- 多源数据 → 信号 → 排序 → 输出的 Pipeline 架构
- LLM 驱动的信号发现 + 结构化 JSON 提取模式

用法：
  python3 signal_discovery_a.py          # 生成今日信号
  python3 signal_discovery_a.py --list   # 列出支持的信号类型
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 日志
LOG_DIR = Path(__file__).parent / ".." / "mine_output" / "signals"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "signal_discovery.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("signal_discovery")

# 加载 free_llm
sys.path.insert(0, str(Path(__file__).parent / ".." / "miner"))
from free_llm import call

# ============================================================
# 信号类型定义 — Blueprint 层，与具体市场解耦
# ============================================================
# 当前默认 A 股市场，但信号类型本身是通用的
# 如需适配其他市场，只需更换数据源层（_get_market_overview / _get_hot_sectors）
SIGNAL_TYPES = {
    "momentum_breakout": {
        "name": "动量突破",
        "desc": "股价突破近期整理平台，成交量放大，短期趋势向上",
        "indicators": ["价格突破20日高点", "成交量>MA5均量1.5倍", "MACD金叉"],
    },
    "mean_reversion": {
        "name": "均值回归",
        "desc": "股价短期超跌，偏离均线过远，存在反弹机会",
        "indicators": ["股价偏离MA20 > -8%", "RSI(14) < 30", "缩量下跌"],
    },
    "volume_price_divergence": {
        "name": "量价背离",
        "desc": "价格与成交量出现背离，预示趋势可能反转",
        "indicators": ["价格新高/成交量未新高", "OBV背离", "筹码松动"],
    },
    "capital_inflow": {
        "name": "资金异动",
        "desc": "主力资金连续净流入，机构建仓迹象明显",
        "indicators": ["主力净流入3日>0", "大单占比>30%", "北向资金增持"],
    },
    "earnings_surprise": {
        "name": "业绩超预期",
        "desc": "季报/预告业绩大幅超预期，市场反应滞后",
        "indicators": ["净利润同比>50%", "营收同比>30%", "预告后涨幅<5%"],
    },
}


class SignalDiscoveryEngine:
    """信号发现引擎 — Blueprint 实现
    
    当前默认 A 股市场，但架构可复用到任何有数据源的市场。
    只需替换 _get_market_overview() 和 _get_hot_sectors() 方法。
    """

    def __init__(self):
        self.adata = None
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.today_compact = datetime.now().strftime("%Y%m%d")
        try:
            import adata
            self.adata = adata
            logger.info("[adata] 已加载")
        except ImportError:
            logger.warning("[adata] 未安装，将使用纯LLM分析")

    def _get_market_overview(self) -> str:
        """获取市场概况（adata 或 LLM）"""
        if self.adata:
            try:
                # 尝试获取指数行情
                indices = [
                    ("000001", "上证指数"),
                    ("399001", "深证成指"),
                    ("399006", "创业板指"),
                    ("000688", "科创50"),
                ]
                lines = []
                for code, name in indices:
                    try:
                        df = self.adata.stock.market.get_market(stock_code=code, k_type=1)
                        if df is not None and len(df) > 0:
                            latest = df.iloc[-1]
                            close = float(latest.get('close', 0))
                            pre_close = float(latest.get('pre_close', close))
                            change = (close - pre_close) / pre_close * 100 if pre_close > 0 else 0
                            lines.append(f"  {name}: {close:.2f} ({change:+.2f}%)")
                    except:
                        continue
                if lines:
                    return "今日指数:\n" + "\n".join(lines)
            except Exception as e:
                logger.warning(f"[adata] 指数获取失败: {e}")
        return ""

    def _get_hot_sectors(self) -> str:
        """获取热门板块（adata 或 LLM）"""
        if self.adata:
            try:
                # 尝试获取概念板块涨幅
                df = self.adata.stock.market.get_concept_spot()
                if df is not None and len(df) > 0:
                    df = df.sort_values(by='change_pct', ascending=False)
                    top = df.head(5)
                    lines = []
                    for _, row in top.iterrows():
                        name = row.get('name', '')
                        change = row.get('change_pct', 0)
                        lines.append(f"  {name}: {change:+.2f}%")
                    return "热门板块:\n" + "\n".join(lines)
            except Exception as e:
                logger.warning(f"[adata] 板块获取失败: {e}")
        return ""

    def discover_signals(self) -> List[Dict[str, Any]]:
        """发现市场信号 — LLM 驱动
        
        Blueprint 核心逻辑：多源数据输入 → LLM 信号发现 → 结构化 JSON 输出
        当前数据源默认 A 股市场，但 prompt 模板本身是通用的。
        """
        logger.info("[discover] 开始信号发现...")

        # 收集市场数据
        market_data = self._get_market_overview()
        sector_data = self._get_hot_sectors()

        # 构建 prompt
        data_section = ""
        if market_data:
            data_section += market_data + "\n\n"
        if sector_data:
            data_section += sector_data + "\n\n"

        signal_descriptions = []
        for key, info in SIGNAL_TYPES.items():
            signal_descriptions.append(
                f"- {info['name']} ({key}): {info['desc']}\n"
                f"  关键指标: {', '.join(info['indicators'])}"
            )

        prompt = f"""今天是 {self.today}。

{data_section}
请作为量化分析师，基于当前市场环境，从以下信号类型中发现最有价值的2-3个交易信号：

{chr(10).join(signal_descriptions)}

对每个发现的信号，请输出：
1. 信号类型（从上面5种中选择）
2. 信号方向（看多/看空）
3. 置信度（0-100）
4. 相关板块/概念
5. 触发理由（50字以内）
6. 建议关注标的（2-3只，格式：代码 名称）

输出格式必须是合法的JSON数组：
```json
[
  {{
    "type": "momentum_breakout",
    "direction": "看多",
    "confidence": 78,
    "sector": "半导体",
    "reason": "...",
    "stocks": ["603986 兆易创新", "688012 中微公司"]
  }}
]
```
"""

        # 调用 free_llm
        try:
            result = call(
                prompt,
                system="你是专业的量化信号分析师。只输出JSON，不要解释。",
                max_tokens=2000,
                temperature=0.3,
                prefer='glm'
            )
            content = result.get("content", "")

            # 提取 JSON
            signals = self._extract_signals(content)
            logger.info(f"[discover] 发现 {len(signals)} 个信号")

            # 添加元数据
            for s in signals:
                s["discover_date"] = self.today
                s["source"] = f"{result['channel']}/{result['model']}"
                s["discover_time"] = datetime.now().strftime("%H:%M:%S")

            return signals

        except Exception as e:
            logger.error(f"[discover] 信号发现失败: {e}")
            return []

    def _extract_signals(self, text: str) -> List[Dict]:
        """从 LLM 输出中提取 JSON 信号"""
        # 先找 ```json 块
        import re
        m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text, re.IGNORECASE)
        if m:
            json_str = m.group(1)
        else:
            # 找方括号
            m2 = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
            if m2:
                json_str = m2.group(0)
            else:
                json_str = text

        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
        except json.JSONDecodeError:
            logger.warning("[extract] JSON解析失败，尝试逐对象提取")
            # 尝试提取每个 {...}
            objs = []
            for match in re.finditer(r'\{[^{}]*"type"[^{}]*\}', text):
                try:
                    obj = json.loads(match.group(0))
                    objs.append(obj)
                except:
                    continue
            return objs

        return []

    def generate_report(self, signals: List[Dict]) -> str:
        """生成 Markdown 报告"""
        lines = [
            f"# Signal Discovery — {self.today}",
            "",
            f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"> 信号数量: {len(signals)}",
            "",
            "---",
            "",
        ]

        for i, sig in enumerate(signals, 1):
            sig_type = sig.get("type", "unknown")
            type_info = SIGNAL_TYPES.get(sig_type, {"name": sig_type, "desc": ""})
            direction = sig.get("direction", "未知")
            confidence = sig.get("confidence", 0)
            sector = sig.get("sector", "-")
            reason = sig.get("reason", "-")
            stocks = sig.get("stocks", [])
            source = sig.get("source", "LLM")

            # 方向 emoji
            dir_icon = "📈" if "多" in direction else "📉" if "空" in direction else "⚖️"
            # 置信度颜色
            if confidence >= 70:
                conf_color = "🟢"
            elif confidence >= 50:
                conf_color = "🟡"
            else:
                conf_color = "🔴"

            lines.extend([
                f"## 信号 {i}: {type_info['name']} {dir_icon}",
                "",
                f"- **方向**: {direction}",
                f"- **置信度**: {conf_color} {confidence}/100",
                f"- **板块**: {sector}",
                f"- **来源**: {source}",
                "",
                f"**触发理由**: {reason}",
                "",
            ])

            if stocks:
                lines.append("**建议关注**:")
                for s in stocks:
                    lines.append(f"- {s}")
                lines.append("")

            lines.extend([
                "---",
                "",
            ])

        lines.extend([
            "## 免责声明",
            "",
            "本报告由AI自动生成，仅供研究参考，不构成投资建议。",
            "股市有风险，投资需谨慎。",
            "",
        ])

        return "\n".join(lines)

    def save(self, signals: List[Dict], report_md: str):
        """保存信号和报告"""
        # 保存 JSON
        cloud_dir = Path(os.environ.get("CLOUD_DIR", "/workspace/fengzi-repos/mine-seed/cloud/signals"))
        cloud_dir.mkdir(parents=True, exist_ok=True)

        json_file = cloud_dir / f"signals_{self.today_compact}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)
        logger.info(f"[save] JSON: {json_file}")

        # 保存 Markdown
        md_file = cloud_dir / f"signals_{self.today_compact}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(report_md)
        logger.info(f"[save] Markdown: {md_file}")

        # 同时保存到本地输出目录
        local_json = LOG_DIR / f"signals_{self.today_compact}.json"
        local_md = LOG_DIR / f"signals_{self.today_compact}.md"
        with open(local_json, 'w', encoding='utf-8') as f:
            json.dump(signals, f, ensure_ascii=False, indent=2)
        with open(local_md, 'w', encoding='utf-8') as f:
            f.write(report_md)

        return json_file, md_file

    def run(self):
        """完整运行流程"""
        logger.info("=" * 50)
        logger.info("Signal Discovery Engine 启动")
        logger.info("=" * 50)

        t0 = time.time()
        signals = self.discover_signals()
        elapsed = time.time() - t0

        if not signals:
            logger.warning("[run] 未发现信号，生成空报告")
            report_md = f"# Signal Discovery — {self.today}\n\n今日未发现明显信号。\n"
        else:
            report_md = self.generate_report(signals)

        json_file, md_file = self.save(signals, report_md)

        logger.info(f"[run] 完成: {len(signals)} 个信号, {elapsed:.1f}s")
        logger.info(f"[run] 报告: {md_file}")

        return {
            "signals": signals,
            "json_file": str(json_file),
            "md_file": str(md_file),
            "elapsed": elapsed,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Signal Discovery Engine")
    parser.add_argument("--list", action="store_true", help="列出支持的信号类型")
    args = parser.parse_args()

    if args.list:
        print("支持的信号类型:")
        for key, info in SIGNAL_TYPES.items():
            print(f"  {key}: {info['name']} — {info['desc']}")
        return

    discovery = SignalDiscoveryEngine()
    result = discovery.run()
    print(f"\n信号发现完成: {len(result['signals'])} 个信号")
    print(f"报告: {result['md_file']}")


if __name__ == "__main__":
    main()
