#!/usr/bin/env python3
"""
Multi Data Source Manager — 多数据源管理器

不绑死单一数据源，实现自动降级：
  Level 1: 新浪财经 (sina) — 实时行情
  Level 2: 东方财富 (eastmoney) — 实时行情
  Level 3: 腾讯财经 (tencent) — 实时行情
  Level 4: Baostock — 历史数据
  Level 5: akshare — 历史数据

设计原则：
  - 纯标准库实现（新浪/东方财富/腾讯），无需额外安装
  - Baostock/akshare 作为可选依赖，失败时降级
  - 自动健康检测，动态选择最佳数据源
  - 统一接口，对上层透明
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

LOG_DIR = Path(__file__).parent.parent / 'mine_output' / 'advisor'
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'data_source.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataSourceManager:
    """多数据源管理器"""
    
    def __init__(self):
        self.sources = {
            'sina': {'available': True, 'priority': 1, 'latency': 0},
            'eastmoney': {'available': True, 'priority': 2, 'latency': 0},
            'tencent': {'available': True, 'priority': 3, 'latency': 0},
            'xueqiu': {'available': False, 'priority': 3, 'latency': 0},
            'baostock': {'available': False, 'priority': 4, 'latency': 0},
            'akshare': {'available': False, 'priority': 5, 'latency': 0},
        }
        self._detect_optional_sources()
        self._health_check()
    
    def _detect_optional_sources(self):
        """检测可选数据源是否可用"""
        try:
            import baostock
            self.sources['baostock']['available'] = True
            logger.info("Baostock 数据源可用")
        except ImportError:
            logger.debug("Baostock 不可用")
        
        try:
            import akshare
            self.sources['akshare']['available'] = True
            logger.info("akshare 数据源可用")
        except ImportError:
            logger.debug("akshare 不可用")
        
        try:
            import lxml
            self.sources['xueqiu']['available'] = True
            logger.info("雪球数据源可用")
        except ImportError:
            logger.debug("雪球数据源不可用(lxml未安装)")
    
    def _health_check(self):
        """健康检查，测试各数据源"""
        test_codes = ['sh600000', 'sz000001']
        
        for source in ['sina', 'eastmoney', 'tencent']:
            try:
                start = time.time()
                if source == 'sina':
                    self._get_sina_quotes(test_codes[:1])
                elif source == 'eastmoney':
                    self._get_eastmoney_quotes(test_codes[:1])
                elif source == 'tencent':
                    from stock_query import get_stock_query
                    sq = get_stock_query()
                    sq.get_quote(['600000'])
                self.sources[source]['latency'] = round(time.time() - start, 2)
                logger.info(f"数据源 {source} 健康检查通过，延迟 {self.sources[source]['latency']}s")
            except Exception as e:
                self.sources[source]['available'] = False
                logger.warning(f"数据源 {source} 健康检查失败: {e}")
    
    def _get_sina_quotes(self, codes: List[str]) -> List[Dict]:
        """新浪财经实时行情"""
        url = f"http://hq.sinajs.cn/list={','.join(codes)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.sina.com.cn',
        }
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('gbk', errors='replace')
        
        results = []
        for line in data.strip().split('\n'):
            match = re.match(r'var hq_str_(\w+)="(.+)"', line)
            if match:
                code = match.group(1)
                fields = match.group(2).split(',')
                if len(fields) >= 5:
                    results.append({
                        'code': code.replace('sh', '').replace('sz', ''),
                        'name': fields[0],
                        'price': float(fields[3]) if fields[3] else 0,
                        'open': float(fields[1]) if fields[1] else 0,
                        'high': float(fields[4]) if fields[4] else 0,
                        'low': float(fields[5]) if fields[5] else 0,
                        'volume': int(float(fields[8])) if fields[8] else 0,
                        'amount': float(fields[9]) if fields[9] else 0,
                        'change': float(fields[10]) if fields[10] else 0,
                        'change_percent': float(fields[11]) if fields[11] else 0,
                        'source': 'sina',
                    })
        return results
    
    def _get_eastmoney_quotes(self, codes: List[str]) -> List[Dict]:
        """东方财富实时行情"""
        results = []
        
        for code in codes:
            market = '1' if code.startswith('sh') else '0'
            ts_code = code.replace('sh', '').replace('sz', '')
            
            url = (
                f"http://push2.eastmoney.com/api/qt/stock/get?"
                f"ut=fa5fd1943c7b386f172d6893dbfba10b&"
                f"invt=2&fltt=2&fields=f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f104,f105,f92,f116,f93,f100,f101,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f152&"
                f"secid={market}.{ts_code}"
            )
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://quote.eastmoney.com',
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            
            if data.get('data'):
                d = data['data']
                results.append({
                    'code': ts_code,
                    'name': d.get('f58', ''),
                    'price': d.get('f43', 0),
                    'open': d.get('f46', 0),
                    'high': d.get('f44', 0),
                    'low': d.get('f47', 0),
                    'volume': d.get('f51', 0),
                    'amount': d.get('f168', 0),
                    'change': d.get('f104', 0),
                    'change_percent': d.get('f105', 0),
                    'source': 'eastmoney',
                })
        
        return results
    
    def get_quotes(self, codes: List[str]) -> List[Dict]:
        """获取实时行情（自动降级）"""
        normalized_codes = []
        for c in codes:
            c = c.strip().lower()
            if not c.startswith('sh') and not c.startswith('sz'):
                if c.startswith('6'):
                    c = f'sh{c}'
                else:
                    c = f'sz{c}'
            normalized_codes.append(c)
        
        available_sources = sorted(
            [s for s in self.sources if self.sources[s]['available']],
            key=lambda x: (self.sources[x]['priority'], self.sources[x]['latency'])
        )
        
        for source in available_sources:
            try:
                if source == 'sina':
                    return self._get_sina_quotes(normalized_codes)
                elif source == 'eastmoney':
                    return self._get_eastmoney_quotes(normalized_codes)
                elif source == 'tencent':
                    from stock_query import get_stock_query
                    sq = get_stock_query()
                    return sq.get_quote([c.replace('sh', '').replace('sz', '') for c in normalized_codes])
                elif source == 'baostock':
                    return self._get_baostock_quotes(normalized_codes)
                elif source == 'akshare':
                    return self._get_akshare_quotes(normalized_codes)
            except Exception as e:
                logger.warning(f"数据源 {source} 获取行情失败: {e}")
                self.sources[source]['available'] = False
        
        logger.error("所有数据源均不可用")
        return []
    
    def _get_baostock_kline(self, code: str, days: int = 30) -> List[Dict]:
        """Baostock 历史K线"""
        import baostock as bs
        
        bs.login()
        
        market = 'sh' if code.startswith('6') else 'sz'
        bs_code = f"{market}.{code}"
        
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,open,high,low,close,volume",
            start_date=(datetime.now() - datetime.timedelta(days=days+30)).strftime('%Y-%m-%d'),
            end_date=datetime.now().strftime('%Y-%m-%d'),
            frequency="d",
            adjustflag="2"
        )
        
        results = []
        while rs.error_code == '0' and rs.next():
            row = rs.get_row_data()
            results.append({
                'date': row[0],
                'open': float(row[1]),
                'high': float(row[2]),
                'low': float(row[3]),
                'close': float(row[4]),
                'volume': int(row[5]),
                'source': 'baostock',
            })
        
        bs.logout()
        return results[-days:] if len(results) > days else results
    
    def _get_akshare_kline(self, code: str, days: int = 30) -> List[Dict]:
        """akshare 历史K线"""
        import akshare as ak
        
        start_date = (datetime.now() - datetime.timedelta(days=days+30)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                start_date=start_date, end_date=end_date, adjust='qfq')
        
        if df is not None and not df.empty:
            results = []
            for _, row in df.iterrows():
                results.append({
                    'date': str(row.get('日期', '')).replace('-', ''),
                    'open': float(row.get('开盘', 0)),
                    'high': float(row.get('最高', 0)),
                    'low': float(row.get('最低', 0)),
                    'close': float(row.get('收盘', 0)),
                    'volume': int(float(row.get('成交量', 0))),
                    'source': 'akshare',
                })
            return results[-days:] if len(results) > days else results
        
        return []
    
    def _get_xueqiu_sentiment(self, codes: List[str]) -> List[Dict]:
        """雪球情绪数据（讨论热度、评论数、用户情绪）"""
        results = []
        
        for code in codes:
            try:
                market = 'SH' if code.startswith('6') else 'SZ'
                ts_code = f"{market}{code}"
                
                url = f"https://xueqiu.com/stock/search.json?code={ts_code}"
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://xueqiu.com/',
                    'Cookie': '',
                }
                
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                
                if data.get('stocks'):
                    stock = data['stocks'][0]
                    results.append({
                        'code': code,
                        'name': stock.get('name', ''),
                        'hot_rank': stock.get('hot_rank', 0),
                        'comment_count': stock.get('comment_count', 0),
                        'follower_count': stock.get('follower_count', 0),
                        'heat_level': stock.get('heat_level', ''),
                        'source': 'xueqiu',
                    })
            except Exception as e:
                logger.warning(f"雪球获取 {code} 情绪数据失败: {e}")
        
        return results
    
    def get_sentiment(self, codes: List[str]) -> List[Dict]:
        """获取股票情绪数据（雪球讨论热度）"""
        if not self.sources['xueqiu']['available']:
            return []
        
        normalized_codes = []
        for c in codes:
            c = c.strip().lower()
            if c.startswith('sh'):
                c = c.replace('sh', '')
            elif c.startswith('sz'):
                c = c.replace('sz', '')
            normalized_codes.append(c)
        
        try:
            return self._get_xueqiu_sentiment(normalized_codes)
        except Exception as e:
            logger.warning(f"雪球情绪数据获取失败: {e}")
            self.sources['xueqiu']['available'] = False
            return []
    
    def get_hist_kline(self, code: str, days: int = 30) -> List[Dict]:
        """获取历史K线（自动降级）"""
        available_sources = sorted(
            [s for s in self.sources if self.sources[s]['available']],
            key=lambda x: self.sources[x]['priority']
        )
        
        for source in available_sources:
            try:
                if source == 'baostock':
                    return self._get_baostock_kline(code, days)
                elif source == 'akshare':
                    return self._get_akshare_kline(code, days)
                elif source == 'tencent':
                    from stock_query import get_stock_query
                    sq = get_stock_query()
                    return sq.get_hist_kline(code, days)
                elif source == 'eastmoney':
                    return self._get_eastmoney_kline(code, days)
            except Exception as e:
                logger.warning(f"数据源 {source} 获取K线失败: {e}")
        
        return []
    
    def _get_eastmoney_kline(self, code: str, days: int = 30) -> List[Dict]:
        """东方财富K线（备选）"""
        market = '1' if code.startswith('6') else '0'
        
        url = (
            f"http://push2his.eastmoney.com/api/qt/stock/kline/get?"
            f"secid={market}.{code}&fields1=f1,f2,f3,f4,f5,f6&"
            f"fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&"
            f"klt=101&fqt=1&end=20500101&lmt={days}"
        )
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        results = []
        if data.get('data', {}).get('klines'):
            for kline in data['data']['klines']:
                parts = kline.split(',')
                if len(parts) >= 6:
                    results.append({
                        'date': parts[0],
                        'open': float(parts[1]),
                        'high': float(parts[2]),
                        'low': float(parts[3]),
                        'close': float(parts[4]),
                        'volume': int(float(parts[5])),
                        'source': 'eastmoney',
                    })
        
        return results
    
    def get_current_price(self, code: str) -> Optional[float]:
        """获取当前价格"""
        quotes = self.get_quotes([code])
        if quotes:
            return quotes[0].get('price')
        return None
    
    def get_source_status(self) -> Dict:
        """获取各数据源状态"""
        return {k: {
            'available': v['available'],
            'priority': v['priority'],
            'latency': v['latency'],
        } for k, v in self.sources.items()}


def clean_cache(days: int = 7) -> Dict[str, Any]:
    """清理过期缓存文件"""
    cache_dir = LOG_DIR / 'cache'
    if not cache_dir.exists():
        return {"cleaned": 0, "total": 0, "freed_bytes": 0}
    
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    cleaned = 0
    total = 0
    freed_bytes = 0
    
    for f in cache_dir.glob('*.json'):
        total += 1
        try:
            # 从文件名提取日期
            match = re.search(r'_(\d{8})\.json$', f.name)
            if match:
                file_date = match.group(1)
                if file_date < cutoff:
                    size = f.stat().st_size
                    f.unlink()
                    cleaned += 1
                    freed_bytes += size
        except Exception:
            pass
    
    return {
        "cleaned": cleaned,
        "total": total,
        "remaining": total - cleaned,
        "freed_bytes": freed_bytes,
        "freed_mb": round(freed_bytes / 1024 / 1024, 2)
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Multi Data Source Manager")
    parser.add_argument("--test", action="store_true", help="Test all data sources")
    parser.add_argument("--quotes", type=str, help="Get quotes for codes (comma-separated)")
    parser.add_argument("--kline", type=str, help="Get kline for code")
    parser.add_argument("--clean-cache", type=int, nargs='?', const=7, help="Clean cache older than N days (default 7)")
    args = parser.parse_args()
    
    dsm = DataSourceManager()
    
    if args.test:
        print("数据源状态:")
        for source, status in dsm.get_source_status().items():
            status_str = "✅" if status['available'] else "❌"
            print(f"  {status_str} {source}: priority={status['priority']}, latency={status['latency']}s")
    
    if args.quotes:
        codes = args.quotes.split(',')
        quotes = dsm.get_quotes(codes)
        print(f"\n获取行情 ({len(quotes)} 条):")
        for q in quotes:
            print(f"  {q['name']}({q['code']}): ¥{q['price']} ({q['source']})")
    
    if args.kline:
        kline = dsm.get_hist_kline(args.kline, days=5)
        print(f"\n获取K线 ({len(kline)} 条):")
        for k in kline:
            print(f"  {k['date']}: close={k['close']} ({k['source']})")
    
    if args.clean_cache is not None:
        result = clean_cache(args.clean_cache)
        print(f"缓存清理 (保留 {args.clean_cache} 天):")
        print(f"  总文件数: {result['total']}")
        print(f"  已清理: {result['cleaned']}")
        print(f"  剩余: {result['remaining']}")
        print(f"  释放空间: {result['freed_mb']} MB")


if __name__ == "__main__":
    main()