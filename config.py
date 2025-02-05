import os
from dotenv import load_dotenv

load_dotenv()

CHAT_ID = os.getenv("CHAT_CHANNEL_ID")
#bot
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BETA_TOKEN = os.getenv("BETA_TELEGRAM_BOT_TOKEN")
DB_PATH = os.getenv("DATABASE_PATH", "db.db")

#telegram ids
OWNER_ID = os.getenv("OWNER_ID")
LOG_ID = os.getenv("LOG_CHANNEL_ID")
CHAT_ID = os.getenv("CHAT_CHANNEL_ID")
VOUCH_ID = os.getenv("VOUCHES_CHANNEL_ID")
UPDATES_ID = os.getenv("UPDATES_CHANNEL_ID")
MAIN_ID = os.getenv("MAIN_CHANNEL_ID")
LOGO_GIF = os.getenv("LOGO_GIF")

#proxy
PROXY_IP = os.getenv("PROXY_IP")
PROXY_PORT = os.getenv("PROXY_PORT")

#rpc
BITCOIN_RPC_USER = os.getenv("BITCOIN_RPC_USER")
BITCOIN_RPC_PASSWORD = os.getenv("BITCOIN_RPC_PASSWORD")
BITCOIN_RPC_HOST = os.getenv("BITCOIN_RPC_HOST")
BITCOIN_RPC_PORT = os.getenv("BITCOIN_RPC_PORT")
LITECOIN_RPC_USER = os.getenv("LITECOIN_RPC_USER")
LITECOIN_RPC_PASSWORD = os.getenv("LITECOIN_RPC_PASSWORD")
LITECOIN_RPC_HOST = os.getenv("LITECOIN_RPC_HOST")
LITECOIN_RPC_PORT = os.getenv("LITECOIN_RPC_PORT")