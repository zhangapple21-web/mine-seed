#!/usr/bin/env python3
import os, json, urllib.request


class TGPusher:
    def __init__(self, token=None, chat_id=None):
        # Bot 1 (8384...) is invalid. Use Bot 2 (@Sck01Bot) as default.
        self.token = token or os.environ.get("TG_BOT_TOKEN_2", "") or os.environ.get("TG_BOT_TOKEN_1", "")
        self.chat_id = chat_id or os.environ.get("TG_CHAT_ID", "")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text, parse_mode="Markdown"):
        if not self.token or not self.chat_id:
            return {"ok": False, "error": "Missing token or chat_id"}

        data = {
            "chat_id": self.chat_id,
            "text": text[:4096],
            "parse_mode": parse_mode,
        }

        try:
            req = urllib.request.Request(
                f"{self.base_url}/sendMessage",
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_document(self, file_path, caption=""):
        if not self.token or not self.chat_id:
            return {"ok": False, "error": "Missing token or chat_id"}

        import urllib.parse
        boundary = "----TGFormBoundary"
        with open(file_path, "rb") as f:
            file_data = f.read()

        file_name = os.path.basename(file_path)
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{self.chat_id}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="document"; filename="{file_name}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

        try:
            req = urllib.request.Request(
                f"{self.base_url}/sendDocument",
                data=body,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def test_connection(self):
        if not self.token:
            return {"ok": False, "error": "No token"}

        try:
            req = urllib.request.Request(f"{self.base_url}/getMe")
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            return {"ok": False, "error": str(e)}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="TG Pusher")
    parser.add_argument("--token", help="TG Bot Token")
    parser.add_argument("--chat-id", help="TG Chat ID")
    parser.add_argument("--message", help="Message to send")
    parser.add_argument("--file", help="File to send")
    parser.add_argument("--test", action="store_true", help="Test connection")
    args = parser.parse_args()

    pusher = TGPusher(token=args.token, chat_id=args.chat_id)

    if args.test:
        result = pusher.test_connection()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.file:
        result = pusher.send_document(args.file, caption=args.message or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.message:
        result = pusher.send_message(args.message)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()