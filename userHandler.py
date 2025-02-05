from decimal import Decimal
import os
import logging
import re
import qrcode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from rpcHandler import getRpc
from walletHandler import create_or_load_wallet, new_btc_address, new_ltc_address
from validate_wallet import check_wallet_address_slow
from errorHandler import handle_user_error, not_started_error
from dbHandler import get_currency, get_seller_id, get_buyer_id, get_status, get_seller_wallet, get_buyer_wallet, get_wallet, set_buyer, set_buyer_wallet, set_seller, set_seller_wallet, update_status, set_currency, get_buyer, get_seller, get_amount, get_unique_id, new_entry, get_txid

async def set_buyer_command(update, context):
    chat_id = update.effective_chat.id
    currency = await get_currency(chat_id)
    if currency is None:
       await not_started_error(update, context)
       return
    try:
        sender_id = update.effective_user.id
        seller_id = await get_seller_id(chat_id)
        buyer_id = await get_buyer_id(chat_id)
        status = await get_status(chat_id)
        seller_wallet = await get_seller_wallet(chat_id)
        wallet = await get_wallet(chat_id)

        logging.info(f"Sender_id: {sender_id} | seller_id: {seller_id}")
        if buyer_id is not None:
            if int(status) != 1:
                logging.info("Buyer has already been set")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return
        if seller_id is not None:
            if int(seller_id) == int(sender_id):
                logging.info("Seller and sender are the same")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return

        address = ''.join(update.message.text.split()[1:])
        if len(address) == 0:
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return

        curr = await check_wallet_address_slow(address)
        if address == wallet:
                logging.info("Transaction and sender wallets are the same")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return
        if seller_wallet is not None:
            if address == seller_wallet:
                logging.info("Seller and sender wallets are the same")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return
            
        if curr == 'INVALID':
            logging.error('Invalid wallet address provided by buyer')
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return
        elif curr != await get_currency(chat_id):
            logging.error('Wrong wallet address provided by buyer')
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return

        await set_buyer(chat_id, sender_id, "@"+update.effective_user.username)
        await set_buyer_wallet(chat_id, address)
        await context.bot.sendMessage(chat_id=chat_id, text=f"")

        await check_users(update, context)

    except Exception as e:
        await handle_user_error(update, context, e)
        

async def set_seller_command(update, context):
    chat_id = update.effective_chat.id
    currency = await get_currency(chat_id)
    if currency is None:
        await not_started_error(update, context)
        return
    try:
        sender_id = update.effective_user.id
        buyer_id = await get_buyer_id(chat_id)
        seller_id = await get_seller_id(chat_id)
        status = await get_status(chat_id)
        buyer_wallet = await get_buyer_wallet(chat_id)
        wallet = await get_wallet(chat_id)

        logging.info(f"Sender_id: {sender_id} | buyer_id: {buyer_id}")
        if seller_id is not None:
            if int(status) != 1:
                logging.info("Seller has already been set")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return

        if buyer_id is not None:
            if int(buyer_id) == int(sender_id):
                logging.info("Seller and sender are the same")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return


        address = ''.join(update.message.text.split()[1:])
        
        if len(address) == 0:
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return

        curr = await check_wallet_address_slow(address)
        if address == wallet:
                logging.info("Transaction and sender wallets are the same")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return
        if buyer_wallet is not None:
            if address == buyer_wallet:
                logging.info("Seller and sender wallets are the same")
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return
            
        if curr == 'INVALID':
            logging.error('Invalid wallet address provided by buyer')
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return
        elif curr != await get_currency(chat_id):
            logging.error('Wrong wallet address provided by seller')
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return

        await set_seller(chat_id, sender_id, "@"+update.effective_user.username)
        await set_seller_wallet(chat_id, address)

        await context.bot.sendMessage(chat_id=chat_id, text=f"")

        await check_users(update, context)

    except Exception as e:
        await handle_user_error(update, context, e)

async def currency_selection(update, context):
    try:
        logging.info("Asking for currency")
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        logging.info(f"User {user_id} is selecting a currency in chat {chat_id}")

        keyboard = [[InlineKeyboardButton("BTC", callback_data='currency_BTC')], [InlineKeyboardButton("LTC", callback_data='currency_LTC')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.sendMessage(
            chat_id=chat_id,
            text="",
            reply_markup=reply_markup
        )


    except Exception as e:
        logging.error(f"Error in currency_selection: {e}")
        await handle_user_error(update, context, str(e))

async def handle_currency_selection(update, context, query):
    try:
        chat_id = update.effective_chat.id
        curr = await get_currency(chat_id)
        sender_id = update.effective_user.id        
        user_choice = query.data
        
        if not user_choice.startswith('currency_'):
            return

        currency = user_choice.split('_')[1]

        if curr is not None:
            logging.info(f"Currency already set to {curr}")
            await context.bot.sendMessage(
                chat_id=chat_id,
                text=f""
            )
            return

        logging.info(f"User {sender_id} chose {currency} in chat {chat_id}")

        if currency == 'LTC':
            await new_ltc_address(update)
        elif currency == 'BTC':
            await new_btc_address(update)
        if await get_wallet(chat_id) is None:
            await context.bot.sendMessage(
                chat_id=chat_id,
                text=""
            )
            return

        await update_status(chat_id, 1)
        await set_currency(chat_id, currency)
        await context.bot.sendMessage(
            chat_id=chat_id,
            text=(
                ""
            ),
            parse_mode="Markdown"
        )

    except Exception as e:
        logging.error(f"Error in handle_currency_selection: {e}")
        await handle_user_error(update, context, str(e))        


async def start_transaction(update, context):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        buyer = await get_buyer(chat_id)
        seller = await get_seller(chat_id)
        status = await get_status(chat_id)
        currency = await get_currency(chat_id)


        logging.info(f"User {user_id} is trying to start a new transaction in chat {chat_id}")

        if status is not None:
            if status == 0:
                await currency_selection(update,context)
                return
            elif status == 1:
                await context.bot.sendMessage(chat_id=chat_id, text=f"")
                return
            elif status == 2:
                await context.bot.sendMessage(chat_id=chat_id, text=f"")
                await send_status(update, context)
                return
            elif status == 3:
                await context.bot.sendMessage(chat_id=chat_id, text="")
                await send_status(update, context)
                return
            elif status == 4 or status == 5:
                await context.bot.sendMessage(chat_id=chat_id, text="")
                await send_status(update, context)
                return
            else:
                await context.bot.sendMessage(chat_id=chat_id, text=f"")
                return

        await new_entry(chat_id, 0)

        await context.bot.sendMessage(chat_id=chat_id, text="")
        
        await currency_selection(update, context)        

    except Exception as e:
        logging.error(f"Error in currency start_transaction: {e}")
        await handle_user_error(update, context, str(e))

async def check_users(update, context):
    try:
        logging.info("Checking if users meet the requiremets")
        chat_id = update.effective_chat.id
        seller_id = await get_seller_id(chat_id)
        buyer_id = await get_buyer_id(chat_id)
        if seller_id is None or buyer_id is None:
            logging.info("Seller/Buyer not set yet")
            return
        await update_status(chat_id, 2)
        await context.bot.sendMessage(
            chat_id=chat_id,
            text=""
        )
        await send_status(update, context)

    except Exception as e:
        logging.error(e)

async def send_status(update, context):
    chat_id = update.effective_chat.id
    status = await get_status(chat_id)
    if status is None:
            await not_started_error(update, context)
            return
    try:
        logging.info("Sending status:")
        seller_id = await get_seller_id(chat_id)
        seller = await get_seller(chat_id)
        buyer_id = await get_buyer_id(chat_id)
        buyer = await get_buyer(chat_id)
        address = await get_wallet(chat_id)
        curr = await get_currency(chat_id)
        amount = await get_amount(chat_id)
        uuid = await get_unique_id(chat_id)
        sent_amount, fee, confirmations, txid = await get_transaction_status(update, context)
        url = f'https://live\\.blockcypher\\.com/{str(curr).lower()}/tx/{txid}' if txid else ''

        if seller or buyer:
            seller = re.sub(r'([_*[\]()~`>#+-=|{}.!\\])', r'\\\1', seller)
            buyer = re.sub(r'([_*[\]()~`>#+-=|{}.!\\])', r'\\\1', buyer)

        if amount is not None:
            amount = Decimal(f"{amount:.4g}")

        # Enhanced status message
        if confirmations == -1:
            transaction_status = "Not sent"
        elif confirmations >= 6:
            transaction_status = "Confirmed"
        elif confirmations >= 0 and confirmations < 6:
            transaction_status = "Pending\\.\\.\\."
        status_message = (
            ""
        )

        img = qrcode.make(address)
        qr_image_path = f"./qrcode_{chat_id}.png"
        img.save(qr_image_path)
        await context.bot.sendPhoto(
                chat_id=chat_id, 
                photo=open(qr_image_path, 'rb'), 
                caption=status_message, 
                parse_mode="MarkdownV2"
            )
        if os.path.exists(qr_image_path):
                os.remove(qr_image_path)
    except Exception as e:
        logging.error(f"error in send_status: {e}")


async def get_transaction_status(update=None, context=None):
    try:
        chat_id = update.effective_chat.id
        txid = await get_txid(chat_id)
        if txid is None:
            return None, None, -1, None
        curr = await get_currency(chat_id)
        unique_id = await get_unique_id(chat_id)
        wallet_name = f"{curr.lower()}_wallet_{chat_id}_{unique_id}"
        await create_or_load_wallet(rpc=await getRpc(curr=curr), wallet_name=wallet_name)
        rpc = await getRpc(curr, wallet_name=wallet_name)

        status = await rpc.gettransaction(txid)
        amount = status['amount']
        fee = status['fee']
        confirmations = int(status['confirmations'])
        return amount, fee, confirmations, txid
    except Exception as e:
        logging.info(f"Error in getting transaction status: {e}")
        return None, None, -1, None