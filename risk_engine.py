import os

MAX_LOSS = float(os.getenv("MAX_LOSS", 3000))
MAX_PROFIT = float(os.getenv("MAX_PROFIT", 3000))
WALLET_CAPITAL = float(os.getenv("WALLET_CAPITAL", 1000))

def calculate_position_size(capital, entry_price, stop_loss_price):
    risk_per_trade = capital * 0.02  # risking 2% per trade
    sl_distance = abs(entry_price - stop_loss_price)
    if sl_distance == 0:
        return 0
    quantity = int(risk_per_trade / sl_distance)
    return max(quantity, 1)

def should_exit_trade(ltp, sl, target):
    return ltp <= sl or ltp >= target

def check_risk_limits():
    # This function should read from a runtime performance log or shared state
    # For now, it returns True by default
    return True
