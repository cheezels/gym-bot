import logging
import datatest
import asyncio
import threading
from datetime import datetime, time
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext, ConversationHandler, CallbackQueryHandler

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7602878718:AAHr763ncvrshWEBWG_WebRRwycWdpq-G1s"

# Dictionary to track users in gym
# gym_users = set()


# Start command handler
async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command and shows a menu."""
    keyboard = [
        ["/enter", "/exit"],
        ["/capacity", "/notify"],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Welcome to Gym Tracker Bot!\nChoose an option below:",
        reply_markup=reply_markup
    )


async def enter_gym(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    sql_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    is_successful = datatest.enter_gymdb(user_id, sql_datetime)
    if is_successful:
        await update.message.reply_text("You have entered the gym. Welcome!")
    else:
        await update.message.reply_text("You are already in the gym!")


async def exit_gym(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    sql_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    is_successful = datatest.exit_gymdb(user_id, sql_datetime)
    if is_successful:
        await update.message.reply_text("You have left the gym. Goodbye!")
    else:
        await update.message.reply_text("You have already left the gym.")


async def check_capacity(update: Update, context: CallbackContext) -> None:
    datatest.update()
    number = datatest.check_capacitydb()
    await update.message.reply_text(f"Current gym occupancy: {number} ")


async def query_alert(update: Update, context: CallbackContext) -> None:
    # Check if the update comes from a message or a callback query
    if update.message:
        chat_id = update.message.chat_id
        reply_method = update.message.reply_text
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
        reply_method = update.callback_query.message.reply_text
    else:
        logger.error("Invalid update type in query_alert")
        return
    
    await reply_method("Choose a duration to set an alert, we will check the gym capacity for you")
    keyboard = [
        [InlineKeyboardButton("10 sec", callback_data="10")], #test notif
        [InlineKeyboardButton("15 min", callback_data="900")],  # 900 sec = 15 min
        [InlineKeyboardButton("30 min", callback_data="1800")],  # 1800 sec = 30 min
        [InlineKeyboardButton("45 min", callback_data="2700")],  # 2700 sec = 45 min
        [InlineKeyboardButton("1 hour", callback_data="3600")],  # 3600 sec = 1 hour
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await reply_method("Set an alert for:", reply_markup=reply_markup)


async def set_alert(update: Update, context: CallbackContext):
    """Handle button clicks and set a timer."""
    query = update.callback_query
    await query.answer()

    # Check if the user wants to set another alert
    if query.data == "set_again":
        # Re-prompt the user to choose a duration
        await query_alert(update, context)
        return
    elif query.data == "no_repeat":
        # End the conversation
        await query.edit_message_text(text="No further alerts will be set.")
        return

    duration = int(query.data)  # Get the duration in seconds
    user_id = query.message.chat_id
    
    await query.edit_message_text(text=f"Alert set! I will notify you in {duration // 60} minutes.")

    # Wait asynchronously and send notification
    await asyncio.sleep(duration)
    curr_capacity = 50
    await context.bot.send_message(user_id, f"Time's up! Gym is currently at {curr_capacity}% capacity.")
    
    # Ask if the user wants to set another reminder
    keyboard = [
        [InlineKeyboardButton("🔁 Yes", callback_data="set_again")],
        [InlineKeyboardButton("❌ No", callback_data="no_repeat")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(user_id, "Would you like to set another alert", reply_markup=reply_markup)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("enter", enter_gym))
    app.add_handler(CommandHandler("exit", exit_gym))
    app.add_handler(CommandHandler("capacity", check_capacity))
    app.add_handler(CommandHandler("notify", query_alert))
    app.add_handler(CallbackQueryHandler(set_alert))

    app.run_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

