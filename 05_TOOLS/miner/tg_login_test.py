#!/usr/bin/env python3
"""
TG Login Test — 分两步测试TG登录和验证码接收
Step 1: python tg_login_test.py --phone +855xxxx --send-code
Step 2: python tg_login_test.py --phone +855xxxx --code 12345
"""
import os, sys, json, asyncio, argparse
from pathlib import Path

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError

API_ID = 38398440
API_HASH = "3460f304c16a186c2300debc673b2ed0"
SESSION_FILE = str(Path(__file__).parent / "tg_collections")
STATE_FILE = Path(__file__).parent / "tg_login_state.json"


async def send_code(phone):
    """Step 1: 发送验证码"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"ALREADY_LOGGED_IN")
        print(f"User: {getattr(me, 'first_name', '')} {getattr(me, 'last_name', '')} (id={me.id})")
        await client.disconnect()
        return

    try:
        result = await client.send_code_request(phone)
        # Save state for step 2
        state = {
            "phone": phone,
            "phone_code_hash": result.phone_code_hash,
            "sent": True,
        }
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"CODE_SENT")
        print(f"Phone: {phone}")
        print(f"Phone code hash saved to {STATE_FILE}")
    except FloodWaitError as e:
        print(f"FLOOD_WAIT")
        print(f"Need to wait {e.seconds} seconds before retrying")
    except Exception as e:
        print(f"ERROR")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")

    await client.disconnect()


async def login_with_code(phone, code, password=None):
    """Step 2: 用验证码登录"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    # Load phone_code_hash from state
    phone_code_hash = None
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        phone_code_hash = state.get("phone_code_hash")

    try:
        if phone_code_hash:
            await client.sign_in(
                phone=phone,
                code=code,
                phone_code_hash=phone_code_hash,
            )
        else:
            await client.sign_in(phone=phone, code=code)

        me = await client.get_me()
        print(f"LOGIN_SUCCESS")
        print(f"User: {getattr(me, 'first_name', '')} {getattr(me, 'last_name', '')} (id={me.id})")
        print(f"Session saved to {SESSION_FILE}.session")

        # Clean up state
        if STATE_FILE.exists():
            STATE_FILE.unlink()

    except SessionPasswordNeededError:
        print(f"PASSWORD_NEEDED")
        print("Two-step verification is enabled. Need password.")
        if password:
            try:
                await client.sign_in(password=password)
                me = await client.get_me()
                print(f"LOGIN_SUCCESS")
                print(f"User: {getattr(me, 'first_name', '')} {getattr(me, 'last_name', '')} (id={me.id})")
            except Exception as e:
                print(f"PASSWORD_ERROR: {e}")
        else:
            # Save state for password step
            state = {"phone": phone, "need_password": True}
            STATE_FILE.write_text(json.dumps(state), encoding="utf-8")

    except PhoneCodeInvalidError:
        print(f"CODE_INVALID")
        print("The verification code is invalid or expired.")
    except Exception as e:
        print(f"ERROR")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")

    await client.disconnect()


async def check_session():
    """Check if existing session is still valid"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"SESSION_VALID")
        print(f"User: {getattr(me, 'first_name', '')} {getattr(me, 'last_name', '')} (id={me.id})")
    else:
        print(f"SESSION_INVALID")
        print("Session expired or not logged in. Need to re-login.")

    await client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="TG Login Test")
    parser.add_argument("--phone", help="Phone number (e.g. +855xxxxxxx)")
    parser.add_argument("--code", help="Verification code")
    parser.add_argument("--password", help="Two-step verification password")
    parser.add_argument("--send-code", action="store_true", help="Step 1: Send verification code")
    parser.add_argument("--check", action="store_true", help="Check existing session")
    args = parser.parse_args()

    if args.check:
        asyncio.run(check_session())
    elif args.send_code and args.phone:
        asyncio.run(send_code(args.phone))
    elif args.code and args.phone:
        asyncio.run(login_with_code(args.phone, args.code, args.password))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
