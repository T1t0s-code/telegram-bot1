import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.environ.get("8107829492:AAHQm_DMEx-x9crS-E0ZnUbT2FgVz3GE2dA")
ADMIN_ID = 5024732090  # <-- PUT YOUR TELEGRAM USER ID

USERS_FILE = "users.txt"
pending_text = None


# ---------- helpers ----------
def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as f:
        return set(int(line.strip()) for line in f if line.strip())


def save_user(user_id: int):
    users = load_users()
    users.add(user_id)
    with open(USERS_FILE, "w") as f:
        for uid in users:
            f.write(f"{uid}\n")


# ---------- commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📩 Get message", callback_data="GET_TEXT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Bot ready.\nPress the button when instructed.",
        reply_markup=reply_markup
    )


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID")
        return

    user_id = int(context.args[0])
    save_user(user_id)
    await update.message.reply_text(f"User {user_id} approved permanently.")


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = load_users()
    if not users:
        await update.message.reply_text("No approved users.")
        return

    text = "Approved users:\n" + "\n".join(str(u) for u in users)
    await update.message.reply_text(text)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    global pending_text

    if not update.message.caption:
        await update.message.reply_text("Send photo WITH text.")
        return

    pending_text = update.message.caption
    photo = update.message.photo[-1].file_id

    users = load_users()
    for user_id in users:
        await context.bot.send_photo(chat_id=user_id, photo=photo)

    await update.message.reply_text("Photo sent to all approved users.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    users = load_users()

    if user_id not in users:
        await query.message.reply_text("You are not approved.")
        return

    if not pending_text:
        await query.message.reply_text("No message available.")
        return

    await query.message.reply_text(pending_text)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Text sent to user {user_id}"
    )


# ---------- main ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("list", list_users))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
