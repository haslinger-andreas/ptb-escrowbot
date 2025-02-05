from telegram import ChatMember, Update
from telegram.ext import ContextTypes
from dbHandler import get_all_transactions
from config import OWNER_ID
from messageHandler import media_handler

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user.id == int(OWNER_ID):
        return
    transactions = await get_all_transactions()

    text=f"""
total transactions: {len(transactions)}
"""
    await media_handler(update, context, text)

async def user_info(update: Update, context:ContextTypes.DEFAULT_TYPE):
    sender_id = update.effective_user.id
    if int(OWNER_ID) != int(sender_id):
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        
        user_info = f"""
        *User Information*
        - First Name\\: {user.first_name or 'N/A'}
        - Last Name\\: {user.last_name or 'N/A'}
        - Username\\: @{user.username or 'N/A'}
        - User ID\\: {user.id}
        """
        await update.message.reply_text(user_info, parse_mode="MarkdownV2")
    else:
        await update.message.reply_text("Please reply to a message to get user information.")
        return

async def check_admin_status(update:Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    bot_id = context.bot.id
    admins = await context.bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == bot_id and admin.status == ChatMember.ADMINISTRATOR:
            await context.bot.sendMessage(chat_id=update.effective_chat.id, text=f"The bot is set as admin")
            return
    await context.bot.sendMessage(
            chat_id=update.effective_chat.id,
            text=(
                "🚫 *The bot is not currently set as an admin in this group\\.*\n\n"
                "For the bot to work correctly, it needs admin rights to manage transactions and assist as needed\\. "
                "Follow the video guide above to set the bot as an admin\\. Let us know if you need further help\\!"
            ),
            parse_mode="MarkdownV2")
    return