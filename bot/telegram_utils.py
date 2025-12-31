

import requests
import os

BOT_TOKEN = "8559021305:AAGWBCaz0-aNWiRsTY0BN9PqO2J-NE_FZLs"
CHAT_ID ="6635912493"

# BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
# CHAT_ID = os.getenv("TG_CHAT_ID")

def send_telegram(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram not configured")
        return

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=5
        )
    except Exception as e:
        print("Telegram error:", e)



send_telegram("✅ Telegram connected successfully")