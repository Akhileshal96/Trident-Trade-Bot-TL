import pandas as pd
import numpy as np

def calculate_ema(data, period=20):
    return data['Close'].ewm(span=period, adjust=False).mean()

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def should_enter_trade(data, market_trend):
    data = data.copy()
    data['EMA20'] = calculate_ema(data, 20)
    data['RSI'] = calculate_rsi(data)
    data['MACD'], data['MACD_signal'] = calculate_macd(data)

    latest = data.iloc[-1]

    trend_match = (
        (market_trend == 'bullish' and latest['EMA20'] < latest['Close']) or
        (market_trend == 'bearish' and latest['EMA20'] > latest['Close'])
    )

    rsi_condition = (
        latest['RSI'] > 50 if market_trend == 'bullish'
        else latest['RSI'] < 50
    )

    macd_condition = (
        latest['MACD'] > latest['MACD_signal'] if market_trend == 'bullish'
        else latest['MACD'] < latest['MACD_signal']
    )

    if trend_match and rsi_condition and macd_condition:
        return True

    return False
