from decimal import Decimal
import logging
from telegram import Update
from telegram.ext import ContextTypes
from errorHandler import not_started_error, handle_wallet_error
from rpcHandler import getRpc
from dbHandler import get_all_wallets, get_amount, get_currency, get_status, set_wallet, get_unique_id
from rpc import JSONRPCException


async def create_or_load_wallet(rpc, wallet_name):
    if await is_wallet_on_disk(rpc, wallet_name):
        loaded_wallets = await rpc.listwallets()
        if wallet_name in loaded_wallets:
            logging.info(f"Wallet {wallet_name} exists on disk. Already loaded")
            return
        logging.info(f"Wallet {wallet_name} exists on disk. Loading it ...")
        await rpc.loadwallet(wallet_name)
    else:
        logging.info(f"Creating wallet {wallet_name} ...")
        await rpc.createwallet(wallet_name)

async def unload_wallets(rpc):
    try:
            loaded_wallets = await rpc.listwallets()
            for wallet in loaded_wallets:
                await rpc.unloadwallet(wallet)
                logging.info(f"unloaded: {wallet}")
    except JSONRPCException as e:
        print(f"{e.code} | {e.message}")

async def is_wallet_on_disk(rpc, wallet_name):
    try:
            wallets_info = await rpc.listwalletdir()
            wallet_paths = [w['name'] for w in wallets_info['wallets']]
            return wallet_name in wallet_paths
    except Exception as e:
        logging.error(f"Error checking wallet on disk: {e}")
        return False

async def new_btc_address(update):
    try:
        chat_id = update.effective_chat.id
        unique_id = await get_unique_id(chat_id)
        wallet_name = f"btc_wallet_{update.effective_chat.id}_{unique_id}"
        rpc = await getRpc('BTC', wallet_name=wallet_name)
        if rpc is None:
            logging.warning("Rpc client set to none")
            raise ValueError("Invalid currency")
        logging.info(f"Creating new wallet: {wallet_name}")
        await create_or_load_wallet(rpc, wallet_name)
        new_address = await rpc.getnewaddress()
        await set_wallet(chat_id, new_address)

    except Exception as e:
        logging.error(f"Error generating Bitcoin address: {e} | {e}")

async def new_ltc_address(update):
    try:
        chat_id = update.effective_chat.id
        unique_id = await get_unique_id(chat_id)
        wallet_name = f"ltc_wallet_{update.effective_chat.id}_{unique_id}"
        rpc = await getRpc('LTC', wallet_name=wallet_name)
        if rpc is None:
            logging.warning("Rpc client set to none")
            raise ValueError("Invalid currency")
        logging.info(f"Creating new wallet: {wallet_name}")

        await create_or_load_wallet(rpc, wallet_name)
        new_address = await rpc.getnewaddress()
        await set_wallet(chat_id, new_address)

    except Exception as e:
        logging.error(f"Error generating Litecoin address: {e} | {e}")

async def get_estimated_fee(tx_size_vbytes=141, fee_rate_sat_per_vbyte=16):
    try:
        total_fee_sats = tx_size_vbytes * fee_rate_sat_per_vbyte
        total_fee = total_fee_sats / 100_000_000
        return total_fee
        
    except Exception as ex:
        logging.error(f"Error getting estimated fee: {ex}")
        return None

async def escrow_balance(update, context):
    try:
        amount = await get_amount(update.effective_chat.id)
        currency = await get_currency(update.effective_chat.id)
        status = await get_status(update.effective_chat.id)

        if amount is not None:
            amount = Decimal(f"{amount:.4g}")

            amount_str = str(amount)
            for char in ['_', '*', '`', '[', ']']:
                amount_str = amount_str.replace(char, f'\\{char}')
        elif amount is None:
            amount = "0"
        message = f""

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode='Markdown'
        )
    except:
        await not_started_error(update, context)

async def verify_wallet(update:Update, context:ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        wallets = await get_all_wallets()
        address = ''.join(update.message.text.split()[1:])
        if len(address) == 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text="",
                parse_mode="MarkdownV2"
            )
            return
        elif address in wallets:
            message = ""
        else:
            message = ""
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        await handle_wallet_error(update, context, e)