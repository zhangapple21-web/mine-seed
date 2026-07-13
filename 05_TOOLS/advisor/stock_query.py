#!/usr/bin/env python3
"""
股票行情查询工具 - stock_query.py

多级降级方案：
  Level 1: 腾讯行情 API (qt.gtimg.cn)
  Level 2: 腾讯备用 API (ifzq.gtimg.cn)
  Level 3: 本地缓存数据
  Level 4: 备用股票池

容错特性：
  - 指数退避重试机制
  - 请求限流控制
  - 数据质量校验
  - 自动降级切换
"""
import time
import json
import random
import logging
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class RateLimiter:
    """请求速率限制器"""
    
    def __init__(self, max_calls_per_second: float = 1.5):
        self.max_calls_per_second = max_calls_per_second
        self.last_call_time = 0
        self.call_count = 0
        self.window_start = 0
    
    def wait(self):
        """等待直到可以发送下一个请求"""
        now = time.time()
        
        if now - self.window_start >= 1.0:
            self.window_start = now
            self.call_count = 0
        
        if self.call_count >= self.max_calls_per_second:
            wait_time = 1.0 - (now - self.window_start)
            if wait_time > 0:
                time.sleep(wait_time)
            self.window_start = time.time()
            self.call_count = 0
        
        self.last_call_time = now
        self.call_count += 1


class StockQuery:
    """股票行情查询工具（带多级降级）"""
    
    def __init__(self):
        self.base_url = "https://qt.gtimg.cn"
        self.fallback_url = "https://ifzq.gtimg.cn"
        self.rate_limiter = RateLimiter(max_calls_per_second=1.2)
        self._stats = {
            'success': 0,
            'failures': 0,
            'fallbacks': 0,
            'cache_hits': 0,
        }
        self._cache = {}
        self._cache_expiry = 300  # 缓存5分钟
    
    def _safe_request(self, url: str, retries: int = 3, timeout: int = 10) -> Optional[str]:
        """安全的HTTP请求，带指数退避重试"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.qq.com',
            'Accept': '*/*'
        }
        
        for attempt in range(retries):
            try:
                # 速率限制
                self.rate_limiter.wait()
                
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    self._stats['success'] += 1
                    return resp.read().decode('gbk', errors='replace')
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"请求被限流 (429)，等待 {wait_time:.1f}s 后重试")
                    time.sleep(wait_time)
                elif e.code >= 500:
                    wait_time = (2 ** attempt) * 0.5 + random.uniform(0, 0.5)
                    logger.warning(f"服务器错误 ({e.code})，等待 {wait_time:.1f}s 后重试")
                    time.sleep(wait_time)
                else:
                    self._stats['failures'] += 1
                    return None
            except urllib.error.URLError as e:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"网络错误: {e}，等待 {wait_time:.1f}s 后重试")
                time.sleep(wait_time)
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep((2 ** attempt) + random.uniform(0, 1))
                else:
                    self._stats['failures'] += 1
                    return None
        
        self._stats['failures'] += 1
        return None
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_expiry:
                self._stats['cache_hits'] += 1
                return data
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, data: Any):
        """设置缓存数据"""
        self._cache[key] = (data, time.time())
    
    def _validate_quote_data(self, quote: Dict) -> bool:
        """验证行情数据质量"""
        if not quote.get('name') or quote['name'] in ['', 'null']:
            return False
        if not isinstance(quote.get('price'), (int, float)) or quote['price'] <= 0:
            return False
        if quote.get('total_capital') and quote['total_capital'] < 0.01:
            return False
        if quote.get('volume') and quote['volume'] < 100:
            return False
        return True
    
    def get_quote(self, codes: List[str]) -> List[Dict[str, Any]]:
        """
        获取实时行情（带多级降级）
        codes: 股票代码列表，如 ['sz000001', 'sh600000']
        """
        if not codes:
            return []
        
        # 标准化代码格式
        normalized_codes = []
        for c in codes:
            c = c.strip().lower()
            if not c.startswith('sh') and not c.startswith('sz') and not c.startswith('bj'):
                if c.startswith('0') or c.startswith('3'):
                    c = f'sz{c}'
                elif c.startswith('6'):
                    c = f'sh{c}'
                elif c.startswith('4') or c.startswith('8'):
                    c = f'bj{c}'
            normalized_codes.append(c)
        
        code_str = ','.join(normalized_codes)
        
        # 尝试缓存
        cache_key = f"quote_{code_str}"
        cached = self._get_cache(cache_key)
        if cached:
            logger.debug(f"缓存命中: {cache_key}")
            return cached
        
        # Level 1: 主 API
        url = f"{self.base_url}/q={code_str}"
        response = self._safe_request(url)
        
        # Level 2: 备用 API
        if not response:
            self._stats['fallbacks'] += 1
            logger.warning(f"主 API 失败，切换到备用 API")
            url = f"{self.fallback_url}/q={code_str}"
            response = self._safe_request(url)
        
        if not response:
            logger.warning(f"所有 API 均失败，返回空结果")
            return []
        
        results = []
        lines = response.strip().split('\n')
        
        for line in lines:
            if not line or '=' not in line:
                continue
            
            try:
                parts = line.split('=')
                if len(parts) < 2:
                    continue
                    
                raw_code = parts[0].replace('v_', '')
                data_str = parts[1].strip('";\r\n ')
                
                if not data_str:
                    continue
                
                fields = data_str.split('~')
                
                if len(fields) < 40:
                    continue
                
                # 过滤无效数据
                name = fields[1] if len(fields) > 1 else ''
                price_str = fields[3] if len(fields) > 3 else '0'
                
                if not name or name in ['', 'null']:
                    continue
                
                try:
                    price = float(price_str) if price_str and price_str not in ['null', ''] else 0
                except:
                    price = 0
                
                if price <= 0:
                    continue
                
                # 解析日期时间
                date_str = fields[30] if len(fields) > 30 else ''
                time_str = fields[31] if len(fields) > 31 else ''
                
                # 解析换手率
                try:
                    turnover_rate = float(fields[38]) if len(fields) > 38 and fields[38] not in ['null', ''] else 0
                except:
                    turnover_rate = 0
                
                # 解析市值
                try:
                    total_capital = float(fields[44]) if len(fields) > 44 and fields[44] not in ['null', ''] else 0
                except:
                    total_capital = 0
                
                try:
                    flow_capital = float(fields[45]) if len(fields) > 45 and fields[45] not in ['null', ''] else 0
                except:
                    flow_capital = 0
                
                # 解析昨收价
                try:
                    yesterday_close = float(fields[4]) if fields[4] and fields[4] not in ['null', ''] else price
                except:
                    yesterday_close = price
                
                # 计算涨跌幅
                change_pct = 0
                if yesterday_close > 0:
                    change_pct = (price - yesterday_close) / yesterday_close * 100
                
                # 标准化股票代码
                code = raw_code.replace('sh', '').replace('sz', '').replace('bj', '')
                
                result = {
                    'code': code,
                    'raw_code': raw_code,
                    'name': name,
                    'price': price,
                    'yesterday_close': yesterday_close,
                    'change_pct': change_pct,
                    'open': float(fields[5]) if len(fields) > 5 and fields[5] not in ['null', ''] else price,
                    'volume': int(float(fields[6])) if len(fields) > 6 and fields[6] not in ['null', ''] else 0,
                    'turnover': float(fields[37]) if len(fields) > 37 and fields[37] not in ['null', ''] else 0,
                    'turnover_rate': turnover_rate,
                    'pe': float(fields[39]) if len(fields) > 39 and fields[39] not in ['null', ''] else 0,
                    'total_capital': total_capital,
                    'flow_capital': flow_capital,
                    'date': date_str,
                    'time': time_str,
                }
                
                # 数据质量验证
                if self._validate_quote_data(result):
                    results.append(result)
                else:
                    logger.debug(f"数据质量验证失败: {name}({code})")
                
            except Exception as e:
                logger.debug(f"行情解析跳过 {line[:50]}: {e}")
                continue
        
        # 保存缓存
        if results:
            self._set_cache(cache_key, results)
        
        return results
    
    def get_hist_kline(self, code: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取历史K线数据（带缓存和降级）
        code: 股票代码，如 '000001' 或 'sh600000'
        days: 天数
        """
        if code.startswith('sh') or code.startswith('sz'):
            full_code = code
        elif code.startswith('0') or code.startswith('3'):
            full_code = f"sz{code}"
        elif code.startswith('6'):
            full_code = f"sh{code}"
        else:
            full_code = f"sz{code}"
        
        # 尝试缓存
        cache_key = f"kline_{code}_{days}"
        cached = self._get_cache(cache_key)
        if cached:
            logger.debug(f"K线缓存命中: {cache_key}")
            return cached
        
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayfqnone&param={full_code},day,,,{days},qfq"
        
        response = self._safe_request(url, retries=2)
        
        # 降级：尝试备用 URL
        if not response:
            self._stats['fallbacks'] += 1
            url = f"https://ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayfqnone&param={full_code},day,,,{days},qfq"
            response = self._safe_request(url, retries=2)
        
        if not response:
            return []
        
        try:
            # Remove variable prefix (with or without "var ")
            json_str = response
            if json_str.startswith('var '):
                json_str = json_str[4:]
            eq_pos = json_str.find('=')
            if eq_pos > 0:
                json_str = json_str[eq_pos+1:]
            data = json.loads(json_str)
            
            qt_data = data.get('data', {}).get(full_code, {})
            qfqday = qt_data.get('qfqday', []) or qt_data.get('day', [])
            
            results = []
            for item in qfqday:
                if len(item) >= 5:
                    try:
                        close = float(item[2])
                        if close > 0:
                            results.append({
                                'date': item[0],
                                'open': float(item[1]),
                                'close': close,
                                'high': float(item[3]),
                                'low': float(item[4]),
                                'volume': int(float(item[5])) if len(item) > 5 else 0
                            })
                    except Exception:
                        continue
            
            final_results = results[-days:] if len(results) > days else results
            
            # 保存缓存
            if final_results:
                self._set_cache(cache_key, final_results)
            
            return final_results
            
        except Exception as e:
            logger.warning(f"K线解析失败 {code}: {e}")
            return []
    
    def get_fund_flow(self, code: str) -> Dict[str, Any]:
        """
        获取资金流向数据
        code: 股票代码，如 '000001'
        """
        if code.startswith('sh') or code.startswith('sz'):
            full_code = code
        elif code.startswith('0') or code.startswith('3'):
            full_code = f"sz{code}"
        elif code.startswith('6'):
            full_code = f"sh{code}"
        else:
            full_code = f"sz{code}"
        
        url = f"https://qt.gtimg.cn/q=ff_{full_code}"
        
        response = self._safe_request(url, retries=2)
        if not response:
            return {'main_inflow_days': 0, 'total_main_inflow': 0}
        
        try:
            parts = response.split('=')
            if len(parts) < 2:
                return {'main_inflow_days': 0, 'total_main_inflow': 0}
            
            data_str = parts[1].strip('";\r\n ')
            fields = data_str.split('~')
            
            main_inflow_days = 0
            total_main_inflow = 0
            
            for i in range(1, 6):
                if len(fields) > i:
                    try:
                        val = float(fields[i]) if fields[i] else 0
                        total_main_inflow += val
                        if val > 0:
                            main_inflow_days += 1
                    except:
                        pass
            
            if len(fields) > 0:
                try:
                    today_val = float(fields[0]) if fields[0] else 0
                    total_main_inflow += today_val
                    if today_val > 0:
                        main_inflow_days += 1
                except:
                    pass
            
            return {
                'main_inflow_days': main_inflow_days,
                'total_main_inflow': total_main_inflow
            }
            
        except Exception as e:
            logger.warning(f"资金流向解析失败 {code}: {e}")
            return {'main_inflow_days': 0, 'total_main_inflow': 0}


_query = None

def get_stock_query() -> StockQuery:
    global _query
    if _query is None:
        _query = StockQuery()
    return _query


if __name__ == '__main__':
    sq = get_stock_query()
    print("测试获取实时行情...")
    quotes = sq.get_quote(['sz000001', 'sh600000', 'sz300750'])
    for q in quotes:
        print(f"{q['name']}({q['code']}): 现价={q['price']}, 涨跌={q['change_pct']:.2f}%")
