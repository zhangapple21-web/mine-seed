#!/usr/bin/env python3
"""
Daily Runner — 荐股系统每日自动化执行器

无人干预执行流程：
  1. 更新历史推荐表现（PerformanceTracker.update_all）
  2. 运行荐股引擎（StockAdvisor.run）
  3. 推送报告到 Telegram
  4. 检查是否需要触发优化
  5. 更新 CURRENT_STATE.md 健康度

容错特性：
  - 每步独立错误处理，不中断整体流程
  - 完整的日志记录
  - 失败重试机制
  - 运行状态持久化

用法:
  python daily_runner.py           # 立即执行
  python daily_runner.py --schedule  # 注册为 Windows 定时任务
  python daily_runner.py --check    # 检查上次运行状态
"""

import os
import sys
import json
import subprocess
import argparse
import time
import traceback
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent.parent
ADVISOR_DIR = WORKSPACE / "05_TOOLS" / "advisor"
MINER_DIR = WORKSPACE / "05_TOOLS" / "miner"

sys.path.insert(0, str(ADVISOR_DIR))

LOG_FILE = ADVISOR_DIR.parent / "mine_output" / "advisor" / "daily_runner.log"
STATUS_FILE = ADVISOR_DIR.parent / "mine_output" / "advisor" / "runner_status.json"


class RunnerLogger:
    """运行日志记录器"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        print(log_line.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)


class RunnerStatus:
    """运行状态管理器"""
    
    def __init__(self, status_file: Path):
        self.status_file = status_file
        self.status = self._load_status()
    
    def _load_status(self) -> dict:
        """加载状态文件"""
        if self.status_file.exists():
            try:
                return json.loads(self.status_file.read_text(encoding='utf-8'))
            except Exception:
                pass
        return {
            "last_run_time": "",
            "last_run_success": False,
            "steps": {},
            "error_message": "",
            "health_score": 0,
            "recommendations": [],
        }
    
    def save_status(self, success: bool, steps: dict = None, 
                    error_message: str = "", health_score: int = 0,
                    recommendations: list = None):
        """保存状态"""
        self.status = {
            "last_run_time": datetime.now().isoformat(),
            "last_run_success": success,
            "steps": steps or {},
            "error_message": error_message,
            "health_score": health_score,
            "recommendations": recommendations or [],
        }
        self.status_file.write_text(json.dumps(self.status, ensure_ascii=False, indent=2), encoding='utf-8')
    
    def get_status(self) -> dict:
        """获取状态"""
        return self.status.copy()


def run_performance_update(logger: RunnerLogger, max_retries: int = 2) -> bool:
    """更新历史推荐表现"""
    logger.log("[1/5] 更新历史表现数据...")
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                [sys.executable, str(ADVISOR_DIR / "performance_tracker.py"), "--update"],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                logger.log("  ✓ 表现数据更新完成")
                return True
            else:
                logger.log(f"  ⚠ 更新失败(尝试 {attempt+1}/{max_retries}): {result.stderr[:200]}", "WARNING")
        except Exception as e:
            logger.log(f"  ⚠ 更新异常(尝试 {attempt+1}/{max_retries}): {e}", "WARNING")
        
        if attempt < max_retries - 1:
            time.sleep(5)
    
    logger.log("  ✗ 更新失败，跳过此步骤", "ERROR")
    return False


def run_stock_advisor(logger: RunnerLogger, max_retries: int = 2) -> tuple[bool, list]:
    """运行荐股引擎"""
    logger.log("[2/5] 运行荐股引擎...")
    
    recommendations = []
    
    for attempt in range(max_retries):
        try:
            from stock_advisor import StockAdvisor
            advisor = StockAdvisor()
            success, report = advisor.run()
            
            if success:
                logger.log("  ✓ 荐股引擎执行成功")
                
                # 提取推荐股票信息
                import re
                for match in re.finditer(r'推荐\d+：([^（]+)（(\d{6})）', report[:2000]):
                    recommendations.append({
                        "name": match.group(1),
                        "code": match.group(2),
                    })
                
                rec_str = ', '.join([f"{r['name']}({r['code']})" for r in recommendations])
                logger.log(f"  推荐结果: {rec_str}")
                return True, recommendations
            else:
                logger.log(f"  ⚠ 荐股引擎执行完成但结果不完整(尝试 {attempt+1}/{max_retries})", "WARNING")
        
        except Exception as e:
            logger.log(f"  ✗ 荐股引擎异常(尝试 {attempt+1}/{max_retries}): {e}", "ERROR")
            logger.log(f"  异常详情: {traceback.format_exc()[:500]}", "DEBUG")
        
        if attempt < max_retries - 1:
            time.sleep(10)
    
    logger.log("  ✗ 荐股引擎多次失败", "ERROR")
    return False, recommendations


def push_to_telegram(logger: RunnerLogger, max_retries: int = 2) -> bool:
    """推送报告到 Telegram"""
    logger.log("[3/5] 推送 Telegram...")
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                [sys.executable, str(WORKSPACE / "05_TOOLS" / "worker_stock_advisor.py"),
                 "--tg", "--force"],
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                logger.log("  ✓ TG 推送完成")
                return True
            else:
                logger.log(f"  ⚠ TG 推送失败(尝试 {attempt+1}/{max_retries}): {result.stderr[:200]}", "WARNING")
        except Exception as e:
            logger.log(f"  ⚠ TG 推送异常(尝试 {attempt+1}/{max_retries}): {e}", "WARNING")
        
        if attempt < max_retries - 1:
            time.sleep(3)
    
    logger.log("  ✗ TG 推送失败，跳过此步骤", "ERROR")
    return False


def check_and_optimize(logger: RunnerLogger) -> tuple[bool, int]:
    """检查是否需要触发优化"""
    logger.log("[4/5] 检查优化需求...")
    
    try:
        from performance_tracker import PerformanceTracker
        from adaptive_scorer import AdaptiveScorer
        
        tracker = PerformanceTracker()
        scorer = AdaptiveScorer()
        
        health = scorer.get_health_score(tracker)
        health_score = health.get('score', 0)
        
        if scorer.should_trigger_optimization(tracker, consecutive_losses_threshold=3):
            logger.log(f"  ⚠ 触发因子优化，正在生成分析报告...", "WARNING")
            logger.log(f"  当前健康度: {health_score}/100 ({health.get('status', 'unknown')})")
            return True, health_score
        else:
            logger.log(f"  ✓ 表现正常，健康度: {health_score}/100")
            return False, health_score
    
    except Exception as e:
        logger.log(f"  ⚠ 优化检查异常: {e}", "WARNING")
        return False, 0


def check_circuit_breaker(logger: RunnerLogger) -> bool:
    """熔断检查：健康度低于阈值时暂停推荐
    
    熔断阈值策略：
    - 健康度 >= 60: 正常推荐
    - 40 <= 健康度 < 60: 警告状态，仍推荐但标记风险
    - 健康度 < 40: 熔断触发，暂停推荐并强制优化
    
    额外条件：
    - 连续5次T+1亏损也触发熔断
    """
    try:
        from performance_tracker import PerformanceTracker
        from adaptive_scorer import AdaptiveScorer
        
        tracker = PerformanceTracker()
        scorer = AdaptiveScorer()
        
        health = scorer.get_health_score(tracker)
        health_score = health.get('score', 0)
        
        # 检查推荐记录是否足够
        summary = tracker.get_summary(10)
        total_recs = summary.get('total_recommendations', 0)
        
        if total_recs < 5:
            logger.log(f"  ✓ 推荐记录不足({total_recs}条)，跳过熔断检查")
            return True
        
        # 条件1：健康度低于40
        if health_score < 40:
            logger.log(f"  ⚠ 熔断触发：健康度 {health_score}/100 < 40")
            return False
        
        # 警告状态：健康度 40-60
        if 40 <= health_score < 60:
            logger.log(f"  ⚠ 警告：健康度 {health_score}/100，建议关注")
        
        # 条件2：连续5次T+1亏损
        recent = sorted(tracker.records.values(), 
                       key=lambda r: r.recommend_date, reverse=True)[:10]
        consecutive_losses = 0
        for rec in recent:
            if rec.return_t1 is not None:
                if rec.return_t1 < 0:
                    consecutive_losses += 1
                    if consecutive_losses >= 5:
                        logger.log(f"  ⚠ 熔断触发：连续 {consecutive_losses} 次T+1亏损")
                        return False
                else:
                    consecutive_losses = 0
        
        # 条件3：最近10次T+1胜率 < 20%
        win_rate_t1 = summary.get('win_rates', {}).get('T+1')
        if win_rate_t1 is not None and win_rate_t1 < 20:
            logger.log(f"  ⚠ 熔断触发：最近10次T+1胜率仅 {win_rate_t1}% < 20%")
            return False
        
        logger.log(f"  ✓ 熔断检查通过，健康度: {health_score}/100")
        return True
        
    except Exception as e:
        logger.log(f"  ⚠ 熔断检查异常: {e}", "WARNING")
        return True


def force_optimization(logger: RunnerLogger) -> bool:
    """强制触发因子优化（熔断时调用）"""
    logger.log("[F] 强制触发因子优化...")
    
    try:
        from performance_tracker import PerformanceTracker
        from adaptive_scorer import AdaptiveScorer
        
        tracker = PerformanceTracker()
        scorer = AdaptiveScorer()
        
        # 执行自适应调整
        adjusted, adjustments = scorer.analyze_and_adjust(tracker)
        
        if adjusted:
            logger.log(f"  ✓ 权重调整完成: {len(adjustments)} 个因子")
        else:
            logger.log(f"  ⚠ 权重调整未触发，可能样本不足")
        
        # 生成优化任务
        task = scorer.generate_optimization_task(tracker)
        
        # 保存优化任务
        task_dir = ADVISOR_DIR.parent / "mine_output" / "advisor" / "optimization_tasks"
        task_dir.mkdir(parents=True, exist_ok=True)
        task_file = task_dir / f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        task_file.write_text(json.dumps(task, ensure_ascii=False, indent=2), encoding='utf-8')
        
        logger.log(f"  ✓ 优化任务已保存: {task_file.name}")
        return True
        
    except Exception as e:
        logger.log(f"  ✗ 强制优化失败: {e}", "ERROR")
        return False


def update_current_state(logger: RunnerLogger) -> bool:
    """更新 CURRENT_STATE.md"""
    logger.log("[5/5] 更新系统状态...")
    
    try:
        from performance_tracker import PerformanceTracker
        from adaptive_scorer import AdaptiveScorer
        
        tracker = PerformanceTracker()
        scorer = AdaptiveScorer()
        health = scorer.get_health_score(tracker)
        
        state_file = WORKSPACE / 'CURRENT_STATE.md'
        if state_file.exists():
            content = state_file.read_text(encoding='utf-8')
            
            health_section = f"""## 荐股系统健康度

> 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

- **健康度评分**: {health.get('score', 50)}/100 ({health.get('status', 'unknown')})
- **最近30天推荐次数**: {health.get('summary', {}).get('total_recommendations', 0)}
- **T+5胜率**: {health.get('summary', {}).get('win_rates', {}).get('T+5', 'N/A')}%
- **T+5平均收益**: {health.get('summary', {}).get('avg_returns', {}).get('T+5', 'N/A')}%

"""
            
            import re
            if '## 荐股系统健康度' in content:
                pattern = r'## 荐股系统健康度\n.*?(?=\n## |\Z)'
                content = re.sub(pattern, health_section.strip(), content, flags=re.DOTALL)
            else:
                content = content.rstrip() + '\n\n' + health_section
            
            state_file.write_text(content, encoding='utf-8')
            logger.log("  ✓ CURRENT_STATE.md 更新完成")
        else:
            logger.log("  ⚠ CURRENT_STATE.md 不存在", "WARNING")
        
        return True
    
    except Exception as e:
        logger.log(f"  ⚠ 更新 CURRENT_STATE 失败: {e}", "WARNING")
        return False


def run_all(logger: RunnerLogger, status_manager: RunnerStatus):
    """执行完整流程"""
    logger.log("=" * 60)
    logger.log(f"每日荐股自动化执行器启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.log("=" * 60)
    
    # 记录事件
    try:
        from daily_event_logger import DailyEventLogger
        evt_logger = DailyEventLogger()
        evt_logger.log("DAILY_RUN_START", "每日荐股自动化执行开始")
    except Exception:
        evt_logger = None
    
    start_time = time.time()
    steps = {}
    recommendations = []
    health_score = 0
    success = True
    
    try:
        # 1. 更新历史表现
        step1_ok = run_performance_update(logger)
        steps["performance_update"] = step1_ok
        if evt_logger:
            evt_logger.log("PERF_UPDATE", "历史表现数据更新完成", {"success": step1_ok})
        
        # 熔断检查：健康度低于阈值时暂停推荐
        health_ok = check_circuit_breaker(logger)
        if not health_ok:
            logger.log("  ⚠ 熔断触发：系统健康度过低，暂停今日推荐", "WARNING")
            if evt_logger:
                evt_logger.log("CIRCUIT_BREAKER", "健康度过低，暂停推荐", {"triggered": True})
            
            step2_ok = False
            recs = []
            
            # 强制触发优化
            force_optimization(logger)
        else:
            # 2. 运行荐股引擎（即使步骤1失败也继续）
            step2_ok, recs = run_stock_advisor(logger)
        steps["stock_advisor"] = step2_ok
        recommendations = recs
        if evt_logger:
            rec_str = ', '.join([f"{r['name']}({r['code']})" for r in recs])
            evt_logger.log("RECOMMEND", f"荐股引擎执行完成: {rec_str}", {"success": step2_ok, "count": len(recs)})
        
        # 3. 推送 TG
        step3_ok = push_to_telegram(logger)
        steps["telegram_push"] = step3_ok
        if evt_logger:
            evt_logger.log("TG_PUSH", "Telegram推送完成", {"success": step3_ok})
        
        # 4. 检查优化
        step4_ok, hs = check_and_optimize(logger)
        steps["optimization_check"] = step4_ok
        health_score = hs
        if evt_logger:
            evt_logger.log("OPTIMIZE_CHECK", f"优化检查完成，健康度: {hs}/100", {"triggered": step4_ok, "health_score": hs})
        
        # 5. 更新状态
        step5_ok = update_current_state(logger)
        steps["state_update"] = step5_ok
        
        # 整体成功判断
        success = step2_ok  # 荐股引擎成功是关键
        
    except Exception as e:
        success = False
        logger.log(f"  ✗ 执行流程异常: {e}", "ERROR")
        logger.log(f"  异常详情: {traceback.format_exc()[:500]}", "DEBUG")
        if evt_logger:
            evt_logger.log("ERROR", f"执行流程异常: {e}", {"error": str(e)})
    
    elapsed = time.time() - start_time
    logger.log(f"\n{'='*60}")
    logger.log(f"执行完成，耗时 {elapsed:.1f} 秒")
    logger.log(f"整体状态: {'✓ 成功' if success else '✗ 失败'}")
    logger.log(f"健康度: {health_score}/100")
    final_rec_str = ', '.join([f"{r['name']}({r['code']})" for r in recommendations])
    logger.log(f"推荐结果: {final_rec_str}")
    logger.log(f"{'='*60}")
    
    if evt_logger:
        evt_logger.log("DAILY_RUN_END", f"每日荐股执行完成，耗时 {elapsed:.1f}s", {
            "success": success,
            "health_score": health_score,
            "elapsed_seconds": round(elapsed, 1),
            "recommendations": [r['code'] for r in recommendations]
        })
    
    # 保存状态
    status_manager.save_status(
        success=success,
        steps=steps,
        health_score=health_score,
        recommendations=recommendations
    )


def schedule_task():
    """注册 Windows 定时任务（工作日 9:20 执行）"""
    print("注册 Windows 定时任务...")
    
    task_name = "ACE_StockAdvisor_Daily"
    script_path = Path(__file__).resolve()
    python_path = sys.executable
    
    cmd = (
        f'schtasks /create /tn "{task_name}" '
        f'/tr "\\"{python_path}\" \\"{script_path}\"" '
        f'/sc weekly /d MON,TUE,WED,THU,FRI /st 09:20 '
        f'/f /ru SYSTEM'
    )
    
    print(f"\n命令: {cmd}")
    print("\n请手动以管理员身份运行以下命令:")
    print(cmd)
    print("\n或者使用 Windows Task Scheduler GUI 创建任务:")
    print(f"  程序: {python_path}")
    print(f"  参数: {script_path}")
    print(f"  触发器: 每周一~五 9:20")
    print(f"  运行身份: SYSTEM（避免用户登录问题）")


def check_status():
    """检查上次运行状态"""
    status_manager = RunnerStatus(STATUS_FILE)
    status = status_manager.get_status()
    
    print("\n上次运行状态:")
    print(f"  时间: {status.get('last_run_time', '未运行')}")
    print(f"  结果: {'✓ 成功' if status.get('last_run_success') else '✗ 失败'}")
    print(f"  健康度: {status.get('health_score', 0)}/100")
    
    if status.get('error_message'):
        print(f"  错误: {status['error_message']}")
    
    if status.get('recommendations'):
        recs = status['recommendations']
        rec_display = ', '.join([f"{r['name']}({r['code']})" for r in recs])
        print(f"  推荐: {rec_display}")
    
    if status.get('steps'):
        print("\n  步骤详情:")
        for step, ok in status['steps'].items():
            print(f"    {'✓' if ok else '✗'} {step}")


def main():
    parser = argparse.ArgumentParser(description="Stock Advisor Daily Runner")
    parser.add_argument("--schedule", action="store_true", help="Show schedule command")
    parser.add_argument("--check", action="store_true", help="Check last run status")
    args = parser.parse_args()
    
    logger = RunnerLogger(LOG_FILE)
    status_manager = RunnerStatus(STATUS_FILE)
    
    if args.schedule:
        schedule_task()
    elif args.check:
        check_status()
    else:
        run_all(logger, status_manager)


if __name__ == "__main__":
    main()