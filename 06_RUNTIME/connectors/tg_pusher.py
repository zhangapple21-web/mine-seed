#!/usr/bin/env python3
"""
TG Pusher - Telegram Bot Connector
===================================

Message Pipeline:
  Stock Advisor (Markdown)
    → _extract_summary (parse tables, build HTML)
    → send_message (HTML parse_mode)
    → Telegram API

SAFETY RULE: Never escape HTML after adding tags.
Always escape raw text FIRST, then wrap in tags.
"""
import os, json, urllib.request, re


class TGPusher:
    def __init__(self, token=None, chat_id=None):
        self.token = token or os.environ.get("TG_BOT_TOKEN_2", "") or os.environ.get("TG_BOT_TOKEN_1", "")
        self.chat_id = chat_id or os.environ.get("TG_CHAT_ID", "")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    @staticmethod
    def _html_escape(text):
        """Escape HTML special chars. Use BEFORE adding any HTML tags."""
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

    @staticmethod
    def _tag(tag, text):
        """Wrap already-escaped text in an HTML tag."""
        return f"<{tag}>{text}</{tag}>"

    @staticmethod
    def _bold(text):
        return TGPusher._tag("b", TGPusher._html_escape(text))

    @staticmethod
    def _italic(text):
        return TGPusher._tag("i", TGPusher._html_escape(text))

    @staticmethod
    def _code(text):
        return TGPusher._tag("code", TGPusher._html_escape(text))

    def send_message(self, text, parse_mode="HTML"):
        """Send message. If parse_mode=HTML, text must already have proper HTML tags."""
        if not self.token or not self.chat_id:
            return {"ok": False, "error": "Missing token or chat_id"}

        text = text.strip()
        if len(text) > 4096:
            text = text[:4093] + "..."

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
        """Send document file."""
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
        """
        Send full report to TG:
        1. Parse Markdown report → extract key info
        2. Build clean HTML summary message
        3. Send summary message + full document

        This is the MAIN entry point for report delivery.
        """
        if not self.token or not self.chat_id:
            return {"ok": False, "error": "Missing token or chat_id"}

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            summary_html = self._build_summary_html(content)

            msg_result = self.send_message(summary_html, parse_mode="HTML")
            if not msg_result.get("ok"):
                plain_summary = self._build_summary_plain(content)
                msg_result = self.send_message(plain_summary, parse_mode=None)
                if not msg_result.get("ok"):
                    return {"ok": False, "error": f"Message send failed: {msg_result.get('error')}"}

            doc_result = self.send_document(file_path, caption="完整报告")

            return {
                "ok": True,
                "message_sent": True,
                "document_sent": doc_result.get("ok", False),
                "doc_error": None if doc_result.get("ok") else doc_result.get("error"),
            }

        except Exception as e:
            import traceback
            return {"ok": False, "error": str(e), "trace": traceback.format_exc()}

    def _build_summary_html(self, content):
        """
        Parse Markdown report and build HTML summary for TG.
        
        SAFETY: All user-facing text is escaped via _bold() / _html_escape()
        before being inserted into HTML. No raw user text goes into <b> tags
        without escaping first.
        
        Supported sections:
        - 推荐1/推荐2 sections (with | key | value | tables)
        - 操作建议 section
        """
        lines = content.split('\n')
        parts = []
        in_recommend = False
        recommend_count = 0
        in_suggestion = False

        for line in lines:
            line = line.rstrip()

            # Recommend section headers: "## 推荐1：xxx"
            rec_match = re.match(r'^##\s*推荐\d+[：:]\s*(.+)', line)
            if rec_match and recommend_count < 2:
                in_recommend = True
                in_suggestion = False
                recommend_count += 1
                title = rec_match.group(1).strip()
                parts.append(self._bold(f"推荐{recommend_count}：{title}"))
                continue

            # Other level-2 headers (stop recommend parsing)
            if line.startswith('## '):
                in_recommend = False
                if '操作建议' in line:
                    in_suggestion = True
                    parts.append("")
                    parts.append(self._bold("操作建议:"))
                else:
                    in_suggestion = False
                continue

            # Skip all level-3 headers inside recommend
            if line.startswith('### ') or line.startswith('---'):
                continue

            # Table separator: |------|------|
            if re.match(r'^\|[-:| ]+\|$', line):
                continue

            # Table rows inside recommend section: | 指标名 | 数值 |
            if in_recommend and line.startswith('|'):
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) >= 2 and cells[0] not in ('指标', '项目', '操作'):
                    key = cells[0]
                    val = cells[1]
                    parts.append(f"{self._bold(key + ':')} {self._html_escape(val)}")
                continue

            # Table rows inside suggestion section
            if in_suggestion and line.startswith('|'):
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) >= 2 and cells[0] not in ('操作', '指标'):
                    key = cells[0]
                    val = cells[1]
                    parts.append(f"• {self._bold(key)}: {self._html_escape(val)}")
                continue

            # Bullet points
            if in_recommend and line.startswith('- '):
                parts.append(f"• {self._html_escape(line[2:])}")
                continue

        # Truncate to safe length
        result = "\n".join(parts)
        if len(result) > 3800:
            result = result[:3797] + "..."
        return result

    def _build_summary_plain(self, content):
        """Fallback: plain text summary if HTML fails."""
        lines = content.split('\n')
        parts = []
        in_rec = False
        count = 0

        for line in lines:
            if re.match(r'^##\s*推荐\d+', line) and count < 2:
                in_rec = True
                count += 1
                parts.append(line.replace('#', '').strip())
            elif in_rec and line.startswith('|'):
                if re.match(r'^\|[-:| ]+\|$', line):
                    continue
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if len(cells) >= 2 and cells[0] not in ('指标',):
                    parts.append(f"  {cells[0]}: {cells[1]}")
            elif line.startswith('## ') and count >= 2:
                break

        return "\n".join(parts)[:3800]

    def test_connection(self):
        """Test bot API connection."""
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