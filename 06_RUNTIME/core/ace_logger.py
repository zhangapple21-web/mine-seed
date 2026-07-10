#!/usr/bin/env python3
"""
ACE Logger - Unified logging for Runtime & Workers
Default: silent (log to file only), verbose mode for debugging
"""
import os, sys, logging
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent.parent.parent / "02_MEMORY" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name="ace", level=logging.INFO, silent=True, log_dir=None):
    """
    Get a logger instance.
    
    Args:
        name: logger name
        level: logging level
        silent: if True, only log to file (no console output)
        log_dir: custom log directory
    
    Returns:
        logging.Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers = []
    
    # File handler - always enabled
    log_path = (log_dir or LOG_DIR) / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    
    # Console handler - only when not silent
    if not silent:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(fmt)
        logger.addHandler(ch)
    
    return logger


def silence_all():
    """Silence all third-party loggers"""
    for log_name in ["urllib3", "requests", "telethon", "asyncio"]:
        logging.getLogger(log_name).setLevel(logging.WARNING)


if __name__ == "__main__":
    # Test
    log = get_logger("test", silent=False)
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    print(f"Log file: {LOG_DIR / 'test_' + datetime.now().strftime('%Y%m%d') + '.log'}")