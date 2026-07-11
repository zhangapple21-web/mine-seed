#!/usr/bin/env python3
"""Verify which .session files are valid Telethon sessions with user info"""
import sqlite3, sys, os
from pathlib import Path

def check_session(fpath):
    """Check a session file and return user info"""
    try:
        conn = sqlite3.connect(str(fpath))
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cursor.fetchall()}
        if not tables:
            return {"path": str(fpath), "status": "empty", "tables": []}

        # Check version
        version = None
        if "version" in tables:
            cursor = conn.execute("SELECT * FROM version")
            version = cursor.fetchall()

        # Check for user entity (self)
        user_info = None
        if "entities" in tables:
            cursor = conn.execute(
                "SELECT id, hash, username, phone, name FROM entities "
                "WHERE username IS NOT NULL OR phone IS NOT NULL LIMIT 10"
            )
            rows = cursor.fetchall()
            if rows:
                user_info = [
                    {"id": r[0], "username": r[2], "phone": r[3], "name": r[4]}
                    for r in rows
                ]

        conn.close()
        return {
            "path": str(fpath),
            "status": "valid",
            "tables": list(tables),
            "version": version,
            "entities": user_info,
            "size": Path(fpath).stat().st_size,
        }
    except Exception as e:
        return {"path": str(fpath), "status": "error", "error": str(e)}

# Session files to check
session_files = [
    r"C:\Users\User\tg_collections.session",
    r"C:\Users\User\ace_workspace\mine-seed\05_TOOLS\miner\tg_collections.session",
    r"C:\Users\User\ace_workspace\mine-seed\05_TOOLS\miner\tg_bot_Bot1_Invalid.session",
    r"C:\Users\User\ace_workspace\mine-seed\05_TOOLS\miner\tg_bot_Bot2_Sck01Bot.session",
]

print("=" * 60)
print("Session Verification Report")
print("=" * 60)

for sf in session_files:
    if not Path(sf).exists():
        print(f"\n[MISSING] {sf}")
        continue
    result = check_session(sf)
    print(f"\n[{result['status'].upper()}] {Path(sf).name} ({result.get('size', 0)} bytes)")
    if result["status"] == "valid":
        print(f"  Tables: {', '.join(result['tables'][:5])}")
        if result.get("version"):
            print(f"  Version: {result['version']}")
        if result.get("entities"):
            print(f"  Entities ({len(result['entities'])}):")
            for e in result["entities"][:5]:
                print(f"    id={e['id']} @{e.get('username','')} {e.get('phone','')} {e.get('name','')}")
        else:
            print(f"  No entities with username/phone found")
    elif result["status"] == "error":
        print(f"  Error: {result['error']}")
