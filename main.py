import datetime
import random
import re
import os
from pytz import timezone
import telegram
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import logging
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ConversationHandler, Filters, MessageHandler
from machine import Machine
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
MENU = 1

Tbot = telegram.Bot(API_KEY)

washertimer = 32*60
dryertimer = 32*60
WASHER_ONE = Machine(washertimer, "Washer ONE")
WASHER_TWO = Machine(washertimer, "Washer TWO")
DRYER_ONE = Machine(dryertimer, "Dryer ONE")
DRYER_TWO = Machine(dryertimer, "Dryer TWO")

all_machines = [DRYER_ONE, DRYER_TWO, WASHER_ONE, WASHER_TWO]


def main():
    updater = Updater(API_KEY)
    # Test Laundry Bot
    # updater = Updater("5480884899:AAH5QJV9TL4Ls9DxJzFZwCEvJcfqWxiAwpc")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
    entry_points=[
      CommandHandler('start', start),
      CommandHandler("select", select),
      CommandHandler("status", status),
##      MessageHandler(
##        ~Filters.command & Filters.regex(re.compile(r"done", re.IGNORECASE)),
##        handle_message)
    ],
    states={
      MENU: [
        CallbackQueryHandler(cancel, pattern='^' + 'exit' + '$'),
        CallbackQueryHandler(cancel, pattern='^' + 'exits' + '$'),
        #
        # # which callback_data does start get call
        CallbackQueryHandler(double_confirm_dryer_one_callback,
                             pattern='^' + 'dryer_one' + '$'),
        CallbackQueryHandler(double_confirm_washer_one_callback,
                             pattern='^' + 'washer_one' + '$'),
        CallbackQueryHandler(double_confirm_dryer_two_callback,
                             pattern='^' + 'dryer_two' + '$'),
        CallbackQueryHandler(double_confirm_washer_two_callback,
                             pattern='^' + 'washer_two' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_dryer_one' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_washer_one' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_dryer_two' + '$'),
        CallbackQueryHandler(backtomenu, pattern='^' + 'no_washer_two' + '$'),
        CallbackQueryHandler(set_timer_dryer_one,
                             pattern='^' + 'yes_dryer_one' + '$'),
        CallbackQueryHandler(set_timer_washer_one,
                             pattern='^' + 'yes_washer_one' + '$'),
        CallbackQueryHandler(set_timer_dryer_two,
                             pattern='^' + 'yes_dryer_two' + '$'),
        CallbackQueryHandler(set_timer_washer_two,
                             pattern='^' + 'yes_washer_two' + '$'),
      ]
    },
    fallbacks=[
      CommandHandler('start', start),
      CommandHandler("select", select),
      CommandHandler("status", status),
      # MessageHandler(
      #   ~Filters.command & Filters.regex(re.compile(r"done", re.IGNORECASE)),
      #   handle_message)
    ],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()

def start(update: Update, context: CallbackContext) -> None:
  # Don't allow users to use /start command in group chats
  if update.message.chat.type != 'private':
    Tbot.send_message(
      chat_id=update.message.from_user.id,
      text=
      f"""Hi @{update.message.from_user.username},\n\nThanks for calling me in the groupchat. To prevent spamming in the group, please type /start to me privately in this chat instead!"""
    )
    return MENU

  keyboard = [[InlineKeyboardButton('Exit', callback_data='exit')]]
  if len(context.args) > 0:
    return

  reply_markup = InlineKeyboardMarkup(keyboard)
  update.message.reply_text(
    'Welcome to Dragon Laundry Bot!\U0001f600\U0001F606\U0001F923\n\nUse the following commands to use this bot:\n/select: Select the washer/dryer that you want to use\n/status: Check the status of Washers and Dryers\n\nThank you for using the bot!\nCredit to: @Kaijudo',
    reply_markup=reply_markup)
  return MENU

def select(update: Update, context: CallbackContext) -> None:
  # Don't allow users to use /select command in group chats
  if update.message.chat.type != 'private':
    return MENU
  keyboard = [[
    InlineKeyboardButton('Dryer One', callback_data='dryer_one'),
    InlineKeyboardButton('Dryer Two', callback_data='dryer_two')
  ], [
    InlineKeyboardButton('Washer One', callback_data='washer_one'),
    InlineKeyboardButton('Washer Two', callback_data='washer_two'),
              ], [InlineKeyboardButton('Exit', callback_data='exit')]]

  reply_markup = InlineKeyboardMarkup(keyboard)

  update.message.reply_text(
    '\U0001F606\U0001F923 Please choose a service: \U0001F606\U0001F923',
    reply_markup=reply_markup)
  return MENU

def cancel(update: Update, context: CallbackContext) -> int:
  """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
  query = update.callback_query
  query.answer()
  query.edit_message_text(
    text="Haiyaaa then you call me for what\n\nUse /start again to call me")
  return ConversationHandler.END

def create_inline_for_callback(machineName):
    callbackName = machineName.replace(" ", "_")
    textName = machineName.upper()
    keyboard = [[
        InlineKeyboardButton('Yes', callback_data=f'yes_{callbackName}'),
    ], [InlineKeyboardButton('No', callback_data=f'no_{callbackName}')]]
    markup = InlineKeyboardMarkup(keyboard)
    text = f"Timer for {textName} will begin?"
    return (text, markup)

def double_confirm_dryer_one_callback(update: Update,
                                     _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  text, markup = create_inline_for_callback("dryer one")
  query.edit_message_text(text= text, reply_markup= markup)
  return MENU


def double_confirm_washer_one_callback(update: Update,
                                      _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  text, markup = create_inline_for_callback("washer one")
  query.edit_message_text(text=text, reply_markup=markup)
  return MENU


def double_confirm_dryer_two_callback(update: Update,
                                     _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  text, markup = create_inline_for_callback("dryer two")
  query.edit_message_text(text= text, reply_markup= markup)
  return MENU

def double_confirm_washer_two_callback(update: Update,
                                     _: CallbackContext) -> int:
  query = update.callback_query
  query.answer()
  text, markup = create_inline_for_callback("washer two")
  query.edit_message_text(text= text, reply_markup= markup)
  return MENU

def backtomenu(update: Update, context: CallbackContext) -> None:
  query = update.callback_query
  query.answer()
  keyboard = [[InlineKeyboardButton('Exit', callback_data='exits')]]

  reply_markup = InlineKeyboardMarkup(keyboard)
  query.edit_message_text(
    'Welcome to Dragon Laundry Bot!\n\nUse the following commands to use this bot:\n/select: Select the washer/dryer that you want to use\n/status: Check the status of Washers and Dryers\n\nThank you for using the bot!\nCredit to: @Kaijudo',
    reply_markup=reply_markup)

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
        text= 'Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it'
    )
    machine.alarm()


def set_timer(update, context, machine):
    machineName = machine.getName()
    underscoreName = machineName.lower().replace(" ", "_")
    upperName = machineName.upper()

    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    query = update.callback_query
    query.answer()

    job_removed = remove_job_if_exists(str(chat_id), context)

    if not (machine.start_machine(update.effective_message.chat.username)):
        text = f"{upperName} is currently in use. Please come back again later!"
        query.message.delete()
        Tbot.send_message(chat_id=chat_id, text=text)
    else:
        context.job_queue.run_once(lambda context: alarm(context, machine), machine.getTimeToComplete(),
                                   context=chat_id, name=underscoreName)

    text = f"Timer Set for {machine.total_time()} for {upperName}. Please come back again!"
    # if job_removed:
    #    text = 'Status Update: QR DRYER is available'
    query.message.delete()
    Tbot.send_message(chat_id=chat_id, text=text)
    return MENU


def set_timer_dryer_one(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, DRYER_ONE)


def set_timer_washer_one(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, WASHER_ONE)


def set_timer_dryer_two(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, DRYER_TWO)


def set_timer_washer_two(update: Update, context: CallbackContext) -> None:
    set_timer(update, context, WASHER_TWO)

def status(update: Update, context: CallbackContext) -> None:
  global WASHER_ONE, WASHER_TWO, DRYER_ONE, DRYER_TWO

  DRYER_ONE_TIMER = DRYER_ONE.status()
  DRYER_TWO_TIMER = DRYER_TWO.status()
  WASHER_ONE_TIMER = WASHER_ONE.status()
  WASHER_TWO_TIMER = WASHER_TWO.status()

  reply_text = f'''Status of Laundry Machines:
  
Dryer One: {DRYER_ONE_TIMER}
  
Dryer Two: {DRYER_TWO_TIMER}
  
Washer One: {WASHER_ONE_TIMER}
  
Washer Two: {WASHER_TWO_TIMER}'''

  # Don't allow users to use /status command in group chats
  if update.message.chat.type != 'private':
    Tbot.send_message(
      chat_id=update.message.from_user.id,
      text=
      f"""Hi @{update.message.from_user.username} ,thanks for calling me in the groupchat. \n\nTo prevent spamming in the group, I have sent you a private message instead!\n\n{reply_text}"""
    )
    return MENU
  update.message.reply_text(reply_text)

if __name__ == '__main__':
  main()
