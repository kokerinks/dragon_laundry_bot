import os
import telegram
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
)
from machine import Machine
from dotenv import load_dotenv
from utils import is_deployed
from laundry_firebase import LaundryFirebase

load_dotenv()
LaundryFirebase.authenticate()

API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
MENU = 1

TBOT = telegram.Bot(API_KEY)

WASHER_TIMER = 32 * 60
DRYER_TIMER = 32 * 60
DRYER_ONE = Machine(DRYER_TIMER, "DRYER ONE")
DRYER_TWO = Machine(DRYER_TIMER, "DRYER TWO")
WASHER_ONE = Machine(WASHER_TIMER, "WASHER ONE")
WASHER_TWO = Machine(WASHER_TIMER, "WASHER TWO")


def main():
    updater = Updater(API_KEY)
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("select", select),
            CommandHandler("status", status),
        ],
        states={
            MENU: [
                CallbackQueryHandler(cancel, pattern="^exit$"),
                CallbackQueryHandler(cancel, pattern="^exits$"),
                CallbackQueryHandler(
                    double_confirm_dryer_one_callback, pattern="^dryer_one$"
                ),
                CallbackQueryHandler(
                    double_confirm_dryer_two_callback, pattern="^dryer_two$"
                ),
                CallbackQueryHandler(
                    double_confirm_washer_one_callback,
                    pattern="^washer_one$",
                ),
                CallbackQueryHandler(
                    double_confirm_washer_two_callback, pattern="^washer_two$"
                ),
                CallbackQueryHandler(backtomenu, pattern="^no_dryer_one$"),
                CallbackQueryHandler(backtomenu, pattern="^no_dryer_two$"),
                CallbackQueryHandler(backtomenu, pattern="^no_washer_one$"),
                CallbackQueryHandler(backtomenu, pattern="^no_washer_two$"),
                CallbackQueryHandler(set_timer_dryer_one, pattern="^yes_dryer_one$"),
                CallbackQueryHandler(set_timer_dryer_two, pattern="^yes_dryer_two$"),
                CallbackQueryHandler(set_timer_washer_one, pattern="^yes_washer_one$"),
                CallbackQueryHandler(set_timer_washer_two, pattern="^yes_washer_two$"),
            ]
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("select", select),
            CommandHandler("status", status),
        ],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    if is_deployed:
        updater.start_webhook(
            listen="0.0.0.0",
            port=os.environ.get("PORT", 8080),
            webhook_url="https://dragon-laundry-bot-beta.fly.dev",
        )
    else:
        updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


WELCOME_MESSAGE = (
    f"Welcome to Dragon Laundry Bot ({os.environ.get('VERSION','dev')})!\n\nUse the following commands to use this bot:\n/select: Select the washer/dryer that you want to use\n/status: Check the status of Washers and Dryers\n\nThank you for using the bot!\nCredit to: @Kaijudo",
)


def start(update: Update, context: CallbackContext) -> None:
    # Don't allow users to use /start command in group chats
    if update.message.chat.type != "private":
        TBOT.send_message(
            chat_id=update.message.from_user.id,
            text=f"Hi @{update.message.from_user.username},\n\nThanks for calling me in the groupchat. To prevent spamming in the group, please type /start to me privately in this chat instead!",
        )
        return MENU

    if len(context.args) > 0:
        return

    keyboard = [[InlineKeyboardButton("Exit", callback_data="exit")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=reply_markup,
    )
    return MENU


def select(update: Update, context: CallbackContext) -> None:
    # Don't allow users to use /select command in group chats
    if update.message.chat.type != "private":
        return MENU
    keyboard = [
        [
            InlineKeyboardButton("Dryer One", callback_data="dryer_one"),
            InlineKeyboardButton("Dryer Two", callback_data="dryer_two"),
        ],
        [
            InlineKeyboardButton("Washer One", callback_data="washer_one"),
            InlineKeyboardButton("Washer Two", callback_data="washer_two"),
        ],
        [InlineKeyboardButton("Exit", callback_data="exit")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "\U0001F606\U0001F923 Please choose a service: \U0001F606\U0001F923",
        reply_markup=reply_markup,
    )
    return MENU


def cancel(update: Update, context: CallbackContext) -> int:
    """
    Returns `ConversationHandler.END`, which tells the ConversationHandler that the conversation is over
    """
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Haiyaaa then you call me for what\n\nUse /start again to call me"
    )
    return ConversationHandler.END


def create_inline_for_callback(machine_name):
    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=f"yes_{machine_name}"),
        ],
        [InlineKeyboardButton("No", callback_data=f"no_{machine_name}")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    text = f"Timer for {machine_name.upper()} will begin?"
    return (text, markup)


def double_confirm_dryer_one_callback(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    text, markup = create_inline_for_callback("dryer_one")
    query.edit_message_text(text=text, reply_markup=markup)
    return MENU


def double_confirm_dryer_two_callback(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    text, markup = create_inline_for_callback("dryer_two")
    query.edit_message_text(text=text, reply_markup=markup)
    return MENU


def double_confirm_washer_one_callback(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    text, markup = create_inline_for_callback("washer_one")
    query.edit_message_text(text=text, reply_markup=markup)
    return MENU


def double_confirm_washer_two_callback(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    text, markup = create_inline_for_callback("washer_two")
    query.edit_message_text(text=text, reply_markup=markup)
    return MENU


def backtomenu(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("Exit", callback_data="exits")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        WELCOME_MESSAGE,
        reply_markup=reply_markup,
    )


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def alarm(context: CallbackContext, machine) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(
        job.context,
        text="Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it",
    )
    machine.alarm()


def set_timer(update, context, machine):
    machine_name = machine.get_name()
    underscore_name = machine_name.lower().replace(" ", "_")
    upper_name = machine_name.upper()

    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    query = update.callback_query
    query.answer()

    job_removed = remove_job_if_exists(str(chat_id), context)

    if not (machine.start_machine(update.effective_message.chat.username)):
        text = f"{upper_name} is currently in use. Please come back again later!"
        query.message.delete()
        TBOT.send_message(chat_id=chat_id, text=text)
    else:
        context.job_queue.run_once(
            lambda context: alarm(context, machine),
            machine.get_time_to_complete(),
            context=chat_id,
            name=underscore_name,
        )

    text = f"Timer Set for {machine.time_left_mins()}mins for {upper_name}. Please come back again!"
    query.message.delete()
    TBOT.send_message(chat_id=chat_id, text=text)
    return MENU


def set_timer_dryer_one(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, DRYER_ONE)


def set_timer_dryer_two(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, DRYER_TWO)


def set_timer_washer_one(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, WASHER_ONE)


def set_timer_washer_two(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, WASHER_TWO)


def status(update: Update, context: CallbackContext) -> None:
    DRYER_ONE_TIMER = DRYER_ONE.status()
    DRYER_TWO_TIMER = DRYER_TWO.status()
    WASHER_ONE_TIMER = WASHER_ONE.status()
    WASHER_TWO_TIMER = WASHER_TWO.status()

    reply_text = f"""Status of Laundry Machines:
  
Dryer One: {DRYER_ONE_TIMER}
  
Dryer Two: {DRYER_TWO_TIMER}
  
Washer One: {WASHER_ONE_TIMER}
  
Washer Two: {WASHER_TWO_TIMER}"""

    # Don't allow users to use /status command in group chats
    if update.message.chat.type != "private":
        TBOT.send_message(
            chat_id=update.message.from_user.id,
            text=f"""Hi @{update.message.from_user.username} ,thanks for calling me in the groupchat. \n\nTo prevent spamming in the group, I have sent you a private message instead!\n\n{reply_text}""",
        )
        return MENU
    update.message.reply_text(reply_text)


if __name__ == "__main__":
    main()
