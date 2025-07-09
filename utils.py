import pandas as pd
from kite_api import kite

def get_candles(symbol, interval="5minute", days=2):
    from datetime import datetime, timedelta
    try:
        instrument = f"NSE:{symbol}"
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days)
        candles = kite.historical_data(
            instrument_token=kite.ltp(instrument)[instrument]["instrument_token"],
            from_date=from_date,
            to_date=to_date,
            interval=interval
        )
        df = pd.DataFrame(candles)
        df["datetime"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        print(f"Error fetching candles for {symbol}: {e}")
        return pd.DataFrame()

def calculate_ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df["close"].ewm(span=fast, adjust=False).mean()
    exp2 = df["close"].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line
