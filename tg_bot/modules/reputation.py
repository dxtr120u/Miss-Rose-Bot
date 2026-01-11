import html
import time
from typing import Optional, List

from telegram import Message, Chat, Update, Bot, User, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, run_async, Filters

from tg_bot import dispatcher, LOGGER
from tg_bot.modules.helper_funcs.chat_status import user_admin, bot_admin, can_restrict
from tg_bot.modules.helper_funcs.extraction import extract_user
import tg_bot.modules.sql.reputation_sql as sql

MERCI_COOLDOWN = 120  # 2 minutes
merci_cooldowns = {}

__mod_name__ = "Reputation"
__help__ = """
 - /merci: Reply to a message to give a reputation point.
 - /rep: Check your reputation.
 - /toprep: Show the leaderboard.

*Admin only:*
 - /rmrep <user> <amount>: Remove reputation points from a user. Amount can be 1, 2, 5, 10, 50.
"""

def __stats__():
    return "Reputation stats are not yet implemented."

def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


@run_async
def merci_command(bot: Bot, update: Update):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if not message.reply_to_message:
        message.reply_text("You need to reply to a message to give a reputation point.")
        return

    replied_user = message.reply_to_message.from_user
    
    if replied_user.id == user.id:
        message.reply_text("You can't give a reputation point to yourself.")
        return

    cooldown_key = (chat.id, user.id)
    if cooldown_key in merci_cooldowns and time.time() - merci_cooldowns[cooldown_key] < MERCI_COOLDOWN:
        remaining_time = int(MERCI_COOLDOWN - (time.time() - merci_cooldowns[cooldown_key]))
        message.reply_text(f"You must wait {remaining_time} seconds before giving another point.")
        return

    new_rep = sql.add_rep(chat.id, replied_user.id, 1)
    merci_cooldowns[cooldown_key] = time.time()
    
    message.reply_text(f"{replied_user.first_name} has received a reputation point! Their new reputation is {new_rep}.")


@run_async
def rep_command(bot: Bot, update: Update):
    chat = update.effective_chat
    user = update.effective_user
    
    rep = sql.get_rep(chat.id, user.id)
    update.effective_message.reply_text(f"Your current reputation is {rep}.")


@run_async
def toprep_command(bot: Bot, update: Update):
    chat = update.effective_chat
    leaderboard = sql.get_chat_leaderboard(chat.id)
    
    if not leaderboard:
        update.effective_message.reply_text("There is no reputation leaderboard in this chat yet.")
        return

    msg = "<b>Reputation Leaderboard:</b>\n"
    for i, user_rep in enumerate(leaderboard):
        try:
            user_info = chat.get_member(user_rep.user_id)
            msg += f"{i+1}. {user_info.user.first_name}: {user_rep.reputation}\n"
        except BadRequest:
            # User is not in the chat anymore
            pass
            
    update.effective_message.reply_text(msg, parse_mode=ParseMode.HTML)


@run_async
@user_admin
def rmrep_command(bot: Bot, update: Update, args: List[str]):
    chat = update.effective_chat
    message = update.effective_message
    
    if len(args) != 2:
        message.reply_text("Usage: /rmrep <user> <amount>. Amount can be 1, 2, 5, 10, 50.")
        return

    user_id = extract_user(message, [args[0]])
    if not user_id:
        message.reply_text("I can't find that user.")
        return

    try:
        amount = int(args[1])
        if amount not in [1, 2, 5, 10, 50]:
            message.reply_text("Invalid amount. Please use one of: 1, 2, 5, 10, 50.")
            return
    except ValueError:
        message.reply_text("Invalid amount. Please specify a number.")
        return

    new_rep = sql.rm_rep(chat.id, user_id, amount)
    message.reply_text(f"Removed {amount} reputation points. Their new reputation is {new_rep}.")


REPUTATION_GROUP = 100
MERCI_HANDLER = CommandHandler("merci", merci_command, filters=Filters.group)
REP_HANDLER = CommandHandler("rep", rep_command, filters=Filters.group)
TOPREP_HANDLER = CommandHandler("toprep", toprep_command, filters=Filters.group)
RMREP_HANDLER = CommandHandler("rmrep", rmrep_command, pass_args=True, filters=Filters.group)

dispatcher.add_handler(MERCI_HANDLER, group=REPUTATION_GROUP)
dispatcher.add_handler(REP_HANDLER, group=REPUTATION_GROUP)
dispatcher.add_handler(TOPREP_HANDLER, group=REPUTATION_GROUP)
dispatcher.add_handler(RMREP_HANDLER, group=REPUTATION_GROUP)
