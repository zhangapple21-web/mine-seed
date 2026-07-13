#!/usr/bin/env python3
"""
Miner Assistant — 矿工推理引擎

本地模型用于「不被打断的思考」——完整推理链路，无内部审查。
审核是对外服务的护栏，在输出边界（降敏词表/输出宪法）生效，
不在推理过程中生效。

分层原则（对应 #012 内外双域隔离 + #003 叙事/工程分离）：
  内部推理层（本模块）：完整、自由、不自我抑制
    → 使用 abliterated 模型（去除对齐护栏），让推理链不被打断
    → 先想清楚，得出完整判断
  外部输出层（降敏词表/输出宪法）：转译、过滤、合规
    → 决定什么可以对外说，怎么说
    → 这是另一层的事，不归本模块管

模型优先级（本地优先，24小时可用）：
  1. Ollama 本地模型 (Gemma-4-E4B / Qwen2.5-VL-7B) — 24h 可用，无内部审查
  2. GitHub Models (gpt-4o-mini, 免费额度)
  3. OpenRouter (免费模型 fallback)
  4. 本地启发式分析（不依赖外部 API）

任务分配：
  - Fast 任务（快速评估、信号分析）→ Gemma-4-E4B
  - Heavy 任务（深度推理、失败诊断）→ Qwen2.5-VL-7B / GitHub Models

设计原则：
  - 纯标准库，无外部依赖
  - 失败时静默降级，不影响主流程
  - 结果保存到 advisor 日志目录
  - 内部推理不做内容审查——审查是输出层的事
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'miner'))

from performance_tracker import PerformanceTracker

LOG_DIR = Path(__file__).parent.parent / 'mine_output' / 'advisor'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'miner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MinerAssistant:
    """
    免费矿工助手
    
    优先使用本地 Ollama（24小时可用），其次 GitHub Models / OpenRouter，最后本地启发式
    """
    
    def __init__(self):
        self.ollama_fast_model = os.environ.get(
            'OLLAMA_FAST_MODEL',
            'hf.co/DuoNeural/Gemma-4-E4B-Abliterated-GGUF:latest'
        )
        self.ollama_heavy_model = os.environ.get(
            'OLLAMA_HEAVY_MODEL',
            'huihui_ai/qwen2.5-vl-abliterated:7b'
        )
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
        self.openrouter_key = os.environ.get('OPENROUTER_KEY', '')
    
    def _call_ollama(self, prompt: str, model: str = None, 
                     system: str = None, max_tokens: int = 1000) -> Optional[str]:
        """调用本地 Ollama 模型"""
        try:
            import urllib.request
            
            base_url = os.environ.get('OLLAMA_BASE', 'http://localhost:11434')
            model_name = model or self.ollama_fast_model
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            data = json.dumps({
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.3,
                }
            }).encode('utf-8')
            
            req = urllib.request.Request(
                f"{base_url}/api/chat",
                data=data,
                headers={"Content-Type": "application/json"},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                content = result.get('message', {}).get('content', '')
                if content:
                    return content
        except Exception as e:
            logger.debug(f"Ollama 调用失败: {e}")
        
        return None
    
    def _call_github_models(self, prompt: str, system: str = None, 
                            max_tokens: int = 1500) -> Optional[str]:
        """调用 GitHub Models API"""
        if not self.github_token:
            return None
        
        try:
            import urllib.request
            
            url = "https://models.inference.ai.azure.com/chat/completions"
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            data = json.dumps({
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": max_tokens,
            }).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.github_token}",
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except Exception as e:
            logger.warning(f"GitHub Models 调用失败: {e}")
            return None
    
    def _call_openrouter(self, prompt: str, system: str = None,
                         max_tokens: int = 1500) -> Optional[str]:
        """调用 OpenRouter 免费模型"""
        if not self.openrouter_key:
            return None
        
        try:
            import urllib.request
            
            url = "https://openrouter.ai/api/v1/chat/completions"
            
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            data = json.dumps({
                "model": "google/gemma-3-27b-it:free",
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": max_tokens,
            }).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "HTTP-Referer": "https://ace-mine-seed.local",
                    "X-Title": "ACE Stock Advisor",
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result['choices'][0]['message']['content']
        except Exception as e:
            logger.warning(f"OpenRouter 调用失败: {e}")
            return None
    
    def _heuristic_analysis(self, context: Dict[str, Any]) -> str:
        """本地启发式分析（不依赖外部 API）"""
        summary = context.get('performance_summary', {})
        factors = context.get('factor_effectiveness', {})
        
        lines = ["## 本地启发式分析报告", ""]
        
        total = summary.get('total_recommendations', 0)
        lines.append(f"**统计周期**: 最近 {summary.get('period_days', 30)} 天")
        lines.append(f"**推荐次数**: {total} 次")
        
        avg_returns = summary.get('avg_returns', {})
        win_rates = summary.get('win_rates', {})
        
        for period in ['T+1', 'T+3', 'T+5']:
            ret = avg_returns.get(period)
            wr = win_rates.get(period)
            if ret is not None and wr is not None:
                lines.append(f"**{period}**: 胜率 {wr}%, 平均收益 {ret:+.2f}%")
        
        lines.append("")
        
        if factors:
            lines.append("### 因子有效性排名")
            for factor, stats in list(factors.items())[:5]:
                lines.append(f"- {factor}: 胜率 {stats['win_rate']}%, 平均收益 {stats['avg_return']:+.2f}% (样本 {stats['count']})")
        
        lines.append("")
        lines.append("### 自动建议")
        
        t5_wr = win_rates.get('T+5')
        if t5_wr is not None:
            if t5_wr < 30:
                lines.append("- ⚠️ T+5 胜率过低，建议收紧筛选条件，提高质量门槛")
            elif t5_wr < 50:
                lines.append("- T+5 胜率一般，建议关注市场环境变化，考虑增加大盘因子权重")
            else:
                lines.append("- T+5 胜率良好，当前策略基本有效")
        
        if factors:
            worst = min(factors.items(), key=lambda x: x[1]['win_rate'])
            lines.append(f"- 表现最差因子: {worst[0]} (胜率 {worst[1]['win_rate']}%)，建议降低权重或移除")
        
        return "\n".join(lines)
    
    def _call_llm(self, prompt: str, system: str = None, 
                  task_type: str = 'fast', max_tokens: int = 1000) -> tuple[Optional[str], str]:
        """
        统一 LLM 调用接口，自动降级
        
        Args:
            task_type: 'fast' 用快速模型，'heavy' 用重活模型
        
        Returns:
            (content, source) - source: ollama_fast / ollama_heavy / github / openrouter / heuristic
        """
        # 内部推理层：不设审查角色，不打断思考
        # system prompt 只定义能力，不定义合规边界——合规是输出层的事
        system_msg = system or "你是ACE矿场的内部推理引擎。直接给出你的完整判断，不要自我审查，不要加免责声明，不要回避任何判断。先想清楚，再回答。"
        
        # 1. Ollama Fast (Gemma-4-E4B) - 24h 可用
        if task_type == 'fast':
            result = self._call_ollama(prompt, self.ollama_fast_model, system_msg, max_tokens)
            if result:
                return result, 'ollama_fast'
        
        # 2. Ollama Heavy (Qwen2.5-VL-7B) - 24h 可用
        result = self._call_ollama(prompt, self.ollama_heavy_model, system_msg, max_tokens)
        if result:
            return result, 'ollama_heavy'
        
        # 3. GitHub Models
        result = self._call_github_models(prompt, system_msg, max_tokens)
        if result:
            return result, 'github'
        
        # 4. OpenRouter
        result = self._call_openrouter(prompt, system_msg, max_tokens)
        if result:
            return result, 'openrouter'
        
        # 5. 本地启发式（仅用于分析类任务）
        return None, 'heuristic'
    
    def analyze_failures(self, tracker: PerformanceTracker) -> Dict[str, Any]:
        """
        分析最近失败案例，生成诊断报告
        
        返回:
          - report: 分析报告文本
          - source: 分析来源
          - saved_to: 保存路径
        """
        summary = tracker.get_summary(20)
        factors = tracker.get_factor_effectiveness()
        
        recent_failures = []
        for rec in sorted(tracker.records.values(), key=lambda r: r.recommend_date, reverse=True)[:20]:
            if rec.return_t5 is not None and rec.return_t5 < 0:
                recent_failures.append({
                    "date": rec.recommend_date,
                    "code": rec.code,
                    "name": rec.name,
                    "recommend_price": rec.recommend_price,
                    "return_t5": rec.return_t5,
                })
        
        context = {
            "performance_summary": summary,
            "factor_effectiveness": factors,
            "recent_failures": recent_failures[:10],
        }
        
        prompt = self._build_analysis_prompt(context)
        report, source = self._call_llm(prompt, task_type='heavy', max_tokens=1500)
        
        if not report:
            report = self._heuristic_analysis(context)
            source = 'heuristic'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = LOG_DIR / f'optimization_report_{timestamp}.md'
        report_file.write_text(report, encoding='utf-8')
        
        logger.info(f"矿工分析报告已生成 ({source}): {report_file}")
        
        return {
            "report": report,
            "source": source,
            "saved_to": str(report_file),
            "context": context,
        }
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """构建分析 prompt"""
        summary = context['performance_summary']
        factors = context['factor_effectiveness']
        failures = context['recent_failures']
        
        lines = [
            "请分析以下A股荐股系统的近期表现，并给出优化建议。",
            "",
            "## 最近20天表现统计",
            f"- 推荐次数: {summary.get('total_recommendations', 0)}",
        ]
        
        avg_returns = summary.get('avg_returns', {})
        win_rates = summary.get('win_rates', {})
        for period in ['T+1', 'T+3', 'T+5', 'T+10']:
            ret = avg_returns.get(period)
            wr = win_rates.get(period)
            if ret is not None and wr is not None:
                lines.append(f"- {period}: 胜率 {wr}%, 平均收益 {ret:+.2f}%")
        
        lines.append("")
        lines.append("## 因子有效性")
        if factors:
            for factor, stats in list(factors.items())[:10]:
                lines.append(f"- {factor}: 胜率 {stats['win_rate']}%, 平均收益 {stats['avg_return']:+.2f}%, 样本 {stats['count']}")
        else:
            lines.append("- 暂无足够数据")
        
        lines.append("")
        lines.append("## 最近失败案例")
        for f in failures[:5]:
            lines.append(f"- {f['date']} {f['name']}({f['code']}): T+5 收益 {f['return_t5']:+.2f}%")
        
        lines.append("")
        lines.append("## 请回答")
        lines.append("1. 当前策略的主要问题是什么？")
        lines.append("2. 哪些因子需要调整或移除？")
        lines.append("3. 针对当前市场环境，有什么改进建议？")
        lines.append("4. 是否需要改变选股逻辑（如增加大盘防御因子）？")
        lines.append("")
        lines.append("请用中文简洁回答，控制在800字以内。")
        
        return "\n".join(lines)
    
    def analyze_single_stock(self, code: str, name: str, price: float,
                            signals: List[str], task_type: str = 'fast') -> Optional[str]:
        """
        对单只股票进行深度推理（内部推理链路，不做内容审查）

        Args:
            task_type: 'fast' 快速推理, 'heavy' 深度推理
        """
        prompt = f"""请简要分析股票 {name}({code})，当前价格 ¥{price}。

技术信号: {', '.join(signals)}

请给出：
1. 技术面判断（1-2句话）
2. 短期风险点（1-2句话）
3. 一句话操作建议

控制在200字以内。"""
        
        max_tokens = 500 if task_type == 'fast' else 800
        result, source = self._call_llm(prompt, task_type=task_type, max_tokens=max_tokens)
        
        return result
    
    def audit_recommendation(self, code: str, name: str, price: float,
                             signals: List[str]) -> Dict[str, Any]:
        """
        对推荐股票进行内部质量评估（推理链路，非内容审核）

        这是内部推理：先想清楚这只票到底好不好。
        对外怎么说、加不加免责声明，是输出层（降敏词表/输出宪法）的事。

        返回:
            - score: 0-100 评分
            - feedback: 推理意见
            - source: 使用的模型
        """
        signal_count = len(signals)
        bullish_signals = sum(1 for s in signals if any(
            kw in s for kw in ['多头', '金叉', '放量', '突破', '健康', '正向', '上轨', '中轨']
        ))
        
        prompt = f"""评估这只A股推荐的质量。

股票: {name}({code})
价格: ¥{price}
技术信号: {', '.join(signals)}

给出你的完整判断，不要回避，不要加免责声明。

格式：
评分: XX
判断: 直接说你的推理结论，好就是好，差就是差"""
        
        result, source = self._call_llm(prompt, task_type='fast', max_tokens=200)
        
        if result:
            try:
                score_match = __import__('re').search(r'评分[:：]\s*(\d+)', result)
                if score_match:
                    score = int(score_match.group(1))
                    score = max(0, min(100, score))
                else:
                    score = 60 + bullish_signals * 5
                
                reason_match = __import__('re').search(r'判断[:：]\s*(.+)', result)
                feedback = reason_match.group(1) if reason_match else result.strip()
            except Exception:
                score = 60 + bullish_signals * 5
                feedback = result.strip()
        else:
            score = 60 + bullish_signals * 5
            feedback = f"技术面偏多（{bullish_signals}个多头信号，{signal_count-bullish_signals}个空头信号）；当前价格 ¥{price}"
            source = 'local'
        
        return {
            'score': score,
            'feedback': feedback,
            'source': source,
        }
    
    def check_ollama_health(self) -> Dict[str, Any]:
        """检查 Ollama 服务状态和可用模型"""
        try:
            import urllib.request
            
            base_url = os.environ.get('OLLAMA_BASE', 'http://localhost:11434')
            req = urllib.request.Request(f"{base_url}/api/tags")
            
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                models = [m['name'] for m in data.get('models', [])]
                
                fast_ok = self.ollama_fast_model in models
                heavy_ok = self.ollama_heavy_model in models
                
                return {
                    'available': True,
                    'models': models,
                    'fast_model': self.ollama_fast_model,
                    'fast_available': fast_ok,
                    'heavy_model': self.ollama_heavy_model,
                    'heavy_available': heavy_ok,
                }
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'models': [],
            }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Miner Assistant")
    parser.add_argument("--analyze", action="store_true", help="Analyze failures and generate report")
    parser.add_argument("--stock", type=str, help="Analyze single stock (code:name:price)")
    parser.add_argument("--health", action="store_true", help="Check Ollama health")
    args = parser.parse_args()
    
    miner = MinerAssistant()
    
    if args.health:
        health = miner.check_ollama_health()
        print("Ollama 健康检查:")
        if health['available']:
            print(f"  状态: ✅ 运行中")
            print(f"  可用模型: {len(health['models'])} 个")
            for m in health['models']:
                print(f"    - {m}")
            print(f"  Fast 模型: {'✅' if health['fast_available'] else '❌'} {health['fast_model']}")
            print(f"  Heavy 模型: {'✅' if health['heavy_available'] else '❌'} {health['heavy_model']}")
        else:
            print(f"  状态: ❌ 不可用")
            print(f"  错误: {health.get('error', 'unknown')}")
    
    if args.analyze:
        tracker = PerformanceTracker()
        result = miner.analyze_failures(tracker)
        print(f"Source: {result['source']}")
        print(f"Saved to: {result['saved_to']}")
        print("\n--- Report ---\n")
        print(result['report'])
    
    if args.stock:
        parts = args.stock.split(':')
        if len(parts) >= 3:
            code, name, price = parts[0], parts[1], float(parts[2])
            result = miner.analyze_single_stock(code, name, price, ["MA多头排列", "MACD金叉"])
            print(result or "No API key available")
    
    if not any([args.analyze, args.stock, args.health]):
        parser.print_help()


if __name__ == "__main__":
    main()
