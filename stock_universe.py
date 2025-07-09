import requests

def fetch_nse_symbols(index="NIFTY 50"):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    url_map = {
        "NIFTY 50": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050",
        "BANKNIFTY": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK",
        "FINNIFTY": "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20FINANCIAL%20SERVICES"
    }
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        res = session.get(url_map.get(index, ""), headers=headers)
        data = res.json().get("data", [])
        return [stock["symbol"] + ".NS" for stock in data]
    except Exception as e:
        print(f"⚠️ Error fetching live index data: {e}")
        return []

def get_nifty_50_stocks():
    return fetch_nse_symbols("NIFTY 50")
