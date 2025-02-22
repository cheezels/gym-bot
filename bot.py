from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = "7602878718:AAHr763ncvrshWEBWG_WebRRwycWdpq-G1s"

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Welcome to Gym Tracker Bot! Use /enter to check in and /exit to check out.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot is running...")

    app.run_polling()

if __name__ == "__main__":
    main()
