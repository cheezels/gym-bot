import logging
import asyncio
import threading
from datetime import datetime, time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext, ConversationHandler

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

CAPACITY = 0;
DELAY = 1;

async def set_alert(update: Update, context: CallbackContext):
    """Start the conversation to set an alert."""
    await update.message.reply_text("Enter the gym capacity threshold:")
    return CAPACITY  # Move to next state

async def get_capacity(update: Update, context: CallbackContext):
    """Store the capacity and ask for delay time."""
    context.user_data["capacity"] = update.message.text  # Store the input
    await update.message.reply_text("Enter the delay time in minutes:")
    return DELAY  # Move to next state

async def get_delay(update: Update, context: CallbackContext):
    """Store the delay time and schedule the notification."""
    user_id = update.message.chat_id
    capacity = context.user_data["capacity"]
    delay_minutes = int(update.message.text)  # Convert to int
    delay_seconds = delay_minutes * 60  # Convert to seconds

    # Confirm with user
    await update.message.reply_text(f"✅ Alert set: I'll notify you in {delay_minutes} minutes if gym capacity is below {capacity}.")

    # Schedule notification
    threading.Timer(delay_seconds, send_notification, args=(context.bot, user_id, capacity)).start()

    return ConversationHandler.END  # End conversation

def send_notification(bot, user_id, capacity):
    """Send notification after the delay."""
    bot.send_message(user_id, f"⏰ Gym capacity alert! The capacity is now below {capacity}.")

async def cancel(update: Update, context: CallbackContext):
    """Cancel the conversation."""
    await update.message.reply_text("❌ Alert setup cancelled.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enter", enter_gym))
    app.add_handler(CommandHandler("exit", exit_gym))
    app.add_handler(CommandHandler("capacity", check_capacity))
    app.add_handler(CommandHandler("setalert", set_alert))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("setalert", set_alert)],
        states={
            CAPACITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_capacity)],
            DELAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_delay)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

