import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))  # Ensure it's an integer