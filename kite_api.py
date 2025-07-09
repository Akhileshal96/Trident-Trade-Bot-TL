from kiteconnect import KiteConnect, KiteTicker import pandas as pd import logging import os from dotenv import load_dotenv

load_dotenv()

KITE_API_KEY = os.getenv("KITE_API_KEY") ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")

kite = KiteConnect(api_key=KITE_API_KEY) kite.set_access_token(ZERODHA_ACCESS_TOKEN)

def get_ltp(symbol): try: quote = kite.ltp([symbol]) return quote[symbol]['last_price'] except Exception as e: logging.error(f"Error getting LTP for {symbol}: {e}") return None

def get_historical_data(symbol, interval, days): try: instrument = kite.ltp([symbol]) token = list(instrument[symbol].values())[0]['instrument_token'] df = pd.DataFrame(kite.historical_data( instrument_token=token, from_date=pd.Timestamp.today() - pd.Timedelta(days=days), to_date=pd.Timestamp.today(), interval=interval )) return df except Exception as e: logging.error(f"Error getting historical data for {symbol}: {e}") return pd.DataFrame()

def place_order(symbol, qty, transaction_type): try: return kite.place_order( variety=kite.VARIETY_REGULAR, exchange=kite.EXCHANGE_NSE, tradingsymbol=symbol, transaction_type=transaction_type, quantity=qty, product=kite.PRODUCT_MIS, order_type=kite.ORDER_TYPE_MARKET ) except Exception as e: logging.error(f"Order placement failed for {symbol}: {e}") return None

def e_order(symbol, qty): return place_order(symbol, qty, kite.TRANSACTION_TYPE_SELL)

def b_order(symbol, qty): return place_order(symbol, qty, kite.TRANSACTION_TYPE_BUY)

