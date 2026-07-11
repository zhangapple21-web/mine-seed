#!/usr/bin/env python3
"""
TG Bot login test — connect using Bot token.
"""
import asyncio
import sys
from pathlib import Path
from telethon import TelegramClient

API_ID = 38398440
API_HASH = "3460f304c16a186c2300debc673b2ed0"

BOTS = {
    "Bot1_Invalid": "8384310757:AAEhfTTMaYrV_n9hXFjBUMh2LdeeWkB-Czo",
    "Bot2_Sck01Bot": "8446702999:AAHw51HYX_EwZhnzmJpQFUy734SnaZpzsCI",
}


async def test_bot(name, token):
    session_file = str(Path(__file__).parent / f"tg_bot_{name}")
    print(f"\n=== Testing {name} ===", flush=True)
    try:
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.connect()
        me = await client.sign_in(bot_token=token)
        print(f"SUCCESS! Bot: {getattr(me, 'first_name', '')} (id={me.id}, username=@{getattr(me, 'username', 'N/A')})", flush=True)
        await client.disconnect()
        return True
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}", flush=True)
        return False


async def main():
    sys.stdout.reconfigure(line_buffering=True)
    for name, token in BOTS.items():
        await test_bot(name, token)


if __name__ == "__main__":
    asyncio.run(main())
