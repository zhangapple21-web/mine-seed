#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
build_full_zip.py

一键生成完整项目 ZIP：
1. 先调用 gen_manifest.py 更新 metadata/manifest.json
2. 再调用 backup_zip.py 打包 personas/lexicons/configs/metadata/scripts
"""

import subprocess
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def run(cmd):
    print(f"▶ 运行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode != 0:
        print(f"❌ 命令执行失败: {' '.join(cmd)}")
        sys.exit(result.returncode)

def main():
    scripts_dir = PROJECT_ROOT / "scripts"

    gen_script = scripts_dir / "gen_manifest.py"
    backup_script = scripts_dir / "backup_zip.py"

    if gen_script.exists():
        run([sys.executable, str(gen_script)])
    else:
        print("⚠️ 未找到 gen_manifest.py，跳过 manifest 生成")

    if backup_script.exists():
        run([sys.executable, str(backup_script)])
    else:
        print("⚠️ 未找到 backup_zip.py，无法生成备份 ZIP")

if __name__ == "__main__":
    main()
