from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import LOG_ID
from dbHandler import add_new_contact_request
from errorHandler import handle_user_error
from messageHandler import media_handler
from rate_limiter import RateLimiter

rate_limter = RateLimiter(300)

async def contact_request(update:Update, context: ContextTypes.DEFAULT_TYPE):
    allowed, message = await rate_limter.is_allowed(context)
    if not allowed:
        await media_handler(update, context, message)
        return
    try:
        chat_id = update.effective_chat.id
        msg = ' '.join(update.message.text.split()[1:])
        invite_link = None
        try:
            invite_link = await context.bot.export_chat_invite_link(chat_id=chat_id)
        except:
            pass
        t = (
                ""
        )
        
        await media_handler(update, context, t)
        uuid = await add_new_contact_request(user_id=update.effective_user.id,username = update.effective_user.username ,chat_id=chat_id, reason=msg if len(msg) > 0 else None)

        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Claim", callback_data=f"claim_{uuid}")]])
        await context.bot.sendMessage(chat_id=LOG_ID, text=f"", parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        await handle_user_error(update, context, e)

async def report_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        msg = ' '.join(update.message.text.split()[1:])
        if len(msg) == 0:
            await context.bot.send_message(
            chat_id=chat_id,
            text="",
            parse_mode="Markdown"
            )
            return
        else:
            allowed, message = await rate_limter.is_allowed(context)
            if not allowed:
                await context.bot.sendMessage(chat_id=update.effective_chat.id, text=message, parse_mode="Markdown")
                return
            t = (
           ""
        )
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=t,
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            chat_id=LOG_ID,
            text=f"",
            parse_mode="Markdown"
        )

    except Exception as e:
        await handle_user_error(update, context, e)