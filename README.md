🤖 Trident Trade Bot

A fully automated Zerodha-based intraday trading bot that uses technical indicators (EMA, RSI, MACD) and market trend context to analyze and execute trades on NIFTY 50 stocks. Includes live Telegram control, SL/TP logic, and risk management.


---

🚀 Features

✅ Real-time NIFTY 50 scanner

📈 EMA, RSI, MACD strategy with market trend alignment

🔁 Automated buy and exit via Zerodha Kite

💼 Risk management (capital, SL, profit/loss limits)

📲 Telegram bot for remote control and alerts

🧾 Trade logging and daily P&L tracking



---

⚙️ Setup Instructions

1. Clone the Repo

git clone https://github.com/yourusername/trident-bot.git
cd trident-bot

2. Install Requirements

pip install -r requirements.txt

3. Configure Environment Variables

Create a .env file:

KITE_API_KEY=your_kite_api_key
ZERODHA_ACCESS_TOKEN=your_access_token

TELEGRAM_API_ID=your_telegram_api_id
TELEGRAM_API_HASH=your_api_hash
BOT_TOKEN=your_telegram_bot_token
AUTHORIZED_USERS=123456789,987654321

WALLET_CAPITAL=1000
MAX_PROFIT=300
MAX_LOSS=200

4. Run the Bot

python main.py


---

🤖 Telegram Commands

/start - Show available commands
/status - Show trading status
/stop - Pause trading
/resume - Resume trading
/log - Show latest trades
/token <token> - Update Zerodha token
/setprofit <amount> - Update max profit limit
/setloss <amount> - Update max loss limit
/setcapital <amount> - Update wallet capital


---

📊 Strategy Logic

EMA20 > EMA50

RSI rising and < 60

MACD > Signal

Bullish market context


If 4/4 match → Trade is executed ✅


---

📎 Notes

Zerodha token must be refreshed daily via /token

Live capital is used — trade responsibly!

MIS orders only (auto square-off)



---

🔐 Disclaimer

This bot executes real trades. Use with caution and test thoroughly before going live with real capital.


---

👨‍💻 Developer

Created by Akhilesh A L (@tridenttradesbot)

Happy Trading! 💸

