# Secure & Automated Escrow Bot for Cryptocurrency Transactions  

This is a **fully automated Telegram escrow bot** designed to facilitate secure peer-to-peer Bitcoin and Litecoin transactions. Built using `python-telegram-bot` (PTB), the bot ensures **trust, transparency, and automation** in digital asset trades.  

## 🚀 Features  
- **Escrow Services**: Securely holds funds until transaction conditions are met.  
- **Automated Wallet Management**: Generates unique deposit addresses for each transaction.  
- **Transaction Monitoring**: Tracks balances, confirmations, and payment statuses in real-time.  
- **Refund & Payment Processing**: Automates refunds and releases funds as required.  
- **User Verification**: Ensures users meet predefined conditions before participating.  
- **Admin Tools**: Ban/unban users, manage transactions, and monitor disputes.  
- **Support System**: Integrated messaging for contacting support directly through the bot.  
- **Error Handling & Logging**: Automatic error detection and logging for troubleshooting.  

## 🛠️ Technical Stack  
- **Python 3.8+**  
- **python-telegram-bot (PTB)**  
- **Bitcoin & Litecoin Core (RPC Integration)**  
- **SQLite for Transaction Logging**  
- **Tor Proxy for Enhanced Privacy**  
- **Asynchronous Processing with `asyncio`**  

## 🔧 How It Works  
1. A user initiates an escrow transaction.  
2. The bot generates a unique wallet address for deposits.  
3. Funds are held securely until transaction conditions are met.  
4. Upon confirmation, funds are either released or refunded.  
5. All transaction data is logged for transparency and tracking.  

## 📦 Setup & Installation  

### **1. Clone the Repository**  
```bash
git clone https://github.com/haslinger-andreas/ptb-escrowbot.git
cd ptb-escrowbot
```
### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```
### **3. Configure Your Bot**
Edit the config.py and .env file with your Telegram bot token, Bitcoin/Litecoin RPC credentials, and other settings.
### **4. Run the Bot**
```bash
python escrowbot.py
```
### **🤝 Contributing**
Contributions are welcome! Feel free to fork the repository, open an issue, or submit a pull request.
### **⚖️ License**
This project is licensed under the **MIT License**.