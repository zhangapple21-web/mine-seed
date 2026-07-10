import os, json, urllib.request, urllib.error

# Load env from miner_env.sh
env_path = r"C:\Users\User\ace_workspace\mine-seed\05_TOOLS\miner\miner_env.sh"
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("export ") and "=" in line:
            k, v = line[7:].split("=", 1)
            v = v.strip().strip('"').strip("'")
            os.environ[k] = v

results = []
for key in ["TG_BOT_TOKEN_1", "TG_BOT_TOKEN_2"]:
    token = os.environ.get(key, "")
    if not token:
        results.append(f"{key}: NOT SET")
        continue
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok"):
                bot = data["result"]
                results.append(f"{key}: @{bot['username']} (id={bot['id']}) OK")
            else:
                results.append(f"{key}: FAIL {data.get('description')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        results.append(f"{key}: HTTP {e.code} {body[:200]}")
    except Exception as e:
        results.append(f"{key}: ERROR {e}")

print("\n".join(results))

# Also get updates to see chats
token = os.environ.get("TG_BOT_TOKEN_1", "")
if token:
    url = f"https://api.telegram.org/bot{token}/getUpdates?limit=5"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok") and data.get("result"):
                chats = set()
                for u in data["result"]:
                    ch = u.get("message", {}).get("chat") or u.get("my_chat_member", {}).get("chat")
                    if ch:
                        chats.add(f"{ch.get('id')} ({ch.get('type')})")
                print("\nRecent chats for Bot 1:")
                print("\n".join(sorted(chats)))
            else:
                print("\nNo recent updates for Bot 1")
    except Exception as e:
        print(f"Updates error: {e}")
