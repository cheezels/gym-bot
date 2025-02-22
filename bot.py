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

# Dictionary to store user inputs temporarily
user_data = {}

async def set_alert(update: Update, context: CallbackContext):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /setalert <capacity> <HH:MM>")
        return

    user_id = update.message.chat_id
    capacity_threshold = int(args[0])
    alert_time = datetime.strptime(args[1], "%H:%M").time()

    # Calculate the delay (time until the alert should run)
    now = datetime.now().time()
    alert_datetime = datetime.combine(datetime.today(), alert_time)

    if alert_time < now:
        await update.message.reply_text("Please input a future time.")
        return

    # Calculate delay for threading
    delay = (alert_datetime - datetime.now()).total_seconds()

    await update.message.reply_text(
        f"✅ Alert set: I'll notify you at {alert_time} minutes if gym capacity is below {capacity_threshold}.")

    # Schedule notification
    threading.Timer(delay, send_notification, args=(context.bot, user_id, capacity_threshold)).start()

def send_notification(bot, user_id, capacity):
    if len(gym_users) < capacity:
        bot.send_message(user_id, f"⏰ Good news! The capacity is now below {capacity}.")
    else:
        bot.send_message(user_id, f"⏰ Bad news! Capacity is still at {len(gym_users)}.")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enter", enter_gym))
    app.add_handler(CommandHandler("exit", exit_gym))
    app.add_handler(CommandHandler("capacity", check_capacity))
    app.add_handler(CommandHandler("setalert", set_alert))

    app.run_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

