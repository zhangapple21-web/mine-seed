#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gen_manifest.py

生成 / 更新 metadata/manifest.json
- 只根据目录结构和文件名推断元信息
- 不读取、不修改任何词库 / 配置 / 人格脚本内容
"""

import json
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METADATA_DIR = PROJECT_ROOT / "metadata"
LEXICONS_DIR = PROJECT_ROOT / "lexicons"
CONFIGS_DIR = PROJECT_ROOT / "configs"
PERSONAS_DIR = PROJECT_ROOT / "personas"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
MANIFEST_PATH = METADATA_DIR / "manifest.json"


def infer_channel_from_path(path: Path) -> str:
    """
    从 lexicons 子目录名推断 channel
    lexicons/telegram/xxx.json -> telegram
    """
    try:
        parts = path.relative_to(LEXICONS_DIR).parts
        if len(parts) >= 2:
            return parts[0].lower()
    except ValueError:
        pass
    return "other"


def infer_format_from_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return "json_pairs"
    if suffix == ".csv":
        return "csv"
    if suffix in (".txt", ".md"):
        return "txt_pairs"
    return "custom"


def infer_trigger_mode(path: Path) -> str:
    """
    不解析内容，根据文件名给一个默认值
    """
    name = path.stem.lower()
    if "fuzzy" in name:
        return "fuzzy"
    if "regex" in name:
        return "regex"
    if "embed" in name or "semantic" in name:
        return "embedding"
    return "keyword_exact"


def snake_id_from_path(path: Path) -> str:
    """
    lexicons/telegram/qa_keywords.json -> telegram_qa_keywords
    """
    try:
        rel = path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel = path
    parts = list(rel.parts)
    if len(parts) >= 2 and parts[0] in ("lexicons", "configs", "personas", "scripts", "metadata"):
        parts = parts[1:]
    base = "_".join(p.replace(".", "_") for p in parts)
    return base.lower()


def scan_lexicons():
    entries = []
    if not LEXICONS_DIR.exists():
        return entries

    for root, _, files in os.walk(LEXICONS_DIR):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(PROJECT_ROOT)
            channel = infer_channel_from_path(full_path)
            fmt = infer_format_from_suffix(full_path)
            trig = infer_trigger_mode(full_path)
            lex_id = snake_id_from_path(full_path)

            entry = {
                "id": lex_id,
                "path": str(rel_path).replace("\\", "/"),
                "channel": channel,
                "trigger_mode": trig,
                "direction": "inbound",
                "format": fmt,
                "schema": {
                    "pair_mode": "qa",
                    "key_field": "question",
                    "reply_field": "answer",
                    "extra_fields": []
                },
                "priority": 100,
                "enabled": True,
                "semantic_tags": [],
                "notes": "auto-generated manifest entry"
            }
            entries.append(entry)
    return entries


def scan_simple_dir(base_dir: Path, type_name: str):
    entries = []
    if not base_dir.exists():
        return entries

    for root, _, files in os.walk(base_dir):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(PROJECT_ROOT)
            entries.append({
                "path": str(rel_path).replace("\\", "/"),
                "type": type_name,
                "notes": f"auto-scanned {type_name} file"
            })
    return entries


def load_existing_manifest():
    if MANIFEST_PATH.exists():
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def main():
    METADATA_DIR.mkdir(exist_ok=True)

    existing = load_existing_manifest()

    manifest = {
        "version": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": existing.get("description", "R1 人格 + 词库 manifest（自动生成）"),
        "lexicons": scan_lexicons(),
        "configs": scan_simple_dir(CONFIGS_DIR, "config"),
        "personas": scan_simple_dir(PERSONAS_DIR, "persona"),
        "scripts": scan_simple_dir(SCRIPTS_DIR, "script")
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print("✅ manifest 已生成/更新:", MANIFEST_PATH)


if __name__ == "__main__":
    main()
