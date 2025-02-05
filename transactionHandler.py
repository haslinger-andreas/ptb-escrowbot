import logging
from decimal import Decimal
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dbHandler import get_buyer_id, get_seller_id, get_seller_wallet, get_buyer_wallet, get_status, get_currency, get_amount, new_entry, reset_fresh_entry, update_chat_id, update_status, set_txid, get_unique_id, set_transaction_amount, set_amount
from rpcHandler import getRpc
from errorHandler import handle_escrow_error, handle_not_group, handle_transaction_error, handle_user_error, not_started_error, not_started_error
from config import OWNER_ID
from rpc import JSONRPCException
from walletHandler import create_or_load_wallet

async def pay_seller(update, context):
    try:
        chat_id = update.effective_chat.id
        buyer_id = await get_buyer_id(chat_id)
        seller_id = await get_seller_id(chat_id)
        sender_id = update.effective_user.id
        seller_wallet = await get_seller_wallet(chat_id)
        status = await get_status(chat_id)
        currency = await get_currency(chat_id)
        amount_to_send = await get_amount(chat_id)
        uuid = await get_unique_id(chat_id)

        if status is None:
            await not_started_error(update, context)
            return
        if int(OWNER_ID) != int(sender_id):
            if seller_id is sender_id or int(buyer_id) != int(sender_id or int(OWNER_ID) != int(sender_id)):
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return

        if status != 3:
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return

        wallet_to_load = f"{currency.lower()}_wallet_{chat_id}_{uuid}"
        try:
            txid = await send_transaction(wallet_to_load, chat_id, seller_wallet, amount_to_send, 6, "conservative")
            if not txid:
                await handle_transaction_error(update, context)
                return
        except JSONRPCException as e:
            await handle_escrow_error(update, context)
            return
        await update_status(chat_id, 4)
        await show_transaction(
            update, 
            context, 
            seller_wallet, 
            txid, 
            amount_to_send,
            currency,
            transaction_type="seller"
        )
    except:
        await handle_transaction_error(update, context)

async def refund_buyer(update, context):
    try:
        chat_id = update.effective_chat.id
        buyer_id = await get_buyer_id(chat_id)
        seller_id = await get_seller_id(chat_id)
        sender_id = update.effective_user.id
        buyer_wallet = await get_buyer_wallet(chat_id)
        status = await get_status(chat_id)
        currency = await get_currency(chat_id)
        amount_to_send = await get_amount(chat_id)
        uuid = await get_unique_id(chat_id)

        if status is None:
            await not_started_error(update, context)
            return

        if int(OWNER_ID) != int(sender_id):
            if buyer_id == sender_id or int(seller_id) != int(sender_id):
                await context.bot.sendMessage(chat_id=chat_id, text="")
                return
        if status != 3:
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return

        wallet_to_load = f"{currency.lower()}_wallet_{chat_id}_{uuid}"
        try:
            txid = await send_transaction(wallet_to_load, chat_id, buyer_wallet, amount_to_send, 6, "conservative")
            if not txid:
                await handle_transaction_error(update, context)
                return
        except JSONRPCException as e:
            logging.error(f"something went wrong: {e}")
            await handle_escrow_error(update, context)
            return
        await update_status(chat_id, 5)
        await show_transaction(
            update, 
            context, 
            buyer_wallet, 
            txid, 
            amount_to_send,
            currency,
            transaction_type="buyer"
        )
    except JSONRPCException as e:
        await handle_transaction_error(update, context)
        logging.error(f"{e.message} | {e.code} ")

async def send_transaction(wallet_to_load, chat_id, address, amount, conf_target=6, estimate_mode="economical"):
    try:
        amount = Decimal(amount)
        curr = wallet_to_load[0:3]
        await create_or_load_wallet(rpc=await getRpc(curr=curr), wallet_name=wallet_to_load)
        rpc = await getRpc(curr, wallet_name=wallet_to_load)
        if rpc is None:
            logging.warning("RPC client set to None.")
            raise ValueError("Invalid currency")

        txid = await rpc.sendtoaddress(
            address,
            float(amount),
            f"EscrowDealDone: {chat_id}",
            "",              
            True,   
            False,           
            conf_target,     
            estimate_mode   
        )
            
        logging.info(f"Transaction sent. TXID: {txid}")
        await set_txid(chat_id, txid)
        await set_transaction_amount(chat_id, float(amount))
        await set_amount(chat_id, 0)
        return txid

    except JSONRPCException as e:
        logging.error(f"JSONRPCException during transaction: {e.code} | {e.message}")
        return None
    except Exception as ex:
        logging.error(f"Error sending transaction: {ex}")
        return None

async def show_transaction(update, context, address, txid, amount, currency, transaction_type="seller"):
    transaction_role = "Seller" if transaction_type == "seller" else "Buyer"
    try:
        message = (
        ""
        )
        await context.bot.sendMessage(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.info(f"Error showing transaction: {e}")

async def reset_transaction(update, context):
    chat_id = update.effective_chat.id
    status = await get_status(chat_id)
    if status is None:
        await not_started_error(update, context)
        return
    try:
        user_id = update.effective_user.id
        seller_id = await get_seller_id(chat_id)
        buyer_id = await get_buyer_id(chat_id)

        if buyer_id is None and seller_id is None:
            await reset_fresh_entry(chat_id)
            await context.bot.sendMessage(chat_id=chat_id, text=".")
            return
        if user_id != int(seller_id) and user_id != int(buyer_id):
            await context.bot.sendMessage(chat_id=chat_id, text="")
            return

        context.chat_data['reset_initiator_id']=user_id

        keyboard = [[InlineKeyboardButton("YES", callback_data='reset_YES')], [InlineKeyboardButton("NO", callback_data='reset_NO')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.sendMessage(
            chat_id=chat_id,
            text="",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        await handle_user_error(update, context, e)

async def handle_reset_transaction(update, context, query):
    try:
        user_choice= query.data
        chat_id = update.effective_chat.id
        responder_id = query.from_user.id
        initiator_id = context.chat_data.get('reset_initiator_id')

        buyer_id = await get_buyer_id(chat_id)
        seller_id = await get_seller_id(chat_id)

        if not user_choice.startswith('reset_'):
            return

        if initiator_id == int(seller_id) and responder_id != int(seller_id):
            logging.info("buyer confirmed")
        elif initiator_id == int(buyer_id) and responder_id != int(buyer_id):
            logging.info("seller confirmed")
        else:
            await query.answer("")
            return

        action = user_choice.split('_')[1]
        if action.upper() == 'YES':
            await update_chat_id(chat_id)
            await new_entry(chat_id)
            await context.bot.sendMessage(chat_id=chat_id, text="")
        elif action.upper() == 'NO':
            await context.bot.sendMessage(chat_id=chat_id, text="")
        await query.answer()

    except Exception as e:
        await handle_user_error(update, context, e)   