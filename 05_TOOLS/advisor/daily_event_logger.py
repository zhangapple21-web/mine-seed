#!/usr/bin/env python3
"""
Daily Event Logger — 时间感知日志记录器

确保系统时刻知道：
  - 当前时间
  - 今天发生了什么
  - 系统状态变化

设计原则：
  - 自动记录每日事件
  - 支持查询历史事件
  - 与健康度和诊断报告集成
  - 提供时间线视图
"""

import os
import sys
import json
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
        logging.FileHandler(LOG_DIR / 'event.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DailyEventLogger:
    """每日事件记录器"""
    
    EVENT_TYPES = [
        'STARTUP',      # 系统启动
        'RECOMMEND',    # 荐股执行
        'AUDIT',        # 审计完成
        'UPDATE',       # 表现更新
        'OPTIMIZE',     # 优化触发
        'POLICY',       # 策略变更
        'HEALTH',       # 健康度变化
        'ERROR',        # 错误发生
        'WARNING',      # 警告发生
        'SHUTDOWN',     # 系统关闭
    ]
    
    def __init__(self):
        self.events: List[Dict] = []
        self.today_str = datetime.now().strftime('%Y%m%d')
        self._load_events()
    
    def _load_events(self):
        """加载事件日志"""
        event_file = LOG_DIR / 'daily_events.json'
        if event_file.exists():
            try:
                self.events = json.loads(event_file.read_text(encoding='utf-8'))
                logger.info(f"加载事件日志: {len(self.events)} 条")
            except Exception as e:
                logger.warning(f"加载事件日志失败: {e}")
                self.events = []
    
    def _save_events(self):
        """保存事件日志"""
        event_file = LOG_DIR / 'daily_events.json'
        event_file.write_text(json.dumps(self.events, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def log(self, event_type: str, message: str, details: Dict = None):
        """记录事件"""
        if event_type not in self.EVENT_TYPES:
            logger.warning(f"未知事件类型: {event_type}")
            return
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y%m%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'type': event_type,
            'message': message,
            'details': details or {},
        }
        
        self.events.append(event)
        
        # 清理90天前的旧事件
        cutoff = (datetime.now() - timedelta(days=90)).strftime('%Y%m%d')
        self.events = [e for e in self.events if e['date'] >= cutoff]
        
        self._save_events()
        
        logger.info(f"[{event_type}] {message}")
    
    def log_startup(self):
        """记录系统启动"""
        self.log('STARTUP', '荐股系统启动', {
            'timestamp': datetime.now().isoformat(),
            'date': self.today_str,
        })
    
    def log_recommendation(self, stocks: List[Dict]):
        """记录荐股执行"""
        self.log('RECOMMEND', f"荐股完成，推荐 {len(stocks)} 只股票", {
            'stocks': stocks,
            'count': len(stocks),
        })
    
    def log_audit(self, audit_results: List[Dict]):
        """记录审计完成"""
        total = len(audit_results)
        avg_score = sum(r['overall_score'] for r in audit_results) / total if total > 0 else 0
        self.log('AUDIT', f"审计完成，平均评分 {avg_score:.1f}/100", {
            'results': audit_results,
            'avg_score': avg_score,
        })
    
    def log_performance_update(self, updated_count: int):
        """记录表现更新"""
        self.log('UPDATE', f"表现数据更新完成，更新 {updated_count} 条记录", {
            'updated_count': updated_count,
        })
    
    def log_optimization(self, triggered: bool, reason: str = ""):
        """记录优化触发"""
        if triggered:
            self.log('OPTIMIZE', f"触发优化: {reason}", {
                'triggered': True,
                'reason': reason,
            })
        else:
            self.log('OPTIMIZE', "无需优化", {
                'triggered': False,
            })
    
    def log_policy_change(self, policy_id: str, change_type: str):
        """记录策略变更"""
        self.log('POLICY', f"策略变更: {policy_id} {change_type}", {
            'policy_id': policy_id,
            'change_type': change_type,
        })
    
    def log_health(self, score: int, status: str):
        """记录健康度变化"""
        self.log('HEALTH', f"健康度: {score}/100 ({status})", {
            'score': score,
            'status': status,
        })
    
    def log_error(self, message: str, error: Exception = None):
        """记录错误"""
        details = {'message': message}
        if error:
            details['error_type'] = type(error).__name__
            details['error_str'] = str(error)
        self.log('ERROR', message, details)
    
    def log_warning(self, message: str):
        """记录警告"""
        self.log('WARNING', message)
    
    def log_shutdown(self):
        """记录系统关闭"""
        self.log('SHUTDOWN', '荐股系统关闭')
    
    def get_today_events(self) -> List[Dict]:
        """获取今日事件"""
        return [e for e in self.events if e['date'] == self.today_str]
    
    def get_recent_events(self, days: int = 7) -> List[Dict]:
        """获取最近N天事件"""
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        return [e for e in self.events if e['date'] >= cutoff]
    
    def get_timeline(self, days: int = 7) -> Dict[str, List[Dict]]:
        """获取时间线视图"""
        recent = self.get_recent_events(days)
        timeline = {}
        
        for event in sorted(recent, key=lambda x: x['timestamp']):
            date = event['date']
            if date not in timeline:
                timeline[date] = []
            timeline[date].append({
                'time': event['time'],
                'type': event['type'],
                'message': event['message'],
            })
        
        return timeline
    
    def get_daily_summary(self, date_str: str = None) -> Dict[str, Any]:
        """获取某日摘要"""
        date_str = date_str or self.today_str
        
        day_events = [e for e in self.events if e['date'] == date_str]
        
        summary = {
            'date': date_str,
            'total_events': len(day_events),
            'by_type': {},
            'recommendations': [],
            'health_score': None,
        }
        
        for event in day_events:
            evt_type = event['type']
            summary['by_type'][evt_type] = summary['by_type'].get(evt_type, 0) + 1
            
            if evt_type == 'RECOMMEND':
                summary['recommendations'].extend(event['details'].get('stocks', []))
            elif evt_type == 'HEALTH':
                summary['health_score'] = event['details'].get('score')
        
        return summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Daily Event Logger")
    parser.add_argument("--timeline", type=int, default=7, help="Show timeline for N days")
    parser.add_argument("--today", action="store_true", help="Show today's events")
    parser.add_argument("--summary", action="store_true", help="Show today's summary")
    parser.add_argument("--log", type=str, help="Log event (type:message)")
    args = parser.parse_args()
    
    logger = DailyEventLogger()
    
    if args.timeline:
        timeline = logger.get_timeline(args.timeline)
        print(f"时间线（最近{args.timeline}天）:")
        for date, events in timeline.items():
            print(f"\n📅 {date}")
            for evt in events:
                print(f"  {evt['time']} [{evt['type']}] {evt['message']}")
    
    if args.today:
        events = logger.get_today_events()
        print(f"\n今日事件 ({len(events)} 条):")
        for evt in events:
            print(f"  {evt['time']} [{evt['type']}] {evt['message']}")
    
    if args.summary:
        summary = logger.get_daily_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    if args.log:
        parts = args.log.split(':', 1)
        if len(parts) >= 2:
            evt_type, message = parts[0], parts[1]
            logger.log(evt_type.upper(), message)


if __name__ == "__main__":
    main()