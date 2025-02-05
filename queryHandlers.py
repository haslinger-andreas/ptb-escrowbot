import logging
from telegram import Update
from telegram.ext import ContextTypes
from adminHandler import admin_menu, user_info, check_admin_status
from banHandler import ban_user, is_allowed, unban_user
from errorHandler import handle_not_group
from contactHandler import contact_request, report_request
from misc import real_bot, send_review, send_tos, what_is_escrow, send_start
from transactionHandler import handle_reset_transaction, pay_seller, refund_buyer, reset_transaction
from userHandler import handle_currency_selection, send_status, start_transaction, set_buyer_command, set_seller_command
from walletHandler import escrow_balance, verify_wallet

async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user.username:
        await context.bot.sendMessage(
            chat_id=update.effective_chat.id,
            text=(
                "⚠️ *Username Required*\n\n"
                "You must set a username in your Telegram profile to use this bot\\. "
                "Need help? Feel free to reach out!"
            ),
            parse_mode="MarkdownV2"
        )
        logging.warning(f"User {update.effective_user.id} attempted to send a command without a username.")
        return

    if await is_allowed(update=update) is False:
        return

    command = update.message.text.split()[0].lstrip("/").split("@")[0]
    group_commands = {
        "transaction": start_transaction,
        "buyer": set_buyer_command,
        "seller": set_seller_command,
        "refund": refund_buyer,
        "pay": pay_seller,
        "contact": contact_request,
        "restart": reset_transaction,
        "check": check_admin_status,
        "balance": escrow_balance,
        "review": send_review,
        "info": user_info,
        "ban": ban_user,
        "unban": unban_user,
        "status": send_status,
    }

    global_commands = {
        "start": send_start,
        "terms": send_tos,
        "verify": verify_wallet,
        "report": report_request,
        "real": real_bot,
        "admin_view": admin_menu,
    }

    if command in group_commands:
        if not await is_group(update, context):
            await handle_not_group(update, context)
        await group_commands[command](update, context)
        return

    if command in global_commands:
        await global_commands[command](update, context)
        return

async def callBackQuery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query      
    user_choice = query.data
    print(user_choice)

    if user_choice.startswith('reset_'):
        await handle_reset_transaction(update, context, query)
        return
        
    if user_choice.startswith('currency_'):
        await handle_currency_selection(update, context, query)
        return

    if user_choice == 'sendtos':
        await send_tos(update, context, query)
        return

    if user_choice == 'whatsescrow':
        await what_is_escrow(update, context, query)
        return

    if user_choice == 'send_start':
        await send_start(update, context, query)

async def is_group(update:Update, context:ContextTypes.DEFAULT_TYPE):
    info = await context.bot.getChat(update.effective_chat.id)
    chat_type = info['type']
    print(chat_type)
    return chat_type in ['group', 'supergroup']