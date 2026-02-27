import os
import re
import logging
from flask import Flask
from threading import Thread
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

warns = {}

# --------- Anti Spam Function ---------
async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    user = message.from_user
    text = message.text

    if not text:
        return

    # Detect links
    if re.search(r"http[s]?://|t\.me|@\w+", text.lower()):
        await message.delete()

        user_id = user.id
        warns[user_id] = warns.get(user_id, 0) + 1

        if warns[user_id] >= 3:
            await update.effective_chat.restrict_member(
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=None,
            )
            await update.effective_chat.send_message(
                f"🚫 {user.first_name} muted for spamming."
            )
        else:
            await update.effective_chat.send_message(
                f"⚠️ {user.first_name} warning {warns[user_id]}/3"
            )

# --------- Start Command ---------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Group Protection Bot is Active!\n\nAnti-Spam Enabled."
    )

# --------- Flask App (Render Needs Web Service Running) ---------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --------- Main ---------
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), anti_spam)
    )

    application.run_polling()

if __name__ == "__main__":
    Thread(target=run_flask).start()
    main()
