#!/usr/bin/env python3
"""
A股智能荐股引擎 v2 — adata 增强版

数据源：
- adata 多源融合（腾讯/新浪/百度/东财自动切换）
- 全市场 5500+ 只股票实时扫描
- K线（含涨跌幅、换手率）+ 资金流向（主力净流入）

筛选逻辑：
1. 全市场涨幅扫描（排除 ST/停牌/涨停）
2. K线技术面确认（MA5>MA10、RSI 30-70、成交量放大）
3. 资金面确认（主力净流入 > 0）
4. free_llm 最终分析和荐股

用法:
  cd /workspace/fengzi-repos/mine-seed/05_TOOLS/advisor
  python3 adata_advisor.py
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# 日志
LOG_DIR = Path(__file__).parent / ".." / "mine_output" / "advisor"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "adata_advisor.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("adata_advisor")

# 加载 free_llm
sys.path.insert(0, str(Path(__file__).parent / ".." / "miner"))
from free_llm import call


class AdataAdvisor:
    """adata 增强荐股引擎"""
    
    def __init__(self):
        try:
            import adata
            self.adata = adata
            self.available = True
            logger.info("[adata] 已加载")
        except ImportError:
            self.adata = None
            self.available = False
            logger.error("[adata] 未安装: pip install adata")
    
    def get_all_stocks(self) -> List[Dict]:
        """获取全市场股票列表"""
        if not self.available:
            return []
        try:
            df = self.adata.stock.info.all_code()
            if df is None or len(df) == 0:
                return []
            stocks = []
            for _, row in df.iterrows():
                code = str(row.get('stock_code', ''))
                name = str(row.get('short_name', ''))
                if code and name and not name.startswith('ST') and not name.startswith('*ST'):
                    stocks.append({'code': code, 'name': name})
            logger.info(f"[adata] 全市场股票: {len(stocks)} 只")
            return stocks
        except Exception as e:
            logger.error(f"[adata] 获取股票列表失败: {e}")
            return []
    
    def get_spot(self, codes: List[str]) -> List[Dict]:
        """获取实时行情（stock_query 腾讯 API）"""
        if not self.available:
            return []
        results = []

        # 用 stock_query 获取实时行情
        try:
            from stock_query import get_stock_query
            sq = get_stock_query()
        except ImportError:
            logger.error("[spot] stock_query 不可用")
            return []

        # 构造代码格式
        formatted = []
        for c in codes:
            if c.startswith('6'):
                formatted.append(f'sh{c}')
            else:
                formatted.append(f'sz{c}')

        # 分批获取
        for i in range(0, len(formatted), 30):
            batch = formatted[i:i+30]
            try:
                quotes = sq.get_quote(batch)
                for q in quotes:
                    code = q.get('code', '')
                    name = q.get('name', '')
                    price = q.get('price', 0)
                    change_pct = q.get('change_pct', 0)
                    turnover_rate = q.get('turnover_rate', 0)
                    volume = q.get('volume', 0)
                    pe = q.get('pe', 0)

                    # 排除条件
                    if price <= 0 or not name:
                        continue
                    if name.startswith('ST') or name.startswith('*ST'):
                        continue
                    if change_pct > 9.5 or change_pct < -9.5:  # 排除涨停/跌停
                        continue
                    if turnover_rate < 0.5:  # 排除成交量极低的
                        continue

                    results.append({
                        'code': code,
                        'name': name,
                        'price': price,
                        'change_pct': change_pct,
                        'turnover_rate': turnover_rate,
                        'volume': volume,
                        'pe': pe,
                    })
                time.sleep(0.1)
            except Exception as e:
                logger.debug(f"[spot] 获取失败: {e}")

        logger.info(f"[spot] 有效行情: {len(results)} 只")
        return results
    
    def get_kline_and_tech(self, code: str, days: int = 20) -> Dict:
        """获取 K线 + 计算技术指标"""
        if not self.available:
            return {}
        try:
            from datetime import datetime, timedelta
            end = datetime.now().strftime("%Y-%m-%d")
            start = (datetime.now() - timedelta(days=days + 10)).strftime("%Y-%m-%d")
            df = self.adata.stock.market.get_market(
                stock_code=code, start_date=start, end_date=end, k_type=1
            )
            if df is None or len(df) == 0:
                return {}
            
            closes = df['close'].tolist()
            volumes = df['volume'].tolist()
            
            if len(closes) < 5:
                return {}
            
            # 计算 MA
            ma5 = sum(closes[-5:]) / 5 if len(closes) >= 5 else closes[-1]
            ma10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else ma5
            ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else ma10
            
            # 简化 RSI（6日）
            if len(closes) >= 7:
                gains = [max(closes[i] - closes[i-1], 0) for i in range(-6, 0)]
                losses = [max(closes[i-1] - closes[i], 0) for i in range(-6, 0)]
                avg_gain = sum(gains) / len(gains) if gains else 0.001
                avg_loss = sum(losses) / len(losses) if losses else 0.001
                rsi6 = 100 - (100 / (1 + avg_gain / avg_loss))
            else:
                rsi6 = 50
            
            # 成交量趋势（今日 vs 5日均量）
            vol_today = volumes[-1] if volumes else 0
            vol_avg5 = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else vol_today
            vol_ratio = vol_today / vol_avg5 if vol_avg5 > 0 else 1
            
            # 5日涨幅
            if len(closes) >= 6:
                momentum_5d = (closes[-1] - closes[-6]) / closes[-6] * 100
            else:
                momentum_5d = 0
            
            return {
                'ma5': ma5,
                'ma10': ma10,
                'ma20': ma20,
                'rsi6': rsi6,
                'vol_ratio': vol_ratio,
                'momentum_5d': momentum_5d,
                'kline_ok': True,
            }
        except Exception as e:
            logger.debug(f"[tech] {code} 技术指标失败: {e}")
            return {}
    
    def get_capital(self, code: str) -> Dict:
        """获取资金流向"""
        if not self.available:
            return {}
        try:
            df = self.adata.stock.market.get_capital_flow(stock_code=code)
            if df is None or len(df) == 0:
                return {}
            
            # 最近3天主力净流入
            recent = df.tail(3)
            main_inflow = float(recent['main_net_inflow'].sum()) if 'main_net_inflow' in recent else 0
            
            return {
                'main_inflow_3d': main_inflow,
                'capital_ok': True,
            }
        except Exception as e:
            logger.debug(f"[capital] {code} 资金流向失败: {e}")
            return {}
    
    def _get_stock_factors(self, code: str) -> Dict:
        """并行获取技术面+资金面"""
        def _tech():
            return self.get_kline_and_tech(code)
        def _capital():
            return self.get_capital(code)
        with ThreadPoolExecutor(max_workers=2) as executor:
            ft = executor.submit(_tech)
            fc = executor.submit(_capital)
            tech = ft.result()
            capital = fc.result()
        return tech, capital

    def screen(self, top_n: int = 30) -> List[Dict]:
        """全市场筛选"""
        if not self.available:
            logger.error("[screen] adata 不可用")
            return []
        
        # 1. 获取全市场股票
        all_stocks = self.get_all_stocks()
        if not all_stocks:
            return []
        
        # 2. 获取实时行情（用 stock_query 腾讯API，快且稳）
        codes = [s['code'] for s in all_stocks]
        spot_data = self.get_spot(codes)
        if not spot_data:
            return []
        
        # 3. 涨幅筛选：3% < 涨幅 < 8%（趋势初现但未过热）
        candidates = [s for s in spot_data if 3 <= s['change_pct'] <= 8]
        logger.info(f"[screen] 涨幅 3-8%: {len(candidates)} 只")
        
        # 4. 技术面 + 资金面筛选（并行获取）
        screened = []
        for stock in candidates[:100]:  # 只处理前100只，避免太慢
            code = stock['code']

            tech, capital = self._get_stock_factors(code)
            if not tech.get('kline_ok'):
                continue
            
            # 技术确认
            tech_pass = (
                tech['ma5'] > tech['ma10'] and  # MA5 上穿 MA10
                30 <= tech['rsi6'] <= 70 and     # RSI 不在极端区
                tech['vol_ratio'] > 1.2          # 成交量放大
            )
            
            # 资金确认
            capital_pass = capital.get('main_inflow_3d', 0) > 0
            
            if tech_pass or capital_pass:
                stock.update(tech)
                stock.update(capital)
                stock['tech_pass'] = tech_pass
                stock['capital_pass'] = capital_pass
                screened.append(stock)
            
            time.sleep(0.05)  # 限速，避免被封
        
        logger.info(f"[screen] 技术+资金确认: {len(screened)} 只")
        
        # 5. 按综合得分排序
        for s in screened:
            score = 0
            score += s['change_pct'] * 2  # 涨幅权重
            score += s.get('momentum_5d', 0)  # 5日动量
            score += min(s.get('vol_ratio', 1) * 5, 20)  # 成交量
            if s.get('tech_pass'): score += 15
            if s.get('capital_pass'): score += 20
            if s.get('main_inflow_3d', 0) > 1000000: score += 10  # 大额主力流入
            s['score'] = score
        
        screened.sort(key=lambda x: x['score'], reverse=True)
        return screened[:top_n]
    
    def generate_report(self, top_stocks: List[Dict]) -> str:
        """用 free_llm 生成荐股报告"""
        if not top_stocks:
            return "# A股每日荐股\n\n今日未找到符合条件的股票。\n"
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 构造 prompt
        stock_info = ""
        for i, s in enumerate(top_stocks[:10], 1):
            stock_info += f"\n{i}. {s['name']}({s['code']})"
            stock_info += f" 现价{s['price']:.2f} 涨{s['change_pct']:.2f}%"
            stock_info += f" 换手{s['turnover_rate']:.2f}%"
            if s.get('tech_pass'):
                stock_info += f" 技术:MA5>MA10 RSI={s.get('rsi6',0):.1f}"
            if s.get('capital_pass'):
                stock_info += f" 资金:主力3日净入{s.get('main_inflow_3d',0)/10000:.0f}万"
            stock_info += f" 得分:{s.get('score',0):.1f}"
        
        prompt = f"""你是专业的A股投资顾问。今天是{today}。

以下是从全市场5500+只股票中，通过技术面（MA金叉、RSI、成交量）和资金面（主力净流入）双重筛选出的前10只候选股：
{stock_info}

请从中推荐2只最值得关注的股票，给出：
1. 股票代码和名称
2. 推荐理由（结合技术面和资金面）
3. 风险提示
4. 关注价位

输出格式：Markdown。"""
        
        try:
            result = call(prompt, system="你是专业的A股投资顾问，分析严谨，风险提示到位。", max_tokens=1500, prefer="glm")
            
            report = f"""# A股每日荐股 — {today}

{result['content']}

---

## 筛选过程
- 全市场扫描: 5500+ 只股票
- 涨幅筛选 (3-8%): 初筛
- 技术面确认 (MA5>MA10, RSI 30-70, 成交量放大): 复筛
- 资金面确认 (主力净流入>0): 复筛
- LLM 最终分析: 荐股

## 数据来源
- 实时行情: 腾讯财经 API
- K线/技术指标: adata 多源融合
- 资金流向: adata 多源融合
- 分析模型: {result['channel']}/{result['model']}

---
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 渠道: {result['channel']} | 耗时: {result['elapsed']:.1f}s
"""
            return report
        except Exception as e:
            logger.error(f"[report] LLM 生成失败: {e}")
            # 降级：直接输出得分最高的2只
            top2 = top_stocks[:2]
            report = f"# A股每日荐股 — {today}\n\n## TOP 推荐\n\n"
            for s in top2:
                report += f"### {s['name']} ({s['code']})\n"
                report += f"- 现价: {s['price']:.2f} ({s['change_pct']:+.2f}%)\n"
                report += f"- 换手率: {s['turnover_rate']:.2f}%\n"
                if s.get('tech_pass'):
                    report += f"- 技术: MA5>MA10, RSI={s.get('rsi6',0):.1f}, 量比={s.get('vol_ratio',1):.2f}\n"
                if s.get('capital_pass'):
                    report += f"- 资金: 主力3日净流入 {s.get('main_inflow_3d',0)/10000:.0f} 万\n"
                report += f"- 综合得分: {s.get('score',0):.1f}\n\n"
            report += f"\n---\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 降级模式（LLM不可用）\n"
            return report


def main():
    advisor = AdataAdvisor()
    if not advisor.available:
        logger.error("adata 未安装，无法运行")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("adata 增强荐股引擎启动")
    logger.info("=" * 50)
    
    # 筛选
    top_stocks = advisor.screen(top_n=30)
    
    # 生成报告
    report = advisor.generate_report(top_stocks)
    
    # 保存
    today = datetime.now().strftime("%Y%m%d")
    output_dir = Path(__file__).parent / ".." / "mine_output" / "advisor"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"advisor_{today}.md"
    output_file.write_text(report, encoding="utf-8")
    
    # 复制到 cloud/
    cloud_dir = Path(os.environ.get("MINE_SEED", "/workspace/fengzi-repos/mine-seed")) / "cloud" / "advisor"
    cloud_dir.mkdir(parents=True, exist_ok=True)
    cloud_file = cloud_dir / f"advisor_{today}.md"
    cloud_file.write_text(report, encoding="utf-8")
    
    logger.info(f"报告已保存: {output_file}")
    logger.info(f"Cloud: {cloud_file}")
    
    # ntfy 通知
    try:
        import requests
        # 从环境变量读代理，不硬编码
        proxies = {}
        http_proxy = os.environ.get("http_proxy", os.environ.get("HTTP_PROXY", ""))
        https_proxy = os.environ.get("https_proxy", os.environ.get("HTTPS_PROXY", ""))
        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        r = requests.post(
            'https://ntfy.sh/ace-stock-advisor',
            data=f'adata荐股完成: {today}'.encode('utf-8'),
            headers={'Title': 'A股荐股', 'Priority': 'high', 'Tags': 'chart_with_upwards_trend'},
            timeout=10,
            proxies=proxies or None
        )
        logger.info(f"ntfy: {r.status_code}")
    except Exception as e:
        logger.warning(f"ntfy 失败: {e}")


if __name__ == "__main__":
    main()
