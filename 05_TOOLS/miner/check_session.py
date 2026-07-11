#!/usr/bin/env python3
"""Check if existing TG session files are still authorized."""
import asyncio
from telethon import TelegramClient

API_ID = 38398440
API_HASH = "3460f304c16a186c2300debc673b2ed0"

SESSION_FILES = [
    "tg_collections.session",
    r"C:\Users\User\tg_collections.session",
]

async def check():
    for sf in SESSION_FILES:
        print(f"--- Checking: {sf} ---")
        try:
            client = TelegramClient(sf, API_ID, API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                me = await client.get_me()
                name = getattr(me, "first_name", "")
                uid = me.id
                phone = getattr(me, "phone", "N/A")
                print(f"  AUTHORIZED! {name} (id={uid}, phone={phone})")
            else:
                print("  NOT authorized (session expired)")
            await client.disconnect()
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")

asyncio.run(check())
