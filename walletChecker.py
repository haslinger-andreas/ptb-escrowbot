from telegram.ext import ContextTypes
from rpcHandler import getRpc
from dbHandler import get_amount, get_wallets, set_amount, get_chat_id, get_unique_id, get_currency, new_entry, set_currency, set_wallet, update_status, get_status
from validate_wallet import check_wallet_address_fast
from walletHandler import create_or_load_wallet, get_estimated_fee
import logging
from rpc import JSONRPCException
import asyncio

active_wallets = set()
btc_semaphore = asyncio.Semaphore(1)
ltc_semaphore = asyncio.Semaphore(1)

async def update_wallets():
    global active_wallets
    
    db_wallets = await get_wallets()

    add_wallets = db_wallets - active_wallets
    remove_wallets = active_wallets - db_wallets

    active_wallets.update(add_wallets)
    active_wallets.difference_update(remove_wallets)

    logging.info(f"Active wallets updated to: {active_wallets}")    

async def sort_wallets(wallets):
    btc_wallets = []
    ltc_wallets = []

    for wallet in wallets:
        currency = await check_wallet_address_fast(wallet)
        if currency.upper() == 'BTC':
            btc_wallets.append(wallet)
        elif currency.upper() == 'LTC':
            ltc_wallets.append(wallet)
        else:
            logging.warning(f"Unknown currency for wallet {wallet}: {currency}")

    return btc_wallets, ltc_wallets

async def check_wallets(context: ContextTypes.DEFAULT_TYPE):
    await update_wallets()
    logging.info("checking wallets")
    global active_wallets
    btc_wallets, ltc_wallets = await sort_wallets(active_wallets)

    await asyncio.gather(
        process_wallets(context, btc_wallets, 'BTC'),
        process_wallets(context, ltc_wallets, 'LTC')
        )


async def process_wallets(context, wallets, currency):
    tasks = [check_wallet(context, wallet, currency) for wallet in wallets]
    await asyncio.gather(*tasks)

async def check_wallet(context, wallet, currency,):
    try:
            chat_id = await get_chat_id(wallet)
            unique_id = await get_unique_id(chat_id)
            prefix = currency.lower()
            await checker_logic(context, prefix, chat_id, unique_id, currency)
    except Exception as e:
        logging.error(f"Error checking Wallet: {wallet}: {e}")

async def checker_logic(context, prefix, chat_id, uuid, curr):
    try:
        wallet_name = f"{prefix}_wallet_{chat_id}_{uuid}"
        await create_or_load_wallet(rpc=await getRpc(curr=curr), wallet_name=wallet_name)
        rpc = await getRpc(curr=curr, wallet_name=wallet_name)
        amount = await rpc.getbalance()
        logging.info(wallet_name)
        await set_amount(chat_id, float(amount))
        if curr.upper() == 'BTC':
            fee = await get_estimated_fee()
            if amount > fee:
                await update_status(chat_id, 3)  
                await context.bot.sendMessage(chat_id=chat_id, text=".", parse_mode="MarkdownV2")
                logging.info("updated status and sent message to users")
        elif curr.upper() == 'LTC':
            if amount > 0:
                await update_status(chat_id, 3)
                await context.bot.sendMessage(chat_id=chat_id, text="", parse_mode="MarkdownV2")
                logging.info("updated status and sent message to users")
    except JSONRPCException as e:
        logging.error(f"JSONRPCException checking wallets: {e.code} | {e.message}")
    except Exception as ex:
        logging.error(f"Error checking wallets: {ex}")