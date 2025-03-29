import json
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Import configuration
from config import Config

# Logging setup
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load user data
USER_FILE = "user.json"
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        users = json.load(f)
else:
    users = {}

# Command to add report
async def add(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id not in users:
        users[chat_id] = {"group": None, "posts": []}
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/add <group_link> <post_url>`", parse_mode="Markdown")
        return
    
    group_link = context.args[0]
    post_url = " ".join(context.args[1:])

    users[chat_id]["group"] = group_link
    users[chat_id]["posts"].append(post_url)
    
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)
    
    await update.message.reply_text(f"✅ Added Post: {post_url} in Group: {group_link}")

# Command to send report
async def send_report(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id not in users or not users[chat_id]["group"]:
        await update.message.reply_text("❌ No group or posts found! Use `/add` first.", parse_mode="Markdown")
        return
    
    group = users[chat_id]["group"]
    posts = "\n".join(users[chat_id]["posts"])
    message = f"📢 **Report:**\n🔗 Group: {group}\n📌 Posts:\n{posts}"
    
    await context.bot.send_message(chat_id=Config.ADMIN_CHAT_ID, text=message, parse_mode="Markdown")
    await update.message.reply_text("✅ Report sent successfully!")
    users.pop(chat_id)

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("👋 Welcome! Use `/add` to add a report.")

def main():
    app = Application.builder().token(Config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("send_report", send_report))

    app.run_polling()

if __name__ == "__main__":
    main()