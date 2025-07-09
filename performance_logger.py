import os
from datetime import datetime

LOG_FILE = "trade_log.csv"

def log_trade(symbol, action, price, qty, pnl=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{now},{symbol},{action},{price},{qty},{pnl if pnl is not None else ''}\n")

def get_last_log_summary(n=5):
    if not os.path.exists(LOG_FILE):
        return "No trades logged yet."

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()[-n:]

    summary = "\n".join(lines)
    return summary if summary else "No recent trades."
