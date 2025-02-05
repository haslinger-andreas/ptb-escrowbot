import logging
from config import LOG_ID
from messageHandler import media_handler


async def handle_wallet_error(update, context, error_message):
    logging.error(f"Wallet error : {error_message}")
    text=(
            ""
        )
    await media_handler(update, context, text)
    await context.bot.sendMessage(
        chat_id=LOG_ID,
        text=f"",
        parse_mode="Markdown"
    )

async def handle_node_error(update, context):
    logging.error(f"Node failure or unsynched")
    text=(
            ""
        )
    await media_handler(update, context, text)

async def handle_user_error(update, context, error_message):
    logging.error(f"User error : {error_message}")
    text=(
            ""
        )
    await media_handler(update, context, text)
    await context.bot.sendMessage(
        chat_id=LOG_ID,
        text=f"",
        parse_mode="Markdown"
    )

async def handle_escrow_error(update, context, error_message=None):
    await logging.error(f"Escrow error : {error_message}")
    await context.bot.sendMessage(
    chat_id=update.effective_chat.id,
        text=(
            ""
        ),
        parse_mode="Markdown"
    )
    await context.bot.sendMessage(
        chat_id=LOG_ID,
        text=f"",
        parse_mode="Markdown"
    )

async def handle_transaction_error(update, context):
    await context.bot.sendMessage(
    chat_id=update.effective_chat.id,
        text=(
            ""
        ),
        parse_mode="Markdown"
    )

async def not_started_error(update, context):
    await context.bot.sendMessage(
        chat_id=update.effective_chat.id,
        text=(
            ""
        ),
        parse_mode="Markdown"
    )

async def handle_not_group(update, context):
    await context.bot.sendMessage(
        chat_id=update.effective_chat.id,
        text=(
            ""
        ),
        parse_mode="Markdown"
    )
