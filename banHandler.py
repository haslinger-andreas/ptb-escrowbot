from config import OWNER_ID, CHAT_ID, LOG_ID 
from dbHandler import get_all_banned_users, add_ban_user, remove_ban_user
from errorHandler import handle_user_error

async def ban_user(update, context):
    sender_id = update.effective_user.id
    if int(OWNER_ID) != int(sender_id):
        return
    try:
        if update.message.reply_to_message:
            msg = ' '.join(update.message.text.split()[1:])
            user = update.message.reply_to_message.from_user
            if len(msg) == 0:
                await update.message.reply_text(
                "",
                parse_mode="Markdown"
                )
                return
            status = await add_ban_user(user.id, user.username, msg)
            await context.bot.banChatMember(CHAT_ID, user.id)
            if status:
                await update.message.reply_text("")
                await context.bot.send_message(
                chat_id=LOG_ID,
                text=f"",
                parse_mode="Markdown"
                )
                return
            await update.message.reply_text("")
        else:
            await update.message.reply_text("")

    except Exception as e:
        await handle_user_error(update, context, e)

async def unban_user(update, context):
    sender_id = update.effective_user.id
    if int(OWNER_ID) != int(sender_id):
        return
    try:
        if update.message.reply_to_message:
            user = update.message.reply_to_message.from_user
            msg = ' '.join(update.message.text.split()[1:])
            if len(msg) == 0:
                await update.message.reply_text(
                "",
                parse_mode="Markdown"
                )
                return
            status = await remove_ban_user(str(user.id))
            await context.bot.unbanChatMember(CHAT_ID, user.id)
            if status:
                await update.message.reply_text("")
                await context.bot.send_message(
                chat_id=LOG_ID,
                text=f"",
                parse_mode="Markdown"
                )
                return
            await update.message.reply_text("", parse_mode="Markdown")
        else:
            await update.message.reply_text("")

    except Exception as e:
        await handle_user_error(update, context, e)

async def is_allowed(update):
    user_id = update.effective_user.id
    banned_users = await get_all_banned_users()
    if int(update.effective_chat.id) == int(CHAT_ID):
        return False
    if user_id in banned_users:
        await update.message.reply_text("")
        return False