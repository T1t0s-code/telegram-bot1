from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8107829492:AAHQm_DMEx-x9crS-E0ZnUbT2FgVz3GE2dA"
ADMIN_ID = 5024732090  # replace with YOUR Telegram user ID

approved_users = set()
pending_text = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot active.\nApproved users can use /send."
    )


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /approve USER_ID")
        return

    user_id = int(context.args[0])
    approved_users.add(user_id)
    await update.message.reply_text(f"User {user_id} approved.")


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

    await update.message.reply_text("Photo sent.")


async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in approved_users:
        await update.message.reply_text("Not approved.")
        return

    if not pending_text:
        await update.message.reply_text("No message available.")
        return

    await update.message.reply_text(pending_text)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Text sent to user {update.effective_user.id}"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("send", send_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()


if __name__ == "__main__":
    main()