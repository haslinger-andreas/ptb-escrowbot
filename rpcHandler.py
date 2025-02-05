from rpc import BitcoinCoreClient, JSONRPCException
import logging
from config import BITCOIN_RPC_HOST, BITCOIN_RPC_PASSWORD, BITCOIN_RPC_PORT, BITCOIN_RPC_USER, LITECOIN_RPC_HOST, LITECOIN_RPC_PASSWORD, LITECOIN_RPC_PORT, LITECOIN_RPC_USER

BITCOIN_RPC_URL = f"http://{BITCOIN_RPC_USER}:{BITCOIN_RPC_PASSWORD}@{BITCOIN_RPC_HOST}:{BITCOIN_RPC_PORT}"
LITECOIN_RPC_URL = f"http://{LITECOIN_RPC_USER}:{LITECOIN_RPC_PASSWORD}@{LITECOIN_RPC_HOST}:{LITECOIN_RPC_PORT}"

async def getBtc_Rpc(wallet_name=None):
    btc_rpc = BitcoinCoreClient(rpc_url=BITCOIN_RPC_URL)
    try:
        if wallet_name:
            return BitcoinCoreClient(rpc_url=BITCOIN_RPC_URL, wallet_name=wallet_name)
        return btc_rpc
    except JSONRPCException as e:
        logging.error(f"{e.code} | {e.message}")

async def getLtc_Rpc(wallet_name=None):
    try:
        ltc_rpc = BitcoinCoreClient(rpc_url=LITECOIN_RPC_URL)
        if wallet_name:
            return BitcoinCoreClient(rpc_url=LITECOIN_RPC_URL, wallet_name=wallet_name)
        return ltc_rpc
    except JSONRPCException as e:
        logging.error(f"{e.code} | {e.message}")

async def getRpc(curr, wallet_name=None):    
    try:
        curr = str(curr)
        if curr.upper() == 'BTC':
            return await getBtc_Rpc(wallet_name)
        if curr.upper() == 'LTC':
            return await getLtc_Rpc(wallet_name)
        else:
            return None
    except JSONRPCException as e:
        logging.error(f"Error getting RPC: {e.code} | {e.message}")
