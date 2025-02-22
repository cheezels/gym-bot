import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7602878718:AAHr763ncvrshWEBWG_WebRRwycWdpq-G1s"

# Dictionary to track users in gym
gym_users = set()

# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command and shows a menu."""
    keyboard = [
        ["/enter", "/exit"],
        ["/capacity"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Welcome to Gym Tracker Bot!\nChoose an option below:",
        reply_markup=reply_markup
    )


async def enter_gym(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in gym_users:
        await update.message.reply_text("You are already in the gym!")
    else:
        gym_users.add(user_id)
        await update.message.reply_text("You have entered the gym. Welcome!")

async def exit_gym(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id in gym_users:
        gym_users.remove(user_id)
        await update.message.reply_text("You have left the gym. Goodbye!")
    else:
        await update.message.reply_text("You have already left the gym.")

async def check_capacity(update: Update, context: CallbackContext) -> None:
    number = len(gym_users)
    await update.message.reply_text(f"Current gym occupancy: {number} ")



def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enter", enter_gym))
    app.add_handler(CommandHandler("exit", exit_gym))
    app.add_handler(CommandHandler("capacity", check_capacity))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
