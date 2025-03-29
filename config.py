import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "your_telegram_bot_token")
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "your_admin_chat_id")