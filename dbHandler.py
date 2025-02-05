import logging
import aiosqlite
import uuid
from config import DB_PATH
async def init_db():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    uuid TEXT PRIMARY KEY,
                    wallet TEXT UNIQUE,
                    chat_id TEXT,
                    currency TEXT,
                    status INTEGER,
                    buyer TEXT,
                    buyer_id TEXT,
                    buyer_wallet TEXT,
                    seller TEXT,
                    seller_id TEXT,
                    seller_wallet TEXT,
                    amount REAL,
                    txid TEXT,
                    transaction_amount REAL
                )
            ''')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_chat_id ON transactions (chat_id)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_wallet ON transactions (wallet)')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_unique_id ON transactions (uuid)')
            await db.commit()
            logging.info("Transactions initialized successfully.")
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS Banned_Users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT,
                    reason TEXT
                )
            ''')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON Banned_Users (user_id)')
            await db.commit()
            logging.info("Banned Users initialized successfully.")
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS contact_requests (
                    contact_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    username TEXT,
                    chat_id TEXT,
                    reason TEXT,
                    status TEXT,
                    support_id TEXT
                )
            ''')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON contact_requests (user_id)')
            await db.commit()
            logging.info("Contact requests initialized successfully.")
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bot_info (
                    version TEXT,
                    description TEXT,
                    status TEXT
                )
            ''')
            await db.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON contact_requests (user_id)')
            await db.commit()
            logging.info("Contact requests initialized successfully.")
    except aiosqlite.Error as e:
        logging.error(f"Failed to initialize database: {e}")

async def gen_UUID():
    return str(uuid.uuid4())

async def new_entry(chat_id, status=0):
    try:
        uuid_str = await gen_UUID()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO transactions (uuid, chat_id, status) VALUES (?, ?, ?)",
                (uuid_str, chat_id, status)
            )
            await db.commit()
        logging.info(f"New transaction started for chat_id: {chat_id} with UUID: {uuid_str}")
        return uuid_str
    except aiosqlite.IntegrityError as e:
        logging.error(f"Integrity Error creating new entry: {e}")
    except aiosqlite.Error as e:
        logging.error(f"Database Error creating new entry: {e}")

async def reset_fresh_entry(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute('''
                UPDATE transactions 
                SET wallet = NULL,
                    currency = NULL,
                    buyer = NULL,
                    buyer_id = NULL,
                    buyer_wallet = NULL,
                    seller = NULL,
                    seller_id = NULL,
                    seller_wallet = NULL,
                    amount = NULL,
                    txid = NULL,
                    status = 0,
                    transaction_amount = NULL
                WHERE chat_id = ?
            ''', (chat_id,))
            await db.commit()
        logging.info(f"Transaction has been reset {chat_id} with UUID")
    except aiosqlite.IntegrityError as e:
        logging.error(f"Integrity Error creating new entry: {e}")
    except aiosqlite.Error as e:
        logging.error(f"Database Error creating new entry: {e}")

async def update_status(chat_id, new_status):
    try:
        while await get_status(chat_id) != new_status:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute(
                    "UPDATE transactions SET status = ? WHERE chat_id = ?",
                    (new_status, chat_id)
                )
                await db.commit()
            logging.info(f"Updated status to {new_status} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error updating status: {e}")

async def update_chat_id(chat_id):
    try:
        status = await get_status(chat_id)
        if status >= 4:
            new_chat_id = '-finished'+str(chat_id)
        else:
            new_chat_id = '-reset'+str(chat_id)
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET chat_id = ?, status = -1 WHERE chat_id = ?",
                (new_chat_id, chat_id)
                )
            await db.commit()
            logging.info(f"Updated status to {new_chat_id} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error updating status: {e}")

async def set_wallet(chat_id, wallet):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET wallet = ? WHERE chat_id = ?",
                (wallet, chat_id)
            )
            await db.commit()
        logging.info(f"Set wallet {wallet} for chat_id: {chat_id}")
    except aiosqlite.IntegrityError as e:
        logging.error(f"Integrity Error setting wallet: {e}")
    except aiosqlite.Error as e:
        logging.error(f"Database Error setting wallet: {e}")

async def set_currency(chat_id, currency):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET currency = ? WHERE chat_id = ?",
                (currency, chat_id)
            )
            await db.commit()
        logging.info(f"Set currency to {currency} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting currency: {e}")

async def set_buyer(chat_id, buyer_id, buyer):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET buyer_id = ?, buyer = ? WHERE chat_id = ?",
                (buyer_id, buyer, chat_id)
            )
            await db.commit()
        logging.info(f"Set buyer {buyer} (ID: {buyer_id}) for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting buyer: {e}")

async def set_seller(chat_id, seller_id, seller):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET seller_id = ?, seller = ? WHERE chat_id = ?",
                (seller_id, seller, chat_id)
            )
            await db.commit()
        logging.info(f"Set seller {seller} (ID: {seller_id}) for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting seller: {e}")

async def set_buyer_wallet(chat_id, buyer_wallet):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET buyer_wallet = ? WHERE chat_id = ?",
                (buyer_wallet, chat_id)
            )
            await db.commit()
        logging.info(f"Set buyer_wallet {buyer_wallet} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting buyer_wallet: {e}")

async def set_seller_wallet(chat_id, seller_wallet):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET seller_wallet = ? WHERE chat_id = ?",
                (seller_wallet, chat_id)
            )
            await db.commit()
        logging.info(f"Set seller_wallet {seller_wallet} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting seller_wallet: {e}")

async def set_amount(chat_id, amount):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET amount = ? WHERE chat_id = ?",
                (amount, chat_id)
            )
            await db.commit()
        logging.info(f"Set amount {amount} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting amount: {e}")

async def set_transaction_amount(chat_id, amount):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET transaction_amount = ? WHERE chat_id = ?",
                (amount, chat_id)
            )
            await db.commit()
        logging.info(f"Set transaction_amount {amount} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting amount: {e}")

async def set_txid(chat_id, txid):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE transactions SET txid = ? WHERE chat_id = ?",
                (txid, chat_id)
            )
            await db.commit()
        logging.info(f"Set Txid {txid} for chat_id: {chat_id}")
    except aiosqlite.Error as e:
        logging.error(f"Error setting amount: {e}")

async def get_status(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT status FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting status: {e}")
        return None

async def get_wallet(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT wallet FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting wallet: {e}")
        return None

async def get_buyer_id(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT buyer_id FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting buyer_id: {e}")
        return None

async def get_seller_id(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT seller_id FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting seller_id: {e}")
        return None

async def get_buyer(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT buyer FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting buyer: {e}")
        return None

async def get_seller(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT seller FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting seller: {e}")
        return None

async def get_currency(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT currency FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting currency: {e}")
        return None

async def get_buyer_wallet(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT buyer_wallet FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting buyer_wallet: {e}")
        return None

async def get_seller_wallet(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT seller_wallet FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting seller_wallet: {e}")
        return None

async def get_unique_id(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT uuid FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting uuid: {e}")
        return None

async def get_amount(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT amount FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting amount: {e}")
        return None

async def get_transaction_amount(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT transaction_amount FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting transaction_amount: {e}")
        return None

async def get_chat_id(address):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT chat_id FROM transactions WHERE wallet = ?", (address,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting amount: {e}")
        return None

async def get_wallets():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"SELECT wallet FROM transactions WHERE status = ?", (2,)) as cursor:
                rows = await cursor.fetchall()
                db_wallet_address = set(row[0] for row in rows)
                return db_wallet_address
    except aiosqlite.Error as e:
        logging.error(f"Error getting active wallets: {e}")
        return set()

async def get_all_wallets():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"SELECT wallet FROM transactions") as cursor:
                rows = await cursor.fetchall()
                db_wallet_address = set(row[0] for row in rows)
                return db_wallet_address
    except aiosqlite.Error as e:
        logging.error(f"Error getting active wallets: {e}")
        return set()

async def get_txid(chat_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT txid FROM transactions WHERE chat_id = ?", (chat_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None
    except aiosqlite.Error as e:
        logging.error(f"Error getting txid: {e}")
        return None

async def get_all_transactions():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"SELECT * FROM transactions") as cursor:
                rows = await cursor.fetchall()
                transactions = [
                    {
                        "uuid": row[0],
                        "wallet": row[1],
                        "chat_id": row[2],
                        "currency": row[3],
                        "status": row[4],
                        "buyer": row[5],
                        "buyer_id": row[6],
                        "buyer_wallet": row[7],
                        "seller": row[8],
                        "seller_id": row[9],
                        "seller_wallet": row[10],
                        "amount": row[11],
                        "txid": row[12],
                        "transaction_amount": row[13]
                        } for row in rows
                    ]
                return transactions
    except aiosqlite.Error as e:
        logging.error(f"Error gatting transactions: {e}")
        return None

async def add_new_contact_request(user_id, username,chat_id, reason=None, status="Unresolved"):
    try:
        uuid = await gen_UUID()
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO contact_requests (contact_id, user_id, username, chat_id, reason, status) VALUES (?, ?, ?, ?, ?, ?)",
                (uuid, user_id, username, chat_id, reason, status)
            )
            await db.commit()
        logging.info(f"New contact request added for chat_id: {chat_id}")
        return uuid
    except aiosqlite.IntegrityError as e:
        logging.error(f"Integrity Error creating new entry: {e}")
        return None
    except aiosqlite.Error as e:
        logging.error(f"Database Error creating new entry: {e}")
        return None

async def set_support_for_request(contact_id, support_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE contact_requests SET support_id = ? WHERE contact_id = ?",
                (support_id, contact_id))
            await db.commit()
            logging.info("added support")
    except aiosqlite.Error as e:
        logging.error(f"Error adding support: {e}")

async def set_status_for_request(contact_id, status):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "Update contact_requests SET status = ? WHERE contact_id = ?",
                (status, contact_id))
            await db.commit()
            logging.info("updated status")
    except aiosqlite.Error as e:
        logging.error(f"Error updating status: {e}")

async def add_ban_user(user_id, username, reason):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO Banned_Users (user_id, username, reason) VALUES (?, ?, ?)",
                (str(user_id), str(username), reason,)
            )
            await db.commit()
        logging.info(f"Added {user_id} to banned users")
        return True
    except aiosqlite.IntegrityError as e:
        logging.error(f"Integrity Error creating new entry: {e}")
    except aiosqlite.Error as e:
        logging.error(f"Database Error creating new entry: {e}")

async def remove_ban_user(user_id):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "DELETE FROM Banned_Users WHERE user_id = (?)",
                (user_id,)
            )
            await db.commit()
        logging.info(f"Deleted {user_id} from banned users")
        return True 
    except aiosqlite.IntegrityError as e:
        logging.error(f"Integrity Error deleting entry: {e}")
    except aiosqlite.Error as e:
        logging.error(f"Database Error deleting entry: {e}")    

async def get_all_banned_users():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(f"SELECT user_id FROM Banned_Users") as cursor:
                rows = await cursor.fetchall()
                users = set(int(row[0]) for row in rows)
                return users
    except aiosqlite.Error as e:
        logging.error(f"Error getting active wallets: {e}")
        return set()