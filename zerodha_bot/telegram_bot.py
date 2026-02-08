import json
import logging
from pathlib import Path

import pandas as pd
import telebot
from kiteconnect import KiteConnect

try:
    from .config import KITE_ACCESS_TOKEN, KITE_API_KEY, TELEGRAM_TOKEN, missing_env_vars
except ImportError:  # script execution fallback
    from config import KITE_ACCESS_TOKEN, KITE_API_KEY, TELEGRAM_TOKEN, missing_env_vars

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
EXCLUDE_FILE = BASE_DIR / "excluded.json"
TRADES_FILE = LOG_DIR / "trades.jsonl"
APP_LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_excluded():
    try:
        with open(EXCLUDE_FILE, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
        stocks = data.get("stocks", [])
        return {symbol.strip().upper() for symbol in stocks if isinstance(symbol, str) and symbol.strip()}
    except Exception:
        return set()


def save_excluded(excluded_set):
    with open(EXCLUDE_FILE, "w", encoding="utf-8") as file_obj:
        json.dump({"stocks": sorted(excluded_set)}, file_obj, indent=2)


def create_kite_client():
    missing = missing_env_vars("KITE_API_KEY", "KITE_ACCESS_TOKEN")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    kite = KiteConnect(api_key=KITE_API_KEY)
    kite.set_access_token(KITE_ACCESS_TOKEN)
    return kite


def register_handlers(bot, kite):
    @bot.message_handler(commands=["help"])
    def cmd_help(message):
        help_text = (
            "/help - List commands\n"
            "/status - Account balance and positions\n"
            "/summary - Trade summary (P/L)\n"
            "/exclude SYMBOL - Exclude stock\n"
            "/include SYMBOL - Include stock\n"
            "/tokenlink - Get Kite login URL\n"
            "/log - Show recent log lines\n"
            "/exportlog - Export log file\n"
            "/exporttrades - Export trade history\n"
            "/health - Bot health check"
        )
        bot.reply_to(message, help_text)

    @bot.message_handler(commands=["status"])
    def cmd_status(message):
        try:
            margins = kite.margins(segment="equity")
            net_balance = margins.get("net", None)
            text = f"💰 *Available Margin:* {net_balance}\n\n"
        except Exception:
            bot.send_message(message.chat.id, "Error retrieving account margins.", parse_mode="Markdown")
            return

        try:
            positions = kite.positions().get("net", [])
            open_positions = [pos for pos in positions if pos.get("quantity", 0) != 0]
            if open_positions:
                text += "*Open Positions:*\n"
                for pos in open_positions:
                    text += (
                        f" - {pos.get('tradingsymbol')}: Qty {pos.get('quantity')}, "
                        f"P&L {pos.get('pnl')}\n"
                    )
            else:
                text += "No open positions."
        except Exception:
            text += "No open positions."

        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    @bot.message_handler(commands=["summary"])
    def cmd_summary(message):
        try:
            df = pd.read_json(TRADES_FILE, lines=True)
            total_trades = df.shape[0]
            profit = 0.0
            for _, row in df.iterrows():
                if row["action"] == "BUY":
                    profit -= row["price"] * row["quantity"]
                elif row["action"] == "SELL":
                    profit += row["price"] * row["quantity"]
            text = f"📈 *Trade Summary:*\nTotal Trades: {total_trades}\nNet P/L: {profit:.2f}"
        except Exception:
            text = "No trades logged yet."
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    @bot.message_handler(commands=["exclude"])
    def cmd_exclude(message):
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /exclude SYMBOL")
            return

        symbol = parts[1].strip().upper()
        excluded = load_excluded()
        if symbol in excluded:
            bot.reply_to(message, f"{symbol} is already excluded.")
            return

        excluded.add(symbol)
        save_excluded(excluded)
        bot.reply_to(message, f"{symbol} has been excluded from trading.")

    @bot.message_handler(commands=["include"])
    def cmd_include(message):
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "Usage: /include SYMBOL")
            return

        symbol = parts[1].strip().upper()
        excluded = load_excluded()
        if symbol not in excluded:
            bot.reply_to(message, f"{symbol} was not in the exclude list.")
            return

        excluded.remove(symbol)
        save_excluded(excluded)
        bot.reply_to(message, f"{symbol} has been included for trading.")

    @bot.message_handler(commands=["tokenlink"])
    def cmd_tokenlink(message):
        try:
            bot.reply_to(message, f"Login here: {kite.login_url()}")
        except Exception:
            bot.reply_to(message, "Error generating token link.")

    @bot.message_handler(commands=["log"])
    def cmd_log(message):
        try:
            with open(APP_LOG_FILE, "r", encoding="utf-8") as file_obj:
                lines = file_obj.readlines()[-20:]
            log_text = "".join(lines) or "Log is empty."
            bot.reply_to(message, f"```\n{log_text}\n```", parse_mode="Markdown")
        except Exception:
            bot.reply_to(message, "Could not read log file.")

    @bot.message_handler(commands=["exportlog"])
    def cmd_exportlog(message):
        try:
            with open(APP_LOG_FILE, "rb") as file_obj:
                bot.send_document(message.chat.id, file_obj)
        except Exception:
            bot.reply_to(message, "Failed to export log file.")

    @bot.message_handler(commands=["exporttrades"])
    def cmd_exporttrades(message):
        try:
            df = pd.read_json(TRADES_FILE, lines=True)
            excel_path = LOG_DIR / "trades.xlsx"
            df.to_excel(excel_path, index=False)
            with open(TRADES_FILE, "rb") as json_file, open(excel_path, "rb") as excel_file:
                bot.send_document(message.chat.id, json_file)
                bot.send_document(message.chat.id, excel_file)
        except Exception:
            bot.reply_to(message, "Failed to export trades.")

    @bot.message_handler(commands=["health"])
    def cmd_health(message):
        bot.reply_to(message, "🤖 Bot is running and healthy.")


def main():
    missing = missing_env_vars("TELEGRAM_TOKEN", "KITE_API_KEY", "KITE_ACCESS_TOKEN")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    kite = create_kite_client()
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    register_handlers(bot, kite)

    logger.info("Telegram bot polling...")
    bot.polling(non_stop=True, skip_pending=True)


if __name__ == "__main__":
    main()
