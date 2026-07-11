#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile
from pathlib import Path
import sys

def restore(zip_path: str, target_root: str = None):
    zip_path = Path(zip_path).resolve()
    if target_root:
        target_root = Path(target_root).resolve()
    else:
        target_root = Path(__file__).resolve().parent.parent

    if not zip_path.exists():
        print(f"❌ 未找到备份文件: {zip_path}")
        sys.exit(1)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(path=target_root)

    print(f"✅ 恢复完成：{zip_path} → {target_root}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python restore_from_zip.py 备份文件.zip [目标目录]")
        sys.exit(1)
    restore(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
