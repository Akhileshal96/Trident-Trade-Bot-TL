import os
from dotenv import load_dotenv

load_dotenv()

# Zerodha Kite Connect configuration
KITE_API_KEY = os.getenv("KITE_API_KEY")
KITE_API_SECRET = os.getenv("KITE_API_SECRET")
KITE_ACCESS_TOKEN = os.getenv("KITE_ACCESS_TOKEN")

# Telegram Bot configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def missing_env_vars(*keys):
    """Return a list of missing/blank env var names."""
    missing = []
    for key in keys:
        value = os.getenv(key)
        if value is None or not value.strip():
            missing.append(key)
    return missing
