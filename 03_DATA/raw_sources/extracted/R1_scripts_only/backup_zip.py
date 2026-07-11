#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR = PROJECT_ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)

def make_backup_zip():
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = BACKUP_DIR / f"R1_persona_lexicons_{ts}.zip"

    include_dirs = [
        "personas",
        "lexicons",
        "configs",
        "metadata",
        "scripts"
    ]

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for d in include_dirs:
            full_dir = PROJECT_ROOT / d
            if not full_dir.exists():
                continue
            for root, _, files in os.walk(full_dir):
                for f in files:
                    full_path = Path(root) / f
                    rel_path = full_path.relative_to(PROJECT_ROOT)
                    zf.write(full_path, arcname=str(rel_path))

    print(f"✅ 备份完成: {zip_name}")

if __name__ == "__main__":
    make_backup_zip()
