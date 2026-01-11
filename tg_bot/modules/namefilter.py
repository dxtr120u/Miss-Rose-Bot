from telegram import Update, Bot
from telegram.ext import CommandHandler, run_async

from tg_bot import dispatcher
from tg_bot.modules.helper_funcs.chat_status import user_admin
import tg_bot.modules.sql.namefilter_sql as sql

__mod_name__ = "Name Filter"
__help__ = """
*Admin only:*
 - /setfiltremsg <message>: Sets the message to be sent when a user with a blacklisted name joins.
 You can use {first_name} in the message.
 - /resetfiltremsg: Resets the message to the default one.
"""

@run_async
@user_admin
def set_filter_message(bot: Bot, update: Update, args):
    chat = update.effective_chat
    if not args:
        update.effective_message.reply_text("You need to provide a message.")
        return
        
    message = " ".join(args)
    sql.set_message(chat.id, message)
    update.effective_message.reply_text("Name filter message updated.")

@run_async
@user_admin
def reset_filter_message(bot: Bot, update: Update):
    chat = update.effective_chat
    sql.set_message(chat.id, "User {first_name} has a blacklisted name. Should I take action?")
    update.effective_message.reply_text("Name filter message reset to default.")

NAMEFILTER_GROUP = 102
SET_HANDLER = CommandHandler("setfiltremsg", set_filter_message, pass_args=True)
RESET_HANDLER = CommandHandler("resetfiltremsg", reset_filter_message)

dispatcher.add_handler(SET_HANDLER, group=NAMEFILTER_GROUP)
dispatcher.add_handler(RESET_HANDLER, group=NAMEFILTER_GROUP)
