import logging
import asyncio
from logging.handlers import RotatingFileHandler
import nest_asyncio
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, filters
from dbHandler import init_db
from walletChecker import check_wallets
from queryHandlers import callBackQuery_handler, command_handler
from config import PROXY_IP, PROXY_PORT, TOKEN, BETA_TOKEN

nest_asyncio.apply()

TOR_PROXY_URL=f'socks5://{PROXY_IP}:{PROXY_PORT}'
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(
            'escrow_bot.log', maxBytes=5 * 1024 * 1024, backupCount=3
        ),
        logging.StreamHandler()
    ]
 )
       
async def main_async(application):

    await init_db()

    job_queue = application.job_queue
    wallet_checker = job_queue.run_repeating(check_wallets, interval=600)
    await application.create_task(wallet_checker.run(application))
    
    
if __name__=='__main__':
    if not TOKEN:
        raise ValueError("Bot token not set in .env")
    application = ApplicationBuilder().token(TOKEN).proxy(TOR_PROXY_URL).get_updates_proxy(TOR_PROXY_URL).build()

    application.add_handler(MessageHandler(filters.COMMAND, command_handler))
    application.add_handler(CallbackQueryHandler(callBackQuery_handler))

    asyncio.run(main_async(application))
    application.run_polling()
