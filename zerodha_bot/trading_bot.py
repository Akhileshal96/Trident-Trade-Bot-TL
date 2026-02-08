import argparse
import datetime
import json
import logging
import time
from pathlib import Path

import pytz
from kiteconnect import KiteConnect

try:
    from .config import KITE_ACCESS_TOKEN, KITE_API_KEY, missing_env_vars
except ImportError:  # script execution fallback
    from config import KITE_ACCESS_TOKEN, KITE_API_KEY, missing_env_vars

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
PREDICTIONS_FILE = BASE_DIR / "predictions.json"
EXCLUDE_FILE = BASE_DIR / "excluded.json"

PROFIT_TARGET = 0.02  # 2% profit target
STOP_LOSS = 0.01  # 1% stop loss

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

TZ = pytz.timezone("Asia/Kolkata")


def load_predictions():
    if not PREDICTIONS_FILE.exists():
        logger.warning("Predictions file not found: %s", PREDICTIONS_FILE)
        return []

    try:
        with open(PREDICTIONS_FILE, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    except Exception as exc:
        logger.error("Failed to read predictions file: %s", exc)
        return []

    stocks = data.get("stocks", [])
    normalized = [symbol.strip().upper() for symbol in stocks if isinstance(symbol, str) and symbol.strip()]
    return sorted(set(normalized))


def load_excluded_stocks():
    if not EXCLUDE_FILE.exists():
        return set()

    try:
        with open(EXCLUDE_FILE, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
        stocks = data.get("stocks", [])
        return {symbol.strip().upper() for symbol in stocks if isinstance(symbol, str) and symbol.strip()}
    except Exception as exc:
        logger.error("Failed to parse excluded symbols file: %s", exc)
        return set()


def log_trade(action, symbol, quantity, price):
    entry = {
        "timestamp": datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "price": price,
    }
    with open(LOG_DIR / "trades.jsonl", "a", encoding="utf-8") as file_obj:
        file_obj.write(json.dumps(entry) + "\n")


def create_kite_client():
    missing = missing_env_vars("KITE_API_KEY", "KITE_ACCESS_TOKEN")
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    kite = KiteConnect(api_key=KITE_API_KEY)
    kite.set_access_token(KITE_ACCESS_TOKEN)
    return kite


def place_market_order(kite, symbol, quantity, transaction_type, dry_run):
    if dry_run:
        mock_order_id = f"dry-run-{transaction_type.lower()}-{symbol}-{int(time.time())}"
        logger.info("DRY RUN: %s %s qty=%s", transaction_type, symbol, quantity)
        return mock_order_id

    return kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=kite.EXCHANGE_NSE,
        tradingsymbol=symbol,
        transaction_type=transaction_type,
        quantity=quantity,
        order_type=kite.ORDER_TYPE_MARKET,
        product=kite.PRODUCT_MIS,
    )


def run_trading_loop(kite, poll_seconds=30, max_cycles=None, dry_run=False):
    symbols_to_trade = load_predictions()
    excluded_stocks = load_excluded_stocks()
    open_trades = {}

    logger.info("Symbols to trade: %s", symbols_to_trade)
    logger.info("Excluded symbols: %s", sorted(excluded_stocks))
    logger.info("Starting trading loop...")

    cycle_count = 0
    while True:
        cycle_count += 1
        now = datetime.datetime.now(TZ)
        current_time = now.time()

        if datetime.time(9, 30) <= current_time <= datetime.time(15, 15):
            try:
                margins = kite.margins(segment="equity")
                wallet = float(margins.get("net", 0.0) or 0.0)
            except Exception as exc:
                logger.error("Failed to fetch margins: %s", exc)
                wallet = 0.0

            for symbol in symbols_to_trade:
                if symbol in excluded_stocks or symbol in open_trades:
                    continue

                instrument = f"NSE:{symbol}"
                try:
                    quote = kite.ltp([instrument])
                    last_price = float(quote[instrument]["last_price"])
                except Exception as exc:
                    logger.error("Failed to fetch price for %s: %s", symbol, exc)
                    continue

                if wallet < last_price or last_price <= 0:
                    continue

                qty = int(wallet // last_price)
                if qty < 1:
                    continue

                try:
                    order_id = place_market_order(
                        kite=kite,
                        symbol=symbol,
                        quantity=qty,
                        transaction_type=kite.TRANSACTION_TYPE_BUY,
                        dry_run=dry_run,
                    )
                    logger.info("BUY %s: qty=%s at %s (Order ID: %s)", symbol, qty, last_price, order_id)
                    log_trade("BUY", symbol, qty, last_price)

                    open_trades[symbol] = {
                        "quantity": qty,
                        "buy_price": last_price,
                        "target": last_price * (1 + PROFIT_TARGET),
                        "stop": last_price * (1 - STOP_LOSS),
                    }
                    wallet -= qty * last_price
                except Exception as exc:
                    logger.error("Error placing BUY order for %s: %s", symbol, exc)

            for symbol, trade_info in list(open_trades.items()):
                qty = trade_info["quantity"]
                target = trade_info["target"]
                stop = trade_info["stop"]

                instrument = f"NSE:{symbol}"
                try:
                    quote = kite.ltp([instrument])
                    last_price = float(quote[instrument]["last_price"])
                except Exception as exc:
                    logger.error("Failed to fetch price for %s (exit check): %s", symbol, exc)
                    continue

                should_exit = last_price >= target or last_price <= stop or current_time >= datetime.time(15, 10)
                if not should_exit:
                    continue

                try:
                    order_id = place_market_order(
                        kite=kite,
                        symbol=symbol,
                        quantity=qty,
                        transaction_type=kite.TRANSACTION_TYPE_SELL,
                        dry_run=dry_run,
                    )
                    logger.info("SELL %s: qty=%s at %s (Order ID: %s)", symbol, qty, last_price, order_id)
                    log_trade("SELL", symbol, qty, last_price)
                except Exception as exc:
                    logger.error("Error placing SELL order for %s: %s", symbol, exc)

                open_trades.pop(symbol, None)

            time.sleep(poll_seconds)
        else:
            time.sleep(max(15, poll_seconds))

        if max_cycles is not None and cycle_count >= max_cycles:
            logger.info("Max cycles reached (%s), exiting trading loop", max_cycles)
            break


def parse_args():
    parser = argparse.ArgumentParser(description="Run Zerodha intraday trading bot")
    parser.add_argument("--dry-run", action="store_true", help="Do not place real orders")
    parser.add_argument("--poll-seconds", type=int, default=30, help="Polling interval in seconds")
    parser.add_argument("--max-cycles", type=int, default=None, help="Optional max loop cycles before exit")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        kite = create_kite_client()
        run_trading_loop(
            kite=kite,
            poll_seconds=max(5, args.poll_seconds),
            max_cycles=args.max_cycles,
            dry_run=args.dry_run,
        )
    except KeyboardInterrupt:
        logger.info("Trading bot stopped by user.")
    except Exception as exc:
        logger.exception("Unexpected error in trading bot: %s", exc)
        raise


if __name__ == "__main__":
    main()
