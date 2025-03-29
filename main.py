import json
import os
import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

Import configuration

from config import Config

Logging setup

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO) logger = logging.getLogger(name)

Load user data

USER_FILE = "user.json" if os.path.exists(USER_FILE): with open(USER_FILE, "r") as f: users = json.load(f) else: users = {}

Command to add string session

async def addstring(update: Update, context: CallbackContext): chat_id = str(update.effective_chat.id) if not context.args: await update.message.reply_text("❌ Please provide a valid string session.") return

string_session = " ".join(context.args)
users[chat_id] = {"session": string_session, "group": None, "posts": [], "reporting": False}

with open(USER_FILE, "w") as f:
    json.dump(users, f, indent=4)

await update.message.reply_text("✅ String session added successfully!")

Start command

async def start(update: Update, context: CallbackContext): chat_id = str(update.effective_chat.id) if chat_id not in users or "session" not in users[chat_id]: await update.message.reply_text("❌ Please add your string session first using /addstring <session>.") return

keyboard = [
    [InlineKeyboardButton("📌 Add Report", callback_data="add_report")],
    [InlineKeyboardButton("🚀 Start Reporting", callback_data="start_reporting")]
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

Handle button clicks

async def button_click(update: Update, context: CallbackContext): query = update.callback_query chat_id = str(query.message.chat.id) await query.answer()

if query.data == "add_report":
    await query.message.reply_text("🔗 Send the group link you want to report.")
    context.user_data["step"] = "group_link"
elif query.data == "start_reporting":
    if chat_id in users and users[chat_id]["group"]:
        users[chat_id]["reporting"] = True
        with open(USER_FILE, "w") as f:
            json.dump(users, f, indent=4)
        await query.message.reply_text("🚀 Reporting started! Use /stop to stop it.")
        await start_reporting(chat_id, context)
    else:
        await query.message.reply_text("❌ No report found. Use /add first.")

Handle messages for group link, post link, and report reason

async def message_handler(update: Update, context: CallbackContext): chat_id = str(update.effective_chat.id) text = update.message.text

if "step" in context.user_data:
    step = context.user_data["step"]
    if step == "group_link":
        users[chat_id]["group"] = text
        context.user_data["step"] = "post_link"
        await update.message.reply_text("📌 Send the post link you want to report.")
    elif step == "post_link":
        users[chat_id]["posts"].append(text)
        context.user_data["step"] = "report_reason"
        await update.message.reply_text("❓ What is the reason for this report?")
    elif step == "report_reason":
        users[chat_id]["reason"] = text
        context.user_data.pop("step")
        with open(USER_FILE, "w") as f:
            json.dump(users, f, indent=4)
        await update.message.reply_text("✅ Report added! Use /start and press 'Start Reporting' to begin.")

Function to continuously report

async def start_reporting(chat_id, context): while chat_id in users and users[chat_id].get("reporting", False): group = users[chat_id]["group"] posts = users[chat_id]["posts"] reason = users[chat_id].get("reason", "Spam or Inappropriate Content")

message = f"🚨 **Reporting Alert** 🚨\n🔗 Group: {group}\n📌 Posts: {'\n'.join(posts)}\n⚠️ Reason: {reason}"
    await context.bot.send_message(chat_id=Config.ADMIN_CHAT_ID, text=message, parse_mode="Markdown")
    await context.bot.send_message(chat_id, "✅ Report sent! Continuing...")
    time.sleep(30)  # Wait 30 seconds before next report

Stop reporting

async def stop(update: Update, context: CallbackContext): chat_id = str(update.effective_chat.id) if chat_id in users: users[chat_id]["reporting"] = False with open(USER_FILE, "w") as f: json.dump(users, f, indent=4) await update.message.reply_text("⏹️ Reporting stopped!") else: await update.message.reply_text("❌ No active reporting found.")

Main function

def main(): app = Application.builder().token(Config.BOT_TOKEN).build()

app.add_handler(CommandHandler("addstring", addstring))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
app.add_handler(CallbackQueryHandler(button_click))

app.run_polling()

if name == "main": main()

