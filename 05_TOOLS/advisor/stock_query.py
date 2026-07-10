#!/usr/bin/env python3
"""
腾讯行情API降级方案 - stock_query.py
当akshare被限流时使用此工具获取股票数据
"""
import time
import json
import random
import logging
from typing import Optional, List, Dict, Any
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

class StockQuery:
    """腾讯行情查询工具"""
    
    def __init__(self):
        self.base_url = "https://qt.gtimg.cn"
        self.fallback_url = "https://ifzq.gtimg.cn"
        
    def _safe_request(self, url: str, retries: int = 3) -> Optional[str]:
        """安全的HTTP请求，带重试"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.qq.com',
            'Accept': '*/*'
        }
        
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    return resp.read().decode('gbk', errors='replace')
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1 + random.uniform(0, 1))
                else:
                    return None
        return None
    
    def get_quote(self, codes: List[str]) -> List[Dict[str, Any]]:
        """
        获取实时行情
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
        url = f"{self.base_url}/q={code_str}"
        
        response = self._safe_request(url)
        if not response:
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
                
                results.append(result)
                
            except Exception as e:
                logger.debug(f"行情解析跳过 {line[:50]}: {e}")
                continue
        
        return results
    
    def get_hist_kline(self, code: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        获取历史K线数据
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
        
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?_var=kline_dayfqnone&param={full_code},day,,,{days},qfq"
        
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
                    results.append({
                        'date': item[0],
                        'open': float(item[1]),
                        'close': float(item[2]),
                        'high': float(item[3]),
                        'low': float(item[4]),
                        'volume': int(float(item[5])) if len(item) > 5 else 0
                    })
            
            return results[-days:] if len(results) > days else results
            
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
