from kite_api import get_historical_data, place_order, e_order, get_ltp
from telegram_bot import start_telegram_bot
from stock_universe import get_nifty_50_stocks
from context_engine import detect_market_context
from strategy_engine_v2 import should_enter_trade
from risk_engine import calculate_position_size, should_exit_trade
from performance_logger import log_trade
from state_manager import is_bot_running
import time
import os

WALLET_CAPITAL = float(os.getenv("WALLET_CAPITAL", 1000))
MAX_PROFIT = float(os.getenv("MAX_PROFIT", 3000))
MAX_LOSS = float(os.getenv("MAX_LOSS", 1000))

daily_profit = 0
daily_loss = 0
open_positions = {}

def run_bot():
    global daily_profit, daily_loss
    print("🚀 Trident Bot Started")

    while True:
        if not is_bot_running():
            print("⏸️ Bot paused. Waiting to resume...")
            time.sleep(10)
            continue

        trend = detect_market_context()
        print(f"📈 Market Trend: {trend}")

        stocks = get_nifty_50_stocks()
        for stock in stocks:
            try:
                ltp = get_ltp(stock)
                data = get_historical_data(stock, interval="5minute", days=3)

                if should_enter_trade(data, trend):
                    if stock in open_positions:
                        continue  # Already in trade

                    sl, target = data['Close'].iloc[-1] * 0.98, data['Close'].iloc[-1] * 1.03
                    qty = calculate_position_size(WALLET_CAPITAL, data['Close'].iloc[-1], sl)

                    order_id = place_order(stock, qty, "BUY")
                    open_positions[stock] = {
                        "qty": qty,
                        "entry": ltp,
                        "sl": sl,
                        "target": target,
                        "order_id": order_id
                    }
                    log_trade(stock, "BUY", ltp, qty)
                    print(f"🟢 Entered trade: {stock} at {ltp}")

                elif stock in open_positions:
                    position = open_positions[stock]
                    if should_exit_trade(ltp, position["sl"], position["target"]):
                        e_order(stock, position["qty"])
                        pnl = (ltp - position["entry"]) * position["qty"]
                        daily_profit += pnl if pnl > 0 else 0
                        daily_loss += -pnl if pnl < 0 else 0
                        log_trade(stock, "SELL", ltp, position["qty"], pnl)
                        print(f"🔴 Exited trade: {stock} at {ltp}, PnL: ₹{pnl:.2f}")
                        del open_positions[stock]

                # Risk management
                if daily_profit >= MAX_PROFIT:
                    print(f"🎯 Daily profit target ₹{MAX_PROFIT} hit. Stopping bot.")
                    break
                if daily_loss >= MAX_LOSS:
                    print(f"⚠️ Daily loss limit ₹{MAX_LOSS} hit. Stopping bot.")
                    break

            except Exception as e:
                print(f"⚠️ Error processing {stock}: {e}")

        time.sleep(60)  # wait before next cycle

if __name__ == "__main__":
    import threading
    bot_thread = threading.Thread(target=start_telegram_bot)
    bot_thread.start()
    run_bot()
