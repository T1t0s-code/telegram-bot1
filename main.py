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
ADMIN_ID = 5024732090  # <-- put YOUR Telegram user ID here

approved_users = set()
pending_text = None


# /start → show button
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📩 Get message", callback_data="GET_TEXT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Welcome.\nPress the button below when instructed.",
        reply_markup=reply_markup
    )


# Admin approves users
async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID")
        return

    user_id = int(context.args[0])
    approved_users.add(user_id)
    await update.message.reply_text(f"User {user_id} approved.")


# Admin sends photo + text
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    global pending_text

    if not update.message.caption:
        await update.message.reply_text("Send photo WITH text.")
        return

    pending_text = update.message.caption
    photo = update.message.photo[-1].file_id

    for user_id in approved_users:
        await context.bot.send_photo(chat_id=user_id, photo=photo)

    await update.message.reply_text("Photo sent to approved users.")


# Button press handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in approved_users:
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


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
