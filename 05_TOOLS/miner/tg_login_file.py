#!/usr/bin/env python3
"""
TG login — default mode (let Telegram decide code delivery).
Polls tg_login_code.txt for the code (non-interactive).
"""
import asyncio
import sys
from pathlib import Path
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, FloodWaitError

API_ID = 38398440
API_HASH = "3460f304c16a186c2300debc673b2ed0"
SESSION_FILE = str(Path(__file__).parent / "tg_collections")
PHONE = "+85592538691"

LOGIN_CODE_FILE = Path(__file__).parent / "tg_login_code.txt"


async def main():
    # Force output flush
    sys.stdout.reconfigure(line_buffering=True)

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    print("Connected to Telegram servers.", flush=True)

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Already logged in: {getattr(me, 'first_name', '')} (id={me.id})", flush=True)
        await client.disconnect()
        return

    print(f"Sending code to {PHONE}...", flush=True)

    result = None
    try:
        result = await client.send_code_request(PHONE)
    except FloodWaitError as e:
        print(f"FLOOD WAIT: {e.seconds}s ({e.seconds // 60} min)", flush=True)
        await client.disconnect()
        return
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", flush=True)
        await client.disconnect()
        return

    sent_type = type(result.type).__name__
    print(f"Code type: {sent_type}", flush=True)
    print(f"Hash: {result.phone_code_hash}", flush=True)

    if hasattr(result, "next_type") and result.next_type:
        print(f"Next type: {type(result.next_type).__name__}", flush=True)

    # Wait for code file
    print(f"Write code to: {LOGIN_CODE_FILE}", flush=True)
    print("Line 1 = code, Line 2 = 2FA password (optional)", flush=True)
    print("Polling every 5s (10 min max)...", flush=True)

    phone_code_hash = result.phone_code_hash

    for attempt in range(120):
        await asyncio.sleep(5)
        if LOGIN_CODE_FILE.exists():
            try:
                lines = LOGIN_CODE_FILE.read_text().strip().splitlines()
                code = lines[0].strip() if lines else ""
                pwd = lines[1].strip() if len(lines) > 1 else ""
                if code:
                    print(f"Code: {code}", flush=True)
                    LOGIN_CODE_FILE.unlink()

                    try:
                        await client.sign_in(phone=PHONE, code=code, phone_code_hash=phone_code_hash)
                    except SessionPasswordNeededError:
                        if pwd:
                            print("Using 2FA password...", flush=True)
                            await client.sign_in(password=pwd)
                        else:
                            print("2FA needed! Write password to tg_login_code.txt", flush=True)
                            for _ in range(60):
                                await asyncio.sleep(5)
                                if LOGIN_CODE_FILE.exists():
                                    new_pwd = LOGIN_CODE_FILE.read_text().strip().splitlines()[0].strip()
                                    if new_pwd:
                                        LOGIN_CODE_FILE.unlink()
                                        await client.sign_in(password=new_pwd)
                                        break
                            else:
                                print("Timeout waiting for 2FA", flush=True)
                                await client.disconnect()
                                return
                    except Exception as e:
                        print(f"Login error: {type(e).__name__}: {e}", flush=True)
                        await client.disconnect()
                        return

                    me = await client.get_me()
                    print(f"LOGIN SUCCESS: {getattr(me, 'first_name', '')} (id={me.id})", flush=True)
                    print(f"Session: {SESSION_FILE}.session", flush=True)
                    await client.disconnect()
                    return
            except Exception as e:
                print(f"Error: {e}", flush=True)
                continue

        if attempt % 12 == 0 and attempt > 0:
            print(f"  Waiting... {attempt * 5}s", flush=True)

    print("Timeout!", flush=True)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
