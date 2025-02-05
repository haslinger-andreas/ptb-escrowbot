from decimal import Decimal
import logging
import re
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from dbHandler import get_buyer, get_currency, get_transaction_amount, get_unique_id, new_entry, get_status, update_chat_id
from errorHandler import handle_user_error
from messageHandler import media_handler
from rate_limiter import RateLimiter
from config import CHAT_ID, VOUCH_ID, LOGO_GIF

rate_limter = RateLimiter(300)

async def send_start(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    if query:
        await query.delete_message()
    welcome_message = f"""

start_message
"""
    keyboard = [[InlineKeyboardButton("How does escrow work", callback_data="whatsescrow"), InlineKeyboardButton("How to use the bot", url="")],
                [InlineKeyboardButton("ToS", callback_data="sendtos")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await media_handler(update=update, context=context, text=welcome_message, file_id=LOGO_GIF, reply_markup=reply_markup)

async def what_is_escrow(update:Update, context: ContextTypes, query=None):
    if query:
        await query.delete_message()
    text = """
how_does_escrow_work
"""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="send_start")]])
    await media_handler(update=update, context=context, text=text, reply_markup=reply_markup)

async def send_tos(update:Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    if query:
        await query.delete_message()
    tos_message = """

    """
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="send_start")]])
    await media_handler(update=update, context=context, text=tos_message, reply_markup=reply_markup)

async def send_review(update:Update, context:ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    status = await get_status(chat_id)

    if status is None or status <= 3:
        await context.bot.sendMessage(chat_id=chat_id, text="")
        return
    try:
        uuid = await get_unique_id(chat_id)
        amount = await get_transaction_amount(chat_id)
        currency = await get_currency(chat_id)
        user = re.sub(r'([_*[\]()~`>#+-=|{}.!\\])', r'\\\1', str(update.effective_user.username))
        msg = ' '.join(update.message.text.split()[1:])
        if amount is not None:
            amount = Decimal(f"{amount:.4g}")
        if msg:
            vouch_message = f"""

"{msg}"
"""
        else:
            vouch_message = f"""

"""

        logging.info(vouch_message if vouch_message else '')

        await context.bot.send_message(
            chat_id=VOUCH_ID,
            text=vouch_message,
            parse_mode='MarkdownV2'
        )
        confirmation_message = """

"""
        await context.bot.send_message(
            chat_id=chat_id,
            text=confirmation_message,
            parse_mode='Markdown'
        )

        await update_chat_id(chat_id)

        await context.bot.send_message(
            chat_id=chat_id,
            text="",
            parse_mode='Markdown'
        )

    except Exception as e:
        await handle_user_error(update, context, e)

async def real_bot(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"",
            parse_mode='Markdown'
        )
    await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"",
            parse_mode='Markdown'
        )