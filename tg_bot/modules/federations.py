import html
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async, Filters

from tg_bot import dispatcher, LOGGER
from tg_bot.modules.helper_funcs.chat_status import user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user
import tg_bot.modules.sql.federation_sql as sql

__mod_name__ = "Federations"
__help__ = """
*Admin only:*
 - /addfed: Adds the current chat to the federation.
 - /rmfed: Removes the current chat from the federation.
 - /fban <user>: Bans a user from all chats in the federation.
"""

@run_async
@user_admin
def add_fed_command(bot: Bot, update: Update):
    chat = update.effective_chat
    sql.add_to_fed(chat.id)
    update.effective_message.reply_text("This chat has been added to the federation.")

@run_async
@user_admin
def rm_fed_command(bot: Bot, update: Update):
    chat = update.effective_chat
    sql.rm_from_fed(chat.id)
    update.effective_message.reply_text("This chat has been removed from the federation.")

@run_async
@user_admin
def fban_command(bot: Bot, update: Update, args: List[str]):
    user_id = extract_user(update.effective_message, args)
    if not user_id:
        update.effective_message.reply_text("You don't seem to be referring to a user.")
        return

    fed_chats = sql.get_all_feds()
    banned_in = 0
    for fed_chat in fed_chats:
        try:
            bot.kick_member(int(fed_chat.chat_id), user_id)
            banned_in += 1
        except BadRequest as excp:
            if excp.message not in ("User not found", "Not enough rights to restrict/unrestrict chat member"):
                LOGGER.warning(f"Could not fban in {fed_chat.chat_id}: {excp.message}")

    update.effective_message.reply_text(f"Federation banned in {banned_in} chats.")


FEDERATION_GROUP = 101
ADDFED_HANDLER = CommandHandler("addfed", add_fed_command, filters=Filters.group)
RMFED_HANDLER = CommandHandler("rmfed", rm_fed_command, filters=Filters.group)
FBAN_HANDLER = CommandHandler("fban", fban_command, pass_args=True, filters=Filters.group)

dispatcher.add_handler(ADDFED_HANDLER, group=FEDERATION_GROUP)
dispatcher.add_handler(RMFED_HANDLER, group=FEDERATION_GROUP)
dispatcher.add_handler(FBAN_HANDLER, group=FEDERATION_GROUP)
