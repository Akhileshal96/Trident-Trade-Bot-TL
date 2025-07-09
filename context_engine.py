import yfinance as yf

def detect_market_context():
    try:
        nifty = yf.download("^NSEI", period="5d", interval="1d")
        if len(nifty) < 2:
            return "neutral"

        change = (nifty['Close'].iloc[-1] - nifty['Close'].iloc[-2]) / nifty['Close'].iloc[-2] * 100

        if change > 0.3:
            return "bullish"
        elif change < -0.3:
            return "bearish"
        else:
            return "neutral"
    except Exception as e:
        print(f"⚠️ Error detecting market context: {e}")
        return "neutral"
