import os
import requests
from core.tools import BaseTool


class TelegramSendMessageTool(BaseTool):
    """
    Send a Telegram message to a chat/group using the Telegram Bot API.
    """
    def __init__(self):
        super().__init__(
            name="TelegramSendMessage",
            description="Send a message to a Telegram chat, group, or channel using a Bot. Useful for notifying team members."
        )

    def get_schema(self):
        return f"""
============= {self.name} =============
{self.description}

Action Value: {self.name}
Action Input Format (JSON):
{{
  "chat_id": "-1001234567890",  // Telegram chat/group ID (get from bot or user)
  "text": "Your message here",
  "parse_mode": "Markdown"      // Optional: "Markdown", "HTML", or empty
}}
==========================================
"""

    def execute(self, **kwargs):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return "Error: TELEGRAM_BOT_TOKEN not set in .env. Get a token from @BotFather on Telegram."

        chat_id = kwargs.get("chat_id")
        text = kwargs.get("text")
        parse_mode = kwargs.get("parse_mode", "Markdown")

        if not chat_id or not text:
            return "Error: 'chat_id' and 'text' are required."

        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": text}
            if parse_mode:
                payload["parse_mode"] = parse_mode

            resp = requests.post(url, json=payload, timeout=10)
            data = resp.json()
            if data.get("ok"):
                return f"✅ Message sent to chat {chat_id}: '{text[:60]}...'" if len(text) > 60 else f"✅ Message sent to chat {chat_id}: '{text}'"
            else:
                return f"Error from Telegram: {data.get('description', 'Unknown error')}"
        except Exception as e:
            return f"TelegramSendMessage failed: {e}"


class TelegramGetUpdatesTool(BaseTool):
    """
    Poll recent messages from a Telegram Bot.
    """
    def __init__(self):
        super().__init__(
            name="TelegramGetUpdates",
            description="Fetch the latest messages/updates received by your Telegram Bot. Use to check for team replies."
        )

    def get_schema(self):
        return f"""
============= {self.name} =============
{self.description}

Action Value: {self.name}
Action Input Format (JSON):
{{
  "limit": 5  // How many recent updates to fetch (max 100)
}}
==========================================
"""

    def execute(self, **kwargs):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return "Error: TELEGRAM_BOT_TOKEN not set in .env."

        limit = kwargs.get("limit", 5)

        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            resp = requests.get(url, params={"limit": limit, "allowed_updates": ["message"]}, timeout=10)
            data = resp.json()
            if not data.get("ok"):
                return f"Error: {data.get('description', 'Unknown error')}"

            updates = data.get("result", [])
            if not updates:
                return "No new messages."

            lines = []
            for u in updates:
                msg = u.get("message", {})
                sender = msg.get("from", {}).get("first_name", "Unknown")
                text = msg.get("text", "[non-text]")
                chat = msg.get("chat", {}).get("title") or msg.get("chat", {}).get("first_name", "Unknown")
                lines.append(f"[{chat}] {sender}: {text}")

            return "\n".join(lines)
        except Exception as e:
            return f"TelegramGetUpdates failed: {e}"


class TelegramGetChatIdTool(BaseTool):
    """
    Get the chat_id of a group or user from recent messages.
    """
    def __init__(self):
        super().__init__(
            name="TelegramGetChatId",
            description="Get available chat IDs from recent Telegram messages. Use this first to discover group/chat IDs."
        )

    def get_schema(self):
        return f"""
============= {self.name} =============
{self.description}

Action Value: {self.name}
Action Input Format (JSON):
{{}}  // No input required
==========================================
"""

    def execute(self, **kwargs):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return "Error: TELEGRAM_BOT_TOKEN not set in .env."

        try:
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            resp = requests.get(url, params={"limit": 20}, timeout=10)
            data = resp.json()
            if not data.get("ok"):
                return f"Error: {data.get('description')}"

            chats = {}
            for u in data.get("result", []):
                msg = u.get("message", {})
                chat = msg.get("chat", {})
                cid = chat.get("id")
                title = chat.get("title") or f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip()
                if cid:
                    chats[cid] = title or f"Chat {cid}"

            if not chats:
                return "No chats found. Send a message to your bot first (or add it to a group), then try again."

            return "\n".join([f"chat_id={cid}  name='{name}'" for cid, name in chats.items()])
        except Exception as e:
            return f"TelegramGetChatId failed: {e}"
