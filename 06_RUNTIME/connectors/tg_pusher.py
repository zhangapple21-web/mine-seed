#!/usr/bin/env python3
import os, json, urllib.request, re


class TGPusher:
    def __init__(self, token=None, chat_id=None):
        self.token = token or os.environ.get("TG_BOT_TOKEN_2", "") or os.environ.get("TG_BOT_TOKEN_1", "")
        self.chat_id = chat_id or os.environ.get("TG_CHAT_ID", "")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def _escape_markdown(self, text):
        special_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{c}' if c in special_chars else c for c in text)

    def send_message(self, text, parse_mode="HTML"):
        if not self.token or not self.chat_id:
            return {"ok": False, "error": "Missing token or chat_id"}

        text = text.strip()
        if len(text) > 4096:
            text = text[:4096] + "..."

        if parse_mode == "Markdown":
            text = self._escape_markdown(text)
        elif parse_mode == "HTML":
            text = text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

        data = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
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

        with open(file_path, "rb") as f:
            file_data = f.read()

        file_name = os.path.basename(file_path)
        boundary = "----TGFormBoundary"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{self.chat_id}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="document"; filename="{file_name}"\r\n'
            f"Content-Type: text/markdown\r\n\r\n"
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

    def send_report(self, file_path):
        """Send report to TG: summary message + full document"""
        if not self.token or not self.chat_id:
            return {"ok": False, "error": "Missing token or chat_id"}

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            summary = self._extract_summary(content)
            msg_result = self.send_message(summary, parse_mode="HTML")

            if not msg_result.get("ok"):
                msg_result = self.send_message(summary, parse_mode=None)
                if not msg_result.get("ok"):
                    return {"ok": False, "error": f"Message send failed: {msg_result.get('error')}"}

            doc_result = self.send_document(file_path, caption="完整报告")

            if doc_result.get("ok"):
                return {"ok": True, "message_sent": True, "document_sent": True}
            else:
                return {"ok": True, "message_sent": True, "document_sent": False, "doc_error": doc_result.get("error")}

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _extract_summary(self, content):
        lines = content.split('\n')
        summary_lines = []
        in_recommend = False
        recommend_count = 0

        for line in lines:
            if line.startswith('## 推荐') and recommend_count < 2:
                in_recommend = True
                recommend_count += 1
                summary_lines.append(line.replace('#', ''))
            elif in_recommend and recommend_count <= 2:
                if line.startswith('|') and '指标' not in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        summary_lines.append(f"<b>{parts[1].strip()}:</b> {parts[2].strip()}")
                elif line.startswith('- ') and len(summary_lines) < 20:
                    summary_lines.append(line)
                elif line.startswith('### ') or line.startswith('---'):
                    in_recommend = False
            elif line.startswith('## 操作建议'):
                summary_lines.append("\n<b>操作建议:</b>")
            elif line.startswith('| 操作 |') or line.startswith('|------'):
                continue
            elif line.startswith('|') and ('仓位' in line or '止损' in line or '止盈' in line):
                parts = line.split('|')
                if len(parts) >= 3:
                    summary_lines.append(f"- {parts[1].strip()}: {parts[2].strip()}")

        return '\n'.join(summary_lines)[:3000]

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
    parser.add_argument("--report", help="Send report (summary + document)")
    parser.add_argument("--test", action="store_true", help="Test connection")
    args = parser.parse_args()

    pusher = TGPusher(token=args.token, chat_id=args.chat_id)

    if args.test:
        result = pusher.test_connection()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.report:
        result = pusher.send_report(args.report)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.file:
        result = pusher.send_document(args.file, caption=args.message or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.message:
        result = pusher.send_message(args.message)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()